from dataclasses import dataclass, field
from typing import List

from models.project import Project

@dataclass
class Result:
    score: int = 0
    assignments: List[Project] = field(default_factory=list)
