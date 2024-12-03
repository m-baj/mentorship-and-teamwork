from dataclasses import dataclass
from skill import Skill

@dataclass
class Project:
    name: str
    duration: int
    score: int
    best_before: int
    required_skills: list[Skill]


