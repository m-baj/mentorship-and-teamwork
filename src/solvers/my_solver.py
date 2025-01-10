import math
from copy import deepcopy
from dataclasses import dataclass, field
from typing import List, Dict
import random

from models.contributor import Contributor
from models.project import Project
from models.assignment import Assignment
from models.skill import Skill
from models.result import Result

from solvers.solver import Solver
from twisted.persisted.styles import upgraded


@dataclass
class NeighborSolver(Solver):
    contributors: List[Contributor]
    projects: List[Project]

    best_result: Result = field(default_factory=Result)
    skill_to_contributors: Dict[str, List[Contributor]] = field(default_factory=dict)

    def solve(self, temperature: int, cooling_rate: float) -> Result:
        # sprawdzic z sortowaniem i z losowym
        self.projects.sort(key=lambda p: p.best_before)

        self.skill_to_contributors = self._map_skills_to_contributors()

        current_assignments = []
        for project in self.projects:
            assignment = self._assign_project(project)
            if assignment:
                current_assignments.append(assignment)

        self.best_result = Result(score = self._evaluate_solution(current_assignments),
                             assignments = current_assignments)

        # mozna dopisac sprawdzanie czy mozna znalezc poprawne rozwiazanie po n iteracjach
        # mozna dodać tabu
        while temperature > 1:

            for contributor in self.contributors:
                if contributor.skill_upgrades:
                    for skill, level in contributor.skill_upgrades.items():
                        contributor.skills[skill] = contributor.skill_upgrades[skill]
                    contributor.skill_upgrades = {}

            neighbor_assignments = self._generate_neighbor(current_assignments)
            neighbor_score = self._evaluate_solution(neighbor_assignments)

            if self._acceptance_probability(self.best_result.score, neighbor_score, temperature) > random.random():
                current_assignments = neighbor_assignments
                self.best_result = Result(score=neighbor_score, assignments=neighbor_assignments)

            temperature *= cooling_rate


    def _map_skills_to_contributors(self) -> Dict[str, List[Contributor]]:
        skill_map = {}
        for contributor in self.contributors:
            for skill, level in contributor.skills.items():
                if skill not in skill_map:
                    skill_map[skill] = []
                skill_map[skill].append(contributor)
        return skill_map

    # wystartowac ze stanu ktory bedzie poprawny
    def _assign_project(self, project: Project) -> Assignment:
        assigned_contributors = []
        for skill, level in project.required_skills.items():
            suitable_contributors = [c for c in self.skill_to_contributors.get(skill, [])]
            if not suitable_contributors:
                return None
            chosen_contributor = random.choice(suitable_contributors)
            assigned_contributors.append(chosen_contributor)
            chosen_contributor.busy_until = project.evaluation_data.begins + project.duration

        return Assignment(project=project, contributors=assigned_contributors)

    def _evaluate_solution(self, assignments: List[Assignment]) -> int:
        total_score = 0
        for assignment in assignments:
            project = assignment.project
            begin_data = max(c.busy_until for c in assignment.contributors)
            end_data = begin_data + project.duration
            for contributor in assignment.contributors:
                contributor.busy_until = end_data
            penalty = 0
            for index, (skill, level) in enumerate(project.required_skills.items()):
                if assignment.contributors[index].skills[skill] < level:
                    penalty += 1000000 + max(0, (project.score -
                            max(0, end_data - project.best_before)))
            score = max(0, (project.score -
                            max(0, end_data - project.best_before))) - penalty
            total_score += score
            self.upgrade_skills(assignment)
        for contributor in self.contributors:
            contributor.busy_until = 0
        return total_score

    # sprobowac dorzucic pracownika z nizszym poziomem do tego z wyzszym
    # randomowy z wiekszym prawdopodobienstwem
    # prawdopodobienstwo zalezne od levelu
    def _generate_neighbor(self, assignments: List[Assignment]) -> List[Assignment]:
        neighbor = assignments[:]

        if random.random() < 0.5:
            random_assignment = random.choice(neighbor)
            if random_assignment.contributors:
                random_idx = random.randint(0, len(random_assignment.contributors) - 1)
                skills = list(random_assignment.project.required_skills.keys())
                skill = skills[random_idx]
                contributors_with_skill = self.skill_to_contributors[skill]
                if contributors_with_skill:
                    new_contributor = random.choice(contributors_with_skill)
                    random_assignment.contributors[random_idx] = new_contributor
        else:
            if len(neighbor) > 1:
                idx1, idx2 = random.sample(range(len(neighbor)), 2)
                neighbor[idx1], neighbor[idx2] = neighbor[idx2], neighbor[idx1]

        return neighbor

    def upgrade_skills(self, assignment: Assignment):
        for index, (skill, level) in enumerate(assignment.project.required_skills.items()):
            contributor = assignment.contributors[index]
            if level == contributor.skills.get(skill, 0):
                if not contributor.skill_upgrades.get(skill):
                    contributor.skill_upgrades[skill] = contributor.skills.get(skill)
                contributor.skills[skill] = contributor.skills.get(skill) + 1
            elif level - 1 == contributor.skills.get(skill):
                max_level = max(c.skills.get(skill, 0) for c in self.contributors)
                if max_level >= level:
                    if not contributor.skill_upgrades.get(skill):
                        contributor.skill_upgrades[skill] = contributor.skills.get(skill)
                    contributor.skills[skill] = contributor.skills.get(skill) + 1

    def _acceptance_probability(self, current_score: int, neighbor_score: int, temperature: float) -> float:
        if neighbor_score > current_score:
            return 1.0
        return math.exp((neighbor_score - current_score) / temperature)
