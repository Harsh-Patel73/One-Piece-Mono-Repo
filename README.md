# OPTCG Monorepo Reference

This repository is the shared One Piece Card Game platform: a Python game engine, an AI training service, and a React/FastAPI simulator. This is the single project reference file. Keep implementation notes, effect audit findings, and onboarding details here so future set work has one source of truth.

## Project Map

```text
repo/
  monitoring/
    grafana/provisioning/datasources/    Grafana datasource config
    prometheus/                          Prometheus config and alerts
  packages/
    game-engine/                         Shared OPTCG engine package
      data/                              Card loading and scraping helpers
      decks/                             Example deck JSON files
      optcg_engine/
        core/                            Immutable-ish core state/action/phase models
        adapters/                        Mutable adapter surface
        effects/                         Parser, resolver, hardcoded registry, set files
        handlers/                        Older handler module
        models/                          Card and enum models
      scripts/                           Effect tester, status/report generators
      tests/                             Focused engine tests
    simulator/
      backend/                           FastAPI + Socket.IO game server
      frontend/                          React + Vite + Zustand client
    training/                            MCTS/neural-network training service
  docker-compose*.yml                    Local/dev/training orchestration
  op*_*.json, st_*.json                  Source card data dumps
```

## Runtime Shape

The project came from two codebases that overlap heavily in game rules. The desired end state is one shared `optcg_engine` used by the simulator, training, and testing flows.

| Area | Main files | Purpose |
| --- | --- | --- |
| Game engine | `packages/game-engine/optcg_engine/game_engine.py` | Mutable game state, turn flow, attacks, pending choices, effect hooks |
| Effect system | `packages/game-engine/optcg_engine/effects/effect_registry.py` | Hardcoded effect registry plus shared helper functions |
| Set effects | `packages/game-engine/optcg_engine/effects/sets/*_effects.py` | Per-card hardcoded registrations loaded by `sets/__init__.py` |
| Effect manager | `packages/game-engine/optcg_engine/effects/manager.py` | Parser fallback and timing bridge into hardcoded effects |
| Simulator backend | `packages/simulator/backend/game/manager.py` | Room/game management and pending-choice forwarding |
| Simulator frontend | `packages/simulator/frontend/src/App.tsx` | Routes for lobby, deck builder, playtest, and effect tester |
| Training | `packages/training/ai`, `packages/training/api` | MCTS, neural net, state encoding, and training API |

## Commands

```bash
# Full stack
docker compose up -d

# Development mode
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Training only
docker compose -f docker-compose.train.yml up -d

# Install game engine locally
cd packages/game-engine
pip install -e .

# Run game-engine tests
cd packages/game-engine
python -m pytest tests/

# Run manual card effect tester
cd packages/game-engine
python scripts/card_effect_tester.py
```

### Local Simulator Servers

Use these commands when running the simulator directly on Windows or from a Codex desktop shell. They avoid these known launcher problems:

- Backend reload mode can trigger Windows Python multiprocessing `PermissionError: [WinError 5] Access is denied`.
- `npx.cmd` can resolve npm shims from the wrong folder when spawned from some shells.
- In Codex desktop shells, the sandbox can inject an uppercase `PATH` alongside Windows `Path`. PowerShell treats environment keys case-insensitively, so `Start-Process` and `Get-ChildItem Env:` can fail with `Item has already been added. Key in dictionary: 'Path' Key being added: 'PATH'`.
- `Start-Process -RedirectStandardOutput/-RedirectStandardError` can keep the launching command attached to a long-running server in the Codex shell. Use terminal panes or plain `Start-Process` without redirection for long-lived dev servers.
- Vite loads `vite.config.ts` through esbuild. In a sandboxed shell this can fail with `Error: spawn EPERM`; run the frontend start outside the sandbox if that happens.

Backend:

```powershell
cd packages/simulator/backend
py -3.14 main.py
```

Frontend:

```powershell
cd packages/simulator/frontend
node node_modules/vite/bin/vite.js --host 0.0.0.0 --port 3000
```

Local URLs:

```text
Frontend: http://localhost:3000
Backend health: http://localhost:8000/health
```

Backend reload is opt-in. Only enable it in an environment where Python multiprocessing/reload works:

```powershell
$env:OPTCG_SIMULATOR_BACKEND_RELOAD = "true"
python main.py
```

If you need to launch the servers with `Start-Process` from a Codex desktop shell, normalize the current PowerShell process environment first:

