from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Contributor:
    id: int
    name: str
    skills: Dict[str, int]
    busy_until: int = 0

    def has_required_skill(self, required_skill: str, level: int) -> bool:
        return self.skills.get(required_skill, 0) >= level

    def has_required_skill_one_level_lower(self, required_skill: str, level: int) -> bool:
        return self.skills.get(required_skill, 0) == level - 1

    def can_mentor(self, skill_name: str, level: int) -> bool:
        return self.skills.get(skill_name, 0) >= level
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name
    