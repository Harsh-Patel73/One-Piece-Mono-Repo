"""
Tokenizer for One Piece TCG effect text.

Preprocesses and tokenizes effect text for parsing.
Handles HTML entities, brackets, and common patterns.
"""

import re
import html
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """Types of tokens in effect text."""
    # Timing keywords (in brackets)
    TIMING = auto()         # [On Play], [Counter], etc.
    KEYWORD = auto()        # [Rush], [Blocker], etc.
    DON_CONDITION = auto()  # [DON!! x1], [DON!! x2]
    ONCE_PER_TURN = auto()  # [Once Per Turn]

    # Actions
    DRAW = auto()
    KO = auto()
    REST = auto()
    PLAY = auto()
    TRASH = auto()
    RETURN = auto()
    SEARCH = auto()
    LOOK = auto()
    REVEAL = auto()
    ADD = auto()
    SET = auto()
    GIVE = auto()
    GAIN = auto()
    ACTIVATE = auto()

    # Targets
    CHARACTER = auto()
    LEADER = auto()
    DON = auto()
    CARD = auto()
    LIFE = auto()
    DECK = auto()
    HAND = auto()

    # Ownership
    YOUR = auto()
    OPPONENT = auto()

    # Numbers
    NUMBER = auto()

    # Modifiers
    UP_TO = auto()
    OR_LESS = auto()
    OR_MORE = auto()
    EXACTLY = auto()

    # Connectors
    AND = auto()
    OR = auto()
    THEN = auto()
    COLON = auto()      # ":" separates cost from effect
    COMMA = auto()

    # Duration
    DURING_THIS_TURN = auto()
    DURING_THIS_BATTLE = auto()

    # Power
    POWER = auto()
    COST = auto()

    # Conditions
    IF = auto()
    MAY = auto()
    CANNOT = auto()

    # Misc
    TYPE = auto()       # {Straw Hat Crew}
    TEXT = auto()       # Unrecognized text
    END = auto()


@dataclass
class Token:
    """A single token from effect text."""
    type: TokenType
    value: str
    position: int

    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}')"


