import json
import matplotlib.pyplot as plt

def uninformed_time_graph(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)

    selected_algorithms = {'bfs', 'dfs', 'ids', 'ucs'}

    times_sum = {}
    times_count = {}

    for entry in data:
        alg = entry.get('algorithm', 'unknown')
        if alg in selected_algorithms:
            time = entry['execution_time']
            times_sum[alg] = times_sum.get(alg, 0) + time
            times_count[alg] = times_count.get(alg, 0) + 1
    avg_times = {alg: times_sum[alg] / times_count[alg] for alg in times_sum}

    plt.figure(figsize=(8, 5))
    plt.bar(avg_times.keys(), avg_times.values(), color="cornflowerblue")
    plt.title("Average Execution Time (BFS, DFS, IDS, UCS)")
    plt.xlabel("Algorithm")
    plt.ylabel("Time (seconds)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def informed_time_graph_for_heuristic(filepath, heuristic):
    with open(filepath, 'r') as f:
        data = json.load(f)

    times_sum = {}
    times_count = {}

    for entry in data:
        if entry.get('heuristic') != heuristic:
            continue

        alg = entry.get('algorithm', 'unknown')

        if alg == 'greedy' or alg == 'astar':
            times_sum[alg] = times_sum.get(alg, 0) + entry['execution_time']
            times_count[alg] = times_count.get(alg, 0) + 1
        elif alg == 'wastar':
            w = entry.get('weight', 1.0)
            key = f"wastar (w={w})"
            times_sum[key] = times_sum.get(key, 0) + entry['execution_time']
            times_count[key] = times_count.get(key, 0) + 1

    avg_times = {}
    for key in times_sum:
        if times_count[key] > 0:
            avg_times[key] = times_sum[key] / times_count[key]

    if not avg_times:
        print(f"No data found for heuristic '{heuristic}'. Skipping chart.")
        return

    plt.figure(figsize=(7, 4))
    plt.bar(avg_times.keys(), avg_times.values(), color="cornflowerblue")
    plt.title(f"Averages for {heuristic.upper()} (Greedy, A*, WA*)")
    plt.xlabel("Algorithm")
    plt.ylabel("Time (seconds)")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(f"informed_time_{heuristic}.png")  
    plt.close() 

def generate_informed_charts(filepath):
    for h in ["h1", "h2", "h3", "h4"]:
        informed_time_graph_for_heuristic(filepath, h)



def all_algorithms_time_graph(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)

    times_sum = {}
    times_count = {}

    for entry in data:
        heuristic = entry.get('heuristic', 'N/A')
        if heuristic not in ["combined_custom", "N/A"]:
            continue

        alg = entry.get('algorithm')
        if not alg:
            continue
        
        if alg == 'wastar':
            w = entry.get('weight', 1.0)
            alg_key = f"wastar (w={w})"
        else:
            alg_key = alg
        
        time = entry.get('execution_time', 0)
        times_sum[alg_key] = times_sum.get(alg_key, 0) + time
        times_count[alg_key] = times_count.get(alg_key, 0) + 1

    avg_times = {}
    for key in times_sum:
        if times_count[key] > 0:
            avg_times[key] = times_sum[key] / times_count[key]

    if not avg_times:
        print("No data found for the specified heuristics.")
        return

    plt.figure(figsize=(8, 5))
    plt.bar(avg_times.keys(), avg_times.values(), color="cornflowerblue")
    plt.title('Average Execution Time')
    plt.xlabel("Algorithm")
    plt.ylabel("Time (seconds)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()




if __name__ == "__main__":
    # uninformed_time_graph("/home/mariajvieira/Desktop/IA/IA_CakeSortPuzzle/results/algorithm_results.json")
    # generate_informed_charts("/home/mariajvieira/Desktop/IA/IA_CakeSortPuzzle/results/algorithm_results.json")
    all_algorithms_time_graph("/home/mariajvieira/Desktop/IA/IA_CakeSortPuzzle/results/algorithm_results.json")