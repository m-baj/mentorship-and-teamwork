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

from utils.parse_output_file import parse_second_output_file

@dataclass
class NeighborSolver(Solver):
    contributors: List[Contributor]
    projects: List[Project]

    best_result: Result = field(default_factory=Result)
    last_result: Result = field(default_factory=Result)
    skill_to_contributors: Dict[str, List[Contributor]] = field(default_factory=dict)

    def solve(self, temperature: int, cooling_rate: float,
              correct_start: bool = True, shuffle: bool = False,
              use_weighted_selection: bool = True) -> Result:
        n = -180000000
        # sprawdzic z sortowaniem i z losowym

        tabu_list = []  # Lista tabu
        tabu_max_size = 300  # Maksymalny rozmiar listy tabu

        if shuffle:
            random.shuffle(self.projects)
        else:
            self.projects.sort(key=lambda p: p.best_before)

        self.skill_to_contributors = self._map_skills_to_contributors()

        current_assignments = []
        for project in self.projects:
            assignment = self._assign_project(project, correct_start, use_weighted_selection)
            if assignment:
                current_assignments.append(assignment)

        self.best_result = Result(score = self._evaluate_solution(current_assignments),
                             assignments = current_assignments)


        # mozna dopisac sprawdzanie czy mozna znalezc poprawne rozwiazanie po n iteracjach
        # mozna dodać tabu
        i_from_last_improvement = 0
        while temperature > 1 and i_from_last_improvement < 100000:
            for contributor in self.contributors:
                if contributor.skill_upgrades:
                    for skill, level in contributor.skill_upgrades.items():
                        contributor.skills[skill] = contributor.skill_upgrades[skill]
                    contributor.skill_upgrades = {}

            neighbor_assignments = self._generate_neighbor(current_assignments)
            neighbor_hash = self._hash_assignments(neighbor_assignments)

            if neighbor_hash in tabu_list:
                continue
            neighbor_score = self._evaluate_solution(neighbor_assignments)

            if self._acceptance_probability(self.best_result.score, neighbor_score, temperature) > random.random():
                current_assignments = neighbor_assignments
                self.best_result = Result(score=neighbor_score, assignments=neighbor_assignments)
                i_from_last_improvement = 0
                tabu_list.append(neighbor_hash)
                if len(tabu_list) > tabu_max_size:
                    tabu_list.pop(0)

                if self.best_result.score > n:
                    print(self.best_result.score)
                    n = min(n + 10000000, self.best_result.score)
            i_from_last_improvement += 1
            temperature *= cooling_rate
        self.last_evaluation()
        print("abc")


    def _map_skills_to_contributors(self) -> Dict[str, List[Contributor]]:
        skill_map = {}
        for contributor in self.contributors:
            for skill, level in contributor.skills.items():
                if skill not in skill_map:
                    skill_map[skill] = []
                skill_map[skill].append(contributor)
        return skill_map

    # wystartowac ze stanu ktory bedzie poprawny
    def _assign_project(self, project: Project, correct_start: bool, use_weighted_selection: bool) -> Assignment:
        assigned_contributors = []
        for skill, level in project.required_skills:
            if correct_start:
                suitable_contributors = [c for c in self.skill_to_contributors.get(skill, [])
                                         if c.has_required_skill(skill, level)]
            else:
                suitable_contributors = [c for c in self.skill_to_contributors.get(skill, [])]
            if not suitable_contributors:
                return None

            if use_weighted_selection:
                # Oblicz wagi na podstawie rozkładu Gaussa
                sigma = 0.5  # Mniejsze sigma dla węższego rozkładu
                weights = []

                for c in suitable_contributors:
                    skill_level = c.skills.get(skill, 0)
                    weight = math.exp(-((skill_level - level) ** 2) / (2 * sigma ** 2))
                    # Premia dla idealnego poziomu
                    if skill_level == level:
                        weight *= 100000
                    elif skill_level > level:
                        weight *= 100
                    weights.append(weight)

                # Wybierz nowego pracownika z odpowiednimi wagami
                chosen_contributor = random.choices(suitable_contributors, weights=weights, k=1)[0]
            else:
                # Losowy wybór pracownika bez wag
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
            for index, (skill, level) in enumerate(project.required_skills):
                if assignment.contributors[index].skills[skill] < level:
                    penalty += 10000000 + max(0, (project.score -
                            max(0, end_data - project.best_before)))
                self.upgrade_skills(assignment, index, skill, level)
            score = max(0, (project.score -
                            max(0, end_data - project.best_before))) - penalty
            total_score += score
        for contributor in self.contributors:
            contributor.busy_until = 0
        return total_score

    # sprobowac dorzucic pracownika z nizszym poziomem do tego z wyzszym
    # randomowy z wiekszym prawdopodobienstwem
    # prawdopodobienstwo zalezne od levelu
    def _generate_neighbor(self, assignments: List[Assignment]) -> List[Assignment]:
        neighbor = assignments[:]

        if random.random() < 0.85:
            random_assignment = random.choice(neighbor)
            weights = []
            for random_idx, c in enumerate(random_assignment.contributors):
                skill = random_assignment.project.required_skills[random_idx][0]
                required_level = random_assignment.project.required_skills[random_idx][1]
                current_level = c.skills.get(skill, 0)
                if current_level < required_level:
                    weight = 10
                else:
                    weight = 1
                weights.append(weight)
            random_idx = random.choices(range(len(random_assignment.contributors)), weights=weights, k=1)[0]
            if random_assignment.contributors:
                # random_idx = random.randint(0, len(random_assignment.contributors) - 1)
                # skills = list(random_assignment.project.required_skills.keys())
                # skill = skills[random_idx]
                skill = random_assignment.project.required_skills[random_idx][0]
                contributors_with_skill = self.skill_to_contributors[skill]
                if contributors_with_skill:
                    # Oblicz wagi na podstawie rozkładu Gaussa
                    required_level = random_assignment.project.required_skills[random_idx][1]
                    sigma = 0.5  # Mniejsze sigma dla węższego rozkładu
                    weights = []

                    for c in contributors_with_skill:
                        skill_level = c.skills.get(skill, 0)
                        weight = math.exp(-((skill_level - required_level) ** 2) / (2 * sigma ** 2))
                        # Premia dla idealnego poziomu
                        if skill_level == required_level:
                            weight *= 10000
                        elif skill_level > required_level:
                            weight *= 10
                        weights.append(weight)
                    new_contributor = random.choices(contributors_with_skill, weights=weights, k=1)[0]
                    random_assignment.contributors[random_idx] = new_contributor
        else:
            if len(neighbor) > 1:
                idx1, idx2 = random.sample(range(len(neighbor)), 2)
                neighbor[idx1], neighbor[idx2] = neighbor[idx2], neighbor[idx1]

        return neighbor

    def upgrade_skills(self, assignment: Assignment, index: int, skill: str, level: int):
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

    def _hash_assignments(self, assignments):
        return tuple(
            (assignment.project.id, tuple(c.id for c in assignment.contributors))
            for assignment in assignments
        )

    def last_evaluation(self):
        total_score = 0
        done_assignments = []
        for assignment in self.best_result.assignments:
            project = assignment.project
            begin_data = max(c.busy_until for c in assignment.contributors)
            end_data = begin_data + project.duration
            penalty = 0
            for index, (skill, level) in enumerate(project.required_skills):
                if assignment.contributors[index].skills[skill] < level:
                    penalty += 10000000 + max(0, (project.score -
                            max(0, end_data - project.best_before)))
                self.upgrade_skills(assignment, index, skill, level)
            score = max(0, (project.score -
                            max(0, end_data - project.best_before))) - penalty
            if score > 0:
                done_assignments.append(assignment)
            else:
                continue
            for contributor in assignment.contributors:
                contributor.busy_until = end_data
            total_score += score
        for contributor in self.contributors:
            contributor.busy_until = 0
        self.last_result = Result(score=total_score, assignments=done_assignments)