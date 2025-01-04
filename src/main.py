from solvers.greedy_solver import GreedySolver
from utils.parse_input_file import parse_input_file

projects, contributors = parse_input_file("../data/a_an_example.in")

solver = GreedySolver(projects, contributors)
print(solver.assignments)