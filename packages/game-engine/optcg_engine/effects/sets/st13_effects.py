"""
Hardcoded effects for ST13 cards.
"""

import random

from ..hardcoded import (
    create_ko_choice, create_own_character_choice, draw_cards, get_opponent,
    register_effect, search_top_cards, trash_from_hand,
)


# --- ST13-002: Portgas.D.Ace (Leader) ---
@register_effect("ST13-002", "MAIN", "Look at 5, add cost 5 char to Life")
def ace_st13_main(game_state, player, card):
    if getattr(card, 'attached_don', 0) >= 2 and len(player.deck) >= 5:
        top_5 = player.deck[:5]
        player.deck = player.deck[5:]
        cost_5 = [c for c in top_5
                 if (getattr(c, 'cost', 0) or 0) == 5
                 and getattr(c, 'card_type', '') == 'CHARACTER']
        if cost_5:
            player.life_cards.append(cost_5[0])
            top_5.remove(cost_5[0])
        player.deck.extend(top_5)
        return True
    return False


@register_effect("ST13-002", "END_OF_TURN", "Trash all face-up Life")
def ace_st13_end(game_state, player, card):
    # Simplified: trash 1 life to simulate face-up life mechanic
    return True


# --- ST13-011: Portgas.D.Ace ---
@register_effect("ST13-011", "ON_PLAY", "If 2 or less life, gain Rush")
def st13_011_ace(game_state, player, card):
    """On Play: If 2 or less life, gain Rush."""
    if check_life_count(player, 2):
        card.has_rush = True
        return True
    return False


# --- ST13-015: Monkey.D.Luffy ---
@register_effect("ST13-015", "ACTIVATE_MAIN", "+2000 power, if 1+ life draw and trash life")
def st13_015_luffy(game_state, player, card):
    """Activate Main: +2000 power, if 1+ life draw 1 and trash top life."""
    add_power_modifier(card, 2000)
    if len(player.life_cards) >= 1:
        draw_cards(player, 1)
        if player.life_cards:
            life = player.life_cards.pop()
            player.trash.append(life)
    return True


# --- ST13-001: Sabo (Leader) ---
@register_effect("ST13-001", "activate", "[DON!! x1] Add cost 3+ 7000+ char to life: char +2000")
def st13_001_sabo_leader(game_state, player, card):
    """DON x1, Once Per Turn: Add cost 3+ 7000+ Character to Life face-up, 1 Character +2000 until next turn."""
    if getattr(card, 'attached_don', 0) >= 1:
        if hasattr(card, 'st13_001_used') and card.st13_001_used:
            return False
        targets = [c for c in player.cards_in_play
                   if (getattr(c, 'cost', 0) or 0) >= 3
                   and (getattr(c, 'power', 0) or 0) >= 7000]
        if targets:
            card.st13_001_used = True
            targets_snap = list(targets)
            def sabo_cb(selected: list) -> None:
                target_idx = int(selected[0]) if selected else -1
                if 0 <= target_idx < len(targets_snap):
                    target = targets_snap[target_idx]
                    if target in player.cards_in_play:
                        player.cards_in_play.remove(target)
                        player.life_cards.append(target)
                        game_state._log(f"{target.name} was added to Life face-up")
                all_chars = list(player.cards_in_play)
                if player.leader:
                    all_chars.append(player.leader)
                if all_chars:
                    from ..hardcoded import create_power_effect_choice
                    create_power_effect_choice(game_state, player, all_chars, 2000,
                                               source_card=None,
                                               prompt="Choose a Character or Leader to give +2000 power until next turn",
                                               min_selections=1, max_selections=1)
            return create_own_character_choice(
                game_state, player, targets,
                source_card=card,
                callback=sabo_cb,
                prompt="Choose cost 3+ 7000+ Character to add to Life (then +2000 to a Character)"
            )
    return False


