from dataclasses import dataclass, field
from typing import List, Tuple, Dict

from solvers.evo_solver import EvoSolver
from utils.parse_input_file import parse_input_file
from utils.parse_output_file import parse_output_file
from models.contributor import Contributor
from models.project import Project
from models.result import Result

@dataclass
class Params:
    ngen: int
    population_size: int
    selection_type: str

@dataclass
class ExperimentResult:
    params: Params
    score: int
    best_individuals: List[int] = field(default_factory=list)
    population_avgs: List[int] = field(default_factory=list)
    best_result: Result = field(default_factory=Result)

@dataclass
class Experiment:
    contributors: List[Contributor]
    projects: List[Project]
    params: Params

    def run(self) -> ExperimentResult:
        print(f"Running experiment with parameters: {self.params}")
        solver = EvoSolver(
            contributors=self.contributors, 
            projects=self.projects, 
            population_size=self.params.population_size, 
            selection_type=self.params.selection_type
        )
        best, avgs = solver.solve(self.params.ngen)
        return ExperimentResult(self.params, solver.best_result.score, best, avgs, solver.best_result)
    

@dataclass
class ExperimentRunner:
    params: List[Params]
    files: List[str]

    def run(self) -> Dict[str, List[ExperimentResult]]:
        results = {}
        for file_name in self.files:
            print(f"Running experiment for file: {file_name}")
            contributors, projects = self._parse_input_file(file_name)
            results[file_name] = []
            for idx, params in enumerate(self.params):
                experiment = Experiment(contributors, projects, params)
                result = experiment.run()
                results[file_name].append(result)
                self._parse_output_file(result.best_result, f"{file_name}_{idx}", contributors)
        return results
    
    def _parse_input_file(self, file_name: str) -> Tuple[List[Contributor], List[Project]]:
        return parse_input_file(f"data/{file_name}.in")

    def _parse_output_file(self, result: Result, file_name: str, contributors: List[Contributor]) -> None:
        return parse_output_file(result, f"out/{file_name}.out", contributors)
    
    