```powershell
$pathValue = [Environment]::GetEnvironmentVariable("Path", "Process")
$upperValue = [Environment]::GetEnvironmentVariable("PATH", "Process")
if (-not [string]::IsNullOrEmpty($upperValue)) { $pathValue = $upperValue }
[Environment]::SetEnvironmentVariable("PATH", $null, "Process")
[Environment]::SetEnvironmentVariable("Path", $pathValue, "Process")
```

This is process-local. It does not change the user or machine environment.

Then launch without stdout/stderr redirection:

```powershell
Start-Process -FilePath py -ArgumentList "-3.14", "main.py" -WorkingDirectory "$PWD\packages\simulator\backend"
Start-Process -FilePath node -ArgumentList "node_modules/vite/bin/vite.js", "--host", "0.0.0.0", "--port", "3000" -WorkingDirectory "$PWD\packages\simulator\frontend"
```

Service ports:

| Service | Port |
| --- | --- |
| Simulator frontend | `3000` in dev, `80` in production container |
| Simulator backend | `8000` locally, `8001` in Docker |
| Training API | `8000` |
| Prometheus | `9090` |
| Grafana | `3001` |

## Effect System Rules

Use `effect_registry.py` helpers for shared actions. Avoid creating a card-local handler for a generic operation if a helper already exists.

Preferred shared helpers:

| Function family | Use for |
| --- | --- |
| `draw_cards`, `trash_from_hand`, `return_don_to_deck`, `add_don_from_deck` | Common resource movement |
| `create_ko_choice`, `create_bottom_deck_choice`, `create_return_to_hand_choice` | Opponent/field removal choices |
| `create_power_effect_choice`, `create_cost_reduction_choice` | Temporary stat changes |
| `create_rest_choice`, `create_set_active_choice`, `create_don_assignment_choice` | Rest/active/DON selection |
| `create_play_from_hand_choice`, `create_play_from_trash_choice` | Play-card effects |
| `create_add_from_trash_choice`, `create_add_to_life_choice` | Zone-to-hand/life effects |
| `create_mode_choice`, `create_target_choice`, `create_multi_target_choice` | Generic mode/target prompts |
| `search_top_cards`, `reorder_top_cards` | Look/reveal/search/order flows |
| `get_opponent`, `check_life_count`, `check_leader_type`, `check_trash_count` | Shared conditions |

Pending choices should prefer callable `callback=` closures when the effect needs card-specific multi-step behavior. If `callback_action=` is used without a callback, it must match a dispatcher branch in `GameState.resolve_pending_choice`.

Current dispatcher-backed `callback_action` values:

```text
add_from_trash_to_hand, add_to_hand_from_trash, add_to_opponent_life,
apply_cost_reduction, apply_power, apply_power_until_next_turn, assign_don,
cannot_attack_target, choose_option, deck_top_or_bottom_all, give_banish,
give_double_attack, give_rush, ko_multi_targets, ko_target, nami_deck_order,
negate_effects, perona_cannot_rest, place_at_bottom, play_from_hand,
play_from_hand_or_trash, play_from_trash, replace_field_card, rest_instead,
rest_target, rest_targets_multi, return_from_trash_to_hand,
return_own_to_hand, return_to_hand, search_add_to_hand, select_mode,
select_target, set_active, trash_from_hand, trash_own_character
```

## OP01-OP06 Handler Sweep

Static sweep date: 2026-04-18.

All direct `PendingChoice(...)` calls in OP01-OP06 currently use callable callbacks, not string-only dispatch. That is good: it avoids the most fragile "same function, different handler string" failure mode.

| Set | Registered effects | Cards covered | Direct pending choices | Shared-helper posture |
| --- | ---: | ---: | ---: | --- |
| OP01 | 125 | 106 | 28 | Uses shared helpers for KO, play-from-hand, power, rest, search, DON, and trash. No string-only pending handlers. |
| OP02 | 119 | 100 | 25 | Uses shared helpers for cost reduction, KO, play-from-hand, optional DON return, search, power, and discard. No string-only pending handlers. |
| OP03 | 135 | 108 | 44 | Uses shared helpers for life, cost, KO, play-from-trash, power, rest, return, search, and trash. No string-only pending handlers. |
| OP04 | 158 | 111 | 4 | Strongest helper adoption; most prompts go through registry helpers/mode helpers. No string-only pending handlers. |
| OP05 | 156 | 112 | 7 | Mix of modern helper usage and older timing labels. No string-only pending handlers. Timing cleanup is needed. |
| OP06 | 154 | 112 | 36 | Uses shared helpers broadly; current uncommitted work exists in this file. No string-only pending handlers. |

## Timing Findings

The active engine/manager hooks recognize these hardcoded timings, case-insensitively:

