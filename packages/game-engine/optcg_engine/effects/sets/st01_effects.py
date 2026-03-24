"""
Hardcoded effects for ST01 cards.
"""

from ..hardcoded import (
    create_don_assignment_choice, create_power_effect_choice, register_effect,
)


# =============================================================================
# LEADER CARD EFFECTS - Starter Decks (ST01-ST29)
# =============================================================================

# --- ST01-001: Monkey.D.Luffy (Leader) ---
@register_effect("ST01-001", "activate", "[Activate: Main] Give Leader/Character up to 1 rested DON")
def st01_001_luffy_leader(game_state, player, card):
    """Once Per Turn: Give this Leader or 1 Character up to 1 rested DON."""
    if hasattr(card, 'st01_001_used') and card.st01_001_used:
        return False
    rested_don = player.don_pool.count("rested")
    if rested_don:
        targets = [player.leader] + player.cards_in_play if player.leader else player.cards_in_play
        if targets:
            card.st01_001_used = True
            return create_don_assignment_choice(
                game_state, player, targets, don_count=1,
                source_card=card, rested_only=True,
                prompt="Choose Leader or Character to give 1 rested DON"
            )
    return False


# =============================================================================
# CHARACTER EFFECTS - STARTER DECKS (ST01-ST14)
# =============================================================================

# --- ST01-002: Usopp ---
@register_effect("ST01-002", "on_attack", "[DON!! x2] Opponent cannot activate Blocker with 5000+ power")
def st01_002_usopp(game_state, player, card):
    """DON x2: Opponent cannot activate Blocker with 5000+ power during this battle."""
    if getattr(card, 'attached_don', 0) >= 2:
        game_state.blocker_power_limit = 4999
        return True
    return False


# --- ST01-004: Sanji ---
@register_effect("ST01-004", "continuous", "[DON!! x2] This Character gains Rush")
def st01_004_sanji(game_state, player, card):
    """DON x2: This Character gains Rush."""
    if getattr(card, 'attached_don', 0) >= 2:
        card.has_rush = True
        return True
    return False


# --- ST01-005: Jinbe ---
@register_effect("ST01-005", "on_attack", "[DON!! x1] Give +1000 power to Leader or Character")
def st01_005_jinbe(game_state, player, card):
    """DON x1: Give Leader or Character other than this card +1000 power."""
    if getattr(card, 'attached_don', 0) >= 1:
        targets = [c for c in player.cards_in_play if c != card] + ([player.leader] if player.leader else [])
        if targets:
            return create_power_effect_choice(game_state, player, targets,
                                              1000, source_card=card,
                                              prompt="Choose Leader or Character to give +1000 power")
    return False


# --- ST01-006: Tony Tony.Chopper ---
@register_effect("ST01-006", "blocker", "[Blocker]")
def st01_006_chopper(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


# --- ST01-007: Nami ---
@register_effect("ST01-007", "activate", "[Activate: Main] Give up to 1 rested DON to Leader or Character")
def st01_007_nami(game_state, player, card):
    """Once Per Turn: Give up to 1 rested DON to Leader or Character."""
    if hasattr(card, 'st01_007_used') and card.st01_007_used:
        return False
    rested_don = player.don_pool.count("rested")
    if rested_don:
        targets = [player.leader] + player.cards_in_play if player.leader else player.cards_in_play
        if targets:
            card.st01_007_used = True
            return create_don_assignment_choice(
                game_state, player, targets, don_count=1,
                source_card=card, rested_only=True,
                prompt="Choose Leader or Character to give 1 rested DON"
            )
    return False


# --- ST01-011: Brook ---
@register_effect("ST01-011", "on_play", "[On Play] Give up to 2 rested DON to Leader or Character")
def st01_011_brook(game_state, player, card):
    """Give up to 2 rested DON cards to Leader or 1 Character."""
    rested_don = player.don_pool.count("rested")
    if rested_don:
        targets = [player.leader] + player.cards_in_play if player.leader else player.cards_in_play
        if targets:
            return create_don_assignment_choice(
                game_state, player, targets, don_count=min(2, len(rested_don)),
                source_card=card, rested_only=True,
                prompt="Choose Leader or Character to give up to 2 rested DON"
            )
    return False


# --- ST01-012: Monkey.D.Luffy ---
@register_effect("ST01-012", "continuous", "[Rush] and [DON!! x2] Blocker disabled")
def st01_012_luffy(game_state, player, card):
    """Rush and DON x2: Opponent cannot activate Blocker."""
    card.has_rush = True
    if getattr(card, 'attached_don', 0) >= 2:
        game_state.blocker_disabled = True
    return True


# --- ST01-013: Roronoa Zoro ---
@register_effect("ST01-013", "continuous", "[DON!! x1] +1000 power")
def st01_013_zoro(game_state, player, card):
    """DON x1: This Character gains +1000 power."""
    if getattr(card, 'attached_don', 0) >= 1:
        card.power_modifier = getattr(card, 'power_modifier', 0) + 1000
        return True
    return False

