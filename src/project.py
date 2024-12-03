from dataclasses import dataclass
from skill import Skill
from typing import List

@dataclass
class Project:
    name: str
    duration: int
    score: int
    best_before: int
    required_skills: List[Skill]


