"""
Hardcoded effects for ST08 cards.
"""

from ..hardcoded import (
    create_cost_reduction_choice, create_ko_choice, draw_cards, get_opponent,
    register_effect, trash_from_hand,
)


# --- ST08-013: Mr.2.Bon.Kurei(Bentham) ---
@register_effect("ST08-013", "END_BATTLE", "May KO opponent's battled char, then KO this")
def mr2_st08_effect(game_state, player, card):
    if hasattr(game_state, 'last_battle_target'):
        target = game_state.last_battle_target
        opponent = get_opponent(game_state, player)
        if target in opponent.cards_in_play:
            opponent.cards_in_play.remove(target)
            opponent.trash.append(target)
        if card in player.cards_in_play:
            player.cards_in_play.remove(card)
            player.trash.append(card)
        return True
    return False


# --- ST08-013: Mr.2.Bon.Kurei(Bentham) ---
@register_effect("ST08-013", "END_OF_BATTLE", "KO opponent's battled Character and this card")
def mr2_effect(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 1:
        # Get opponent's battled character
        opponent = get_opponent(game_state, player)
        if hasattr(game_state, 'current_battle_target'):
            target = game_state.current_battle_target
            if target and target in opponent.cards_in_play:
                # KO both
                opponent.cards_in_play.remove(target)
                opponent.trash.append(target)
                if card in player.cards_in_play:
                    player.cards_in_play.remove(card)
                    player.trash.append(card)
                return True
    return False


# --- ST08-001: Monkey.D.Luffy (Leader) ---
@register_effect("ST08-001", "on_character_ko", "[Your Turn] When Character K.O.'d, give rested DON to Leader")
def st08_001_luffy_leader(game_state, player, card):
    """Your Turn: When a Character is K.O.'d, give up to 1 rested DON to this Leader."""
    rested_don = player.don_pool.count("rested")
    if rested_don:
        card.attached_don = getattr(card, 'attached_don', 0) + 1
        return True
    return False


# --- ST08-002: Uta ---
@register_effect("ST08-002", "continuous", "Cannot be K.O.'d in battle by Leaders")
def st08_002_uta_continuous(game_state, player, card):
    """This Character cannot be K.O.'d in battle by Leaders."""
    card.cannot_be_ko_by_leader = True
    return True


@register_effect("ST08-002", "activate", "[Activate: Main] Rest this: Give opponent's Character -2 cost")
def st08_002_uta_activate(game_state, player, card):
    """Rest this Character: Give opponent's Character -2 cost."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        opponent = get_opponent(game_state, player)
        if opponent.cards_in_play:
            return create_cost_reduction_choice(
                game_state, player, opponent.cards_in_play, -2,
                source_card=card,
                prompt="Choose opponent's Character to give -2 cost"
            )
        return True
    return False


# --- ST08-004: Koby ---
@register_effect("ST08-004", "activate", "[Activate: Main] Rest this: K.O. cost 2 or less Character")
def st08_004_koby(game_state, player, card):
    """Rest this Character: K.O. opponent's cost 2 or less Character."""
    if not getattr(card, 'is_resting', False):
        card.is_resting = True
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 2]
        if targets:
            return create_ko_choice(game_state, player, targets, source_card=card,
                                   prompt="Choose opponent's cost 2 or less Character to KO")
        return True
    return False


# --- ST08-005: Shanks ---
@register_effect("ST08-005", "on_play", "[On Play] Trash 1: K.O. all cost 1 or less Characters")
def st08_005_shanks(game_state, player, card):
    """Trash 1 from hand: K.O. all Characters with cost 1 or less."""
    if player.hand:
        trash_from_hand(player, 1, game_state, card)
        opponent = get_opponent(game_state, player)
        # K.O. all cost 1 or less from both players
        for p in [player, opponent]:
            to_ko = [c for c in p.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 1]
            for c in to_ko:
                p.cards_in_play.remove(c)
                p.trash.append(c)
        return True
    return False


# --- ST08-006: Shirahoshi ---
@register_effect("ST08-006", "blocker", "[Blocker]")
def st08_006_shirahoshi_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("ST08-006", "on_play", "[On Play] Give opponent's Character -4 cost")
def st08_006_shirahoshi_play(game_state, player, card):
    """Give up to 1 of opponent's Characters -4 cost."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_cost_reduction_choice(game_state, player, opponent.cards_in_play,
                                            -4, source_card=card,
                                            prompt="Choose opponent's Character to give -4 cost")
    return True


# --- ST08-007: Nefeltari Vivi ---
@register_effect("ST08-007", "blocker", "[Blocker]")
def st08_007_vivi(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


# --- ST08-008: Higuma ---
@register_effect("ST08-008", "on_play", "[On Play] Give opponent's Character -2 cost")
def st08_008_higuma(game_state, player, card):
    """Give up to 1 of opponent's Characters -2 cost."""
    opponent = get_opponent(game_state, player)
    if opponent.cards_in_play:
        return create_cost_reduction_choice(game_state, player, opponent.cards_in_play,
                                            -2, source_card=card,
                                            prompt="Choose opponent's Character to give -2 cost")
    return True


# --- ST08-009: Makino ---
@register_effect("ST08-009", "on_play", "[On Play] If cost 0 exists, draw 1")
def st08_009_makino(game_state, player, card):
    """If there is a cost 0 Character, draw 1 card."""
    opponent = get_opponent(game_state, player)
    all_chars = player.cards_in_play + opponent.cards_in_play
    cost_zero = [c for c in all_chars
                 if (getattr(c, 'cost', 0) or 0) + getattr(c, 'cost_modifier', 0) <= 0]
    if cost_zero:
        draw_cards(player, 1)
    return True


# --- ST08-013: Mr.2.Bon.Kurei ---
@register_effect("ST08-013", "on_battle", "[DON!! x1] After battle with Character, K.O. both")
def st08_013_bonkurei(game_state, player, card):
    """DON x1: After battling a Character, you may K.O. both this and the opponent's Character."""
    if getattr(card, 'attached_don', 0) >= 1:
        # Mark for mutual KO after battle
        card.mutual_ko_on_battle = True
        return True
    return False

