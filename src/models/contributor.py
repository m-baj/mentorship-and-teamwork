from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Contributor:
    id: int
    name: str
    skills: Dict[str, int]
    skill_upgrades: Dict[str, int] = field(default_factory=dict)
    busy_until: int = 0

    def has_required_skill(self, required_skill: str, level: int) -> bool:
        return self.skills.get(required_skill, 0) >= level
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name
    