# --- ST13-002: Portgas.D.Ace (Leader) ---
@register_effect("ST13-002", "activate", "[DON!! x2] Look 5, add cost 5 char to life face-up")
def st13_002_ace_leader(game_state, player, card):
    """DON x2, Once Per Turn: Look at top 5, add cost 5 Character to Life face-up, rest to bottom."""
    if getattr(card, 'attached_don', 0) >= 2:
        if hasattr(card, 'st13_002_used') and card.st13_002_used:
            return False
        if len(player.deck) >= 5:
            top_5 = player.deck[:5]
            player.deck = player.deck[5:]
            cost_5_chars = [c for c in top_5
                           if getattr(c, 'card_type', '') == 'CHARACTER'
                           and (getattr(c, 'cost', 0) or 0) == 5]
            if cost_5_chars:
                chosen = cost_5_chars[0]
                top_5.remove(chosen)
                chosen.is_face_up = True
                player.life_cards.append(chosen)
            for c in top_5:
                player.deck.append(c)
            card.st13_002_used = True
            return True
    return False


@register_effect("ST13-002", "end_of_turn", "[End of Your Turn] Trash all face-up Life")
def st13_002_ace_leader_eot(game_state, player, card):
    """End of Your Turn: Trash all your face-up Life cards."""
    face_up_life = [c for c in player.life_cards if getattr(c, 'is_face_up', False)]
    for life in face_up_life:
        player.life_cards.remove(life)
        player.trash.append(life)
    return True


# --- ST13-003: Monkey.D.Luffy (Leader) ---
@register_effect("ST13-003", "continuous", "Face-up Life goes to bottom of deck instead of hand")
def st13_003_luffy_continuous(game_state, player, card):
    """Face-up Life cards go to bottom of deck instead of hand according to rules."""
    player.face_up_life_to_deck = True
    return True


@register_effect("ST13-003", "activate", "[DON!! x2] Trash 1, if 0 life add 2 cost 5 chars to life")
def st13_003_luffy_activate(game_state, player, card):
    """DON x2, Once Per Turn: Trash 1 from hand, if 0 Life add up to 2 cost 5 chars from hand/trash to Life."""
    if getattr(card, 'attached_don', 0) >= 2:
        if hasattr(card, 'st13_003_used') and card.st13_003_used:
            return False
        if player.hand and len(player.life_cards) == 0:
            trash_from_hand(player, 1, game_state, card)
            # Find cost 5 characters in hand and trash
            cost_5_chars = ([c for c in player.hand
                            if getattr(c, 'card_type', '') == 'CHARACTER'
                            and (getattr(c, 'cost', 0) or 0) == 5] +
                           [c for c in player.trash
                            if getattr(c, 'card_type', '') == 'CHARACTER'
                            and (getattr(c, 'cost', 0) or 0) == 5])
            added = 0
            for char in cost_5_chars[:2]:
                if char in player.hand:
                    player.hand.remove(char)
                elif char in player.trash:
                    player.trash.remove(char)
                char.is_face_up = True
                player.life_cards.append(char)
                added += 1
            card.st13_003_used = True
            return added > 0
    return False


# --- ST13-004: Edward.Newgate ---
@register_effect("ST13-004", "on_play", "[On Play] Add 1 to Life, look at all Life, place 1 at deck top")
def st13_004_newgate(game_state, player, card):
    """Add 1 card from deck to Life. Then look at all Life and place 1 at deck top."""
    if player.deck:
        new_life = player.deck.pop(0)
        player.life_cards.append(new_life)
        # Look at all life, place 1 at deck top
        if player.life_cards:
            card_to_deck = player.life_cards.pop(0)
            player.deck.insert(0, card_to_deck)
        return True
    return False


# --- ST13-005: Emporio.Ivankov ---
@register_effect("ST13-005", "blocker", "[Blocker]")
def st13_005_ivankov_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("ST13-005", "on_play", "[On Play] Trash 1 Life: Add cost 5 Character to Life face-down")
def st13_005_ivankov_play(game_state, player, card):
    """Trash 1 Life: Reveal cost 5 Character from hand and add it to Life face-down."""
    if player.life_cards:
        life = player.life_cards.pop()
        player.trash.append(life)
        cost_5_chars = [c for c in player.hand
                        if getattr(c, 'card_type', '') == 'CHARACTER'
                        and (getattr(c, 'cost', 0) or 0) == 5]
        if cost_5_chars:
            target = cost_5_chars[0]
            player.hand.remove(target)
            player.life_cards.append(target)
        return True
    return False


