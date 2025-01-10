from dataclasses import dataclass, field
from typing import List, Dict, Optional

from models.skill import Skill
from models.contributor import Contributor

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
    required_skills: Dict[str, int] = field(default_factory=dict)
    assignments: Dict[Skill, Optional[Contributor]] = field(default_factory=dict)
    evaluation_data: Evaluation = field(default_factory=Evaluation)

    def __post_init__(self):
        self.assignments = {skill: None for skill in self.required_skills.keys()}
    
    def __hash__(self):
        return hash(self.name)


# @dataclass
# class AssignedProject(Project):
#     evaluation_data: Evaluation = field(default_factory=Evaluation)