class Tokenizer:
    """Tokenizes One Piece TCG effect text."""

    # Timing keywords - order matters, check combined timings FIRST
    TIMING_PATTERNS = {
        # Combined timing patterns (check these first)
        r'\[When Attacking\]/\[On Block\]': 'WHEN_ATTACKING',  # Use first timing
        r'\[On Play\]/\[When Attacking\]': 'ON_PLAY',
        r'\[On Play\]/\[On K\.?O\.?\]': 'ON_PLAY',
        r'\[On Play\]/\[On Block\]': 'ON_PLAY',
        r'\[Your Turn\]\s*\[On Play\]': 'ON_PLAY',
        r'\[Your Turn\]\s*\[When Attacking\]': 'WHEN_ATTACKING',
        r"\[Opponent'?s?\s*Turn\]\s*\[On K\.?O\.?\]": 'ON_KO',  # Opponent's Turn + On K.O.
        r"\[Opponent'?s?\s*Turn\]\s*\[When Attacking\]": 'WHEN_ATTACKING',
        # Single timings
        r'\[On Play\]': 'ON_PLAY',
        r'\[When Attacking\]': 'WHEN_ATTACKING',
        r'\[On Block\]': 'ON_BLOCK',
        r'\[Counter\]': 'COUNTER',
        r'\[Trigger\]': 'TRIGGER',
        r'\[Activate:\s*Main\]': 'MAIN',
        r'\[End of Your Turn\]': 'END_OF_TURN',
        r'\[Start of Your Turn\]': 'START_OF_TURN',
        r'\[On K\.?O\.?\]': 'ON_KO',
        r"\[On Your Opponent's Attack\]": 'ON_OPPONENT_ATTACK',
        r"\[Your Turn\]": 'YOUR_TURN',
        r"\[Opponent'?s?\s*Turn\]": 'OPPONENT_TURN',
    }

    # Keyword patterns
    KEYWORD_PATTERNS = {
        r'\[Rush\]': 'RUSH',
        r'\[Blocker\]': 'BLOCKER',
        r'\[Banish\]': 'BANISH',
        r'\[Double Attack\]': 'DOUBLE_ATTACK',
    }

    # DON condition pattern
    DON_CONDITION_PATTERN = r'\[DON!!\s*x(\d+)\]'

    # Once per turn
    ONCE_PER_TURN_PATTERN = r'\[Once Per Turn\]'

    # Type pattern (in curly braces)
    TYPE_PATTERN = r'\{([^}]+)\}'

    def __init__(self):
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for performance."""
        self.timing_regex = {
            re.compile(pattern, re.IGNORECASE): name
            for pattern, name in self.TIMING_PATTERNS.items()
        }
        self.keyword_regex = {
            re.compile(pattern, re.IGNORECASE): name
            for pattern, name in self.KEYWORD_PATTERNS.items()
        }
        self.don_regex = re.compile(self.DON_CONDITION_PATTERN, re.IGNORECASE)
        self.once_regex = re.compile(self.ONCE_PER_TURN_PATTERN, re.IGNORECASE)
        self.type_regex = re.compile(self.TYPE_PATTERN)

    def preprocess(self, text: str) -> str:
        """Clean up effect text before tokenizing."""
        if not text:
            return ""

        # Decode HTML entities
        text = html.unescape(text)

        # Replace <br> with newlines
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)

        # Remove other HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Normalize whitespace within lines (preserve newlines for splitting)
        lines = text.split('\n')
        lines = [' '.join(line.split()) for line in lines]
        text = '\n'.join(lines)

        return text.strip()

    def tokenize(self, text: str) -> List[Token]:
        """
        Tokenize effect text into a list of tokens.

        Args:
            text: Raw effect text from card

        Returns:
            List of Token objects
        """
        text = self.preprocess(text)
        if not text:
            return []

        tokens = []
        position = 0

        while position < len(text):
            # Skip whitespace
            while position < len(text) and text[position].isspace():
                position += 1
            if position >= len(text):
                break

            token, length = self._match_token(text, position)
            if token:
                tokens.append(token)
                position += length
            else:
                # Unrecognized character, skip it
                position += 1

        return tokens

    def _match_token(self, text: str, position: int) -> Tuple[Optional[Token], int]:
        """Match a token at the current position."""
        remaining = text[position:]

        # Check timing keywords
        for regex, name in self.timing_regex.items():
            match = regex.match(remaining)
            if match:
                return Token(TokenType.TIMING, name, position), len(match.group())

        # Check keywords (Rush, Blocker, etc.)
        for regex, name in self.keyword_regex.items():
            match = regex.match(remaining)
            if match:
                return Token(TokenType.KEYWORD, name, position), len(match.group())

        # Check DON condition
        match = self.don_regex.match(remaining)
        if match:
            return Token(TokenType.DON_CONDITION, match.group(1), position), len(match.group())

        # Check Once Per Turn
        match = self.once_regex.match(remaining)
        if match:
            return Token(TokenType.ONCE_PER_TURN, 'ONCE_PER_TURN', position), len(match.group())

        # Check type in curly braces
        match = self.type_regex.match(remaining)
        if match:
            return Token(TokenType.TYPE, match.group(1), position), len(match.group())

        # Check for numbers with optional +/- and power notation
        match = re.match(r'([+-]?\d+)(?:000)?', remaining)
        if match:
            return Token(TokenType.NUMBER, match.group(1), position), len(match.group())

        # Check action words
        action_patterns = [
            (r'draw(?:s)?', TokenType.DRAW),
            (r'K\.?O\.?(?:\'d)?', TokenType.KO),
            (r'rest(?:s)?', TokenType.REST),
            (r'play(?:s)?(?:ed)?', TokenType.PLAY),
            (r'trash(?:es)?(?:ed)?', TokenType.TRASH),
            (r'return(?:s)?(?:ed)?', TokenType.RETURN),
            (r'search(?:es)?', TokenType.SEARCH),
            (r'look(?:s)?', TokenType.LOOK),
            (r'reveal(?:s)?', TokenType.REVEAL),
            (r'add(?:s)?', TokenType.ADD),
            (r'set(?:s)?', TokenType.SET),
            (r'give(?:s)?', TokenType.GIVE),
            (r'gain(?:s)?', TokenType.GAIN),
            (r'activate(?:s)?', TokenType.ACTIVATE),
        ]

        for pattern, token_type in action_patterns:
            match = re.match(pattern, remaining, re.IGNORECASE)
            if match:
                return Token(token_type, match.group(), position), len(match.group())

        # Check target words
        target_patterns = [
            (r'Character(?:s)?', TokenType.CHARACTER),
            (r'Leader', TokenType.LEADER),
            (r'DON!!?', TokenType.DON),
            (r'card(?:s)?', TokenType.CARD),
            (r'Life', TokenType.LIFE),
            (r'deck', TokenType.DECK),
            (r'hand', TokenType.HAND),
        ]

        for pattern, token_type in target_patterns:
            match = re.match(pattern, remaining, re.IGNORECASE)
            if match:
                return Token(token_type, match.group(), position), len(match.group())

        # Check ownership
        if re.match(r'your\b', remaining, re.IGNORECASE):
            return Token(TokenType.YOUR, 'your', position), 4
        if re.match(r"opponent'?s?\b", remaining, re.IGNORECASE):
            match = re.match(r"opponent'?s?\b", remaining, re.IGNORECASE)
            return Token(TokenType.OPPONENT, match.group(), position), len(match.group())

        # Check modifiers
        if re.match(r'up to\b', remaining, re.IGNORECASE):
            return Token(TokenType.UP_TO, 'up to', position), 5
        if re.match(r'or less\b', remaining, re.IGNORECASE):
            return Token(TokenType.OR_LESS, 'or less', position), 7
        if re.match(r'or more\b', remaining, re.IGNORECASE):
            return Token(TokenType.OR_MORE, 'or more', position), 7
        if re.match(r'exactly\b', remaining, re.IGNORECASE):
            return Token(TokenType.EXACTLY, 'exactly', position), 7

        # Check connectors
        if remaining[0] == ':':
            return Token(TokenType.COLON, ':', position), 1
        if remaining[0] == ',':
            return Token(TokenType.COMMA, ',', position), 1
        if re.match(r'\band\b', remaining, re.IGNORECASE):
            return Token(TokenType.AND, 'and', position), 3
        if re.match(r'\bor\b', remaining, re.IGNORECASE):
            return Token(TokenType.OR, 'or', position), 2
        if re.match(r'\bthen\b', remaining, re.IGNORECASE):
            return Token(TokenType.THEN, 'then', position), 4

        # Check duration
        if re.match(r'during this turn\b', remaining, re.IGNORECASE):
            return Token(TokenType.DURING_THIS_TURN, 'during this turn', position), 16
        if re.match(r'this turn\b', remaining, re.IGNORECASE):
            return Token(TokenType.DURING_THIS_TURN, 'this turn', position), 9
        if re.match(r'during this battle\b', remaining, re.IGNORECASE):
            return Token(TokenType.DURING_THIS_BATTLE, 'during this battle', position), 18
        if re.match(r'this battle\b', remaining, re.IGNORECASE):
            return Token(TokenType.DURING_THIS_BATTLE, 'this battle', position), 11

        # Check power/cost
        if re.match(r'power\b', remaining, re.IGNORECASE):
            return Token(TokenType.POWER, 'power', position), 5
        if re.match(r'cost\b', remaining, re.IGNORECASE):
            return Token(TokenType.COST, 'cost', position), 4

        # Check conditions
        if re.match(r'\bif\b', remaining, re.IGNORECASE):
            return Token(TokenType.IF, 'if', position), 2
        if re.match(r'\bmay\b', remaining, re.IGNORECASE):
            return Token(TokenType.MAY, 'may', position), 3
        if re.match(r'\bcannot\b', remaining, re.IGNORECASE):
            return Token(TokenType.CANNOT, 'cannot', position), 6

        # Match any word as TEXT
        match = re.match(r'\w+', remaining)
        if match:
            return Token(TokenType.TEXT, match.group(), position), len(match.group())

        # Skip punctuation we don't care about
        if remaining[0] in '.;()[]':
            return None, 1

        return None, 1

    def split_effects(self, text: str) -> List[str]:
        """
        Split text with multiple effects into separate effect strings.

        Effects are typically separated by <br> or newlines, or by
        multiple timing keywords.

        Note: DON conditions like [DON!! x2] are NOT split points - they
        modify the following effect and should stay attached to it.
        """
        text = self.preprocess(text)
        if not text:
            return []

        # Split on newlines first
        parts = text.split('\n')

        # Further split if a part contains multiple timing keywords
        effects = []
        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Find all timing keywords (NOT DON conditions - those modify effects, not separate them)
            # Also don't split combined timings like [When Attacking]/[On Block]
            timing_positions = []
            for regex in self.timing_regex:
                for match in regex.finditer(part):
                    pos = match.start()
                    prefix = part[:pos].strip()

                    # Skip if preceded by / (combined timing like [When Attacking]/[On Block])
                    if pos > 0 and part[pos-1] == '/':
                        continue

                    # Skip if preceded by DON condition (DON modifies the effect, doesn't separate)
                    if prefix.endswith(']') and self.don_regex.search(prefix[-20:] if len(prefix) >= 20 else prefix):
                        if not timing_positions:
                            # If this is the first timing and it's preceded by DON, include from start
                            timing_positions.append(0)
                        continue

                    # Skip [Trigger] when it's part of a card description (e.g., "with a [Trigger]")
                    # This is not a timing keyword in this context
                    if match.group() == '[Trigger]' and re.search(r'\b(?:a|an)\s*$', prefix):
                        continue

                    timing_positions.append(pos)

            # Remove overlapping positions (keep only the first of nearby matches)
            # This handles combined timings like [Opponent's Turn] [On K.O.] where
            # both the combined pattern and individual patterns match
            timing_positions.sort()
            deduped_positions = []
            for pos in timing_positions:
                if not deduped_positions or pos - deduped_positions[-1] > 30:
                    deduped_positions.append(pos)
            timing_positions = deduped_positions

            if len(timing_positions) <= 1:
                effects.append(part)
            else:
                # Split at timing keywords (except first)
                timing_positions.sort()
                for i, pos in enumerate(timing_positions):
                    if i == len(timing_positions) - 1:
                        effects.append(part[pos:].strip())
                    else:
                        effects.append(part[pos:timing_positions[i+1]].strip())

        return [e for e in effects if e]


def extract_keywords(text: str) -> List[str]:
    """
    Extract standalone keywords from effect text.

    Returns list of keyword names like 'RUSH', 'BLOCKER', etc.
    """
    if not text:
        return []

    text = html.unescape(text)
    keywords = []

    patterns = [
        (r'\[Rush\]', 'RUSH'),
        (r'(?<!activate )\[Blocker\]', 'BLOCKER'),
        (r'\[Banish\]', 'BANISH'),
        (r'\[Double Attack\]', 'DOUBLE_ATTACK'),
    ]

    for pattern, keyword in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            keywords.append(keyword)

    return keywords
