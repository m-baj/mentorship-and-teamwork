import pandas as pd

from utils.parse_input_file import parse_input_file
from solvers.my_solver import NeighborSolver
from utils.parse_output_file import parse_second_output_file
from utils.plots import plot

def main():

    input_path = "data/b_better_start_small.in"
    output_path = "out/b_better_start_small.out"
    input_path_c = "data/c_collaboration.in"
    output_path_c = "out/c_collaboration.out"
    input_path_a = "data/a_an_example.in"
    output_path_a = "out/a_an_example.out"

    temperatures = [50, 100]
    cooling_rates = [0.999, 0.9995]
    change_probabilities = [0.75, 0.85]
    correct_starts = [False]
    shuffles = [True, False]
    use_weighted_selections = [True, False]
    weights_pairs = [(100, 10)]



    param_combos = []
    for t in temperatures:
        for cr in cooling_rates:
            for cp in change_probabilities:
                for cs in correct_starts:
                    for s in shuffles:
                        for wsel in use_weighted_selections:
                            if wsel:
                                for w1, w2 in weights_pairs:
                                    param_combos.append((t, cr, cp, cs, s, wsel, w1, w2))
                            else:
                                param_combos.append((t, cr, cp, cs, s, wsel, 1, 1))


    # contributors, projects = parse_input_file(input_path)
    # solver = NeighborSolver(contributors, projects)
    # solver.solve(temperature=50, cooling_rate=0.99, change_probability=0.75, correct_start=False,
    #              shuffle=False, use_weighted_selection=False, weight_1=100, weight_2=10)
    # parse_second_output_file(solver.last_result, output_path)
    # print(solver.last_result.score)
    # df = pd.DataFrame(solver.history)
    # plot(df)

    # contributors, projects = parse_input_file(input_path)
    # solver = NeighborSolver(contributors, projects)
    # solver.solve(temperature=50, cooling_rate=0.999, change_probability=0.85, correct_start=False,
    #              shuffle=False, use_weighted_selection=False, weight_1=100, weight_2=10)
    # parse_second_output_file(solver.last_result, output_path)
    # print(solver.last_result.score)
    # df = pd.DataFrame(solver.history)
    # plot(df)



    for (temp, cool, ch_prob, c_start, do_shuffle, w_select, w1, w2) in param_combos:
        print("\n========================================")
        print(f"Uruchamiam solver z parametrami:")
        print(f"  temperature={temp}, cooling_rate={cool}, change_probability={ch_prob}")
        print(f"  correct_start={c_start}, shuffle={do_shuffle}, use_weighted_selection={w_select}")
        print(f"  weight_1={w1}, weight_2={w2}")
        print("========================================\n")


        num_runs = 10
        scores = []

        for i in range(num_runs):
            c2, p2 = parse_input_file(input_path)
            solver_multi = NeighborSolver(c2, p2)
            solver_multi.solve(
                temperature=temp,
                cooling_rate=cool,
                change_probability=ch_prob,
                correct_start=c_start,
                shuffle=do_shuffle,
                use_weighted_selection=w_select,
                weight_1=w1,
                weight_2=w2
            )
            parse_second_output_file(solver_multi.last_result, output_path)
            scores.append(solver_multi.last_result.score)
            # if i == 0:
            #     df = pd.DataFrame(solver_multi.history)
            #     plot(df)

        data_row = scores + [sum(scores) / len(scores)] + [max(scores)]
        columns = [f"run_{i + 1}" for i in range(num_runs)] + ["avg_score"] + ["max_score"]
        df_scores = pd.DataFrame([data_row], columns=columns)

        print("\n=== Wyniki z 10 uruchomień (last_score) ===")
        print(df_scores)

if __name__ == "__main__":
    main()