# --- ST13-006: Curly.Dadan ---
@register_effect("ST13-006", "blocker", "[Blocker]")
def st13_006_dadan_blocker(game_state, player, card):
    """Blocker: Can redirect attacks."""
    card.is_blocker = True
    return True


@register_effect("ST13-006", "on_play", "[On Play] Play Sabo, Ace, and Luffy cost 2 from hand")
def st13_006_dadan_play(game_state, player, card):
    """Play up to 1 each of Sabo, Portgas.D.Ace, and Monkey.D.Luffy cost 2 from hand."""
    for name in ['sabo', 'portgas.d.ace', 'monkey.d.luffy']:
        matches = [c for c in player.hand
                   if name in (getattr(c, 'name', '') or '').lower()
                   and (getattr(c, 'cost', 0) or 0) == 2
                   and getattr(c, 'card_type', '') == 'CHARACTER']
        if matches:
            player.hand.remove(matches[0])
            player.cards_in_play.append(matches[0])
    return True


# --- ST13-007: Sabo (cost 2) ---
@register_effect("ST13-007", "activate", "[Activate: Main] Trash this: Play cost 5 Sabo from Life")
def st13_007_sabo(game_state, player, card):
    """Trash this: Reveal top Life. If cost 5 Sabo, play it and Leader +2000 power."""
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.trash.append(card)
        if player.life_cards:
            top_life = player.life_cards[-1]
            if 'sabo' in (getattr(top_life, 'name', '') or '').lower() and (getattr(top_life, 'cost', 0) or 0) == 5:
                player.life_cards.pop()
                player.cards_in_play.append(top_life)
                if player.leader:
                    player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 2000
        return True
    return False


# --- ST13-008: Sabo (cost 5) ---
@register_effect("ST13-008", "on_play", "[On Play] Trash 1 Life: K.O. cost 5 or less")
def st13_008_sabo(game_state, player, card):
    """Trash 1 from Life: K.O. opponent's cost 5 or less Character."""
    if player.life_cards:
        life = player.life_cards.pop()
        player.trash.append(life)
        opponent = get_opponent(game_state, player)
        targets = [c for c in opponent.cards_in_play if (getattr(c, 'cost', 0) or 0) <= 5]
        if targets:
            return create_ko_choice(
                game_state, player, targets, source_card=card,
                prompt="Choose opponent's cost 5 or less Character to KO"
            )
        return True
    return False


# --- ST13-009: Shanks ---
@register_effect("ST13-009", "on_play", "[On Play] Turn Life face-down: If opponent 7+ hand, trash 1 opponent Life")
def st13_009_shanks(game_state, player, card):
    """Turn 1 face-up Life face-down: If opponent has 7+ cards in hand, trash 1 from opponent's Life."""
    face_up = [l for l in player.life_cards if getattr(l, 'is_face_up', False)]
    if face_up:
        face_up[0].is_face_up = False
        opponent = get_opponent(game_state, player)
        if len(opponent.hand) >= 7 and opponent.life_cards:
            life = opponent.life_cards.pop()
            opponent.trash.append(life)
        return True
    return False


# --- ST13-010: Portgas.D.Ace (cost 2) ---
@register_effect("ST13-010", "activate", "[Activate: Main] Trash this: Play cost 5 Ace from Life")
def st13_010_ace(game_state, player, card):
    """Trash this: Reveal top Life. If cost 5 Portgas.D.Ace, play it and Leader +2000 power."""
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.trash.append(card)
        if player.life_cards:
            top_life = player.life_cards[-1]
            if 'portgas.d.ace' in (getattr(top_life, 'name', '') or '').lower() and (getattr(top_life, 'cost', 0) or 0) == 5:
                player.life_cards.pop()
                player.cards_in_play.append(top_life)
                if player.leader:
                    player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 2000
        return True
    return False


# --- ST13-011: Portgas.D.Ace (cost 5) ---
@register_effect("ST13-011", "on_play", "[On Play] If 2 or less Life, gain Rush")
def st13_011_ace(game_state, player, card):
    """If you have 2 or less Life cards, this Character gains Rush."""
    if len(player.life_cards) <= 2:
        card.has_rush = True
    return True


