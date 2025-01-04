from dataclasses import dataclass
from typing import List

from models.assignment import Assignment
from solvers.solver import Solver

@dataclass
class GreedySolver(Solver):
    
    def solve(self) -> List[Assignment]:
        assignments = []
        

