import os

from solvers.greedy_solver import GreedySolver
from utils.parse_input_file import parse_input_file
from utils.parse_output_file import parse_output_file
from solvers.my_solver import NeighborSolver
from utils.parse_output_file import parse_second_output_file

print(os.getcwd())

# contributors, projects = parse_input_file("/home/maksbaj/studia/sem5/pop/pop24z/data/a_an_example.in")
contributors, projects = parse_input_file("../data/b_better_start_small.in")
# contributors, projects = parse_input_file("../data/c_collaboration.in")

# solver = GreedySolver(contributors, projects)
# solver.solve(100)

# solver = NeighborSolver(contributors, projects)
# solver.solve(1000, 0.99)

# biblioteka DEAP do ewolucyjnych
solver = NeighborSolver(contributors, projects)
solver.solve(100, 0.9999, False, False, False)
parse_second_output_file(solver.last_result, "../out/b_better_start_small.out")
print(solver.best_result.score, solver.last_result.score)