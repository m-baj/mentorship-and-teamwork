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
    max_iterations: int = 100000

    history: List[Dict[str, float]] = field(default_factory=list)

    def solve(self, temperature: int, cooling_rate: float, change_probability: float,
              correct_start: bool = True, shuffle: bool = False,
              use_weighted_selection: bool = True, weight_1: float = 10000, weight_2: float = 100) -> Result:
        n = -180000000 # tylko do printów

        tabu_list = []
        tabu_max_size = 300

        # sprawdzic z sortowaniem i z losowym
        if shuffle:
            random.shuffle(self.projects)
        else:
            self.projects.sort(key=lambda p: p.best_before)

        self.skill_to_contributors = self._map_skills_to_contributors()

        current_assignments = []
        for project in self.projects:
            assignment = self._assign_project(project, correct_start, use_weighted_selection, weight_1, weight_2)
            if assignment:
                current_assignments.append(assignment)

        self.best_result = Result(score = self._evaluate_solution(current_assignments),
                             assignments = current_assignments)

        i_from_last_improvement = 0
        iterations = 0

        self.last_evaluation()
        self.history.append({
            'iteration': iterations,
            'iteration_from_last_improvement': i_from_last_improvement,
            'temperature': temperature,
            'best_score': self.best_result.score,
            'last_score': self.last_result.score
        })


        # mozna dopisac sprawdzanie czy mozna znalezc poprawne rozwiazanie po n iteracjach
        # mozna dodać tabu
        while temperature > 1 and i_from_last_improvement < self.max_iterations: # 100000 to kilkanaście sekund
            iterations += 1
            for contributor in self.contributors:
                if contributor.skill_upgrades:
                    for skill, level in contributor.skill_upgrades.items():
                        contributor.skills[skill] = contributor.skill_upgrades[skill]
                    contributor.skill_upgrades = {}

            neighbor_assignments = self._generate_neighbor(current_assignments, change_probability, weight_1, weight_2)
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

            self.history.append({
                'iteration': iterations,
                'iteration_from_last_improvement': i_from_last_improvement,
                'temperature': temperature,
                'best_score': self.best_result.score,
                'last_score': self.last_result.score
            })


    def _map_skills_to_contributors(self) -> Dict[str, List[Contributor]]:
        skill_map = {}
        for contributor in self.contributors:
            for skill, level in contributor.skills.items():
                if skill not in skill_map:
                    skill_map[skill] = []
                skill_map[skill].append(contributor)
        return skill_map

    # wystartowac ze stanu ktory bedzie poprawny
    def _assign_project(self, project: Project, correct_start: bool, use_weighted_selection: bool
                        , weight_1: float, weight_2: float) -> Assignment:
        assigned_contributors = []
        team = []
        for skill, level in project.required_skills:
            if correct_start:
                suitable_contributors = [c for c in self.skill_to_contributors.get(skill, [])
                                         if c.has_required_skill(skill, level) and c not in team]
            else:
                suitable_contributors = [c for c in self.skill_to_contributors.get(skill, [])
                                         if c not in team]
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
                        weight *= weight_1
                    elif skill_level > level:
                        weight *= weight_2
                    weights.append(weight)

                # Wybierz nowego pracownika z odpowiednimi wagami
                chosen_contributor = random.choices(suitable_contributors, weights=weights, k=1)[0]
            else:
                # Losowy wybór pracownika bez wag
                chosen_contributor = random.choice(suitable_contributors)
            team.append(chosen_contributor)
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
    def _generate_neighbor(self, assignments: List[Assignment], change_probability: float,
                           weight_1: float, weight_2: float) -> List[Assignment]:
        neighbor = assignments[:]

        if random.random() < change_probability:
            random_assignment = random.choice(neighbor)
            team = random_assignment.contributors[:]
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
                skill = random_assignment.project.required_skills[random_idx][0]
                required_level = random_assignment.project.required_skills[random_idx][1]

                potential_mentors = []
                for con in team:
                    if c.skills.get(skill, 0) >= required_level:
                        potential_mentors.append(con)

                mentee_candidates = []
                if potential_mentors:
                    mentee_candidates = [
                        c for c in self.skill_to_contributors.get(skill, [])
                        if c.skills.get(skill, 0) == required_level - 1
                           and c not in team
                    ]
                if mentee_candidates:
                    mentee = random.choice(mentee_candidates)
                    team[random_idx] = mentee
                    random_assignment.contributors[random_idx] = mentee
                    # print("Mentoring")
                else:
                    available_contributors = [
                        c for c in self.skill_to_contributors.get(skill, [])
                        if c not in team
                    ]
                    if available_contributors:
                        # Oblicz wagi na podstawie rozkładu Gaussa
                        sigma = 0.5
                        weights = []

                        for c in available_contributors:
                            skill_level = c.skills.get(skill, 0)
                            weight = math.exp(-((skill_level - required_level) ** 2) / (2 * sigma ** 2))
                            # Premia dla idealnego poziomu
                            if skill_level == required_level:
                                weight *= weight_1
                            elif skill_level > required_level:
                                weight *= weight_2
                            weights.append(weight)
                        new_contributor = random.choices(available_contributors, weights=weights, k=1)[0]
                        random_assignment.contributors[random_idx] = new_contributor
                        team[random_idx] = new_contributor
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