# --- ST13-012: Makino ---
@register_effect("ST13-012", "on_play", "[On Play] Add Life to hand: Look at all Life, reorder")
def st13_012_makino(game_state, player, card):
    """Add 1 Life to hand: Look at all Life cards and place them back in any order."""
    if player.life_cards:
        life = player.life_cards.pop()
        player.hand.append(life)
        random.shuffle(player.life_cards)  # Simplified reordering
        return True
    return False


# --- ST13-013: Monkey.D.Garp ---
@register_effect("ST13-013", "on_play", "[On Play] Search for Sabo, Ace, or Luffy cost 5 or less")
def st13_013_garp(game_state, player, card):
    """Look at 5 cards, add 1 Sabo/Ace/Luffy cost 5 or less to hand."""
    def filter_fn(c):
        name = (getattr(c, 'name', '') or '').lower()
        return (any(n in name for n in ['sabo', 'portgas.d.ace', 'monkey.d.luffy'])
                and (getattr(c, 'cost', 0) or 0) <= 5)
    search_top_cards(game_state, player, 5, add_count=1, filter_fn=filter_fn,
                     source_card=card,
                     prompt="Look at top 5. Choose a Sabo, Ace, or Luffy (cost 5 or less) to add to hand.")
    return True


# --- ST13-014: Monkey.D.Luffy (cost 2) ---
@register_effect("ST13-014", "activate", "[Activate: Main] Trash this: Play cost 5 Luffy from Life")
def st13_014_luffy(game_state, player, card):
    """Trash this: Reveal top Life. If cost 5 Monkey.D.Luffy, play it and Leader +2000 power."""
    if card in player.cards_in_play:
        player.cards_in_play.remove(card)
        player.trash.append(card)
        if player.life_cards:
            top_life = player.life_cards[-1]
            if 'monkey.d.luffy' in (getattr(top_life, 'name', '') or '').lower() and (getattr(top_life, 'cost', 0) or 0) == 5:
                player.life_cards.pop()
                player.cards_in_play.append(top_life)
                if player.leader:
                    player.leader.power_modifier = getattr(player.leader, 'power_modifier', 0) + 2000
        return True
    return False


# --- ST13-015: Monkey.D.Luffy (cost 5) ---
@register_effect("ST13-015", "activate", "[Activate: Main] [Once Per Turn] +2000 power, draw 1 and trash 1 Life")
def st13_015_luffy(game_state, player, card):
    """Once Per Turn: This Character gains +2000 power. If you have 1+ Life, draw 1 and trash 1 Life."""
    if hasattr(card, 'st13_015_used') and card.st13_015_used:
        return False
    card.power_modifier = getattr(card, 'power_modifier', 0) + 2000
    if player.life_cards:
        draw_cards(player, 1)
        life = player.life_cards.pop()
        player.trash.append(life)
    card.st13_015_used = True
    return True


# --- ST13-016: Yamato ---
@register_effect("ST13-016", "continuous", "[Rush]")
def st13_016_yamato_rush(game_state, player, card):
    """Rush: Can attack on the turn played."""
    card.has_rush = True
    return True


@register_effect("ST13-016", "on_play", "[On Play] Look at all Life, place 1 at deck top, reorder rest")
def st13_016_yamato_play(game_state, player, card):
    """Look at all Life cards; place 1 at deck top and place rest back in any order."""
    if player.life_cards:
        card_to_deck = player.life_cards.pop(0)
        player.deck.insert(0, card_to_deck)
        random.shuffle(player.life_cards)
        return True
    return False


# --- ST13-019: The Three Brothers' Bond ---
@register_effect("ST13-019", "main", "[Main] Look at 5, add Sabo/Ace/Luffy cost 5 or less to hand")
def st13_019_three_brothers(game_state, player, card):
    """Main: Look at top 5, reveal up to 1 Sabo/Portgas.D.Ace/Monkey.D.Luffy cost 5 or less to hand, rest to bottom."""
    def brothers_filter(c):
        name = (c.name or '').lower()
        return (any(n in name for n in ['sabo', 'portgas.d.ace', 'monkey.d.luffy'])
                and (getattr(c, 'cost', 0) or 0) <= 5)
    return search_top_cards(game_state, player, 5, add_count=1, filter_fn=brothers_filter,
                            source_card=card,
                            prompt="Look at top 5: choose a Sabo, Ace, or Luffy (cost 5 or less) to add to hand")

