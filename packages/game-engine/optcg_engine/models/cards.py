from dataclasses import dataclass  # Import the dataclass decorator
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
    
    is_resting: bool = False  # To track if the card is resting
    has_attacked: bool = False  # To track if the card has already attacked
    has_rush: bool = False
    has_banish: bool = False
    has_doubleattack: bool = False
    don_condition_met: bool = False
    attached_don = 0

    def __post_init__(self):
        self.is_resting = False  # Initially not resting
        self.has_attacked = False  # Ensure has_attacked is initialized to False

    def __hash__(self):
        """Generate a hash value for the card, typically based on unique attributes like id."""
        return hash(self.id)  # Assuming the card id is unique

    def __eq__(self, other):
        """Check if two cards are equal based on their id."""
        if isinstance(other, Card):
            return self.id == other.id  # Comparing based on unique id
        return False

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "Card":  # Use a string literal for the class name
        id_ = d["id"]
        id_norm = d["id_normal"]
        name = d["name"]
        ctype = d["cardType"]
        
        def to_int(field: str) -> Optional[int]:
            val = d.get(field)
            if val is None: return None
            try:
                return int(val)
            except:
                return None

        cost = to_int("Cost")
        power = to_int("Power")
        counter = to_int("Counter")
        life = to_int("Life")

        if ("Attribute") != 'null': attribute = ("Attribute")
        else: attribute = ""

        if ("Type") != 'null': card_origin = ("Type")
        else: card_origin = ""

        if ("Trigger") != 'null': trigger = ("Trigger")
        else: trigger = ""

        color_str = d.get("Color") or ""
        colors = [c.strip() for c in color_str.split("/") if c.strip()]

        effect = html.unescape(d.get("Effect") or "")

        img = d.get("image_link")

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
    
    def attack(self, target: "Card") -> bool:  # Use a string literal for the class name
        """Allows the card to attack another card or player."""
        if self.is_resting:
            print(f"{self.name} is resting and cannot attack.")
            return False
        
        if self.has_attacked:
            print(f"{self.name} has already attacked this turn.")
            return False
        
        if self.card_type == "Character" and target.card_type == "Character":
            if self.power and target.power:
                print(f"{self.name} attacks {target.name}.")
                target.is_resting = True  # Mark target as resting after being attacked
                self.has_attacked = True  # Mark the card as having attacked
                # Here, you could implement KO mechanics based on power
                return True
            else:
                print(f"{self.name} cannot attack {target.name}. Invalid power values.")
                return False

        print(f"{self.name} cannot attack {target.name}. Invalid target.")
        return False
    
    def block(self, attacker: "Card") -> bool:  # Use a string literal for the class name
        """Allows the card to block an attack."""
        if self.is_resting:
            print(f"{self.name} is resting and cannot block.")
            return False
        
        if self.card_type == "Character" and attacker.card_type == "Character":
            print(f"{self.name} blocks {attacker.name}'s attack.")
            return True
        return False

    def rest(self) -> None:
        """Rest the card (it can't attack again this turn)."""
        self.is_resting = True
        print(f"{self.name} is now resting and cannot perform actions this turn.")