```text
activate, continuous, counter, end_of_turn, on_attack, on_block,
on_damage_dealt, on_don_attached, on_don_return, on_draw, on_event,
on_event_activated, on_ko, on_ko_prevention, on_opponent_attack,
on_opponent_ko, on_play, on_play_character, trigger
```

OP01, OP02, OP03, and OP06 only use recognized timings after case normalization.

OP04 has likely dead or inconsistent timing labels:

| Timing | Cards/functions | Recommendation |
| --- | --- | --- |
| `on_ko_opponent` | `OP04-086` / `op04_086_chinjao` | Rename or bridge to `on_opponent_ko`; the engine hooks `on_opponent_ko`. |
| `on_opponent_play` | `OP04-024` / `op04_024_sugar_opp_turn` | Add an engine hook or rename if this should be a supported timing. |

OP05 has the largest timing cleanup backlog:

| Timing | Cards/functions | Recommendation |
| --- | --- | --- |
| `WHEN_ATTACKING` | `OP05-031` / `buffalo_effect` | Normalize to `on_attack`. |
| `ACTIVATE_MAIN` | `OP05-119` / `luffy_gear5_activate` | Normalize to `activate`. |
| `MAIN` / `main` | Events including `OP05-019`, `OP05-020`, `OP05-076`, `OP05-096`, `OP05-115`, `OP05-116`, `OP05-119` | Confirm event-main trigger path; if these are played as events, `on_play` may be the current practical hook. Pick one convention. |
| `PASSIVE` | `OP05-086` / `op05_086_vivi` | Normalize to `continuous` or add a real passive hook. |
| `on_life_zero` | `OP05-098` / `op05_098_enel_leader` | Add a life-zero hook or refactor into existing life-damage/life-change logic. |
| `on_leave_prevention` | `OP05-100` / `op05_100_enel_protection` | Add a leave-field replacement hook or map to KO prevention if scope is only KO. |
| `on_life_add` | `OP05-107` / `op05_107_spacey` | Add a life-to-hand/add-from-life event hook. |
| `on_trigger` | `OP05-109` / `op05_109_pagaya` | Add a trigger-activated hook if Pagaya should fire from any trigger. |

## Set Implementation Convention

For future OP07+ work:

1. Register each hardcoded effect with `@register_effect(card_id, timing, description)`.
2. Use only the recognized timing names above unless the engine hook is added in the same change.
3. Prefer registry helpers for any common operation already covered.
4. Use a local callable callback only for true card-specific sequencing.
5. Do not invent new `callback_action` strings unless `GameState.resolve_pending_choice` handles them.
6. For optional effects, include an explicit "skip" option when the prompt can legally be declined.
7. For search/look effects, use `search_top_cards` or extend it instead of reimplementing deck ordering.
8. For cost/power changes, prefer helper-created choices and include duration in the log or state marker.
9. For replacement effects, implement the engine hook first, then wire cards into that hook.

## Known Cleanup Results

This sweep intentionally removed repository-local generated or unused artifacts:

| Removed kind | Reason |
| --- | --- |
| Extra Markdown docs | Consolidated into this single reference file. |
| `.claude/worktrees/` | Old local agent worktrees duplicating the repository. |
| Root dev logs | Runtime logs are ignored and not source. |
| Python `__pycache__/` and `*.egg-info/` | Generated artifacts. |
| Simulator `dist/`, `.vite/`, and `node_modules/` | Generated frontend artifacts; reinstall/build from package files. |
| Tracked Vite cache files under `packages/simulator/.vite/` | Build cache, now ignored. |
| `packages/simulator/frontend/public/images/Snipping Tool Installer.exe` | Unreferenced executable in image assets. |

## Files To Be Careful With

These files had pre-existing local modifications before this sweep began:

```text
packages/game-engine/optcg_engine/effects/PENDING_FIXES.jsonl
packages/game-engine/optcg_engine/effects/sets/op06_effects.py
packages/game-engine/scripts/card_effect_tester.py
```

They were left in place. Review them before committing if they are part of active OP06/effect-tester work.

## Current Priorities

1. Normalize OP04 and OP05 timing labels listed above.
2. Decide whether event `[Main]` effects should register as `on_play`, `main`, or a dedicated event-main timing, then apply consistently.
3. Add missing engine hooks for life-zero, life-add, trigger-activated, and leave-field replacement effects if those card behaviors are required.
4. Keep future set files on shared helpers unless the effect truly requires bespoke sequencing.
5. Continue using this README as the only Markdown reference for project architecture and effect conventions.
