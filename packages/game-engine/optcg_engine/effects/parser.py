"""
Effect parser for One Piece TCG.

Parses effect text into structured Effect objects that can be executed.
Uses pattern matching to identify common effect patterns.
"""

import re
from typing import List, Optional, Tuple
from dataclasses import dataclass

from .effects import (
    Effect, EffectType, EffectTiming, TargetType, Duration,
    TargetRestriction, EffectCost, ParsedCard,
    KEYWORD_RUSH, KEYWORD_BLOCKER, KEYWORD_BANISH, KEYWORD_DOUBLE_ATTACK
)
from .tokenizer import Tokenizer, Token, TokenType, extract_keywords


class EffectParser:
    """
    Parses One Piece TCG effect text into structured Effect objects.

    Uses a combination of regex patterns and token analysis to identify
    effect types and parameters.
    """

    def __init__(self):
        self.tokenizer = Tokenizer()
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for effect matching."""

        # Timing patterns
        self.timing_map = {
            'ON_PLAY': EffectTiming.ON_PLAY,
            'WHEN_ATTACKING': EffectTiming.WHEN_ATTACKING,
            'ON_BLOCK': EffectTiming.ON_BLOCK,
            'COUNTER': EffectTiming.COUNTER,
            'TRIGGER': EffectTiming.TRIGGER,
            'MAIN': EffectTiming.MAIN,
            'END_OF_TURN': EffectTiming.END_OF_TURN,
            'START_OF_TURN': EffectTiming.START_OF_TURN,
            'ON_KO': EffectTiming.ON_KO,
            'ON_OPPONENT_ATTACK': EffectTiming.ON_OPPONENT_ATTACK,
            'YOUR_TURN': EffectTiming.CONTINUOUS,  # Your turn effects are continuous during your turn
            'OPPONENT_TURN': EffectTiming.ON_OPPONENT_ATTACK,  # Opponent turn effects
        }

        # Common effect patterns (regex -> parser method)
        self.effect_patterns = [
            # Conditional effects with life requirements (check these FIRST)
            # Pattern: "If you have X or less Life cards, give ... -Y power"
            (r'if\s+you\s+have\s+(\d+)\s+or\s+less\s+Life\s+cards?,\s+give\s+(?:up\s+to\s+)?(?:\d+\s+)?(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?(?:Leader\s+or\s+)?(?:Character)(?:\s+cards?)?\s+[\u2212\-](\d+)(?:000)?\s+power',
             self._parse_conditional_power_reduce),

            # Pattern: "If your opponent has X or less Life cards, give up to Y rested DON!!"
            (r'if\s+your\s+opponent\s+has\s+(\d+)\s+or\s+less\s+Life\s+cards?,\s+give\s+(?:up\s+to\s+)?(\d+)\s+(?:rested\s+)?DON!!?\s+(?:cards?\s+)?to\s+',
             self._parse_conditional_don_attach),

            # Draw effects: "draw X card(s)"
            (r'draw\s+(\d+)\s+cards?', self._parse_draw),

            # KO effects: "K.O. up to X Character(s)"
            (r'K\.?O\.?\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?Characters?',
             self._parse_ko),

            # Power boost: "+X000 power" or "gains +X000 power"
            (r'(?:gains?\s+)?\+(\d+)(?:000)?\s+power', self._parse_power_boost),

            # Power reduce: "set power to 0" or "-X000 power"
            (r'set\s+(?:the\s+)?power\s+(?:of\s+.+\s+)?to\s+0', self._parse_power_zero),
            (r'-(\d+)(?:000)?\s+power', self._parse_power_reduce),

            # Power reduce alternate: "give X −Y power" (negative power, handles Unicode minus U+2212)
            (r'give\s+(?:up\s+to\s+)?(?:\d+\s+)?(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?(?:Leader|Character)(?:\s+cards?)?\s+[\u2212\-](\d+)(?:000)?\s+power',
             self._parse_power_reduce_opponent),

            # Rest effects: "rest up to X Character(s)/DON"
            (r'rest\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?(?:Characters?|DON!!?)',
             self._parse_rest),

            # DON manipulation: "set up to X DON as active"
            (r'set\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+your\s+)?DON!!?\s+(?:cards?\s+)?as\s+active',
             self._parse_don_activate),

            # Add DON: "add up to X DON from your DON deck"
            (r'add\s+(?:up\s+to\s+)?(\d+)\s+DON!!?', self._parse_don_add),

            # Play card: "play this card" or "play X Character"
            (r'play\s+this\s+card', self._parse_play_this),
            (r'play\s+(?:up\s+to\s+)?(\d+)\s+Character', self._parse_play_character),

            # Return to deck: "return X cards from trash to deck"
            (r'return\s+(?:up\s+to\s+)?(\d+)\s+cards?\s+from\s+(?:your\s+)?trash\s+to\s+(?:the\s+)?(?:bottom\s+of\s+)?(?:your\s+)?deck',
             self._parse_return_to_deck),

            # Cannot be blocked
            (r'cannot\s+be\s+blocked', self._parse_cannot_block),

            # Blocker restriction
            (r'cannot\s+activate\s+(?:a\s+)?\[?Blocker\]?', self._parse_blocker_restriction),

            # Protection: "cannot be K.O.'d"
            (r'cannot\s+be\s+K\.?O\.?', self._parse_protect),

            # Add to life
            (r'add\s+(?:up\s+to\s+)?(\d+)\s+cards?\s+(?:from\s+.+\s+)?to\s+(?:the\s+top\s+of\s+)?(?:your\s+)?Life',
             self._parse_add_life),

            # Search deck: "Look at X cards from the top of your deck" or "reveal the top X cards of deck"
            (r'(?:look\s+at|reveal|search)\s+(?:the\s+top\s+)?(\d+)?\s*cards?\s+(?:from\s+)?(?:the\s+top\s+)?(?:of\s+)?(?:your\s+)?deck',
             self._parse_search),

            # Return to hand: "return X Character(s) to hand"
            (r'return\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?(?:Characters?|cards?)\s+(?:from\s+.+\s+)?to\s+(?:the\s+)?(?:owner\'?s?\s+)?hand',
             self._parse_return_to_hand),

            # Give DON: "give up to X DON!! cards to your Leader/Character"
            (r'give\s+(?:up\s+to\s+)?(\d+)\s+(?:rested\s+)?DON!!?\s+(?:cards?\s+)?to\s+(?:your\s+)?(?:Leader|Character)',
             self._parse_don_attach),

            # Give DON alternate: "Give this Leader or X of your Characters up to Y DON!!"
            (r'give\s+(?:this\s+)?(?:Leader|Character)(?:\s+or\s+\d+\s+of\s+your\s+Characters?)?\s+(?:up\s+to\s+)?(\d+)\s+(?:rested\s+)?DON!!?',
             self._parse_don_attach),

            # Add to hand from look/reveal: "add X to your hand"
            (r'add\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+them\s+)?to\s+(?:your\s+)?hand',
             self._parse_add_to_hand),

            # Trash from field/hand: "trash X Character(s)"
            (r'trash\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?(?:Characters?|cards?)',
             self._parse_trash),

            # Cost reduction: "this card costs X less" or "reduce cost by X"
            (r'(?:this\s+card\s+)?costs?\s+(\d+)\s+less', self._parse_cost_reduce),
            (r'reduce\s+(?:the\s+)?cost\s+(?:of\s+.+\s+)?by\s+(\d+)', self._parse_cost_reduce),

            # Place at bottom of deck
            (r'place\s+(?:up\s+to\s+)?(\d+)?\s*(?:cards?\s+)?(?:at\s+)?(?:the\s+)?bottom\s+(?:of\s+)?(?:the\s+)?(?:owner\'?s?\s+)?deck',
             self._parse_place_bottom),

            # Cannot attack
            (r'cannot\s+attack', self._parse_cannot_attack),

            # Blocker restriction: "cannot activate [Blocker]"
            (r'cannot\s+activate\s+(?:a\s+)?\[?Blocker\]?(?:\s+Character)?(?:\s+that\s+has\s+(\d+)(?:000)?\s+or\s+more\s+power)?',
             self._parse_blocker_restriction_full),

            # Gains keyword: "gains [Rush]"
            (r'gains?\s+\[Rush\]', self._parse_grant_rush),
            (r'gains?\s+\[Blocker\]', self._parse_grant_blocker_parse),

            # Power boost to Leader/Character: "Leader or Character gains +X power"
            (r'(?:your\s+)?(?:Leader|Character)(?:\s+cards?)?\s+(?:other\s+than\s+this\s+card\s+)?gains?\s+\+(\d+)(?:000)?\s+power',
             self._parse_power_boost_other),

            # Look at life and rearrange: "Look at X card from the top of ... Life cards"
            (r'look\s+at\s+(?:up\s+to\s+)?(\d+)\s+cards?\s+from\s+(?:the\s+top\s+of\s+)?(?:your\s+(?:or\s+your\s+)?opponent\'?s?\s+)?Life',
             self._parse_look_life),

            # Look at all Life cards: "Look at all of your Life cards"
            (r'look\s+at\s+all\s+(?:of\s+)?(?:your\s+)?Life\s+cards?',
             self._parse_look_all_life),

            # K.O. rested Characters: "K.O. up to X of your opponent's rested Characters"
            (r'K\.?O\.?\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?rested\s+Characters?',
             self._parse_ko_rested),

            # Give -X cost during this turn: "give ... -X cost during this turn"
            (r'give\s+(?:up\s+to\s+)?(?:\d+\s+)?(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?(?:Characters?|cards?)\s+[\u2212\-](\d+)\s+cost',
             self._parse_give_cost_reduce),

            # Place this Character at bottom of deck: "place this Character at the bottom"
            (r'place\s+this\s+(?:Character|card)\s+(?:at\s+)?(?:the\s+)?bottom\s+(?:of\s+)?(?:the\s+)?(?:owner\'?s?\s+)?deck',
             self._parse_place_self_bottom),

            # Return Character to hand with cost: "Return up to X Character with a cost of Y or less"
            (r'return\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?Characters?\s+(?:with\s+(?:a\s+)?cost\s+(?:of\s+)?(\d+)\s+or\s+less\s+)?to\s+(?:the\s+)?(?:owner\'?s?\s+)?hand',
             self._parse_return_character_to_hand),

            # Look and reorder deck: "Look at X cards from the top of your deck and place them"
            (r'look\s+at\s+(\d+)\s+cards?\s+from\s+(?:the\s+top\s+of\s+)?(?:your\s+)?deck\s+and\s+(?:place|return)\s+them',
             self._parse_look_reorder),

            # DON!! -X cost pattern (return DON as cost): parsed as effect that happened
            (r'DON!!\s*[\u2212\-](\d+)',
             self._parse_don_return_cost),

            # Play specific type Character: "Play up to X {Type} type Character"
            (r'play\s+(?:up\s+to\s+)?(\d+)\s+\{([^}]+)\}\s+type\s+Characters?',
             self._parse_play_type_character),

            # Give -X power pattern without "give" prefix: just "-X power during this turn"
            (r'[\u2212\-](\d+)(?:000)?\s+power\s+during\s+this\s+turn',
             self._parse_power_reduce),

            # Place Character at bottom with cost restriction: "Place up to X Character with cost Y or less at the bottom"
            (r'place\s+(?:up\s+to\s+)?(\d+)\s+Characters?\s+(?:with\s+(?:a\s+)?cost\s+(?:of\s+)?(\d+)\s+or\s+less\s+)?(?:at\s+)?(?:the\s+)?bottom\s+(?:of\s+)?(?:the\s+)?(?:owner\'?s?\s+)?deck',
             self._parse_place_character_bottom),

            # Play specific named card: "Play up to X [Card Name] with cost Y or less"
            (r'play\s+(?:up\s+to\s+)?(\d+)\s+\[([^\]]+)\]\s+(?:with\s+(?:a\s+)?cost\s+(?:of\s+)?(\d+)\s+or\s+less\s+)?(?:from\s+your\s+(?:hand|trash|deck))?',
             self._parse_play_named_card),

            # Attack active Characters: "can also attack your opponent's active Characters"
            (r'(?:can\s+)?(?:also\s+)?attack\s+(?:your\s+)?opponent\'?s?\s+active\s+Characters?',
             self._parse_attack_active),

            # Add card to Life: "add up to X Character to the top of your Life"
            (r'add\s+(?:up\s+to\s+)?(\d+)\s+(?:Characters?|cards?)\s+(?:with\s+.+\s+)?to\s+(?:the\s+)?(?:top|bottom)\s+(?:of\s+)?(?:your\s+)?Life',
             self._parse_add_to_life),

            # Look and place at top in any order: "Look at X cards... place them at the top... in any order"
            (r'look\s+at\s+(\d+)\s+cards?\s+from\s+(?:the\s+top\s+of\s+)?(?:your\s+)?deck[^;]*(?:place|return)\s+them\s+(?:at\s+)?(?:the\s+)?(?:top|bottom)',
             self._parse_look_place),

            # Play multi-type character: "Play up to X {Type1} or {Type2} type Character"
            (r'play\s+(?:up\s+to\s+)?(\d+)\s+\{([^}]+)\}\s+(?:or\s+\{([^}]+)\}\s+)?type\s+Characters?(?:\s+card)?',
             self._parse_play_multi_type),

            # Life to hand as part of effect: "add X card from... your Life cards to your hand"
            (r'add\s+(\d+)\s+cards?\s+from\s+(?:the\s+)?(?:top\s+or\s+bottom\s+of\s+)?(?:your\s+)?Life\s+(?:cards?\s+)?to\s+(?:your\s+)?hand',
             self._parse_life_to_hand),

            # Cannot be KO'd by opponent: "This Character cannot be K.O.'d by your opponent's effects"
            (r'cannot\s+be\s+K\.?O\.?\'?d?\s+by\s+(?:your\s+)?opponent',
             self._parse_protect_from_opponent),

            # Opponent discards: "your opponent discards X cards"
            (r'(?:your\s+)?opponent\s+discards?\s+(\d+)\s+cards?',
             self._parse_opponent_discard),

            # Give all Characters -X cost: "Give all of your opponent's Characters -X cost"
            (r'give\s+all\s+(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?Characters?\s+[\u2212\-](\d+)\s+cost',
             self._parse_give_all_cost_reduce),

            # This Character gains keyword: "This Character gains [Rush/Blocker/etc]"
            (r'(?:this\s+)?(?:Character|card|Leader)\s+gains?\s+\[([^\]]+)\]',
             self._parse_gains_keyword),

            # Set cost to X: "Set the cost of... to X"
            (r'set\s+(?:the\s+)?cost\s+(?:of\s+.+\s+)?to\s+(\d+)',
             self._parse_set_cost),

            # Gains +X cost: "gains +X cost"
            (r'gains?\s+\+(\d+)\s+cost',
             self._parse_gains_cost),

            # Characters can't attack: "Characters cannot attack during this turn"
            (r'Characters?\s+cannot\s+attack',
             self._parse_prevent_attack),

            # Cannot be attacked: "this Character cannot be attacked"
            (r'cannot\s+be\s+attacked',
             self._parse_cannot_be_attacked),

            # Returns all cards to deck: "your opponent returns all cards in their hand to their deck"
            (r'(?:your\s+)?opponent\s+returns?\s+(?:all\s+)?cards?\s+(?:in\s+their\s+hand\s+)?to\s+their\s+deck',
             self._parse_opponent_return_to_deck),

            # Opponent places cards from hand at bottom: "opponent places X cards from their hand at the bottom"
            (r'(?:your\s+)?opponent\s+(?:must\s+)?places?\s+(\d+)\s+cards?\s+from\s+(?:their|the)\s+hand\s+(?:at\s+)?(?:the\s+)?bottom\s+(?:of\s+)?(?:their\s+)?deck',
             self._parse_opponent_place_bottom),

            # Place opponent's Character at Life: "Place up to X of your opponent's Characters at the top/bottom of Life"
            (r'place\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?Characters?\s+(?:with\s+[^;]+?\s+)?(?:at\s+)?(?:the\s+)?(?:top|bottom)\s+(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?Life',
             self._parse_place_at_life),

            # DON!! -X in parentheses (explanation pattern): just mark as DON cost
            (r'DON!!\s*[\u2212\-](\d+)\s*\([^)]+\)',
             self._parse_don_return_cost),

            # Look + reveal + add to hand: "Look at X cards... reveal up to Y... add to hand"
            (r'look\s+at\s+(\d+)\s+cards?\s+from\s+(?:the\s+top\s+of\s+)?(?:your\s+)?deck[^;]*;\s*reveal\s+(?:up\s+to\s+)?(\d+)',
             self._parse_look_reveal_add),

            # Conditional draw: "Draw X card if you have Y or less cards in your hand"
            (r'draw\s+(\d+)\s+cards?\s+if\s+you\s+have\s+(\d+)\s+or\s+less\s+cards?\s+in\s+your\s+hand',
             self._parse_conditional_draw),

            # Add Life card to hand: "Add X card from the top of your Life cards to your hand"
            (r'add\s+(\d+)\s+cards?\s+from\s+the\s+top\s+of\s+(?:your\s+)?Life\s+cards?\s+to\s+(?:your\s+)?hand',
             self._parse_life_to_hand_top),

            # Rest DON cost with circled number: "❶ (You may rest the specified number..."
            (r'[\u2460-\u2473]\s*\([^)]+\)',  # ❶-⓴
             self._parse_circled_cost),

            # Play character from trash rested: "play ... from your trash rested"
            (r'play\s+(?:up\s+to\s+)?(\d+)\s+(?:[^;]+)\s+from\s+your\s+trash\s+rested',
             self._parse_play_from_trash_rested),

            # Set characters as active: "Set up to X ... Characters as active"
            (r'set\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?(?:[^;]+?)?\s*Characters?\s+(?:other\s+than\s+\[[^\]]+\]\s+)?as\s+active',
             self._parse_set_characters_active),

            # Set type Characters as active: "Set up to X of your {Type} type Character cards with cost Y as active"
            (r'set\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?(?:\{[^}]+\}\s+type\s+)?Characters?\s+cards?\s+(?:with\s+[^;]+)?\s*as\s+active',
             self._parse_set_characters_active),

            # Will not become active in refresh phase
            (r'will\s+not\s+become\s+active\s+in\s+(?:your\s+)?(?:opponent\'?s?\s+)?next\s+Refresh\s+Phase',
             self._parse_prevent_refresh),

            # Choose and play from trash: "Choose up to X Character ... from your trash. Play..."
            (r'(?:choose|add)\s+(?:up\s+to\s+)?(\d+)\s+(?:[^;]+)\s+from\s+(?:your\s+)?trash[^.]*\.\s*Play',
             self._parse_choose_play_from_trash),

            # Add to Life face-up: "add ... to the top or bottom of ... Life cards face-up"
            (r'add\s+(?:up\s+to\s+)?(\d+)\s+(?:[^;]+)\s+to\s+(?:the\s+)?(?:top|bottom)\s+(?:of\s+)?(?:the\s+)?(?:owner\'?s?\s+)?Life\s+cards?\s+face-?(?:up|down)',
             self._parse_add_to_life_face),

            # Return multiple characters with different costs
            (r'return\s+(?:up\s+to\s+)?(\d+)\s+Character(?:s)?\s+with\s+(?:a\s+)?cost\s+(?:of\s+)?(\d+)\s+or\s+less\s+and\s+(?:up\s+to\s+)?(\d+)\s+Character(?:s)?\s+with\s+(?:a\s+)?cost\s+(?:of\s+)?(\d+)\s+or\s+less',
             self._parse_return_multiple_characters),

            # Opponent places character at bottom: "opponent places X of their Characters at the bottom"
            (r'(?:your\s+)?opponent\s+places?\s+(\d+)\s+(?:of\s+)?(?:their\s+)?Characters?\s+at\s+(?:the\s+)?bottom',
             self._parse_opponent_place_bottom),

            # Gains Banish during this turn
            (r'gains?\s+\[Banish\]\s+during\s+this\s+turn',
             self._parse_gains_banish_temp),

            # Rest this Character cost: "You may rest this Character:"
            (r'(?:you\s+may\s+)?rest\s+this\s+(?:Character|card)\s*:',
             self._parse_rest_self_cost),

            # Look at deck add with condition: "if your Leader is X, look at..."
            (r'if\s+your\s+Leader\s+(?:is|has)\s+[^,]+,\s+look\s+at\s+(\d+)\s+cards?\s+from',
             self._parse_conditional_look),

            # Set character as active: "Set this Character as active"
            (r'set\s+this\s+(?:Character|card)\s+as\s+active',
             self._parse_set_self_active),

            # Reveal from hand and add to Life: "Reveal ... from your hand and add it to the top of your Life"
            (r'reveal\s+(?:up\s+to\s+)?(\d+)\s+(?:[^;]+)\s+from\s+your\s+hand\s+and\s+add\s+(?:it|them)\s+to\s+(?:the\s+)?(?:top|bottom)\s+(?:of\s+)?(?:your\s+)?Life',
             self._parse_reveal_to_life),

            # Add character from trash to hand with "other than" exclusion
            (r'add\s+(?:up\s+to\s+)?(\d+)\s+(?:[^;]+)\s+other\s+than\s+\[[^\]]+\]\s+from\s+(?:your\s+)?trash\s+to\s+(?:your\s+)?hand',
             self._parse_add_from_trash_except),

            # Give DON to Leader: "give up to X rested DON!! card to 1 of your ... Leader"
            (r'give\s+(?:up\s+to\s+)?(\d+)\s+(?:rested\s+)?DON!!?\s+cards?\s+to\s+(?:\d+\s+of\s+)?(?:your\s+)?(?:[^;]+?)?\s*Leader',
             self._parse_don_attach_leader),

            # Trash from hand for cost: "trash X card from your hand:"
            (r'trash\s+(\d+)\s+(?:[^:]+)?\s*from\s+(?:your\s+)?hand\s*:',
             self._parse_trash_cost),

            # Opponent trashes from hand: "opponent trashes X card from their hand"
            (r'(?:your\s+)?opponent\s+trashes?\s+(\d+)\s+cards?\s+from\s+their\s+hand',
             self._parse_opponent_trash),

            # Cannot be K.O.'d by effects
            (r'cannot\s+be\s+K\.?O\.?\'?d?\s+by\s+effects',
             self._parse_protect_from_effects),

            # Play card rested: "Play ... rested"
            (r'play\s+(?:up\s+to\s+)?(\d+)\s+(?:[^;]+)\s+rested',
             self._parse_play_rested),

            # Take extra turn: "take an extra turn after this one"
            (r'take\s+an\s+extra\s+turn',
             self._parse_extra_turn),

            # Add DON from DON deck and set active
            (r'add\s+(?:up\s+to\s+)?(\d+)\s+DON!!?\s+cards?\s+from\s+(?:your\s+)?DON!!?\s+deck\s+and\s+set\s+(?:it|them)\s+as\s+active',
             self._parse_add_don_active),

            # Conditional add from trash: "If your Leader has the {Type}, add up to X ... from your trash to your hand"
            (r'if\s+your\s+Leader\s+(?:is|has)\s+(?:the\s+)?\{([^}]+)\}\s+type[^,]*,\s+add\s+(?:up\s+to\s+)?(\d+)',
             self._parse_conditional_add_from_trash),

            # Add type Character from trash: "add up to X {Type} type Character from your trash to your hand"
            (r'add\s+(?:up\s+to\s+)?(\d+)\s+\{([^}]+)\}\s+type\s+Characters?\s+(?:cards?\s+)?(?:with\s+[^;]+)?\s*(?:other\s+than\s+\[[^\]]+\]\s+)?from\s+(?:your\s+)?trash\s+to\s+(?:your\s+)?hand',
             self._parse_add_type_from_trash),

            # Add from trash to hand generic: "add up to X ... from your trash to your hand"
            (r'add\s+(?:up\s+to\s+)?(\d+)\s+(?:[^;]+)\s+from\s+(?:your\s+)?trash\s+to\s+(?:your\s+)?hand',
             self._parse_add_generic_from_trash),

            # This Character can attack active: "This Character can also attack your opponent's active Characters"
            (r'this\s+Character\s+can\s+(?:also\s+)?attack\s+(?:your\s+)?opponent\'?s?\s+active\s+Characters?',
             self._parse_can_attack_active),

            # Give power until: "gains +X power until the start of your next turn"
            (r'gains?\s+\+(\d+)(?:000)?\s+power\s+until\s+(?:the\s+)?(?:start\s+of\s+)?(?:your\s+)?next\s+turn',
             self._parse_power_until_next_turn),

            # K.O. all Characters: "K.O. all Characters other than this Character"
            (r'K\.?O\.?\s+all\s+Characters?\s+(?:other\s+than\s+this\s+Character)?',
             self._parse_ko_all),

            # Place all Characters at bottom: "Place all of your Characters except this Character at the bottom"
            (r'place\s+all\s+(?:of\s+)?(?:your\s+)?Characters?\s+(?:except\s+this\s+Character\s+)?at\s+(?:the\s+)?bottom',
             self._parse_place_all_bottom),

            # Return this Character to hand
            (r'return\s+this\s+(?:Character|card)\s+to\s+(?:the\s+)?(?:owner\'?s?\s+)?hand',
             self._parse_return_self_to_hand),

            # Set DON as active: "set up to X of your DON!! cards as active"
            (r'set\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?DON!!?\s+cards?\s+as\s+active',
             self._parse_set_don_active),

            # Draw so that you have X cards: "Draw card(s) so that you have X cards in your hand"
            (r'draw\s+cards?(?:\(s\))?\s+so\s+that\s+you\s+have\s+(\d+)\s+cards?\s+in\s+your\s+hand',
             self._parse_draw_to_hand_size),

            # Give -X power (alternative): "give ... −X power"
            (r'give\s+(?:[^;]+?)[\u2212\-](\d+)(?:000)?\s+power',
             self._parse_give_minus_power),

            # Add DON and rest it: "Add up to X DON!! card from your DON!! deck and rest it"
            (r'add\s+(?:up\s+to\s+)?(\d+)\s+DON!!?\s+cards?\s+from\s+(?:your\s+)?DON!!?\s+deck\s+and\s+rest\s+(?:it|them)',
             self._parse_add_don_rested),

            # Characters with power X or less: "Characters with X power or less"
            (r'Characters?\s+with\s+(\d+)(?:000)?\s+power\s+or\s+less',
             self._parse_characters_power_restriction),

            # Negate On Play effects: "On Play effects are negated"
            (r'\[?On Play\]?\s+effects?\s+(?:is|are)\s+negated',
             self._parse_negate_on_play),

            # Play Character with Trigger: "Play up to X Character card with ... and a [Trigger]"
            (r'play\s+(?:up\s+to\s+)?(\d+)\s+Characters?\s+cards?\s+(?:with\s+[^;]+)?\s*(?:and\s+)?(?:a\s+)?\[Trigger\]',
             self._parse_play_with_trigger),

            # Rest Leader or Character: "Rest up to X of your opponent's Leader or Character cards"
            (r'rest\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?(?:Leader\s+or\s+)?Characters?\s+(?:cards?)?',
             self._parse_rest_leader_or_character),

            # Play multiple specific named cards: "Play up to 1 each of [X], [Y], and [Z] with a cost of..."
            (r'play\s+(?:up\s+to\s+)?(\d+)\s+each\s+of\s+\[([^\]]+)\]',
             self._parse_play_each_of),

            # DON field count condition: "If the number of DON!! cards on your field is equal to or less than..."
            (r'if\s+(?:the\s+)?number\s+of\s+DON!!?\s+cards?\s+on\s+your\s+field\s+is\s+(?:equal\s+to\s+or\s+)?less\s+than',
             self._parse_don_field_condition),

            # Set Leader as active: "Set up to X of your ... Leader as active"
            (r'set\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?(?:\{[^}]+\}\s+type\s+)?Leader\s+as\s+active',
             self._parse_set_leader_active),

            # Add Character to top or bottom of Life: "Add up to X Character to the top or bottom of the owner's Life"
            (r'add\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?(?:\{[^}]+\}\s+type\s+)?Characters?\s+(?:other\s+than\s+\[[^\]]+\]\s+)?(?:with\s+[^;]+)?\s*to\s+(?:the\s+)?(?:top\s+or\s+bottom|bottom\s+or\s+top)\s+(?:of\s+)?(?:the\s+)?(?:owner\'?s?\s+|your\s+opponent\'?s?\s+)?Life',
             self._parse_add_to_life_position),

            # This Character can attack active: without "also"
            (r'(?:this\s+)?Character\s+can\s+attack\s+(?:your\s+)?opponent\'?s?\s+active\s+Characters?',
             self._parse_can_attack_active),

            # Cost of 0: "K.O. up to X of your opponent's Characters with a cost of 0"
            (r'K\.?O\.?\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?Characters?\s+with\s+(?:a\s+)?cost\s+(?:of\s+)?0',
             self._parse_ko_cost_zero),

            # Give -X cost during this turn: "Give ... −X cost during this turn"
            (r'give\s+(?:[^;]+?)[\u2212\-](\d+)\s+cost\s+during\s+this\s+turn',
             self._parse_give_cost_reduction),

            # Gains Leader power: "gains +X power until the start of your next turn"
            (r'(?:your\s+)?Leader\s+gains?\s+\+(\d+)(?:000)?\s+power\s+until',
             self._parse_leader_power_boost),

            # Play card with cost and Trigger: "Play up to X Character card with a cost of Y or less and a [Trigger]"
            (r'play\s+(?:up\s+to\s+)?(\d+)\s+Characters?\s+cards?\s+with\s+(?:a\s+)?cost\s+(?:of\s+)?(\d+)\s+or\s+less\s+and\s+(?:a\s+)?\[Trigger\]',
             self._parse_play_cost_trigger),

            # Rest up to a total: "Rest up to a total of X of your opponent's Characters or DON!!"
            (r'rest\s+(?:up\s+to\s+)?(?:a\s+)?total\s+(?:of\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?(?:Characters?\s+or\s+DON!!?|DON!!?\s+or\s+Characters?)',
             self._parse_rest_total),

            # Play from trash at specific condition: "play this Character card from your trash rested"
            (r'play\s+this\s+(?:Character\s+)?cards?\s+from\s+(?:your\s+)?trash\s+rested',
             self._parse_play_self_from_trash),

            # Base cost condition: "Characters with a base cost of X"
            (r'Characters?\s+with\s+(?:a\s+)?base\s+cost\s+(?:of\s+)?(\d+)',
             self._parse_base_cost_characters),

            # Reveal and play rested: "Reveal 1 card ... you may play that card rested"
            (r'reveal\s+(\d+)\s+cards?\s+from\s+(?:the\s+top\s+of\s+)?(?:your\s+)?deck[^;]*(?:play\s+that\s+card\s+rested)',
             self._parse_reveal_play_rested),

            # Give +X000 power to Characters or Trigger: "give ... +X power during this turn"
            (r'gains?\s+\+(\d+)(?:000)?\s+power\s+during\s+this\s+turn',
             self._parse_power_boost_this_turn),

            # Reduce cost during this turn: "cost will be reduced by X"
            (r'cost\s+will\s+be\s+reduced\s+by\s+(\d+)',
             self._parse_cost_will_reduce),

            # Search deck and play: "search your deck for ... and play"
            (r'search\s+(?:your\s+)?deck\s+for\s+(?:up\s+to\s+)?(\d+)',
             self._parse_search_deck),

            # Set this Leader as active: "set this Leader as active"
            (r'set\s+this\s+Leader\s+as\s+active',
             self._parse_set_this_leader_active),

            # Hand size condition: "If you have X or less cards in your hand"
            (r'if\s+you\s+have\s+(\d+)\s+or\s+less\s+cards?\s+in\s+your\s+hand',
             self._parse_hand_size_condition),

            # DON!! -X cost with high number (10): "DON!! −10:"
            (r'DON!!\s*[\u2212\-](\d+)\s*:',
             self._parse_don_high_cost),

            # Choose one effect: "choose one:"
            (r'choose\s+one\s*:',
             self._parse_choose_one),

            # Play Character with type and cost: "Play up to X {Type} type Character card with a cost of Y"
            (r'play\s+(?:up\s+to\s+)?(\d+)\s+(?:purple\s+)?\{([^}]+)\}\s+type\s+Characters?\s+cards?\s+(?:with\s+(?:a\s+)?cost\s+(?:of\s+)?(\d+)\s+or\s+less)?',
             self._parse_play_type_cost),

            # Add DON from deck (simple): "Add up to X DON!! card from your DON!! deck"
            (r'add\s+(?:up\s+to\s+)?(\d+)\s+DON!!?\s+cards?\s+from\s+(?:your\s+)?DON!!?\s+deck',
             self._parse_add_don_simple),

            # Give Events cost reduction: "Give blue Events in your hand −X cost"
            (r'give\s+(?:[^;]+)?Events?\s+(?:in\s+your\s+hand\s+)?[\u2212\-](\d+)\s+cost',
             self._parse_events_cost_reduce),

            # Opponent's turn effect: "If your rested Character would be K.O.'d"
            (r'if\s+your\s+rested\s+Character\s+would\s+be\s+K\.?O\.?\'?d?',
             self._parse_protect_rested),

            # Opponent returns DON: "Your opponent returns X DON!! card from their field to their DON!! deck"
            (r'(?:your\s+)?opponent\s+returns?\s+(\d+)\s+DON!!?\s+cards?\s+from\s+their\s+field\s+to\s+their\s+DON',
             self._parse_opponent_return_don),

            # When this Character is K.O.'d: "[Opponent's Turn] When this Character is K.O.'d"
            (r'when\s+this\s+Character\s+is\s+K\.?O\.?\'?d?',
             self._parse_on_ko_effect),

            # Circled ?: "?" represents rest 0 DON or optional cost
            (r'\?\s+\(',
             self._parse_optional_cost),

            # Give -X000 power to Leader: "give your opponent's Leader −X power"
            (r'give\s+(?:your\s+)?(?:opponent\'?s?\s+)?Leader\s+[\u2212\-](\d+)(?:000)?\s+power',
             self._parse_leader_power_reduce),

            # This card cannot be trashed: "This card cannot be trashed"
            (r'this\s+(?:card|Character)\s+cannot\s+be\s+trashed',
             self._parse_cannot_trash),

            # You may trash this Character instead
            (r'(?:you\s+may\s+)?trash\s+this\s+(?:Character|card)\s+instead',
             self._parse_trash_self_instead),

            # Play color Character with cost: "Play up to X red/blue/etc Character card with a cost of Y"
            (r'play\s+(?:up\s+to\s+)?(\d+)\s+(?:red|blue|green|purple|black|yellow)\s+Characters?\s+cards?\s+(?:with\s+(?:a\s+)?cost\s+(?:of\s+)?(\d+)\s+or\s+less)?',
             self._parse_play_color_character),

            # Return X DON from field to DON deck (with ?)
            (r'[\u2212\-❶❷❸❹❺]\d*\s*\(',
             self._parse_circled_digit_cost),

            # When K.O.'d by effect: "When this Character is K.O.'d by an effect"
            (r'when\s+this\s+Character\s+is\s+K\.?O\.?\'?d?\s+by\s+(?:an?\s+)?effects?',
             self._parse_ko_by_effect),

            # Leader gains power during turn: "up to X of your Leader gains +Y power during this turn"
            (r'(?:up\s+to\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?Leader\s+gains?\s+\+(\d+)(?:000)?\s+power\s+during\s+this\s+turn',
             self._parse_leader_power_during_turn),

            # Set named Leader as active: "Set up to 1 of your [Card Name] Leader as active" or "Set your [Card Name] Leader as active"
            (r'set\s+(?:up\s+to\s+)?(?:\d+\s+of\s+)?(?:your\s+)?\[([^\]]+)\]\s+Leader\s+as\s+active',
             self._parse_set_named_leader_active),

            # Can attack Characters on play turn: "can attack Characters on the turn in which it is played"
            (r'can\s+(?:also\s+)?attack\s+Characters?\s+on\s+the\s+turn\s+in\s+which\s+(?:it\s+is|they\s+are)\s+played',
             self._parse_attack_on_play_turn),

            # Type Characters can attack on play turn: "{Type} type Characters can attack Characters on the turn"
            (r'\{([^}]+)\}\s+type\s+Characters?\s+can\s+(?:also\s+)?attack\s+Characters?\s+on\s+the\s+turn',
             self._parse_type_attack_on_play),

            # Effect negation: "negate the effect of up to X Character"
            (r'negate\s+the\s+effects?\s+of\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?Characters?',
             self._parse_negate_effect),

            # Cannot be removed from field: "cannot be removed from the field by your opponent's effects"
            (r'cannot\s+be\s+removed\s+from\s+the\s+field\s+by\s+(?:your\s+)?opponent',
             self._parse_cannot_be_removed),

            # Multi-target placement: "Place up to 1 of your opponent's Characters with a cost of X or less and up to 1... with a cost of Y or less"
            (r'place\s+(?:up\s+to\s+)?(\d+)\s+(?:of\s+)?(?:your\s+)?(?:opponent\'?s?\s+)?Characters?\s+(?:with\s+(?:a\s+)?cost\s+(?:of\s+)?(\d+)\s+or\s+less\s+)?and\s+(?:up\s+to\s+)?(\d+)',
             self._parse_multi_place_bottom),

            # Return all hand and draw equal: "Return all cards in your hand to your deck... draw cards equal to the number you returned"
            (r'return\s+all\s+cards?\s+in\s+your\s+hand\s+to\s+(?:your\s+)?deck[^.]*draw\s+cards?\s+equal\s+to',
             self._parse_return_hand_draw_equal),

            # Trash from hand as cost: "You may trash X cards from your hand:"
            (r'you\s+may\s+trash\s+(\d+)\s+cards?\s+from\s+your\s+hand\s*:',
             self._parse_trash_from_hand_cost),

            # Would be K.O.'d replacement: "would be K.O.'d by an effect, you may trash X ... instead"
            (r'would\s+be\s+K\.?O\.?\'?d?\s+by\s+(?:an?\s+)?effects?,\s+you\s+may\s+trash\s+(\d+)',
             self._parse_ko_replacement_trash),

            # Would be removed replacement: "would be removed from the field by your opponent's effect, you may"
            (r'would\s+be\s+removed\s+from\s+the\s+field\s+by\s+(?:your\s+)?opponent\'?s?\s+effects?,\s+you\s+may',
             self._parse_removal_replacement),

            # Cost reduction for type from hand: "cost of playing {Type} type Character cards... will be reduced by X"
            (r'cost\s+of\s+playing\s+\{([^}]+)\}\s+type\s+Characters?\s+cards?\s+(?:[^;]+)?(?:will\s+be\s+)?reduced\s+by\s+(\d+)',
             self._parse_type_cost_reduction),

            # Swap base power: "Swap the base power of the selected Characters"
            (r'swap\s+the\s+(?:base\s+)?power\s+of',
             self._parse_swap_power),

            # When opponent activates Event: "When your opponent activates an Event"
            (r'when\s+your\s+opponent\s+activates?\s+an?\s+Events?',
             self._parse_opponent_event_trigger),

            # Give this card in hand -X cost: "give this card in your hand -X cost"
            (r'give\s+this\s+card\s+in\s+your\s+hand\s+[\u2212\-](\d+)\s+cost',
             self._parse_self_cost_reduction),

            # Place all Characters with cost: "Place all Characters with a cost of X or less at the bottom"
            (r'place\s+all\s+Characters?\s+(?:with\s+(?:a\s+)?cost\s+(?:of\s+)?(\d+)\s+or\s+less\s+)?(?:at\s+)?(?:the\s+)?bottom',
             self._parse_place_all_characters_bottom),

            # End of battle placement: "At the end of a battle... place the opponent's Character at the bottom"
            (r'(?:at\s+)?(?:the\s+)?end\s+of\s+(?:a\s+)?battle[^;]*place\s+(?:the\s+)?(?:opponent\'?s?\s+)?Characters?\s+(?:at\s+)?(?:the\s+)?bottom',
             self._parse_end_battle_place_bottom),

            # When trashed from hand draw: "When a card is trashed from your hand... draw cards equal to"
            (r'when\s+(?:a\s+)?cards?\s+(?:is|are)\s+trashed\s+from\s+your\s+hand[^;]*draw\s+cards?\s+equal\s+to',
             self._parse_trash_trigger_draw),
        ]

        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), parser)
            for pattern, parser in self.effect_patterns
        ]

    def parse(self, effect_text: str) -> List[Effect]:
        """
        Parse effect text into a list of Effect objects.

        Args:
            effect_text: Raw effect text from card

        Returns:
            List of parsed Effect objects
        """
        if not effect_text:
            return []

        effects = []

        # First, extract standalone keywords
        keywords = extract_keywords(effect_text)
        for keyword in keywords:
            if keyword == 'RUSH':
                effects.append(KEYWORD_RUSH)
            elif keyword == 'BLOCKER':
                effects.append(KEYWORD_BLOCKER)
            elif keyword == 'BANISH':
                effects.append(KEYWORD_BANISH)
            elif keyword == 'DOUBLE_ATTACK':
                effects.append(KEYWORD_DOUBLE_ATTACK)

        # Split into separate effect clauses
        effect_parts = self.tokenizer.split_effects(effect_text)

        for part in effect_parts:
            parsed = self._parse_effect_clause(part)
            if parsed:
                effects.extend(parsed)

        return effects

    def _parse_effect_clause(self, text: str) -> List[Effect]:
        """Parse a single effect clause."""
        text = self.tokenizer.preprocess(text)
        if not text:
            return []

        effects = []
        tokens = self.tokenizer.tokenize(text)

        # Extract timing
        timing = EffectTiming.CONTINUOUS
        don_requirement = 0
        once_per_turn = False

        for token in tokens:
            if token.type == TokenType.TIMING:
                timing = self.timing_map.get(token.value, EffectTiming.CONTINUOUS)
            elif token.type == TokenType.DON_CONDITION:
                timing = EffectTiming.DON_CONDITION
                don_requirement = int(token.value)
            elif token.type == TokenType.ONCE_PER_TURN:
                once_per_turn = True

        # Check for conditional timing patterns that aren't in brackets
        # These override DON_CONDITION timing if found
        conditional_timing = self._detect_conditional_timing(text)
        if conditional_timing:
            timing = conditional_timing

        # Check for cost (indicated by colon)
        cost = None
        cost_text = ""
        effect_text = text

        # Look for "You may X:" pattern, but not "choose one:" which is a different pattern
        # Also skip if colon would leave empty effect text
        colon_match = re.search(r':\s*', text)
        if colon_match:
            potential_cost = text[:colon_match.start()]
            potential_effect = text[colon_match.end():]
            # Only split if:
            # 1. Effect text is not empty after split
            # 2. Not a "choose one:" pattern
            if potential_effect.strip() and not re.search(r'choose\s+one\s*$', potential_cost, re.IGNORECASE):
                cost_text = potential_cost
                effect_text = potential_effect
                cost = self._parse_cost(cost_text)

        # Try each pattern
        for regex, parser in self.compiled_patterns:
            match = regex.search(effect_text)
            if match:
                effect = parser(match, effect_text)
                if effect:
                    effect.timing = timing
                    effect.don_requirement = don_requirement
                    effect.once_per_turn = once_per_turn
                    effect.cost = cost
                    effect.raw_text = text
                    effects.append(effect)

        # If no patterns matched, create a generic effect
        if not effects and timing != EffectTiming.CONTINUOUS:
            # At least record the timing for unrecognized effects
            effects.append(Effect(
                effect_type=EffectType.NEGATE,  # Placeholder
                timing=timing,
                don_requirement=don_requirement,
                once_per_turn=once_per_turn,
                raw_text=text,
            ))

        return effects

    def _detect_conditional_timing(self, text: str) -> Optional[EffectTiming]:
        """
        Detect conditional timing patterns that aren't in brackets.

        These are natural language trigger conditions like:
        - "When you take damage" -> ON_TAKE_DAMAGE
        - "your Character ... is K.O.'d" -> ON_YOUR_CHARACTER_KO
        - Both combined (Ace's effect) -> ON_TAKE_DAMAGE (handles both)
        """
        text_lower = text.lower()

        # Pattern: "When you take damage" or "when you take life damage"
        take_damage_pattern = r'when\s+you\s+take\s+(?:life\s+)?damage'

        # Pattern: "your Character with X base power or more is K.O.'d"
        # Also handles: "your Character is K.O.'d"
        character_ko_pattern = r'your\s+character\s+(?:with\s+\d+(?:\s*,?\s*\d+)?\s*(?:base\s+)?power\s+or\s+more\s+)?is\s+k\.?o\.?\'?d'

        has_take_damage = re.search(take_damage_pattern, text_lower) is not None
        has_character_ko = re.search(character_ko_pattern, text_lower) is not None

        # Combined trigger (like Ace's effect): check for both OR either
        # "When you take damage or your Character ... is K.O.'d"
        if has_take_damage and has_character_ko:
            # Combined trigger - use ON_TAKE_DAMAGE as the primary timing
            # The manager will need to check both conditions
            return EffectTiming.ON_TAKE_DAMAGE
        elif has_take_damage:
            return EffectTiming.ON_TAKE_DAMAGE
        elif has_character_ko:
            return EffectTiming.ON_YOUR_CHARACTER_KO

        return None

    def _parse_cost(self, cost_text: str) -> Optional[EffectCost]:
        """Parse the cost part of an effect."""
        cost = EffectCost()
        has_cost = False

        # Rest DON
        match = re.search(r'rest\s+(\d+)\s+(?:of\s+your\s+)?DON', cost_text, re.IGNORECASE)
        if match:
            cost.don_rest = int(match.group(1))
            has_cost = True

        # Return cards from trash to deck
        match = re.search(r'return\s+(\d+)\s+cards?\s+from\s+(?:your\s+)?trash', cost_text, re.IGNORECASE)
        if match:
            cost.trash_return = int(match.group(1))
            has_cost = True

        # Discard cards
        match = re.search(r'discard\s+(\d+)\s+cards?', cost_text, re.IGNORECASE)
        if match:
            cost.discard = int(match.group(1))
            has_cost = True

        # Life to hand
        match = re.search(r'add\s+(\d+)\s+(?:card\s+)?from\s+(?:the\s+top\s+of\s+)?(?:your\s+)?Life\s+(?:cards?\s+)?to\s+(?:your\s+)?hand',
                          cost_text, re.IGNORECASE)
        if match:
            cost.life_to_hand = int(match.group(1))
            has_cost = True

        # DON!! −X (return DON to DON deck as cost) - handles Unicode minus U+2212
        match = re.search(r'DON!!\s*[\u2212\-](\d+)', cost_text, re.IGNORECASE)
        if match:
            cost.don_return = int(match.group(1))
            has_cost = True

        # Rest this Character as cost (indicated by "rest this Character:")
        if re.search(r'rest\s+this\s+(?:Character|card)', cost_text, re.IGNORECASE):
            cost.don_rest = 0  # Mark as having a rest cost but not DON
            has_cost = True

        return cost if has_cost else None

    def _parse_target_restriction(self, text: str) -> Optional[TargetRestriction]:
        """Parse target restrictions from effect text."""
        restriction = TargetRestriction()
        has_restriction = False

        # Cost restriction: "cost of X or less"
        match = re.search(r'(?:with\s+)?(?:a\s+)?cost\s+(?:of\s+)?(\d+)\s+or\s+less', text, re.IGNORECASE)
        if match:
            restriction.cost_max = int(match.group(1))
            has_restriction = True

        match = re.search(r'(?:with\s+)?(?:a\s+)?cost\s+(?:of\s+)?(\d+)\s+or\s+more', text, re.IGNORECASE)
        if match:
            restriction.cost_min = int(match.group(1))
            has_restriction = True

        # Power restriction: "X or less power"
        match = re.search(r'(\d+)(?:000)?\s+or\s+less\s+power', text, re.IGNORECASE)
        if match:
            power = int(match.group(1))
            if power < 100:
                power *= 1000
            restriction.power_max = power
            has_restriction = True

        match = re.search(r'(\d+)(?:000)?\s+or\s+more\s+power', text, re.IGNORECASE)
        if match:
            power = int(match.group(1))
            if power < 100:
                power *= 1000
            restriction.power_min = power
            has_restriction = True

        # Type restriction: {Type Name}
        match = re.search(r'\{([^}]+)\}', text)
        if match:
            restriction.types = [match.group(1)]
            has_restriction = True

        return restriction if has_restriction else None

    def _parse_search_restriction(self, text: str) -> Optional[TargetRestriction]:
        """
        Parse search-specific restrictions from effect text.

        Handles patterns like:
        - 'type including "Whitebeard Pirates"'
        - 'a {Straw Hat Crew} type'
        - 'other than [Izo]'
        - 'with a cost of 3 or less'
        """
        restriction = TargetRestriction()
        has_restriction = False

        # Type restriction with quotes: 'type including "Type Name"'
        match = re.search(r'type\s+including\s*["\u201c]([^"\u201d]+)["\u201d]', text, re.IGNORECASE)
        if match:
            restriction.types = [match.group(1)]
            has_restriction = True

        # Type restriction with braces: {Type Name}
        if not has_restriction:
            match = re.search(r'\{([^}]+)\}', text)
            if match:
                restriction.types = [match.group(1)]
                has_restriction = True

        # "other than [CardName]" exclusion
        match = re.search(r'other\s+than\s+\[([^\]]+)\]', text, re.IGNORECASE)
        if match:
            # Use "!" prefix to indicate exclusion
            restriction.name_contains = '!' + match.group(1)
            has_restriction = True

        # Cost restrictions
        match = re.search(r'(?:with\s+)?(?:a\s+)?cost\s+(?:of\s+)?(\d+)\s+or\s+less', text, re.IGNORECASE)
        if match:
            restriction.cost_max = int(match.group(1))
            has_restriction = True

        match = re.search(r'(?:with\s+)?(?:a\s+)?cost\s+(?:of\s+)?(\d+)\s+or\s+more', text, re.IGNORECASE)
        if match:
            restriction.cost_min = int(match.group(1))
            has_restriction = True

        # Power restrictions
        match = re.search(r'(\d+)(?:000)?\s+or\s+less\s+(?:base\s+)?power', text, re.IGNORECASE)
        if match:
            power = int(match.group(1))
            if power < 100:
                power *= 1000
            restriction.power_max = power
            has_restriction = True

        match = re.search(r'(\d+)(?:000)?\s+or\s+more\s+(?:base\s+)?power', text, re.IGNORECASE)
        if match:
            power = int(match.group(1))
            if power < 100:
                power *= 1000
            restriction.power_min = power
            has_restriction = True

        # Color restrictions
        color_match = re.search(r'\b(red|blue|green|purple|black|yellow)\s+(?:type\s+)?Character', text, re.IGNORECASE)
        if color_match:
            restriction.colors = [color_match.group(1).lower()]
            has_restriction = True

        return restriction if has_restriction else None

    def _determine_target_type(self, text: str) -> TargetType:
        """Determine the target type from text context."""
        text_lower = text.lower()

        if "opponent" in text_lower:
            if "leader" in text_lower:
                return TargetType.OPPONENT_LEADER
            if "character" in text_lower:
                return TargetType.OPPONENT_CHARACTER
            return TargetType.OPPONENT_CHARACTER
        elif "your" in text_lower:
            if "leader" in text_lower:
                return TargetType.YOUR_LEADER
            if "character" in text_lower:
                return TargetType.YOUR_CHARACTER
            return TargetType.YOUR_CHARACTER
        else:
            if "leader" in text_lower:
                return TargetType.ANY_CHARACTER
            return TargetType.ANY_CHARACTER

    # Individual effect parsers

    def _parse_draw(self, match: re.Match, full_text: str) -> Effect:
        """Parse draw effect."""
        count = int(match.group(1))
        return Effect(
            effect_type=EffectType.DRAW,
            timing=EffectTiming.CONTINUOUS,  # Will be set by caller
            value=count,
        )

    def _parse_ko(self, match: re.Match, full_text: str) -> Effect:
        """Parse KO effect."""
        count = int(match.group(1))
        target_type = self._determine_target_type(full_text)
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.KO,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            target_count=count,
            target_count_exact=False,  # "up to"
            target_restriction=restriction,
        )

    def _parse_power_boost(self, match: re.Match, full_text: str) -> Effect:
        """Parse power boost effect."""
        power = int(match.group(1))
        if power < 100:
            power *= 1000

        duration = Duration.INSTANT
        if "this turn" in full_text.lower():
            duration = Duration.THIS_TURN
        elif "this battle" in full_text.lower():
            duration = Duration.THIS_BATTLE

        target_type = self._determine_target_type(full_text)

        return Effect(
            effect_type=EffectType.POWER_BOOST,
            timing=EffectTiming.CONTINUOUS,
            value=power,
            duration=duration,
            target_type=target_type,
        )

    def _parse_power_zero(self, match: re.Match, full_text: str) -> Effect:
        """Parse set power to 0 effect."""
        duration = Duration.THIS_TURN
        target_type = self._determine_target_type(full_text)

        return Effect(
            effect_type=EffectType.POWER_REDUCE,
            timing=EffectTiming.CONTINUOUS,
            value=0,  # Set to 0
            duration=duration,
            target_type=target_type,
        )

    def _parse_power_reduce(self, match: re.Match, full_text: str) -> Effect:
        """Parse power reduction effect."""
        power = int(match.group(1))
        if power < 100:
            power *= 1000

        duration = Duration.THIS_TURN
        if "this battle" in full_text.lower():
            duration = Duration.THIS_BATTLE

        return Effect(
            effect_type=EffectType.POWER_REDUCE,
            timing=EffectTiming.CONTINUOUS,
            value=power,
            duration=duration,
        )

    def _parse_power_reduce_opponent(self, match: re.Match, full_text: str) -> Effect:
        """Parse power reduction to opponent's cards."""
        power = int(match.group(1))
        if power < 100:
            power *= 1000

        duration = Duration.THIS_TURN
        if "this battle" in full_text.lower():
            duration = Duration.THIS_BATTLE

        # Determine target
        if "leader" in full_text.lower():
            target_type = TargetType.OPPONENT_LEADER
        else:
            target_type = TargetType.OPPONENT_CHARACTER

        return Effect(
            effect_type=EffectType.POWER_REDUCE,
            timing=EffectTiming.CONTINUOUS,
            value=power,
            target_type=target_type,
            duration=duration,
        )

    def _parse_conditional_power_reduce(self, match: re.Match, full_text: str) -> Effect:
        """Parse conditional power reduction (e.g., If you have X or less Life cards, give -Y power)."""
        life_threshold = int(match.group(1))
        power = int(match.group(2))
        if power < 100:
            power *= 1000

        duration = Duration.THIS_TURN
        if "this battle" in full_text.lower():
            duration = Duration.THIS_BATTLE

        # Determine target
        if "leader" in full_text.lower():
            target_type = TargetType.OPPONENT_LEADER
        else:
            target_type = TargetType.OPPONENT_CHARACTER

        # Create restriction for life condition
        restriction = TargetRestriction()
        restriction.your_life_max = life_threshold

        return Effect(
            effect_type=EffectType.POWER_REDUCE,
            timing=EffectTiming.CONTINUOUS,
            value=power,
            target_type=target_type,
            target_restriction=restriction,
            duration=duration,
        )

    def _parse_conditional_don_attach(self, match: re.Match, full_text: str) -> Effect:
        """Parse conditional DON attachment (e.g., If opponent has X or less Life cards, give Y DON)."""
        life_threshold = int(match.group(1))
        don_count = int(match.group(2))

        # Determine target for DON attachment
        if "leader" in full_text.lower():
            target_type = TargetType.YOUR_LEADER
        else:
            target_type = TargetType.YOUR_CHARACTER

        # Create restriction for life condition (opponent's life)
        restriction = TargetRestriction()
        restriction.opponent_life_max = life_threshold

        return Effect(
            effect_type=EffectType.DON_ATTACH,
            timing=EffectTiming.CONTINUOUS,
            value=don_count,
            target_type=target_type,
            target_restriction=restriction,
        )

    def _parse_rest(self, match: re.Match, full_text: str) -> Effect:
        """Parse rest effect."""
        count = int(match.group(1))
        target_type = self._determine_target_type(full_text)

        if "don" in full_text.lower():
            target_type = TargetType.OPPONENT_DON if "opponent" in full_text.lower() else TargetType.YOUR_DON

        return Effect(
            effect_type=EffectType.REST,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            target_count=count,
        )

    def _parse_don_activate(self, match: re.Match, full_text: str) -> Effect:
        """Parse DON activation effect."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.DON_ACTIVATE,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_DON,
            target_count=count,
        )

    def _parse_don_add(self, match: re.Match, full_text: str) -> Effect:
        """Parse add DON effect."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.DON_ADD,
            timing=EffectTiming.CONTINUOUS,
            value=count,
        )

    def _parse_play_this(self, match: re.Match, full_text: str) -> Effect:
        """Parse 'play this card' effect."""
        return Effect(
            effect_type=EffectType.PLAY,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
        )

    def _parse_play_character(self, match: re.Match, full_text: str) -> Effect:
        """Parse play character effect."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.PLAY,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_HAND,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_return_to_deck(self, match: re.Match, full_text: str) -> Effect:
        """Parse return to deck effect."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.RETURN_TO_DECK,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_TRASH,
            target_count=count,
        )

    def _parse_cannot_block(self, match: re.Match, full_text: str) -> Effect:
        """Parse cannot be blocked effect."""
        return Effect(
            effect_type=EffectType.REMOVE_BLOCKER,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
        )

    def _parse_blocker_restriction(self, match: re.Match, full_text: str) -> Effect:
        """Parse blocker restriction effect."""
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.REMOVE_BLOCKER,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.OPPONENT_CHARACTER,
            target_restriction=restriction,
        )

    def _parse_protect(self, match: re.Match, full_text: str) -> Effect:
        """Parse protection effect."""
        duration = Duration.THIS_TURN
        if "this battle" in full_text.lower():
            duration = Duration.THIS_BATTLE

        return Effect(
            effect_type=EffectType.PROTECT,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
            duration=duration,
        )

    def _parse_add_life(self, match: re.Match, full_text: str) -> Effect:
        """Parse add to life effect."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.LIFE_ADD,
            timing=EffectTiming.CONTINUOUS,
            value=count,
        )

    def _parse_search(self, match: re.Match, full_text: str) -> Effect:
        """Parse search/look effect with type and name restrictions."""
        count = int(match.group(1)) if match.group(1) else 5

        # Extract type and name restrictions from the full text
        restriction = self._parse_search_restriction(full_text)

        return Effect(
            effect_type=EffectType.SEARCH,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_DECK,
            value=count,
            target_restriction=restriction,
        )

    def _parse_return_to_hand(self, match: re.Match, full_text: str) -> Effect:
        """Parse return to hand effect."""
        count = int(match.group(1))
        target_type = self._determine_target_type(full_text)
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.RETURN_TO_HAND,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_don_attach(self, match: re.Match, full_text: str) -> Effect:
        """Parse give DON / attach DON effect."""
        count = int(match.group(1))

        # Determine target (Leader or Character)
        if "leader" in full_text.lower():
            target_type = TargetType.YOUR_LEADER
        else:
            target_type = TargetType.YOUR_CHARACTER

        return Effect(
            effect_type=EffectType.DON_ATTACH,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            target_count=count,
        )

    def _parse_add_to_hand(self, match: re.Match, full_text: str) -> Effect:
        """Parse add to hand effect (from look/reveal)."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.RETURN_TO_HAND,  # Reuse for adding to hand
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_DECK,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_trash(self, match: re.Match, full_text: str) -> Effect:
        """Parse trash effect."""
        count = int(match.group(1))
        target_type = self._determine_target_type(full_text)
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.TRASH,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_cost_reduce(self, match: re.Match, full_text: str) -> Effect:
        """Parse cost reduction effect."""
        amount = int(match.group(1))

        return Effect(
            effect_type=EffectType.COST_REDUCE,
            timing=EffectTiming.CONTINUOUS,
            value=amount,
            target_type=TargetType.SELF,
        )

    def _parse_place_bottom(self, match: re.Match, full_text: str) -> Effect:
        """Parse place at bottom of deck effect."""
        count = int(match.group(1)) if match.group(1) else 1
        target_type = self._determine_target_type(full_text)

        return Effect(
            effect_type=EffectType.RETURN_TO_DECK,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            target_count=count,
        )

    def _parse_cannot_attack(self, match: re.Match, full_text: str) -> Effect:
        """Parse cannot attack effect."""
        target_type = self._determine_target_type(full_text)
        if target_type == TargetType.ANY_CHARACTER:
            target_type = TargetType.OPPONENT_CHARACTER

        return Effect(
            effect_type=EffectType.REST,  # Effectively prevents attack
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            duration=Duration.THIS_TURN,
        )

    def _parse_blocker_restriction_full(self, match: re.Match, full_text: str) -> Effect:
        """Parse blocker restriction with optional power threshold."""
        restriction = None
        if match.group(1):
            power = int(match.group(1))
            if power < 100:
                power *= 1000
            restriction = TargetRestriction(power_min=power)

        return Effect(
            effect_type=EffectType.REMOVE_BLOCKER,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.OPPONENT_CHARACTER,
            target_restriction=restriction,
            duration=Duration.THIS_BATTLE,
        )

    def _parse_grant_rush(self, match: re.Match, full_text: str) -> Effect:
        """Parse grant Rush effect."""
        return Effect(
            effect_type=EffectType.GRANT_RUSH,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
            duration=Duration.PERMANENT,
        )

    def _parse_grant_blocker_parse(self, match: re.Match, full_text: str) -> Effect:
        """Parse grant Blocker effect."""
        return Effect(
            effect_type=EffectType.GRANT_BLOCKER,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
            duration=Duration.PERMANENT,
        )

    def _parse_power_boost_other(self, match: re.Match, full_text: str) -> Effect:
        """Parse power boost to Leader/Character other than self."""
        power = int(match.group(1))
        if power < 100:
            power *= 1000

        duration = Duration.THIS_TURN
        if "this battle" in full_text.lower():
            duration = Duration.THIS_BATTLE

        # Determine target
        if "leader" in full_text.lower():
            target_type = TargetType.YOUR_LEADER
        else:
            target_type = TargetType.YOUR_CHARACTER

        return Effect(
            effect_type=EffectType.POWER_BOOST,
            timing=EffectTiming.CONTINUOUS,
            value=power,
            target_type=target_type,
            duration=duration,
        )

    def _parse_look_life(self, match: re.Match, full_text: str) -> Effect:
        """Parse look at Life cards effect."""
        count = int(match.group(1))

        # Determine whose life
        if "opponent" in full_text.lower():
            target_type = TargetType.OPPONENT_LEADER  # Use leader as proxy for life
        else:
            target_type = TargetType.YOUR_LIFE

        return Effect(
            effect_type=EffectType.LOOK,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            value=count,
        )

    def _parse_look_all_life(self, match: re.Match, full_text: str) -> Effect:
        """Parse look at all Life cards effect."""
        return Effect(
            effect_type=EffectType.LOOK,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_LIFE,
            value=99,  # All cards
        )

    def _parse_look_reveal_add(self, match: re.Match, full_text: str) -> Effect:
        """Parse look at deck + reveal + add to hand effect."""
        look_count = int(match.group(1))
        reveal_count = int(match.group(2))
        restriction = self._parse_target_restriction(full_text)

        # This is a composite effect - look + reveal + add to hand
        # We'll treat it as a SEARCH effect for simplicity
        return Effect(
            effect_type=EffectType.SEARCH,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_DECK,
            value=look_count,
            target_count=reveal_count,
            target_restriction=restriction,
        )

    def _parse_ko_rested(self, match: re.Match, full_text: str) -> Effect:
        """Parse K.O. rested Characters effect."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        # Add resting restriction
        if restriction is None:
            restriction = TargetRestriction()
        restriction.is_resting = True

        return Effect(
            effect_type=EffectType.KO,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.OPPONENT_CHARACTER,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_give_cost_reduce(self, match: re.Match, full_text: str) -> Effect:
        """Parse give -X cost during this turn effect."""
        amount = int(match.group(1))
        target_type = self._determine_target_type(full_text)

        return Effect(
            effect_type=EffectType.COST_REDUCE,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            value=amount,
            duration=Duration.THIS_TURN,
        )

    def _parse_place_self_bottom(self, match: re.Match, full_text: str) -> Effect:
        """Parse place this Character at bottom of deck effect."""
        return Effect(
            effect_type=EffectType.RETURN_TO_DECK,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
            target_count=1,
        )

    def _parse_return_character_to_hand(self, match: re.Match, full_text: str) -> Effect:
        """Parse return Character to hand with optional cost restriction."""
        count = int(match.group(1))
        target_type = self._determine_target_type(full_text)
        restriction = self._parse_target_restriction(full_text)

        # Check for cost restriction in the match
        if match.lastindex >= 2 and match.group(2):
            if restriction is None:
                restriction = TargetRestriction()
            restriction.cost_max = int(match.group(2))

        return Effect(
            effect_type=EffectType.RETURN_TO_HAND,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_look_reorder(self, match: re.Match, full_text: str) -> Effect:
        """Parse look at deck and reorder effect."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.LOOK,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_DECK,
            value=count,
        )

    def _parse_don_return_cost(self, match: re.Match, full_text: str) -> Effect:
        """Parse DON!! -X as a cost indicator (return DON to deck)."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.DON_REST,  # Return DON as cost
            timing=EffectTiming.CONTINUOUS,
            value=count,
            target_type=TargetType.YOUR_DON,
        )

    def _parse_play_type_character(self, match: re.Match, full_text: str) -> Effect:
        """Parse play specific type Character effect."""
        count = int(match.group(1))
        card_type = match.group(2)  # e.g., "Heart Pirates"

        restriction = TargetRestriction()
        restriction.types = [card_type]

        return Effect(
            effect_type=EffectType.PLAY,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_HAND,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_place_character_bottom(self, match: re.Match, full_text: str) -> Effect:
        """Parse place Character at bottom of deck with optional cost restriction."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        # Check for cost restriction in the match
        if match.lastindex >= 2 and match.group(2):
            if restriction is None:
                restriction = TargetRestriction()
            restriction.cost_max = int(match.group(2))

        target_type = self._determine_target_type(full_text)

        return Effect(
            effect_type=EffectType.RETURN_TO_DECK,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_play_named_card(self, match: re.Match, full_text: str) -> Effect:
        """Parse play specific named card effect."""
        count = int(match.group(1))
        card_name = match.group(2)

        restriction = TargetRestriction()
        restriction.name_contains = card_name

        # Check for cost restriction
        if match.lastindex >= 3 and match.group(3):
            restriction.cost_max = int(match.group(3))

        return Effect(
            effect_type=EffectType.PLAY,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_HAND,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_attack_active(self, match: re.Match, full_text: str) -> Effect:
        """Parse can attack active Characters effect."""
        return Effect(
            effect_type=EffectType.GRANT_RUSH,  # Ability to attack active Characters
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
            duration=Duration.PERMANENT,
            condition="can_attack_active",
        )

    def _parse_add_to_life(self, match: re.Match, full_text: str) -> Effect:
        """Parse add card to Life effect."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.LIFE_ADD,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_DECK,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_look_place(self, match: re.Match, full_text: str) -> Effect:
        """Parse look at deck and place at top/bottom effect."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.LOOK,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_DECK,
            value=count,
        )

    def _parse_play_multi_type(self, match: re.Match, full_text: str) -> Effect:
        """Parse play multi-type Character effect."""
        count = int(match.group(1))
        types = [match.group(2)]
        if match.lastindex >= 3 and match.group(3):
            types.append(match.group(3))

        restriction = TargetRestriction()
        restriction.types = types

        return Effect(
            effect_type=EffectType.PLAY,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_HAND,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_life_to_hand(self, match: re.Match, full_text: str) -> Effect:
        """Parse add Life card to hand effect."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.DRAW,  # Drawing from life
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_LIFE,
            target_count=count,
        )

    def _parse_protect_from_opponent(self, match: re.Match, full_text: str) -> Effect:
        """Parse cannot be K.O.'d by opponent effect."""
        return Effect(
            effect_type=EffectType.PROTECT,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
            duration=Duration.PERMANENT,
        )

    def _parse_opponent_discard(self, match: re.Match, full_text: str) -> Effect:
        """Parse opponent discards effect."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.DISCARD,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.OPPONENT_HAND,
            target_count=count,
        )

    def _parse_give_all_cost_reduce(self, match: re.Match, full_text: str) -> Effect:
        """Parse give all Characters -X cost effect."""
        amount = int(match.group(1))

        target_type = TargetType.OPPONENT_CHARACTERS if "opponent" in full_text.lower() else TargetType.YOUR_CHARACTERS

        return Effect(
            effect_type=EffectType.COST_REDUCE,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            value=amount,
            duration=Duration.THIS_TURN,
        )

    def _parse_gains_keyword(self, match: re.Match, full_text: str) -> Effect:
        """Parse This Character gains [keyword] effect."""
        keyword = match.group(1).upper()

        # Map keyword to effect type
        keyword_map = {
            'RUSH': EffectType.GRANT_RUSH,
            'BLOCKER': EffectType.GRANT_BLOCKER,
            'BANISH': EffectType.GRANT_BANISH,
            'DOUBLE ATTACK': EffectType.GRANT_DOUBLE_ATTACK,
        }

        effect_type = keyword_map.get(keyword, EffectType.GRANT_RUSH)

        return Effect(
            effect_type=effect_type,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
            duration=Duration.PERMANENT,
        )

    def _parse_set_cost(self, match: re.Match, full_text: str) -> Effect:
        """Parse set cost to X effect."""
        cost_value = int(match.group(1))
        target_type = self._determine_target_type(full_text)

        return Effect(
            effect_type=EffectType.COST_REDUCE,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            value=cost_value,  # Set to specific value
            duration=Duration.THIS_TURN,
        )

    def _parse_gains_cost(self, match: re.Match, full_text: str) -> Effect:
        """Parse gains +X cost effect."""
        amount = int(match.group(1))

        return Effect(
            effect_type=EffectType.COST_REDUCE,  # Negative cost reduce = cost increase
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
            value=-amount,  # Negative to indicate increase
            duration=Duration.THIS_TURN,
        )

    def _parse_prevent_attack(self, match: re.Match, full_text: str) -> Effect:
        """Parse Characters cannot attack effect."""
        target_type = TargetType.OPPONENT_CHARACTERS if "opponent" in full_text.lower() else TargetType.YOUR_CHARACTERS

        return Effect(
            effect_type=EffectType.REST,  # Effectively prevents attack
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            duration=Duration.THIS_TURN,
        )

    def _parse_cannot_be_attacked(self, match: re.Match, full_text: str) -> Effect:
        """Parse cannot be attacked effect."""
        return Effect(
            effect_type=EffectType.PROTECT,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
            duration=Duration.THIS_TURN,
        )

    def _parse_opponent_return_to_deck(self, match: re.Match, full_text: str) -> Effect:
        """Parse opponent returns cards to deck effect."""
        return Effect(
            effect_type=EffectType.RETURN_TO_DECK,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.OPPONENT_HAND,
        )

    def _parse_opponent_place_bottom(self, match: re.Match, full_text: str) -> Effect:
        """Parse opponent places cards from hand at bottom of deck."""
        count = int(match.group(1))
        return Effect(
            effect_type=EffectType.RETURN_TO_DECK,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.OPPONENT_HAND,
            value=count,
            raw_text="Opponent places cards at bottom of deck",
        )

    def _parse_place_at_life(self, match: re.Match, full_text: str) -> Effect:
        """Parse place character at life (top/bottom)."""
        count = int(match.group(1)) if match.group(1) else 1
        return Effect(
            effect_type=EffectType.LIFE_ADD,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.OPPONENT_CHARACTER,
            value=count,
            raw_text="Place character at Life",
        )

    def _parse_conditional_draw(self, match: re.Match, full_text: str) -> Effect:
        """Parse conditional draw (draw X if you have Y or less cards in hand)."""
        draw_count = int(match.group(1))
        hand_threshold = int(match.group(2))

        restriction = TargetRestriction()
        # Use a custom field or condition to track hand size requirement
        # For now, we'll just parse the draw effect

        return Effect(
            effect_type=EffectType.DRAW,
            timing=EffectTiming.CONTINUOUS,
            value=draw_count,
            condition=f"hand_size_max:{hand_threshold}",
        )

    def _parse_life_to_hand_top(self, match: re.Match, full_text: str) -> Effect:
        """Parse add Life card from top to hand effect."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.DRAW,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_LIFE,
            value=count,
        )

    def _parse_circled_cost(self, match: re.Match, full_text: str) -> Effect:
        """Parse circled number cost (❶ means rest 1 DON)."""
        # Map circled digits to values
        circled = match.group(0)[0]
        # Unicode circled digits: ① = 0x2460, ② = 0x2461, etc.
        value = ord(circled) - 0x245F  # ① is 1, ② is 2, etc.

        return Effect(
            effect_type=EffectType.DON_REST,
            timing=EffectTiming.CONTINUOUS,
            value=value,
            target_type=TargetType.YOUR_DON,
        )

    def _parse_play_from_trash_rested(self, match: re.Match, full_text: str) -> Effect:
        """Parse play card from trash rested effect."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.PLAY,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_TRASH,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_set_characters_active(self, match: re.Match, full_text: str) -> Effect:
        """Parse set Characters as active effect."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.ACTIVATE,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_CHARACTER,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_prevent_refresh(self, match: re.Match, full_text: str) -> Effect:
        """Parse prevent refresh phase activation effect."""
        target_type = self._determine_target_type(full_text)

        return Effect(
            effect_type=EffectType.REST,  # Prevents becoming active
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            duration=Duration.NEXT_TURN,
        )

    def _parse_choose_play_from_trash(self, match: re.Match, full_text: str) -> Effect:
        """Parse choose and play from trash effect."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.PLAY,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_TRASH,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_add_to_life_face(self, match: re.Match, full_text: str) -> Effect:
        """Parse add to Life face-up/down effect."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.LIFE_ADD,
            timing=EffectTiming.CONTINUOUS,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_return_multiple_characters(self, match: re.Match, full_text: str) -> Effect:
        """Parse return multiple Characters with different cost requirements."""
        count1 = int(match.group(1))
        cost1 = int(match.group(2))
        count2 = int(match.group(3))
        cost2 = int(match.group(4))

        # Return the first (higher cost) part
        restriction = TargetRestriction()
        restriction.cost_max = max(cost1, cost2)

        target_type = self._determine_target_type(full_text)

        return Effect(
            effect_type=EffectType.RETURN_TO_HAND,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            target_count=count1 + count2,
            target_restriction=restriction,
        )

    def _parse_opponent_place_bottom(self, match: re.Match, full_text: str) -> Effect:
        """Parse opponent places Character at bottom of deck."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.RETURN_TO_DECK,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.OPPONENT_CHARACTER,
            target_count=count,
        )

    def _parse_gains_banish_temp(self, match: re.Match, full_text: str) -> Effect:
        """Parse gains Banish during this turn effect."""
        target_type = self._determine_target_type(full_text)

        return Effect(
            effect_type=EffectType.GRANT_BANISH,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            duration=Duration.THIS_TURN,
        )

    def _parse_rest_self_cost(self, match: re.Match, full_text: str) -> Effect:
        """Parse rest this Character as cost effect."""
        return Effect(
            effect_type=EffectType.REST,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
        )

    def _parse_conditional_look(self, match: re.Match, full_text: str) -> Effect:
        """Parse conditional look at deck effect."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.LOOK,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_DECK,
            value=count,
        )

    def _parse_set_self_active(self, match: re.Match, full_text: str) -> Effect:
        """Parse set this Character as active effect."""
        return Effect(
            effect_type=EffectType.ACTIVATE,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
        )

    def _parse_reveal_to_life(self, match: re.Match, full_text: str) -> Effect:
        """Parse reveal from hand and add to Life effect."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.LIFE_ADD,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_HAND,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_add_from_trash_except(self, match: re.Match, full_text: str) -> Effect:
        """Parse add from trash to hand with name exclusion."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.RETURN_TO_HAND,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_TRASH,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_don_attach_leader(self, match: re.Match, full_text: str) -> Effect:
        """Parse give DON to Leader effect."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.DON_ATTACH,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_LEADER,
            value=count,
        )

    def _parse_trash_cost(self, match: re.Match, full_text: str) -> Effect:
        """Parse trash cards from hand as cost."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.TRASH,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_HAND,
            target_count=count,
        )

    def _parse_opponent_trash(self, match: re.Match, full_text: str) -> Effect:
        """Parse opponent trashes from hand effect."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.TRASH,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.OPPONENT_HAND,
            target_count=count,
        )

    def _parse_protect_from_effects(self, match: re.Match, full_text: str) -> Effect:
        """Parse cannot be K.O.'d by effects."""
        return Effect(
            effect_type=EffectType.PROTECT,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
            duration=Duration.PERMANENT,
        )

    def _parse_play_rested(self, match: re.Match, full_text: str) -> Effect:
        """Parse play card rested effect."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.PLAY,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_HAND,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_extra_turn(self, match: re.Match, full_text: str) -> Effect:
        """Parse take an extra turn effect."""
        return Effect(
            effect_type=EffectType.EXTRA_TURN,
            timing=EffectTiming.CONTINUOUS,
        )

    def _parse_add_don_active(self, match: re.Match, full_text: str) -> Effect:
        """Parse add DON from DON deck and set active."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.DON_ADD,
            timing=EffectTiming.CONTINUOUS,
            value=count,
        )

    def _parse_conditional_add_from_trash(self, match: re.Match, full_text: str) -> Effect:
        """Parse conditional add from trash effect."""
        required_type = match.group(1)
        count = int(match.group(2))

        restriction = TargetRestriction()
        restriction.types = [required_type]

        return Effect(
            effect_type=EffectType.RETURN_TO_HAND,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_TRASH,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_add_type_from_trash(self, match: re.Match, full_text: str) -> Effect:
        """Parse add type Character from trash to hand."""
        count = int(match.group(1))
        card_type = match.group(2)

        restriction = TargetRestriction()
        restriction.types = [card_type]

        # Check for cost restriction
        cost_match = re.search(r'cost\s+(?:of\s+)?(\d+)\s+or\s+less', full_text, re.IGNORECASE)
        if cost_match:
            restriction.cost_max = int(cost_match.group(1))

        return Effect(
            effect_type=EffectType.RETURN_TO_HAND,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_TRASH,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_add_generic_from_trash(self, match: re.Match, full_text: str) -> Effect:
        """Parse generic add from trash to hand effect."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.RETURN_TO_HAND,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_TRASH,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_can_attack_active(self, match: re.Match, full_text: str) -> Effect:
        """Parse can attack active Characters effect."""
        return Effect(
            effect_type=EffectType.GRANT_RUSH,  # Represents ability to attack active
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
            duration=Duration.PERMANENT,
            condition="can_attack_active",
        )

    def _parse_power_until_next_turn(self, match: re.Match, full_text: str) -> Effect:
        """Parse power boost until next turn."""
        power = int(match.group(1))
        if power < 100:
            power *= 1000

        target_type = self._determine_target_type(full_text)

        return Effect(
            effect_type=EffectType.POWER_BOOST,
            timing=EffectTiming.CONTINUOUS,
            value=power,
            target_type=target_type,
            duration=Duration.NEXT_TURN,
        )

    def _parse_ko_all(self, match: re.Match, full_text: str) -> Effect:
        """Parse K.O. all Characters effect."""
        return Effect(
            effect_type=EffectType.KO,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_CHARACTERS if "other than this" in full_text.lower() else TargetType.ANY_CHARACTER,
            target_count=99,  # All
        )

    def _parse_place_all_bottom(self, match: re.Match, full_text: str) -> Effect:
        """Parse place all Characters at bottom of deck."""
        return Effect(
            effect_type=EffectType.RETURN_TO_DECK,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_CHARACTERS,
            target_count=99,  # All
        )

    def _parse_return_self_to_hand(self, match: re.Match, full_text: str) -> Effect:
        """Parse return this Character to hand."""
        return Effect(
            effect_type=EffectType.RETURN_TO_HAND,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
        )

    def _parse_set_don_active(self, match: re.Match, full_text: str) -> Effect:
        """Parse set DON as active."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.DON_ACTIVATE,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_DON,
            target_count=count,
        )

    def _parse_draw_to_hand_size(self, match: re.Match, full_text: str) -> Effect:
        """Parse draw to specific hand size."""
        target_size = int(match.group(1))

        return Effect(
            effect_type=EffectType.DRAW,
            timing=EffectTiming.CONTINUOUS,
            value=target_size,
            condition="draw_to_hand_size",
        )

    def _parse_give_minus_power(self, match: re.Match, full_text: str) -> Effect:
        """Parse give -X power effect."""
        power = int(match.group(1))
        if power < 100:
            power *= 1000

        target_type = self._determine_target_type(full_text)

        return Effect(
            effect_type=EffectType.POWER_REDUCE,
            timing=EffectTiming.CONTINUOUS,
            value=power,
            target_type=target_type,
            duration=Duration.THIS_TURN,
        )

    def _parse_add_don_rested(self, match: re.Match, full_text: str) -> Effect:
        """Parse add DON from DON deck and rest it."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.DON_ADD,
            timing=EffectTiming.CONTINUOUS,
            value=count,
        )

    def _parse_characters_power_restriction(self, match: re.Match, full_text: str) -> Effect:
        """Parse effect targeting Characters with power restriction."""
        power = int(match.group(1))
        if power < 100:
            power *= 1000

        restriction = TargetRestriction()
        restriction.power_max = power

        return Effect(
            effect_type=EffectType.KO,  # Usually these are K.O. effects
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.OPPONENT_CHARACTER,
            target_restriction=restriction,
        )

    def _parse_negate_on_play(self, match: re.Match, full_text: str) -> Effect:
        """Parse negate On Play effects."""
        target_type = TargetType.OPPONENT_CHARACTER if "opponent" in full_text.lower() else TargetType.YOUR_CHARACTER

        return Effect(
            effect_type=EffectType.NEGATE,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            condition="negate_on_play",
        )

    def _parse_play_with_trigger(self, match: re.Match, full_text: str) -> Effect:
        """Parse play Character with Trigger effect."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.PLAY,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_HAND,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_rest_leader_or_character(self, match: re.Match, full_text: str) -> Effect:
        """Parse rest Leader or Character effect."""
        count = int(match.group(1))
        target_type = self._determine_target_type(full_text)

        return Effect(
            effect_type=EffectType.REST,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            target_count=count,
        )

    def _parse_play_each_of(self, match: re.Match, full_text: str) -> Effect:
        """Parse play each of multiple named cards."""
        count = int(match.group(1))
        # First name is captured, others are in the text
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.PLAY,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_HAND,
            target_count=count * 3,  # Typically 3 named cards
            target_restriction=restriction,
        )

    def _parse_don_field_condition(self, match: re.Match, full_text: str) -> Effect:
        """Parse DON field count condition effect."""
        # This is a conditional effect - parse the actual effect after the condition
        # Look for play pattern after the condition
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.PLAY,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_HAND,
            target_restriction=restriction,
            condition="don_field_count",
        )

    def _parse_set_leader_active(self, match: re.Match, full_text: str) -> Effect:
        """Parse set Leader as active effect."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.ACTIVATE,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_LEADER,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_add_to_life_position(self, match: re.Match, full_text: str) -> Effect:
        """Parse add to Life at top or bottom effect."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.LIFE_ADD,
            timing=EffectTiming.CONTINUOUS,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_ko_cost_zero(self, match: re.Match, full_text: str) -> Effect:
        """Parse K.O. Characters with cost of 0."""
        count = int(match.group(1))

        restriction = TargetRestriction()
        restriction.cost_exact = 0

        return Effect(
            effect_type=EffectType.KO,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.OPPONENT_CHARACTER,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_give_cost_reduction(self, match: re.Match, full_text: str) -> Effect:
        """Parse give -X cost during this turn."""
        amount = int(match.group(1))
        target_type = self._determine_target_type(full_text)

        return Effect(
            effect_type=EffectType.COST_REDUCE,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            value=amount,
            duration=Duration.THIS_TURN,
        )

    def _parse_leader_power_boost(self, match: re.Match, full_text: str) -> Effect:
        """Parse Leader gains power until next turn."""
        power = int(match.group(1))
        if power < 100:
            power *= 1000

        return Effect(
            effect_type=EffectType.POWER_BOOST,
            timing=EffectTiming.CONTINUOUS,
            value=power,
            target_type=TargetType.YOUR_LEADER,
            duration=Duration.NEXT_TURN,
        )

    def _parse_play_cost_trigger(self, match: re.Match, full_text: str) -> Effect:
        """Parse play Character with cost and Trigger."""
        count = int(match.group(1))
        cost_max = int(match.group(2))

        restriction = TargetRestriction()
        restriction.cost_max = cost_max

        return Effect(
            effect_type=EffectType.PLAY,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_HAND,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_rest_total(self, match: re.Match, full_text: str) -> Effect:
        """Parse rest a total of X Characters or DON."""
        count = int(match.group(1))
        target_type = self._determine_target_type(full_text)

        return Effect(
            effect_type=EffectType.REST,
            timing=EffectTiming.CONTINUOUS,
            target_type=target_type,
            target_count=count,
        )

    def _parse_play_self_from_trash(self, match: re.Match, full_text: str) -> Effect:
        """Parse play this Character from trash rested."""
        return Effect(
            effect_type=EffectType.PLAY,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
        )

    def _parse_base_cost_characters(self, match: re.Match, full_text: str) -> Effect:
        """Parse effect targeting Characters with base cost."""
        cost = int(match.group(1))

        restriction = TargetRestriction()
        restriction.cost_exact = cost

        return Effect(
            effect_type=EffectType.PROTECT,  # Often protection for specific cost
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_CHARACTER,
            target_restriction=restriction,
        )

    def _parse_reveal_play_rested(self, match: re.Match, full_text: str) -> Effect:
        """Parse reveal from deck and play rested."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.PLAY,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_DECK,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_power_boost_this_turn(self, match: re.Match, full_text: str) -> Effect:
        """Parse power boost during this turn."""
        power = int(match.group(1))
        if power < 100:
            power *= 1000

        target_type = self._determine_target_type(full_text)

        return Effect(
            effect_type=EffectType.POWER_BOOST,
            timing=EffectTiming.CONTINUOUS,
            value=power,
            target_type=target_type,
            duration=Duration.THIS_TURN,
        )

    def _parse_cost_will_reduce(self, match: re.Match, full_text: str) -> Effect:
        """Parse cost will be reduced by X."""
        amount = int(match.group(1))

        return Effect(
            effect_type=EffectType.COST_REDUCE,
            timing=EffectTiming.CONTINUOUS,
            value=amount,
            target_type=TargetType.YOUR_HAND,
            duration=Duration.THIS_TURN,
        )

    def _parse_search_deck(self, match: re.Match, full_text: str) -> Effect:
        """Parse search deck effect."""
        count = int(match.group(1))
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.SEARCH,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_DECK,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_set_this_leader_active(self, match: re.Match, full_text: str) -> Effect:
        """Parse set this Leader as active."""
        return Effect(
            effect_type=EffectType.ACTIVATE,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_LEADER,
        )

    def _parse_hand_size_condition(self, match: re.Match, full_text: str) -> Effect:
        """Parse hand size condition effect."""
        hand_size = int(match.group(1))

        # Look for what happens after the condition
        # Usually it's setting Leader as active
        if "set" in full_text.lower() and "leader" in full_text.lower():
            return Effect(
                effect_type=EffectType.ACTIVATE,
                timing=EffectTiming.CONTINUOUS,
                target_type=TargetType.YOUR_LEADER,
                condition=f"hand_size_max:{hand_size}",
            )

        return Effect(
            effect_type=EffectType.DRAW,
            timing=EffectTiming.CONTINUOUS,
            condition=f"hand_size_max:{hand_size}",
        )

    def _parse_don_high_cost(self, match: re.Match, full_text: str) -> Effect:
        """Parse DON!! -X cost with high number."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.DON_REST,
            timing=EffectTiming.CONTINUOUS,
            value=count,
            target_type=TargetType.YOUR_DON,
        )

    def _parse_choose_one(self, match: re.Match, full_text: str) -> Effect:
        """Parse choose one effect."""
        # This is a choice effect - parse the options that follow
        restriction = self._parse_target_restriction(full_text)

        return Effect(
            effect_type=EffectType.CHOOSE,
            timing=EffectTiming.CONTINUOUS,
            target_restriction=restriction,
        )

    def _parse_play_type_cost(self, match: re.Match, full_text: str) -> Effect:
        """Parse play type Character with cost effect."""
        count = int(match.group(1))
        card_type = match.group(2)

        restriction = TargetRestriction()
        restriction.types = [card_type]

        if match.lastindex >= 3 and match.group(3):
            restriction.cost_max = int(match.group(3))

        return Effect(
            effect_type=EffectType.PLAY,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_HAND,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_add_don_simple(self, match: re.Match, full_text: str) -> Effect:
        """Parse add DON from DON deck (simple version)."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.DON_ADD,
            timing=EffectTiming.CONTINUOUS,
            value=count,
        )

    def _parse_events_cost_reduce(self, match: re.Match, full_text: str) -> Effect:
        """Parse give Events cost reduction."""
        amount = int(match.group(1))

        return Effect(
            effect_type=EffectType.COST_REDUCE,
            timing=EffectTiming.CONTINUOUS,
            value=amount,
            target_type=TargetType.YOUR_HAND,
        )

    def _parse_protect_rested(self, match: re.Match, full_text: str) -> Effect:
        """Parse protection for rested Characters."""
        return Effect(
            effect_type=EffectType.PROTECT,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_CHARACTER,
        )

    def _parse_opponent_return_don(self, match: re.Match, full_text: str) -> Effect:
        """Parse opponent returns DON to deck."""
        count = int(match.group(1))

        return Effect(
            effect_type=EffectType.DON_REST,  # Return DON
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.OPPONENT_DON,
            value=count,
        )

    def _parse_on_ko_effect(self, match: re.Match, full_text: str) -> Optional[Effect]:
        """Parse when this Character is K.O.'d effect.

        Returns None because this is just a trigger condition - the actual
        effect should be parsed by other patterns (power boost, play card, etc.)
        """
        return None

    def _parse_optional_cost(self, match: re.Match, full_text: str) -> Effect:
        """Parse optional cost (❶ pattern with question mark)."""
        return Effect(
            effect_type=EffectType.DON_REST,
            timing=EffectTiming.CONTINUOUS,
            value=0,  # Optional
            target_type=TargetType.YOUR_DON,
        )

    def _parse_leader_power_reduce(self, match: re.Match, full_text: str) -> Effect:
        """Parse Leader power reduction."""
        power = int(match.group(1))
        if power < 100:
            power *= 1000

        target_type = TargetType.OPPONENT_LEADER if "opponent" in full_text.lower() else TargetType.YOUR_LEADER

        return Effect(
            effect_type=EffectType.POWER_REDUCE,
            timing=EffectTiming.CONTINUOUS,
            value=power,
            target_type=target_type,
            duration=Duration.THIS_TURN,
        )

    def _parse_cannot_trash(self, match: re.Match, full_text: str) -> Effect:
        """Parse cannot be trashed effect."""
        return Effect(
            effect_type=EffectType.PROTECT,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
            duration=Duration.PERMANENT,
        )

    def _parse_trash_self_instead(self, match: re.Match, full_text: str) -> Effect:
        """Parse trash this Character instead effect."""
        return Effect(
            effect_type=EffectType.TRASH,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
        )

    def _parse_play_color_character(self, match: re.Match, full_text: str) -> Effect:
        """Parse play colored Character with cost effect."""
        count = int(match.group(1))

        restriction = TargetRestriction()
        if match.lastindex >= 2 and match.group(2):
            restriction.cost_max = int(match.group(2))

        return Effect(
            effect_type=EffectType.PLAY,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_HAND,
            target_count=count,
            target_restriction=restriction,
        )

    def _parse_circled_digit_cost(self, match: re.Match, full_text: str) -> Effect:
        """Parse circled digit cost patterns (❶, ❷, etc.)."""
        return Effect(
            effect_type=EffectType.DON_REST,
            timing=EffectTiming.CONTINUOUS,
            value=1,  # Default to 1
            target_type=TargetType.YOUR_DON,
        )

    def _parse_ko_by_effect(self, match: re.Match, full_text: str) -> Effect:
        """Parse When K.O.'d by effect trigger."""
        return Effect(
            effect_type=EffectType.POWER_BOOST,  # Usually gives power on K.O.
            timing=EffectTiming.ON_KO,
            target_type=TargetType.YOUR_LEADER,
        )

    def _parse_leader_power_during_turn(self, match: re.Match, full_text: str) -> Effect:
        """Parse Leader gains power during this turn."""
        power = int(match.group(2))
        if power < 100:
            power *= 1000

        return Effect(
            effect_type=EffectType.POWER_BOOST,
            timing=EffectTiming.CONTINUOUS,
            value=power,
            target_type=TargetType.YOUR_LEADER,
            duration=Duration.THIS_TURN,
        )

    def _parse_set_named_leader_active(self, match: re.Match, full_text: str) -> Effect:
        """Parse Set named Leader as active (e.g., Set your [Uta] Leader as active)."""
        card_name = match.group(1)
        return Effect(
            effect_type=EffectType.ACTIVATE,
            timing=EffectTiming.MAIN,
            target_type=TargetType.YOUR_LEADER,
            raw_text=f"Set [{card_name}] Leader as active",
        )

    def _parse_attack_on_play_turn(self, match: re.Match, full_text: str) -> Effect:
        """Parse can attack Characters on the turn it is played (Rush-like for characters)."""
        return Effect(
            effect_type=EffectType.GRANT_RUSH,
            timing=EffectTiming.ON_PLAY,
            target_type=TargetType.SELF,
            raw_text="Can attack Characters on play turn",
        )

    def _parse_type_attack_on_play(self, match: re.Match, full_text: str) -> Effect:
        """Parse type Characters can attack on play turn."""
        card_type = match.group(1)
        return Effect(
            effect_type=EffectType.GRANT_RUSH,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.YOUR_CHARACTER,
            target_restriction=TargetRestriction(types=[card_type]),
            raw_text=f"{{{card_type}}} type Characters can attack on play turn",
        )

    def _parse_negate_effect(self, match: re.Match, full_text: str) -> Effect:
        """Parse negate the effect of Character."""
        count = int(match.group(1)) if match.group(1) else 1
        return Effect(
            effect_type=EffectType.NEGATE,
            timing=EffectTiming.MAIN,
            value=count,
            target_type=TargetType.OPPONENT_CHARACTER,
            duration=Duration.THIS_TURN,
        )

    def _parse_cannot_be_removed(self, match: re.Match, full_text: str) -> Effect:
        """Parse cannot be removed from field by opponent's effects."""
        return Effect(
            effect_type=EffectType.PROTECT,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
            raw_text="Cannot be removed from field by opponent",
        )

    def _parse_multi_place_bottom(self, match: re.Match, full_text: str) -> Effect:
        """Parse multi-target placement (Place up to X with cost Y and up to Z with cost W)."""
        count1 = int(match.group(1)) if match.group(1) else 1
        cost1 = int(match.group(2)) if match.group(2) else None
        count2 = int(match.group(3)) if match.group(3) else 1
        return Effect(
            effect_type=EffectType.RETURN_TO_DECK,
            timing=EffectTiming.MAIN,
            value=count1 + count2,
            target_type=TargetType.OPPONENT_CHARACTER,
            target_restriction=TargetRestriction(cost_max=cost1) if cost1 else None,
            raw_text=f"Place up to {count1} (cost {cost1}) and {count2} at bottom",
        )

    def _parse_return_hand_draw_equal(self, match: re.Match, full_text: str) -> Effect:
        """Parse return all hand to deck and draw equal."""
        return Effect(
            effect_type=EffectType.DRAW,
            timing=EffectTiming.MAIN,
            value=0,  # Value determined at resolution
            target_type=TargetType.YOUR_DECK,
            raw_text="Return all hand to deck, draw equal",
        )

    def _parse_trash_from_hand_cost(self, match: re.Match, full_text: str) -> Effect:
        """Parse trash from hand as cost (You may trash X cards:)."""
        count = int(match.group(1))
        return Effect(
            effect_type=EffectType.DISCARD,
            timing=EffectTiming.MAIN,
            value=count,
            target_type=TargetType.YOUR_HAND,
            cost=EffectCost(trash_from_hand=count),
        )

    def _parse_ko_replacement_trash(self, match: re.Match, full_text: str) -> Effect:
        """Parse would be K.O.'d, may trash instead."""
        count = int(match.group(1)) if match.group(1) else 1
        return Effect(
            effect_type=EffectType.PROTECT,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
            cost=EffectCost(trash_from_hand=count),
            raw_text=f"May trash {count} card(s) instead of K.O.",
        )

    def _parse_removal_replacement(self, match: re.Match, full_text: str) -> Effect:
        """Parse would be removed, may do something instead."""
        return Effect(
            effect_type=EffectType.PROTECT,
            timing=EffectTiming.CONTINUOUS,
            target_type=TargetType.SELF,
            raw_text="Replacement effect on removal",
        )

    def _parse_type_cost_reduction(self, match: re.Match, full_text: str) -> Effect:
        """Parse cost reduction for playing type Characters from hand."""
        card_type = match.group(1)
        reduction = int(match.group(2))
        return Effect(
            effect_type=EffectType.COST_REDUCE,
            timing=EffectTiming.CONTINUOUS,
            value=reduction,
            target_type=TargetType.YOUR_CHARACTER,
            target_restriction=TargetRestriction(types=[card_type]),
            raw_text=f"{{{card_type}}} type costs {reduction} less to play",
        )

    def _parse_swap_power(self, match: re.Match, full_text: str) -> Effect:
        """Parse swap base power of Characters."""
        return Effect(
            effect_type=EffectType.POWER_BOOST,
            timing=EffectTiming.MAIN,
            target_type=TargetType.OPPONENT_CHARACTER,
            value=0,
            duration=Duration.THIS_TURN,
            raw_text="Swap base power of selected Characters",
        )

    def _parse_opponent_event_trigger(self, match: re.Match, full_text: str) -> Effect:
        """Parse when opponent activates an Event trigger."""
        return Effect(
            effect_type=EffectType.NEGATE,
            timing=EffectTiming.ON_OPPONENT_ATTACK,  # Using as trigger
            target_type=TargetType.OPPONENT_CHARACTER,
            raw_text="Trigger when opponent activates Event",
        )

    def _parse_self_cost_reduction(self, match: re.Match, full_text: str) -> Effect:
        """Parse give this card in hand -X cost."""
        reduction = int(match.group(1))
        return Effect(
            effect_type=EffectType.COST_REDUCE,
            timing=EffectTiming.CONTINUOUS,
            value=reduction,
            target_type=TargetType.SELF,
        )

    def _parse_place_all_characters_bottom(self, match: re.Match, full_text: str) -> Effect:
        """Parse place all Characters with cost at bottom of deck."""
        max_cost = int(match.group(1)) if match.group(1) else None
        return Effect(
            effect_type=EffectType.RETURN_TO_DECK,
            timing=EffectTiming.MAIN,
            value=99,  # All
            target_type=TargetType.OPPONENT_CHARACTER,
            target_restriction=TargetRestriction(cost_max=max_cost) if max_cost else None,
            raw_text="Place all Characters at bottom",
        )

    def _parse_end_battle_place_bottom(self, match: re.Match, full_text: str) -> Effect:
        """Parse at end of battle, place Character at bottom."""
        return Effect(
            effect_type=EffectType.RETURN_TO_DECK,
            timing=EffectTiming.END_OF_TURN,  # End of battle
            value=1,
            target_type=TargetType.OPPONENT_CHARACTER,
            raw_text="At end of battle, place at bottom",
        )

    def _parse_trash_trigger_draw(self, match: re.Match, full_text: str) -> Effect:
        """Parse when card is trashed from hand, draw equal."""
        return Effect(
            effect_type=EffectType.DRAW,
            timing=EffectTiming.CONTINUOUS,
            value=0,  # Equal to cards trashed
            target_type=TargetType.YOUR_DECK,
            raw_text="When trashed from hand, draw equal",
        )

    def parse_card(self, card_id: str, name: str, effect_text: str) -> ParsedCard:
        """
        Parse all effects for a card.

        Args:
            card_id: Card ID
            name: Card name
            effect_text: Full effect text

        Returns:
            ParsedCard with all effects parsed
        """
        effects = self.parse(effect_text)
        keywords = extract_keywords(effect_text)

        return ParsedCard(
            card_id=card_id,
            name=name,
            effects=effects,
            keywords=keywords,
        )


# Singleton parser instance
_parser: Optional[EffectParser] = None


def get_parser() -> EffectParser:
    """Get the singleton parser instance."""
    global _parser
    if _parser is None:
        _parser = EffectParser()
    return _parser


def parse_effect(effect_text: str) -> List[Effect]:
    """
    Convenience function to parse effect text.

    Args:
        effect_text: Raw effect text from card

    Returns:
        List of parsed Effect objects
    """
    return get_parser().parse(effect_text)
