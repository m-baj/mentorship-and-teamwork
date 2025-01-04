from dataclasses import dataclass
from typing import List

from models.skill import Skill

@dataclass
class Contributor:
    id: int
    name: str
    skills: List[Skill]
    busy_until: int = 0