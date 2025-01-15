import pandas as pd
from matplotlib import pyplot as plt


def plot(df: pd.DataFrame):
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
    plt.plot(df['iteration'], df['iteration_from_last_improvement'], label='Iterarion from last improvement ',
             color='red')
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