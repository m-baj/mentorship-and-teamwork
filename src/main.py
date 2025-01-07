import os

from solvers.greedy_solver import GreedySolver
from utils.parse_input_file import parse_input_file

print(os.getcwd())

contributors, projects = parse_input_file("/home/maksbaj/studia/sem5/pop/pop24z/data/a_an_example.in")

solver = GreedySolver(contributors, projects)
solver.solve(5)
print(solver.best_result.score)