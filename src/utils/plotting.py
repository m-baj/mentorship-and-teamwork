import matplotlib.pyplot as plt
from typing import Dict, List
import os

from experiments.experiment import ExperimentResult

def generate_plots(results: Dict[str, List[ExperimentResult]]) -> None:
    for file_name, experiments in results.items():
        for experiment_result in experiments:
            params = experiment_result.params
            generations = list(range(params.ngen))

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 10)) 

            ax1.plot(generations, experiment_result.best_individuals, label="Best Individual Fitness", marker='o', color='blue')
            ax1.set_title("Best Individual Fitness")
            ax1.set_xlabel("Generation")
            ax1.set_ylabel("Fitness")
            ax1.grid(True)
            ax1.legend()

            ax2.plot(generations, experiment_result.population_avgs, label="Population Average Fitness", linestyle='--', color='green')
            ax2.set_title("Population Average Fitness")
            ax2.set_xlabel("Generation")
            ax2.set_ylabel("Fitness")
            ax2.grid(True)
            ax2.legend()

            fig.suptitle(f"File: {file_name}\n Selection: {params.selection_type}, NGen: {params.ngen}, PopSize: {params.population_size}", fontsize=16)

            plot_filename = f"plots/{file_name}_{params.selection_type}_ngen{params.ngen}_pop{params.population_size}.png"
            plt.savefig(plot_filename)
            plt.close()
            print(f"Wykres zapisano do pliku: {plot_filename}")