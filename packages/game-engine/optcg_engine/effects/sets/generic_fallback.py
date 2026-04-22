"""Shared printed-text fallback handlers for underbuilt set files.

These handlers intentionally cover common OPTCG verbs only. Audits should mark
cards registered through this helper as Partial unless manually promoted.
"""

from ..effect_registry import (
    add_don_from_deck,
    add_power_modifier,
    create_ko_choice,
    create_play_from_hand_choice,
    create_power_effect_choice,
    create_rest_choice,
    create_return_to_hand_choice,
    draw_cards,
    get_opponent,
    register_effect,
    search_top_cards,
    trash_from_hand,
)


def _play_this_card_from_trigger(game_state, player, card):
    for zone in (player.hand, player.life_cards, player.trash):
        if card in zone:
            zone.remove(card)
            break
    if card not in player.cards_in_play:
        card.is_resting = False
        setattr(card, "played_turn", game_state.turn_count)
        game_state.play_card_to_field_by_effect(player, card)
        game_state._apply_keywords(card)
        game_state._log(f"{player.name} played {card.name} from Trigger")
    return True


def _number_before(text, phrase, default=None):
    import re
    match = re.search(rf"(\d+)\s+{phrase}", text, re.IGNORECASE)
    return int(match.group(1)) if match else default


def _cost_limit(text, default=None):
    import re
    for pattern in (r"cost(?: of)?(?: equal to or)?(?: less than| or less)?[^0-9]{0,40}(\d+)", r"cost (\d+) or less"):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return default


def _power_limit(text, default=None):
    import re
    match = re.search(r"(\d{4,5}) power or less", text, re.IGNORECASE)
    return int(match.group(1)) if match else default


def _generic_draw_trash(game_state, player, text, card):
    acted = False
    draw_count = _number_before(text, "cards?", None)
    if "draw" in text.lower() and draw_count:
        draw_cards(player, draw_count)
        acted = True
    import re
    match = re.search(r"trash (\d+) cards? from your hand", text, re.IGNORECASE)
    if match:
        trash_from_hand(player, int(match.group(1)), game_state, card)
        acted = True
    return acted


def _generic_power(game_state, player, text, card):
    import re
    match = re.search(r"([+-]\d{3,5}) power", text.replace("\u2212", "-"), re.IGNORECASE)
    if not match:
        return False
    amount = int(match.group(1))
    owner = player if amount > 0 else get_opponent(game_state, player)
    targets = list(owner.cards_in_play)
    if "Leader" in text and owner.leader:
        targets.insert(0, owner.leader)
    if not targets:
        return True
    return create_power_effect_choice(
        game_state, player, targets, amount, source_card=card,
        prompt=f"{card.name}: choose up to 1 target for {amount:+d} power",
        min_selections=0,
    )


def _generic_ko(game_state, player, text, card):
    if "K.O." not in text:
        return False
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    limit = _cost_limit(text)
    power = _power_limit(text)
    if limit is not None:
        targets = [c for c in targets if (getattr(c, "cost", 0) or 0) <= limit]
    if power is not None:
        targets = [c for c in targets if (getattr(c, "power", 0) or 0) + getattr(c, "power_modifier", 0) <= power]
    if "rested" in text.lower():
        targets = [c for c in targets if getattr(c, "is_resting", False)]
    if not targets:
        return True
    return create_ko_choice(game_state, player, targets, source_card=card,
                            prompt=f"{card.name}: K.O. up to 1 matching opponent card",
                            min_selections=0)


def _generic_rest(game_state, player, text, card):
    if "rest up to" not in text.lower():
        return False
    opponent = get_opponent(game_state, player)
    targets = list(opponent.cards_in_play)
    if "Leader" in text and opponent.leader:
        targets.insert(0, opponent.leader)
    limit = _cost_limit(text)
    if limit is not None:
        targets = [c for c in targets if c is opponent.leader or (getattr(c, "cost", 0) or 0) <= limit]
    targets = [c for c in targets if not getattr(c, "is_resting", False)]
    if not targets:
        return True
    return create_rest_choice(game_state, player, targets, source_card=card,
                              prompt=f"{card.name}: Rest up to 1 matching opponent card",
                              min_selections=0)


