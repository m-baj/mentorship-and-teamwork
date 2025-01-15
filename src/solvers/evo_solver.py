from deap import base, creator, tools, algorithms
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
from copy import deepcopy
import random

from models.project import Project
from models.contributor import Contributor
from solvers.solver import Solver
from models.result import Result


IVALID_PROJECT_PENALTY = 0
LEVEL_UP_BONUS = 0
MENTORING_BONUS = 0

selection_types = {
    "tournament": (tools.selTournament, {"tournsize": 3}),
    "roulette": (tools.selRoulette, {}),
    "random": (tools.selRandom, {}),
    "double_tournament": (tools.selDoubleTournament, {"fitness_size" :3, "parsimony_size": 2, "fitness_first": True}),
}

@dataclass
class Individual:
    projects: List[Project] = field(default_factory=list)
    skill_to_contributors: Dict[str, List[Contributor]] = field(default_factory=dict)
    score: int = 0

    def __len__(self):
        return len(self.projects)

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", Individual, fitness=creator.FitnessMax)

@dataclass
class EvoSolver(Solver):
    population_size: int
    selection_type: str
    best_result: Result = field(default_factory=Result)

    def __post_init__(self):
        self.ind_size = len(self.projects)
        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", self._init_individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self._evaluate)
        self.toolbox.register("mutate", self._mutate)

        if self.selection_type not in selection_types:
            raise ValueError(f"Invalid selection type: {self.selection_type}")
        selection_func, selection_params = selection_types[self.selection_type]
        self.toolbox.register("select", selection_func, **selection_params)
        print(sum([project.score for project in self.projects]))
        
    def solve(self, ngen: int) -> Tuple[List[int], List[int]]:
        population = self.toolbox.population(n=self.population_size)
        best_individuals = []
        population_avgs = []

        for ind in population:
            ind.fitness.values = self.toolbox.evaluate(ind)
        
        for gen in range(ngen):
            individuals_avg = sum([ind.fitness.values[0] for ind in population]) / len(population)
            population_avgs.append(individuals_avg)
            print(f"Generation {gen}")
            best = max(population, key=lambda ind: ind.fitness.values[0])
            print(f"Best individual: {best.fitness.values[0]}")
            best_individuals.append(best.fitness.values[0])
            selected = self.toolbox.select(population, len(population))

            mutants = []
            for ind in selected:
                clone = self.toolbox.clone(ind)

                self.toolbox.mutate(clone)
                del clone.fitness.values
                mutants.append(clone)

            for ind in mutants:
                ind.fitness.values = self.toolbox.evaluate(ind)
        
            population[:] = mutants

        best = max(population, key=lambda ind: ind.fitness.values[0])
        assigned_projects = [project for project in best.projects if project.is_valid()]
        self.best_result.assignments = assigned_projects
        self.best_result.score = best.score
        return best_individuals, population_avgs

    def _evaluate(self, individual: creator.Individual) -> Tuple[int]:
        individual.score = 0
        individual_cpy = deepcopy(individual)
        penalty = 0
        bonus = 0
        for project_cpy, project in zip(individual_cpy.projects, individual.projects):
            project_cpy.assignments, project.assignments = [], []
            team = set()    
            for skill_name, skill_level in project_cpy.required_skills:

                contributors, bonus_incr = self._get_contributors(skill_name, skill_level, individual_cpy, team)
                bonus += bonus_incr
                
                if contributors:
                    contributor = random.choice(contributors)
                    project_cpy.assignments.append(((skill_name, skill_level), contributor))
                    project.assignments.append(deepcopy(((skill_name, skill_level), contributor)))
                    team.add(contributor)
                    
            if project_cpy.is_valid():
                project_cpy.evaluation_data.begins = max([c.busy_until for _, c in project_cpy.assignments])
                project_cpy.evaluation_data.ends = project_cpy.evaluation_data.begins + project_cpy.duration
                project_cpy.evaluation_data.score = max(
                    0, project_cpy.score - max(0, project_cpy.evaluation_data.ends - project_cpy.best_before)
                )
                
                for (skill, level), contributor in project_cpy.assignments:
                    contributor.busy_until = project_cpy.evaluation_data.ends
                    if contributor.skills[skill] <= level:
                        contributor.skills[skill] += 1
                        bonus += LEVEL_UP_BONUS

            else:
                penalty += IVALID_PROJECT_PENALTY   
        score = sum([project.evaluation_data.score for project in individual_cpy.projects])    
        individual.score = score    

        return score + bonus - penalty,
    
    def _mutate(self, individual: creator.Individual) -> Tuple[creator.Individual]:
        idx1, idx2 = random.sample(range(len(individual.projects)), 2)
        projects = individual.projects
        projects[idx1], projects[idx2] = projects[idx2], projects[idx1]

        return individual,

    def _crossover(self, ind1: creator.Individual, ind2: creator.Individual) -> Tuple[creator.Individual, creator.Individual]:
        pass

    def _get_contributors(self, skill_name: str, skill_level: int, individual: creator.Individual, team: set) -> List[Contributor]:
        contributors = []
        bonus = 0

        for contributor in individual.skill_to_contributors[skill_name] - team:
            if contributor.has_required_skill_one_level_lower(skill_name, skill_level) and any(
                c.can_mentor(skill_name, skill_level) for c in team
            ):
                bonus += MENTORING_BONUS
                return [contributor], bonus
                
            elif contributor.has_required_skill(skill_name, skill_level):
                contributors.append(contributor)

        return contributors, bonus


    def _init_individual(self) -> creator.Individual:
        projects = random.sample(deepcopy(self.projects), len(self.projects))
        skill_to_contributors = {}
        contributors = deepcopy(self.contributors)

        for contributor in contributors:
            for skill in contributor.skills.keys():
                skill_to_contributors.setdefault(skill, set()).add(contributor)
       
        return creator.Individual(projects=projects, skill_to_contributors=skill_to_contributors)
