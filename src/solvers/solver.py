from dataclasses import dataclass
from typing import List
from abc import ABC, abstractmethod

from models.contributor import Contributor
from models.project import Project


@dataclass
class Solver(ABC):
    contributors: List[Contributor]
    projects: List[Project]

    @abstractmethod
    def solve(self) -> None:
        pass
