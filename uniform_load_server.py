import random
from typing import List, Dict
import matplotlib.pyplot as plt


def run_simulation(
    num_servers: int = 10000,
    max_k: int = 10,
    num_trials: int = 10000,
) -> Dict[int, float]:
    """
    Monte Carlo simulation for randomized load balancing.

    For each trial:
      - Create num_servers loads ~ U(0, 1)
      - For each k in [1..max_k], sample k servers uniformly at random
        and record the minimum load among those k.

    Returns:
      dict: {k: expected_chosen_load_for_k}
    """
    # Accumulate total chosen load for each k
    totals = {k: 0.0 for k in range(1, max_k + 1)}

    for _ in range(num_trials):
        # Random loads for this trial
        loads: List[float] = [random.random() for _ in range(num_servers)]

        # For each k, pick k distinct servers and record the min load
        indices = list(range(num_servers))
        for k in range(1, max_k + 1):
            sampled = random.sample(indices, k)
            chosen_load = min(loads[i] for i in sampled)
            totals[k] += chosen_load

    # Convert totals to expectations
    expectations = {k: totals[k] / num_trials for k in totals}
    return expectations


def main():
    num_servers = 10000
    max_k = int(num_servers*0.05)  # up to 1% of servers
    num_trials = 100

    results = run_simulation(num_servers, max_k, num_trials)

    print(f"Simulation with N={num_servers}, K<= {max_k}, T={num_trials}")
    print("k\tExpected chosen load")
    for k in sorted(results.keys()):
        print(f"{k}\t{results[k]:.4f}")
    
    # Plot the results
    k_values = sorted(results.keys())
    expected_loads = [results[k] for k in k_values]
    
    plt.figure(figsize=(10, 6))
    plt.plot(k_values, expected_loads, marker='o', linewidth=2, markersize=4)
    plt.xlabel('k (number of servers sampled)', fontsize=12)
    plt.ylabel('Expected chosen load', fontsize=12)
    plt.title(f'Randomized Load Balancing (N={num_servers}, Trials={num_trials})', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
