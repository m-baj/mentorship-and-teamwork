import os

from solvers.greedy_solver import GreedySolver
from utils.parse_input_file import parse_input_file
from utils.parse_output_file import parse_output_file
from solvers.my_solver import NeighborSolver

print(os.getcwd())
file_name = "d_dense_schedule"

contributors, projects = parse_input_file(f"/home/maksbaj/studia/sem5/pop/pop24z/data/{file_name}.in")
# contributors, projects = parse_input_file("/home/adam/IdeaProjects/sem_5/pop24z/data/b_better_start_small.in")

solver = GreedySolver(contributors, projects)
solver.solve(1000)
parse_output_file(solver.best_result, f"../out/{file_name}.out", contributors)
# solver = NeighborSolver(contributors, projects)
# solver.solve(1000, 0.99)

# biblioteka DEAP do ewolucyjnych
solver = NeighborSolver(contributors, projects)
solver.solve(1000, 0.99999)
print(solver.best_result.score)