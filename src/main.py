import matplotlib.pyplot as plt

from solvers.greedy_solver import GreedySolver
from solvers.evo_solver import EvoSolver
from utils.parse_input_file import parse_input_file
from utils.parse_output_file import parse_output_file
from utils.plotting import generate_plots
from experiments.experiment import ExperimentRunner
from experiments.experiment import Params

files = [
    "a_an_example",
    "b_better_start_small",
    # "c_collaboration"  
]

params = [
    Params(ngen=100, population_size=100, selection_type="tournament"),
    Params(ngen=100, population_size=100, selection_type="roulette"),
    Params(ngen=100, population_size=100, selection_type="random"),
    Params(ngen=100, population_size=100, selection_type="double_tournament"),
]

runner = ExperimentRunner(params, files)
results = runner.run()
print(results)

generate_plots(results)