from dataclasses import dataclass, field
from typing import List

from models.skill import Skill

@dataclass
class Evaluation:
    begins: int = 0
    ends: int = 0
    score: int = 0

@dataclass
class Project:
    id: int
    name: str
    duration: int
    score: int
    best_before: int
    required_skills: List[Skill]
    evaluation_data: Evaluation = field(default_factory=Evaluation)
