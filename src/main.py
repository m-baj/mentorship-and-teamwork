import os
import matplotlib.pyplot as plt
import pandas as pd

from solvers.greedy_solver import GreedySolver
from utils.parse_input_file import parse_input_file
from utils.parse_output_file import parse_output_file
from solvers.my_solver import NeighborSolver
from utils.parse_output_file import parse_second_output_file

def main():
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
    solver.solve(temperature=100, cooling_rate=0.999, change_probability=0.75, correct_start=False,
                 shuffle=True, use_weighted_selection=False, weight_1=100, weight_2=10)
    parse_second_output_file(solver.last_result, "../out/b_better_start_small.out")


    print("BEST SCORE:", solver.best_result.score)
    print("LAST SCORE:", solver.last_result.score)

    # Tworzenie DataFrame z historii
    df = pd.DataFrame(solver.history)

    # Wykres 1: Score with penalty vs Iterations
    plt.figure(figsize=(10, 6))
    plt.plot(df['iteration'], df['best_score'], label='Best Score', color='blue')
    plt.xlabel('Iteration')
    plt.ylabel('Score')
    plt.title('Scores During Optimization')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Wykres 2: Temperature vs Iterations
    plt.figure(figsize=(10, 6))
    plt.plot(df['iteration'], df['temperature'], label='Temperature', color='red')
    plt.xlabel('Iteration')
    plt.ylabel('Temperature')
    plt.title('Temperature Decay')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Wykres 3: Iterarion from last improvement vs Iterations
    plt.figure(figsize=(10, 6))
    plt.plot(df['iteration'], df['iteration_from_last_improvement'], label='Iterarion from last improvement ', color='red')
    plt.xlabel('Iteration')
    plt.ylabel('Iterarion From Last Improvement ')
    plt.title('Iterarion From Last Improvement During Optimization')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Wykres 4: Correct Score vs Iterations
    plt.figure(figsize=(10, 6))
    plt.plot(df['iteration'], df['last_score'], label='Correct Score', color='orange')
    plt.xlabel('Iteration')
    plt.ylabel('Correct score')
    plt.title('Correct Score During Optimization')
    plt.legend()
    plt.grid(True)
    plt.show()


    num_runs = 10
    scores = []

    for i in range(num_runs):
        c2, p2 = parse_input_file("../data/b_better_start_small.in")
        solver_multi = NeighborSolver(c2, p2)
        solver_multi.solve(
            temperature=100,
            cooling_rate=0.999,
            change_probability=0.75,
            correct_start=False,
            shuffle=True,
            use_weighted_selection=False,
            weight_1=100,
            weight_2=10
        )
        parse_second_output_file(solver_multi.last_result, "../out/b_better_start_small.out")
        scores.append(solver_multi.last_result.score)

    data_row = scores + [sum(scores) / len(scores)]
    columns = [f"run_{i + 1}" for i in range(num_runs)] + ["avg_score"]
    df_scores = pd.DataFrame([data_row], columns=columns)

    print("\n=== Wyniki z 10 uruchomień (last_score) ===")
    print(df_scores)

if __name__ == "__main__":
    main()