def _generic_return(game_state, player, text, card):
    lowered = text.lower()
    if "return" not in lowered or "hand" not in lowered:
        return False
    owner = player if "your characters" in lowered or "your character" in lowered else get_opponent(game_state, player)
    targets = list(owner.cards_in_play)
    limit = _cost_limit(text)
    if limit is not None:
        targets = [c for c in targets if (getattr(c, "cost", 0) or 0) <= limit]
    if not targets:
        return True
    return create_return_to_hand_choice(game_state, player, targets, source_card=card,
                                        prompt=f"{card.name}: Return up to 1 matching Character to hand",
                                        optional=True)


def _generic_play(game_state, player, text, card):
    if "play up to 1" not in text.lower():
        return False
    lowered = text.lower()
    source = player.trash if "from your trash" in lowered else player.hand
    targets = [c for c in source if getattr(c, "card_type", "") == "CHARACTER"]
    limit = _cost_limit(text)
    if limit is not None:
        targets = [c for c in targets if (getattr(c, "cost", 0) or 0) <= limit]
    for type_name in ("supernovas", "kid pirates", "dressrosa", "donquixote pirates", "germa", "odyssey", "straw hat", "navy"):
        if type_name in lowered:
            targets = [c for c in targets if type_name in (getattr(c, "card_origin", "") or "").lower()]
            break
    if not targets:
        return True
    if source is player.trash:
        from ..effect_registry import create_play_from_trash_choice
        return create_play_from_trash_choice(game_state, player, targets, source_card=card,
                                             rest_on_play="rested" in lowered,
                                             prompt=f"{card.name}: Play up to 1 matching Character from trash")
    return create_play_from_hand_choice(game_state, player, targets, source_card=card,
                                        prompt=f"{card.name}: Play up to 1 matching Character from hand")


def _generic_search(game_state, player, text, card):
    lowered = text.lower()
    if "look at" not in lowered or "top" not in lowered:
        return False
    look_count = 5 if "5 cards" in lowered else 3
    add_count = 2 if "add up to 2" in lowered else 1
    type_filter = None
    for type_name in ("supernovas", "kid pirates", "dressrosa", "donquixote pirates", "germa", "odyssey", "straw hat", "navy"):
        if type_name in lowered:
            type_filter = type_name
            break
    return search_top_cards(
        game_state, player, look_count=look_count, add_count=add_count,
        filter_fn=(lambda c: type_filter in (getattr(c, "card_origin", "") or "").lower()) if type_filter else (lambda c: True),
        source_card=card,
        prompt=f"{card.name}: choose matching card(s) to add to hand",
    )


def resolve_generic_effect(game_state, player, card, timing):
    text = getattr(card, "trigger", "") if timing == "trigger" else getattr(card, "effect", "")
    text = (text or "").replace("\u2212", "-")
    if timing == "blocker" or "[Blocker]" in text:
        card.is_blocker = True
        card.has_blocker = True
        if timing == "blocker":
            return True
    if timing == "trigger" and "Activate this card" in text:
        return resolve_generic_effect(game_state, player, card, "counter" if "[Counter]" in text else "on_play")
    if timing == "trigger" and "play this card" in text.lower():
        return _play_this_card_from_trigger(game_state, player, card)
    acted = _generic_draw_trash(game_state, player, text, card)
    if "DON!! deck" in text:
        add_don_from_deck(player, 1, set_active="active" in text.lower())
        return True
    for resolver in (_generic_search, _generic_power, _generic_ko, _generic_rest, _generic_return, _generic_play):
        result = resolver(game_state, player, text, card)
        if result:
            return True
    return acted or True


def register_generic_set_fallback(timing_map, label):
    def make_handler(timing):
        def handler(game_state, player, card):
            return resolve_generic_effect(game_state, player, card, timing)
        return handler

    for card_id, timings in timing_map.items():
        for timing in timings:
            register_effect(card_id, timing, f"Generic {label} printed-text fallback for {timing}")(make_handler(timing))
