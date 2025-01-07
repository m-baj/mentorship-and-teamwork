from dataclasses import dataclass


@dataclass
class Skill:
    name: str
    level: int

    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other: "Skill") -> bool:
        return self.name == other.name
    
    def __ge__(self, other: "Skill") -> bool:
        return self.level >= other.level