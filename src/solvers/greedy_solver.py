from dataclasses import dataclass, field
from typing import List, Tuple
from copy import deepcopy
import random

from models.assignment import Assignment
from models.result import Result
from solvers.solver import Solver
from models.contributor import Contributor
from models.project import Project

@dataclass
class GreedySolver(Solver):
    best_result: Result = field(default_factory=Result)
    
    def solve(self, max_iter: int) -> None:
        for _ in range(max_iter):
            assigned_projects = []
            remaining_projects = deepcopy(self.projects)
            contributors = set(deepcopy(self.contributors))
            for project in remaining_projects:
                busy_untils = []
                is_valid = True
                team = set()
                for skill, level in project.required_skills.items():
                    contributor = self._choose_contributor(skill, level, contributors, team)
                    if contributor is not None:
                        project.assignments[skill] = contributor 
                        busy_untils.append(contributor.busy_until)
                        contributor.busy_until += project.duration
                        team.add(contributor)
                    else:
                        is_valid = False
                        break
                
                if is_valid:
                    project.evaluation_data.begins = max(busy_untils)
                    project.evaluation_data.ends = project.evaluation_data.begins + project.duration
                    project.evaluation_data.score = self._eval_project(project)
                    assigned_projects.append(project)
            
            score = self._calc_score(assigned_projects)
            if score > self.best_result.score:
                self.best_result = Result(score, assigned_projects)
            
            self._swap_two_random_projects()
                   
    def _choose_contributor(self, skill: str, level: int, contributors, team) -> Tuple[Contributor, bool]:
        possible_contributors = [
            contributor for contributor in contributors - team
                if contributor.has_required_skill(skill, level)
        ]
        if not possible_contributors:
            return None
        best = min(possible_contributors, key=lambda c: c.busy_until)
        if best.skills[skill] <= level:
            best.skills[skill] += 1
        return best
    
    def _eval_project(self, project: Project) -> int:
        return max(0, project.score - max(0, project.evaluation_data.ends - project.best_before))

    def _swap_two_random_projects(self):
        first = random.randint(0, len(self.projects) - 1)
        second = random.randint(0, len(self.projects) - 1)
        self.projects[first], self.projects[second] = self.projects[second], self.projects[first]

    def _calc_score(self, assigned_projects: List[Project]) -> int:
        return sum(project.evaluation_data.score for project in assigned_projects)
    

