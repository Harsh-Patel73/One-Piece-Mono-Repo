from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import html


@dataclass
class Card:
    id: str
    id_normal: str
    name: str
    card_type: str
    cost: Optional[int]
    power: Optional[int]
    counter: Optional[int]
    colors: List[str]
    life: Optional[int]
    effect: Optional[str]
    image_link: Optional[str]
    attribute: Optional[str]
    card_origin: Optional[str]
    trigger: Optional[str]

    is_resting: bool = False
    has_attacked: bool = False
    has_rush: bool = False
    has_banish: bool = False
    has_doubleattack: bool = False
    has_blocker: bool = False
    don_condition_met: bool = False
    attached_don: int = 0
    played_turn: Optional[int] = None
    main_activated_this_turn: bool = False

    def __post_init__(self):
        self.is_resting = False
        self.has_attacked = False

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.id == other.id
        return False

    def has_keyword(self, keyword: str) -> bool:
        """Check if card has a specific keyword."""
        if not self.effect:
            return False
        keyword_map = {
            'rush': '[Rush]',
            'blocker': '[Blocker]',
            'banish': '[Banish]',
            'double_attack': '[Double Attack]',
        }
        search = keyword_map.get(keyword.lower(), f'[{keyword}]')
        return search in self.effect

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "Card":
        id_ = d["id"]
        id_norm = d.get("id_normal", id_)
        name = d["name"]
        ctype = d.get("cardType", d.get("card_type", "CHARACTER"))

        def to_int(field: str) -> Optional[int]:
            val = d.get(field)
            if val is None:
                return None
            try:
                return int(val)
            except:
                return None

        cost = to_int("Cost") or to_int("cost")
        power = to_int("Power") or to_int("power")
        counter = to_int("Counter") or to_int("counter")
        life = to_int("Life") or to_int("life")

        attribute = d.get("Attribute") or d.get("attribute") or ""
        card_origin = d.get("Type") or d.get("type") or ""
        trigger = d.get("Trigger") or d.get("trigger") or ""

        color_str = d.get("Color") or d.get("color") or ""
        colors = [c.strip() for c in color_str.split("/") if c.strip()]

        effect = html.unescape(d.get("Effect") or d.get("effect") or "")
        img = d.get("image_link") or d.get("imageUrl")

        return cls(
            id=id_,
            id_normal=id_norm,
            name=name,
            card_type=ctype,
            cost=cost,
            attribute=attribute,
            power=power,
            counter=counter,
            colors=colors,
            card_origin=card_origin,
            trigger=trigger,
            life=life,
            effect=effect,
            image_link=img
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert card to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "id_normal": self.id_normal,
            "name": self.name,
            "card_type": self.card_type,
            "cost": self.cost,
            "power": self.power,
            "counter": self.counter,
            "colors": self.colors,
            "life": self.life,
            "effect": self.effect,
            "image_link": self.image_link,
            "attribute": self.attribute,
            "card_origin": self.card_origin,
            "trigger": self.trigger,
            "is_resting": self.is_resting,
            "has_attacked": self.has_attacked,
            "attached_don": self.attached_don,
        }
