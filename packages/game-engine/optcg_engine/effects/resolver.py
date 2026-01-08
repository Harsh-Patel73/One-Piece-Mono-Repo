"""
Effect resolver for One Piece TCG.

Executes parsed Effect objects against the game state.
"""

from typing import List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass
import random

from .effects import (
    Effect, EffectType, EffectTiming, TargetType, Duration,
    TargetRestriction
)

if TYPE_CHECKING:
    from game_engine import GameState, Player
    from models.cards import Card


@dataclass
class EffectContext:
    """Context for effect resolution."""
    game_state: 'GameState'
    source_card: 'Card'
    source_player: 'Player'
    opponent: 'Player'
    targets: List['Card'] = None

    def __post_init__(self):
        if self.targets is None:
            self.targets = []


@dataclass
class EffectResult:
    """Result of effect resolution."""
    success: bool
    message: str = ""
    state_changed: bool = False
    targets_affected: List['Card'] = None

    def __post_init__(self):
        if self.targets_affected is None:
            self.targets_affected = []


class EffectResolver:
    """
    Resolves (executes) parsed effects against the game state.
    """

    def __init__(self):
        # Map effect types to handler methods
        self.handlers = {
            EffectType.DRAW: self._resolve_draw,
            EffectType.KO: self._resolve_ko,
            EffectType.REST: self._resolve_rest,
            EffectType.POWER_BOOST: self._resolve_power_boost,
            EffectType.POWER_REDUCE: self._resolve_power_reduce,
            EffectType.DON_ADD: self._resolve_don_add,
            EffectType.DON_ACTIVATE: self._resolve_don_activate,
            EffectType.DON_REST: self._resolve_don_rest,
            EffectType.PLAY: self._resolve_play,
            EffectType.RETURN_TO_DECK: self._resolve_return_to_deck,
            EffectType.PROTECT: self._resolve_protect,
            EffectType.LIFE_ADD: self._resolve_life_add,
            EffectType.SEARCH: self._resolve_search,
            EffectType.DISCARD: self._resolve_discard,
            EffectType.REMOVE_BLOCKER: self._resolve_remove_blocker,
            EffectType.GRANT_RUSH: self._resolve_grant_rush,
            EffectType.GRANT_BLOCKER: self._resolve_grant_blocker,
            EffectType.RETURN_TO_HAND: self._resolve_return_to_hand,
            EffectType.DON_ATTACH: self._resolve_don_attach,
            EffectType.TRASH: self._resolve_trash,
            EffectType.COST_REDUCE: self._resolve_cost_reduce,
            EffectType.LOOK: self._resolve_look,
            EffectType.GRANT_BANISH: self._resolve_grant_banish,
            EffectType.GRANT_DOUBLE_ATTACK: self._resolve_grant_double_attack,
            EffectType.LIFE_DAMAGE: self._resolve_life_damage,
            EffectType.REVEAL: self._resolve_reveal,
            EffectType.NEGATE: self._resolve_negate,
            EffectType.ACTIVATE: self._resolve_activate,
        }

    def can_resolve(self, effect: Effect, context: EffectContext) -> bool:
        """
        Check if an effect can be resolved in the current context.

        Validates:
        - DON requirements are met
        - Timing is appropriate
        - Valid targets exist
        - Cost can be paid
        """
        # Check DON requirement
        if effect.don_requirement > 0:
            attached_don = getattr(context.source_card, 'attached_don', 0)
            if attached_don < effect.don_requirement:
                return False

        # Check cost
        if effect.cost:
            if not self._can_pay_cost(effect.cost, context):
                return False

        # Check for valid targets
        if effect.target_type:
            targets = self.get_valid_targets(effect, context)
            if not targets and effect.target_count > 0:
                return False

        return True

    def _can_pay_cost(self, cost, context: EffectContext) -> bool:
        """Check if the cost can be paid."""
        player = context.source_player

        if cost.don_rest > 0:
            active_don = player.don_pool.count("active")
            if active_don < cost.don_rest:
                return False

        if cost.discard > 0:
            if len(player.hand) < cost.discard:
                return False

        if cost.trash_return > 0:
            if len(player.trash) < cost.trash_return:
                return False

        if cost.life_to_hand > 0:
            if len(player.life_cards) < cost.life_to_hand:
                return False

        return True

    def get_valid_targets(
        self,
        effect: Effect,
        context: EffectContext
    ) -> List['Card']:
        """
        Get all valid targets for an effect.

        Used for both validation and AI target selection.
        """
        targets = []
        restriction = effect.target_restriction

        # Determine the pool of potential targets
        if effect.target_type == TargetType.SELF:
            return [context.source_card]

        elif effect.target_type == TargetType.YOUR_CHARACTER:
            targets = list(context.source_player.cards_in_play)

        elif effect.target_type == TargetType.YOUR_CHARACTERS:
            return list(context.source_player.cards_in_play)

        elif effect.target_type == TargetType.OPPONENT_CHARACTER:
            targets = list(context.opponent.cards_in_play)

        elif effect.target_type == TargetType.OPPONENT_CHARACTERS:
            return list(context.opponent.cards_in_play)

        elif effect.target_type == TargetType.YOUR_LEADER:
            return [context.source_player.leader]

        elif effect.target_type == TargetType.OPPONENT_LEADER:
            return [context.opponent.leader]

        elif effect.target_type == TargetType.YOUR_HAND:
            targets = list(context.source_player.hand)

        elif effect.target_type == TargetType.YOUR_TRASH:
            targets = list(context.source_player.trash)

        elif effect.target_type == TargetType.ANY_CHARACTER:
            targets = (
                list(context.source_player.cards_in_play) +
                list(context.opponent.cards_in_play)
            )

        # Apply restrictions
        if restriction and targets:
            targets = self._filter_by_restriction(targets, restriction)

        return targets

    def _filter_by_restriction(
        self,
        cards: List['Card'],
        restriction: TargetRestriction
    ) -> List['Card']:
        """Filter cards by target restriction."""
        result = []

        for card in cards:
            if restriction.cost_max is not None:
                cost = card.cost or 0
                if cost > restriction.cost_max:
                    continue

            if restriction.cost_min is not None:
                cost = card.cost or 0
                if cost < restriction.cost_min:
                    continue

            if restriction.power_max is not None:
                power = card.power or 0
                power += getattr(card, 'attached_don', 0) * 1000
                if power > restriction.power_max:
                    continue

            if restriction.power_min is not None:
                power = card.power or 0
                power += getattr(card, 'attached_don', 0) * 1000
                if power < restriction.power_min:
                    continue

            if restriction.colors:
                card_colors = card.colors or []
                if not any(c in restriction.colors for c in card_colors):
                    continue

            if restriction.types:
                card_type = card.card_origin or ""
                if not any(t in card_type for t in restriction.types):
                    continue

            if restriction.is_resting is not None:
                if card.is_resting != restriction.is_resting:
                    continue

            result.append(card)

        return result

    def resolve(
        self,
        effect: Effect,
        context: EffectContext,
        chosen_targets: List['Card'] = None
    ) -> EffectResult:
        """
        Resolve an effect.

        Args:
            effect: The effect to resolve
            context: Effect context (game state, source card, etc.)
            chosen_targets: Targets chosen by player/AI (if applicable)

        Returns:
            EffectResult indicating success/failure
        """
        # Pay cost first
        if effect.cost:
            self._pay_cost(effect.cost, context)

        # Get handler
        handler = self.handlers.get(effect.effect_type)
        if not handler:
            return EffectResult(
                success=False,
                message=f"No handler for effect type: {effect.effect_type}"
            )

        # Set targets
        if chosen_targets:
            context.targets = chosen_targets
        elif effect.target_type:
            # Auto-select targets for AI
            valid_targets = self.get_valid_targets(effect, context)
            count = min(effect.target_count, len(valid_targets))
            context.targets = valid_targets[:count]

        # Execute
        return handler(effect, context)

    def _pay_cost(self, cost, context: EffectContext):
        """Pay the cost of an effect."""
        player = context.source_player

        # Rest DON
        for _ in range(cost.don_rest):
            if "active" in player.don_pool:
                idx = player.don_pool.index("active")
                player.don_pool[idx] = "rested"

        # Discard (auto-select last cards for AI)
        for _ in range(cost.discard):
            if player.hand:
                card = player.hand.pop()
                player.trash.append(card)

        # Return from trash to deck
        for _ in range(cost.trash_return):
            if player.trash:
                card = player.trash.pop()
                player.deck.append(card)

        # Life to hand
        for _ in range(cost.life_to_hand):
            if player.life_cards:
                card = player.life_cards.pop()
                player.hand.append(card)

    # Effect handlers

    def _resolve_draw(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle draw effect."""
        player = context.source_player
        count = effect.value
        drawn = []

        for _ in range(count):
            if player.deck:
                card = player.deck.pop(0)
                player.hand.append(card)
                drawn.append(card)
                print(f"{player.name} draws {card.name}")

        return EffectResult(
            success=True,
            message=f"Drew {len(drawn)} card(s)",
            state_changed=len(drawn) > 0,
            targets_affected=drawn,
        )

    def _resolve_ko(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle KO effect."""
        targets = context.targets
        ko_count = 0

        for target in targets:
            # Find which player owns this card
            if target in context.source_player.cards_in_play:
                context.source_player.cards_in_play.remove(target)
                context.source_player.trash.append(target)
                ko_count += 1
                print(f"{target.name} is K.O.'d!")
            elif target in context.opponent.cards_in_play:
                context.opponent.cards_in_play.remove(target)
                context.opponent.trash.append(target)
                ko_count += 1
                print(f"{target.name} is K.O.'d!")

        return EffectResult(
            success=ko_count > 0,
            message=f"K.O.'d {ko_count} character(s)",
            state_changed=ko_count > 0,
            targets_affected=targets[:ko_count],
        )

    def _resolve_rest(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle rest effect."""
        targets = context.targets
        rested = []

        for target in targets:
            if not target.is_resting:
                target.is_resting = True
                rested.append(target)
                print(f"{target.name} is rested")

        return EffectResult(
            success=len(rested) > 0,
            message=f"Rested {len(rested)} card(s)",
            state_changed=len(rested) > 0,
            targets_affected=rested,
        )

    def _resolve_power_boost(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle power boost effect."""
        targets = context.targets
        boosted = []

        for target in targets:
            # Add power modifier
            current_mod = getattr(target, 'power_modifier', 0)
            target.power_modifier = current_mod + effect.value
            boosted.append(target)
            print(f"{target.name} gains +{effect.value} power")

        return EffectResult(
            success=len(boosted) > 0,
            message=f"Boosted {len(boosted)} card(s) by {effect.value}",
            state_changed=len(boosted) > 0,
            targets_affected=boosted,
        )

    def _resolve_power_reduce(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle power reduction effect."""
        targets = context.targets
        reduced = []

        for target in targets:
            if effect.value == 0:
                # Set to 0
                target.power_modifier = -(target.power or 0)
                print(f"{target.name}'s power is set to 0")
            else:
                current_mod = getattr(target, 'power_modifier', 0)
                target.power_modifier = current_mod - effect.value
                print(f"{target.name} gets -{effect.value} power")
            reduced.append(target)

        return EffectResult(
            success=len(reduced) > 0,
            message=f"Reduced power of {len(reduced)} card(s)",
            state_changed=len(reduced) > 0,
            targets_affected=reduced,
        )

    def _resolve_don_add(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle add DON effect."""
        player = context.source_player
        count = effect.value
        current = len(player.don_pool)
        new_total = min(current + count, 10)
        added = new_total - current

        player.don_pool.extend(["rested"] * added)  # Added DON is rested by default
        print(f"{player.name} adds {added} DON")

        return EffectResult(
            success=added > 0,
            message=f"Added {added} DON",
            state_changed=added > 0,
        )

    def _resolve_don_activate(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle DON activation effect."""
        player = context.source_player
        count = effect.target_count
        activated = 0

        for i in range(len(player.don_pool)):
            if player.don_pool[i] == "rested" and activated < count:
                player.don_pool[i] = "active"
                activated += 1

        print(f"{player.name} activates {activated} DON")

        return EffectResult(
            success=activated > 0,
            message=f"Activated {activated} DON",
            state_changed=activated > 0,
        )

    def _resolve_don_rest(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle DON rest effect."""
        player = context.source_player
        if effect.target_type == TargetType.OPPONENT_DON:
            player = context.opponent

        count = effect.target_count
        rested = 0

        for i in range(len(player.don_pool)):
            if player.don_pool[i] == "active" and rested < count:
                player.don_pool[i] = "rested"
                rested += 1

        return EffectResult(
            success=rested > 0,
            message=f"Rested {rested} DON",
            state_changed=rested > 0,
        )

    def _resolve_play(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle play card effect."""
        # Check field limit for characters (max 5)
        char_count = sum(1 for c in context.source_player.cards_in_play if c.card_type == "CHARACTER")

        if effect.target_type == TargetType.SELF:
            # Play this card (trigger effect)
            card = context.source_card
            if card.card_type == "CHARACTER" and char_count >= 5:
                print(f"Cannot play {card.name}: field is full (5 characters max).")
                return EffectResult(success=False, message="Field is full")
            if card in context.source_player.trash:
                context.source_player.trash.remove(card)
                context.source_player.cards_in_play.append(card)
                print(f"{card.name} is played from trigger")
                return EffectResult(success=True, state_changed=True)

        # Play from hand
        targets = context.targets
        if targets:
            card = targets[0]
            if card.card_type == "CHARACTER" and char_count >= 5:
                print(f"Cannot play {card.name}: field is full (5 characters max).")
                return EffectResult(success=False, message="Field is full")
            if card in context.source_player.hand:
                context.source_player.hand.remove(card)
                context.source_player.cards_in_play.append(card)
                print(f"{card.name} is played for free")
                return EffectResult(success=True, state_changed=True)

        return EffectResult(success=False, message="No valid card to play")

    def _resolve_return_to_deck(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle return to deck effect."""
        targets = context.targets
        returned = 0

        for target in targets:
            if target in context.source_player.trash:
                context.source_player.trash.remove(target)
                context.source_player.deck.append(target)
                returned += 1

        return EffectResult(
            success=returned > 0,
            message=f"Returned {returned} card(s) to deck",
            state_changed=returned > 0,
        )

    def _resolve_protect(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle protection effect."""
        targets = context.targets if context.targets else [context.source_card]

        for target in targets:
            target.has_protection = True
            print(f"{target.name} cannot be K.O.'d this turn")

        return EffectResult(
            success=True,
            message="Protection granted",
            state_changed=True,
            targets_affected=targets,
        )

    def _resolve_life_add(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle add to life effect."""
        player = context.source_player
        count = effect.value

        if player.deck:
            for _ in range(min(count, len(player.deck))):
                card = player.deck.pop(0)
                player.life_cards.append(card)
            print(f"{player.name} adds {count} card(s) to life")
            return EffectResult(success=True, state_changed=True)

        return EffectResult(success=False, message="No cards in deck")

    def _resolve_search(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle search/look effect."""
        # For AI, just reveal that we looked
        count = effect.value
        print(f"{context.source_player.name} looks at top {count} cards of deck")

        return EffectResult(
            success=True,
            message=f"Looked at {count} cards",
            state_changed=False,
        )

    def _resolve_discard(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle discard effect."""
        targets = context.targets
        discarded = 0

        for target in targets:
            if target in context.source_player.hand:
                context.source_player.hand.remove(target)
                context.source_player.trash.append(target)
                discarded += 1

        return EffectResult(
            success=discarded > 0,
            message=f"Discarded {discarded} card(s)",
            state_changed=discarded > 0,
        )

    def _resolve_remove_blocker(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle remove blocker effect."""
        # This is typically a restriction on opponents
        # Mark the card as having this effect active
        context.source_card.blocks_blockers = True

        return EffectResult(
            success=True,
            message="Blocker restriction applied",
            state_changed=True,
        )

    def _resolve_grant_rush(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle grant Rush effect."""
        target = context.source_card
        target.has_rush = True

        return EffectResult(
            success=True,
            message=f"{target.name} has Rush",
            state_changed=True,
        )

    def _resolve_grant_blocker(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle grant Blocker effect."""
        target = context.source_card
        target.has_blocker = True

        return EffectResult(
            success=True,
            message=f"{target.name} has Blocker",
            state_changed=True,
        )

    def _resolve_return_to_hand(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle return to hand effect."""
        targets = context.targets
        returned = 0

        for target in targets:
            # Check which zone the card is in and return it
            if target in context.source_player.cards_in_play:
                context.source_player.cards_in_play.remove(target)
                context.source_player.hand.append(target)
                returned += 1
                print(f"{target.name} returned to hand")
            elif target in context.opponent.cards_in_play:
                context.opponent.cards_in_play.remove(target)
                context.opponent.hand.append(target)
                returned += 1
                print(f"{target.name} returned to opponent's hand")

        return EffectResult(
            success=returned > 0,
            message=f"Returned {returned} card(s) to hand",
            state_changed=returned > 0,
            targets_affected=targets[:returned],
        )

    def _resolve_don_attach(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle DON attachment effect."""
        targets = context.targets if context.targets else [context.source_player.leader]
        count = effect.target_count
        attached = 0

        # Check if we have rested DON to attach
        rested_don = context.source_player.don_pool.count("rested")
        attach_count = min(count, rested_don)

        if attach_count > 0 and targets:
            target = targets[0]
            current_don = getattr(target, 'attached_don', 0)
            target.attached_don = current_don + attach_count

            # Remove DON from rested pool (they're now attached to card)
            for _ in range(attach_count):
                if "rested" in context.source_player.don_pool:
                    context.source_player.don_pool.remove("rested")
                    attached += 1

            print(f"Attached {attached} DON to {target.name}")

        return EffectResult(
            success=attached > 0,
            message=f"Attached {attached} DON to card",
            state_changed=attached > 0,
        )

    def _resolve_trash(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle trash effect."""
        targets = context.targets
        trashed = 0

        for target in targets:
            if target in context.source_player.cards_in_play:
                context.source_player.cards_in_play.remove(target)
                context.source_player.trash.append(target)
                trashed += 1
                print(f"{target.name} trashed")
            elif target in context.opponent.cards_in_play:
                context.opponent.cards_in_play.remove(target)
                context.opponent.trash.append(target)
                trashed += 1
                print(f"{target.name} trashed")
            elif target in context.source_player.hand:
                context.source_player.hand.remove(target)
                context.source_player.trash.append(target)
                trashed += 1
                print(f"{target.name} trashed from hand")

        return EffectResult(
            success=trashed > 0,
            message=f"Trashed {trashed} card(s)",
            state_changed=trashed > 0,
            targets_affected=targets[:trashed],
        )

    def _resolve_cost_reduce(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle cost reduction effect."""
        # Cost reduction is typically applied as a modifier on the card
        target = context.source_card
        current_reduction = getattr(target, 'cost_reduction', 0)
        target.cost_reduction = current_reduction + effect.value

        print(f"{target.name} cost reduced by {effect.value}")

        return EffectResult(
            success=True,
            message=f"Cost reduced by {effect.value}",
            state_changed=True,
        )

    def _resolve_look(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle look at cards effect (life manipulation)."""
        count = effect.value
        player = context.source_player

        # For life card manipulation
        if effect.target_type == TargetType.YOUR_LIFE:
            if player.life_cards:
                # Look at top card of life (for AI, just log it)
                top_card = player.life_cards[-1] if player.life_cards else None
                if top_card:
                    print(f"{player.name} looks at top Life card: {top_card.name}")
                    return EffectResult(
                        success=True,
                        message=f"Looked at {count} Life card(s)",
                        state_changed=False,
                    )

        elif effect.target_type == TargetType.OPPONENT_LEADER:
            # Looking at opponent's life
            opponent = context.opponent
            if opponent.life_cards:
                top_card = opponent.life_cards[-1] if opponent.life_cards else None
                if top_card:
                    print(f"{player.name} looks at opponent's top Life card")
                    return EffectResult(
                        success=True,
                        message=f"Looked at opponent's Life card",
                        state_changed=False,
                    )

        return EffectResult(
            success=False,
            message="No cards to look at",
            state_changed=False,
        )

    def _resolve_grant_banish(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle grant Banish effect."""
        targets = context.targets if context.targets else [context.source_card]

        for target in targets:
            target.has_banish = True
            print(f"{target.name} has Banish")

        return EffectResult(
            success=True,
            message="Banish granted",
            state_changed=True,
            targets_affected=targets,
        )

    def _resolve_grant_double_attack(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle grant Double Attack effect."""
        targets = context.targets if context.targets else [context.source_card]

        for target in targets:
            target.has_doubleattack = True
            print(f"{target.name} has Double Attack")

        return EffectResult(
            success=True,
            message="Double Attack granted",
            state_changed=True,
            targets_affected=targets,
        )

    def _resolve_life_damage(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle deal life damage effect."""
        count = effect.value if effect.value > 0 else 1
        opponent = context.opponent
        damaged = 0

        for _ in range(count):
            if opponent.life_cards:
                life_card = opponent.life_cards.pop()
                # Check for trigger (will be handled separately)
                has_trigger = bool(life_card.trigger and life_card.trigger.strip())
                opponent.trash.append(life_card)
                damaged += 1
                print(f"{opponent.name} takes life damage! ({len(opponent.life_cards)} remaining)")

        return EffectResult(
            success=damaged > 0,
            message=f"Dealt {damaged} life damage",
            state_changed=damaged > 0,
        )

    def _resolve_reveal(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle reveal cards effect."""
        count = effect.value if effect.value > 0 else 1
        player = context.source_player

        if effect.target_type == TargetType.YOUR_HAND:
            # Reveal from hand
            cards_to_reveal = player.hand[:count]
            print(f"{player.name} reveals from hand: {[c.name for c in cards_to_reveal]}")
            return EffectResult(success=True, message=f"Revealed {len(cards_to_reveal)} cards")

        elif effect.target_type == TargetType.YOUR_DECK:
            # Reveal from top of deck
            cards_to_reveal = player.deck[:count]
            print(f"{player.name} reveals from deck: {[c.name for c in cards_to_reveal]}")
            return EffectResult(success=True, message=f"Revealed {len(cards_to_reveal)} cards")

        elif effect.target_type == TargetType.YOUR_LIFE:
            # Reveal life card
            if player.life_cards:
                top_card = player.life_cards[-1]
                print(f"{player.name} reveals top Life card: {top_card.name}")
                return EffectResult(success=True, message="Revealed life card")

        return EffectResult(success=False, message="Nothing to reveal")

    def _resolve_negate(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle negate effect."""
        # Mark that there's an active negation
        # This is checked during effect resolution
        context.game_state.pending_negate = True
        print(f"{context.source_card.name} negates an effect")

        return EffectResult(
            success=True,
            message="Effect negated",
            state_changed=True,
        )

    def _resolve_activate(self, effect: Effect, context: EffectContext) -> EffectResult:
        """Handle activate/unrest effect."""
        targets = context.targets

        if not targets and effect.target_type == TargetType.SELF:
            targets = [context.source_card]

        activated = []
        for target in targets:
            if target.is_resting:
                target.is_resting = False
                activated.append(target)
                print(f"{target.name} is activated (unrested)")

        return EffectResult(
            success=len(activated) > 0,
            message=f"Activated {len(activated)} card(s)",
            state_changed=len(activated) > 0,
            targets_affected=activated,
        )


# Singleton resolver
_resolver: Optional[EffectResolver] = None


def get_resolver() -> EffectResolver:
    """Get the singleton resolver instance."""
    global _resolver
    if _resolver is None:
        _resolver = EffectResolver()
    return _resolver


def resolve_effect(
    effect: Effect,
    game_state: 'GameState',
    source_card: 'Card',
    source_player: 'Player',
    targets: List['Card'] = None
) -> EffectResult:
    """
    Convenience function to resolve an effect.

    Args:
        effect: The parsed effect to resolve
        game_state: Current game state
        source_card: Card that triggered the effect
        source_player: Player who controls the source card
        targets: Chosen targets (optional, will auto-select if not provided)

    Returns:
        EffectResult
    """
    # Determine opponent
    if game_state.current_player == source_player:
        opponent = game_state.opponent_player
    else:
        opponent = game_state.current_player

    context = EffectContext(
        game_state=game_state,
        source_card=source_card,
        source_player=source_player,
        opponent=opponent,
        targets=targets or [],
    )

    resolver = get_resolver()
    return resolver.resolve(effect, context, targets)
