from dataclasses import dataclass, field
from typing import List, Dict

from models.skill import Skill

@dataclass
class Contributor:
    id: int
    name: str
    skills: Dict[str, int]
    skill_upgrades: Dict[str, int] = field(default_factory=dict)
    busy_until: int = 0

    def has_required_skill(self, required_skill: str, level: int) -> bool:
        return self.skills.get(required_skill, 0) >= level