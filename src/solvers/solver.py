from dataclasses import dataclass, field
from typing import List, Dict
from abc import ABC, abstractmethod

from models.contributor import Contributor
from models.project import Project
from models.assignment import Assignment
from models.result import Result


@dataclass
class Solver(ABC):
    contributors: List[Contributor]
    projects: List[Project]

    @abstractmethod
    def solve(self) -> None:
        pass
