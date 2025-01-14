from dataclasses import dataclass, field
from typing import List, Optional, Tuple

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
    required_skills: List[Tuple[str, int]] = field(default_factory=dict)
    assignments: List[Tuple[Tuple[str, int], Optional[Contributor]]] = field(default_factory=dict)
    unassigned_skills: List[Tuple[str, int]] = field(default_factory=list)
    evaluation_data: Evaluation = field(default_factory=Evaluation)

    def is_valid(self) -> bool:
        return len(self.required_skills) == len(self.assignments) 
        
    def __post_init__(self):
        self.assignments = []
    
    def __hash__(self):
        return hash(self.name)
