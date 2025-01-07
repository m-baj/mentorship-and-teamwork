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
    # assigned_projects: List[AssignedProject] = field(default_factory=list)

    @abstractmethod
    def solve(self) -> None:
        pass
