from dataclasses import dataclass, field
from typing import List
from abc import ABC, abstractmethod

from models.contributor import Contributor
from models.project import Project
from models.assignment import Assignment


@dataclass
class Solver(ABC):
    contributors: List[Contributor]
    projects: List[Project]
    assignments: List[Assignment] = field(init=False)

    def __post_init__(self):
        self.assignments = [Assignment(project) for project in self.projects]

    @abstractmethod
    def solve(self) -> List[Assignment]:
        pass
