import os

from solvers.greedy_solver import GreedySolver
from utils.parse_input_file import parse_input_file
from utils.parse_output_file import parse_output_file
from solvers.my_solver import NeighborSolver

print(os.getcwd())

contributors, projects = parse_input_file("/home/maksbaj/studia/sem5/pop/pop24z/data/a_an_example.in")
# contributors, projects = parse_input_file("/home/adam/IdeaProjects/sem_5/pop24z/data/b_better_start_small.in")

solver = GreedySolver(contributors, projects)
solver.solve(100)
parse_output_file(solver.best_result, "../out/a_an_example.out", contributors)
# solver = NeighborSolver(contributors, projects)
# solver.solve(1000, 0.99)

# biblioteka DEAP do ewolucyjnych
solver = NeighborSolver(contributors, projects)
solver.solve(1000, 0.99999)
print(solver.best_result.score)