# OPTCG Monorepo — Claude Session Guide

## Project Structure

```
packages/
  game-engine/optcg_engine/        # Core Python game engine
    game_engine.py                 # GameState, Player, PendingChoice, resolve_pending_choice
    effects/
      effect_registry.py           # create_* helpers, register_effect, utility fns
      sets/op01_effects.py         # OP01 hardcoded effects
      sets/op02_effects.py         # OP02 hardcoded effects
      CARD_STATUS.md               # Per-card implementation status (column order: ID | Status | Type | Notes)
      PENDING_FIXES.jsonl          # Bug reports — NEVER mark fixed_at; only user does that
  simulator/
    backend/                       # FastAPI + Socket.IO server
      main.py                      # Entry point: socket_app (NOT app)
      game/effect_test_session.py  # Test scenario builder for effect tester
      realtime/socket_handlers.py  # Socket event handlers
    frontend/src/
      hooks/usePlaytestSocket.ts   # BackendCard/Player → PlaytestCard/Player conversion
      pages/EffectTesterPage.tsx   # Full game UI (PlayerBoard, CardDisplay, combat)
```

## Running the Servers

**Backend:** `cd packages/simulator/backend && python -m uvicorn main:socket_app --host 0.0.0.0 --port 8000 --reload`
- Must use `main:socket_app` (not `main:app`) — socket_app wraps FastAPI with Socket.IO ASGI

**Frontend:** `cd packages/simulator/frontend && npm run dev`

---

## Common Effect Patterns

### Registering Effects
```python
from ..hardcoded import register_effect, get_opponent, draw_cards, ...

@register_effect("OP01-001", "on_play", "[On Play] Description")
def card_effect(game_state, player, card):
    ...
    return True  # return True if effect fired, False if conditions not met
```

**Timing strings** (always lowercase):
- `on_play` — when card is played from hand (characters and events)
- `on_attack` / `when_attacking` — when this card attacks (check `attached_don` for DON!! conditions)
- `continuous` — passive; re-evaluated each turn via `_apply_continuous_effects()`
- `on_ko` — when this card is KO'd
- `blocker` — sets `card.has_blocker = True` (DON!! condition checked in `_can_block`)
- `counter` — when played as a counter card
- `activate` — Activate: Main effect (once per turn, rests the card)
- `on_block` — when this card is used as a blocker
- `on_don_attached` — fires on the leader when any card receives DON (e.g. Garp)
- `end_of_turn` — fires at end of current player's turn (e.g. Whitebeard leader)
- `on_event` — fires on the leader when player activates an Event card

**IMPORTANT:** Register timings in lowercase even if the description uses uppercase. The system normalizes to lowercase but duplicate registrations (uppercase + lowercase) both fire — avoid duplicates.

### Power Effects
```python
# Apply power modifier to selected targets (opponent or own cards)
from ..hardcoded import create_power_effect_choice

return create_power_effect_choice(
    game_state, player, targets, -3000,    # 4th arg is positional (power_amount) — do NOT use keyword power_change
    source_card=card,
    prompt="Choose opponent's Character to give -3000 power",
    min_selections=0,   # 0 = optional (player can skip)
    max_selections=2,   # up to N targets
)
```
- `power_modifier` is transient; cleared by `_clear_temporary_effects()` at end of turn
- To persist until end of NEXT turn: use callback `apply_power_until_next_turn` and set `power_modifier_expires_on_turn = turn_count + 1`
- `_clear_temporary_effects` now checks `power_modifier_expires_on_turn` before clearing

### Power Until Next Turn (e.g. OP02-004 Whitebeard)
Use callback action `"apply_power_until_next_turn"` in a PendingChoice with `power_amount` in callback_data. The callback sets `card.power_modifier_expires_on_turn = self.turn_count + 1`.

### Multi-target Power
Use `create_power_effect_choice` with `max_selections=N` — it uses `apply_power` callback which iterates over all selected indices.

### KO Effects
```python
from ..hardcoded import create_ko_choice

return create_ko_choice(game_state, player, targets, source_card=card,
                        prompt="Choose opponent's Character to K.O.")
```

### Cost Reduction
```python
from ..hardcoded import create_cost_reduction_choice

return create_cost_reduction_choice(game_state, player, targets, -1, source_card=card,
                                   prompt="Choose opponent's cost 7 or less to give -1 cost")
```

### Deck Search / Top-N Look
```python
from ..hardcoded import search_top_cards

return search_top_cards(game_state, player, 5, add_count=1,
                        filter_fn=lambda c: c.card_type == 'CHARACTER' and 'SMILE' in (c.card_origin or ''),
                        source_card=card, play_to_field=True,
                        prompt="Look at top 5. Choose a SMILE Character (cost 3 or less) to play.")
```
- `add_count=0` means optional (player can select 0)
- When `filter_fn` finds no valid cards, all 5 are still shown for ordering (player puts them at bottom)

### Deck Reorder (Top 3 → Top or Bottom)
```python
from ..hardcoded import reorder_top_cards

return reorder_top_cards(game_state, player, 3, source_card=card, allow_top=True)
# allow_top=True: player chooses all-to-top or all-to-bottom
# allow_top=False: sequential ordering, all placed at bottom
```

### DON Cost on Counter Cards
```python
from ..hardcoded import return_don_to_deck

auto = return_don_to_deck(game_state, player, 2, source_card=card,
                          after_callback="my_callback_key",
                          after_callback_data={"player_id": player.player_id})
```
The `after_callback` runs inside `resolve_pending_choice` when DON selection is complete.

### On KO Effect (returning card to play)
```python
@register_effect("OP02-018", "on_ko", "[On K.O.] Trash WB card from hand: return this to play rested")
def marco_ko(game_state, player, card):
    if len(player.life_cards) <= 2:
        for hand_card in player.hand:
            if 'Whitebeard Pirates' in (hand_card.card_origin or ''):
                player.hand.remove(hand_card)
                player.trash.append(hand_card)
                if card in player.trash:
                    player.trash.remove(card)
                    player.cards_in_play.append(card)
                    card.is_resting = True
                return True
    return False
```

### End of Turn Effects
Registered with `end_of_turn` timing. Fired in `_end_phase()` for the current player's leader and all field cards. Example: Whitebeard leader adds 1 Life to hand each turn end.

### On DON Attached Effects
Registered with `on_don_attached` timing. Fired in `attach_don()` on the current player's leader whenever any card receives DON. Example: Garp leader gives -1 cost to opponent's cost ≤7 character.

---

## Stage Cards

- `card_type == 'STAGE'` — identified by the field in Card
- Stage cards cannot attack (blocked in `initiate_attack()`)
- Stage cards cannot be targeted in battle (filtered in `get_valid_attack_targets()`)
- Stage cards display in their own section below the leader in the frontend
- Stage cards can use Activate: Main effects

---

## Frontend Data Flow

### BackendCard → PlaytestCard (usePlaytestSocket.ts)
- `card.power` = effective power (base + modifier) — used in card display
- `card.base_power` = base power — used to compute delta badge
- `card.card_type` → `cardType` — used to identify STAGE cards
- `card.don_pool` → `donPool` — pool of 'active'/'rested' strings

### Power/Cost Delta Display (EffectTesterPage.tsx CardDisplay)
```tsx
const powerDelta = (basePower !== null && card.power !== null) ? (card.power - basePower) : 0
// Red strip bottom if powerDown, green if powerUp
const costDelta = (baseCost !== null && card.cost !== null) ? (card.cost - baseCost) : 0
// Blue badge top-left if costDown
```

### Combat Power Display
- `pendingAttack.targetPower` = `defender.power + defender.power_modifier` (always includes modifiers)
- `pendingAttack.availableBlockers[i].power` = `blocker.power + blocker.power_modifier` (includes modifiers — fixed)

---

## Test Scenario Builder (effect_test_session.py)

### Adding Card-Specific Seeding
In `build_game_state()`, after the general timing setup:

```python
card_id = card_data.get("id", "")

# Cards needing Whitebeard Pirates leader
WB_LEADER_CARDS = {"OP02-001", "OP02-009", "OP02-021", ...}
if card_id in WB_LEADER_CARDS and tc.card_type != "LEADER":
    p1.leader = _wb_leader(4)
    p2.leader = _wb_leader(4)

# Cards needing SMILE cards in deck
if card_id in ("OP01-098", "OP01-116"):
    for i in range(3):
        p1.deck.insert(i, _smile(900 + i))
```

### Adding New Leader Archetypes
Add a factory function like `_wb_leader()` that creates a LEADER card with the correct `card_origin` type string.

---

## Known Pitfalls

1. **`power_change` vs `power_amount`**: `create_power_effect_choice` takes `power_amount` as a positional 4th arg. Never use `power_change=` as a keyword — it silently passes 0.

2. **Duplicate timing registrations**: If both `"ON_KO"` and `"on_ko"` are registered for the same card, both fire. Remove the uppercase/stale one.

3. **Event card timing**: Event effects must use `"on_play"` timing (not `"MAIN"`, `"main"`, etc.) to be triggered by `_trigger_on_play_effects()`.

4. **0-cost card DON spending**: The DON-spending loop breaks when `used >= cost`, so a `cost=0` correctly rests 0 DON. This was a past bug — the guard is in `play_card()`.

5. **CARD_STATUS.md column order**: Must be `| ID | Status | Type | Notes |` — the parser reads `parts[2]` as status. Wrong column order causes cards to not load in the tester.

6. **`socket_app` not `app`**: Uvicorn must use `main:socket_app` as the entry point.

7. **`_recalc_continuous_effects()`**: Called when a card is rested for attack (`attacker.is_resting = True`). Resets all `power_modifier` to 0 and reapplies continuous effects for both players. Blocker power includes modifier because `available_blockers` is built AFTER this call.
