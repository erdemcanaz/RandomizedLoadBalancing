import random
from typing import List, Dict
import matplotlib.pyplot as plt
import numpy as np


def simulate_random_placement(
    num_bins: int = 100,
    num_balls: int = 100,
    num_trials: int = 1000,
) -> Dict[str, any]:
    """
    Simulate placing balls into bins with purely random placement.
    Each ball is placed into a randomly selected bin.
    
    Returns:
        dict: Statistics including max load, average load distribution
    """
    max_loads = []
    load_distributions = []
    
    for _ in range(num_trials):
        bins = [0] * num_bins
        
        for _ in range(num_balls):
            chosen_bin = random.randint(0, num_bins - 1)
            bins[chosen_bin] += 1
        
        max_loads.append(max(bins))
        load_distributions.append(bins.copy())
    
    return {
        'max_loads': max_loads,
        'avg_max_load': np.mean(max_loads),
        'std_max_load': np.std(max_loads),
        'load_distributions': load_distributions,
        'avg_distribution': np.mean(load_distributions, axis=0)
    }


def simulate_best_of_two(
    num_bins: int = 100,
    num_balls: int = 100,
    num_trials: int = 1000,
) -> Dict[str, any]:
    """
    Simulate placing balls into bins using "best of two" strategy.
    For each ball, pick two random bins and place it in the one with fewer balls.
    This is the "power of two random choices" approach.
    
    Returns:
        dict: Statistics including max load, average load distribution
    """
    max_loads = []
    load_distributions = []
    
    for _ in range(num_trials):
        bins = [0] * num_bins
        
        for _ in range(num_balls):
            # Pick two random bins
            bin1 = random.randint(0, num_bins - 1)
            bin2 = random.randint(0, num_bins - 1)
            
            # Place ball in the bin with fewer balls
            if bins[bin1] <= bins[bin2]:
                bins[bin1] += 1
            else:
                bins[bin2] += 1
        
        max_loads.append(max(bins))
        load_distributions.append(bins.copy())
    
    return {
        'max_loads': max_loads,
        'avg_max_load': np.mean(max_loads),
        'std_max_load': np.std(max_loads),
        'load_distributions': load_distributions,
        'avg_distribution': np.mean(load_distributions, axis=0)
    }


def simulate_best_of_k(
    num_bins: int = 100,
    num_balls: int = 100,
    k: int = 3,
    num_trials: int = 1000,
) -> Dict[str, any]:
    """
    Simulate placing balls into bins using "best of k" strategy.
    For each ball, pick k random bins and place it in the one with fewest balls.
    
    Returns:
        dict: Statistics including max load, average load distribution
    """
    max_loads = []
    load_distributions = []
    
    for _ in range(num_trials):
        bins = [0] * num_bins
        
        for _ in range(num_balls):
            # Pick k random bins
            sampled_bins = random.sample(range(num_bins), k)
            
            # Place ball in the bin with fewest balls
            min_bin = min(sampled_bins, key=lambda idx: bins[idx])
            bins[min_bin] += 1
        
        max_loads.append(max(bins))
        load_distributions.append(bins.copy())
    
    return {
        'max_loads': max_loads,
        'avg_max_load': np.mean(max_loads),
        'std_max_load': np.std(max_loads),
        'load_distributions': load_distributions,
        'avg_distribution': np.mean(load_distributions, axis=0)
    }


def main():
    num_bins = 100
    num_balls = 100000
    num_trials = 25
    max_k = 5
    
    print(f"Balls-in-Bins Simulation")
    print(f"Bins: {num_bins}, Balls: {num_balls}, Trials: {num_trials}")
    print("="*60)
    
    # Run simulations
    random_results = simulate_random_placement(num_bins, num_balls, num_trials)
    best_of_two_results = simulate_best_of_two(num_bins, num_balls, num_trials)
    
    # Run for various k values
    k_results = {}
    for k in range(1, max_k + 1):
        if k == 1:
            k_results[k] = random_results
        elif k == 2:
            k_results[k] = best_of_two_results
        else:
            k_results[k] = simulate_best_of_k(num_bins, num_balls, k, num_trials)
    
    # Print statistics
    print("\nStrategy: Random Placement (k=1)")
    print(f"  Average Maximum Load: {random_results['avg_max_load']:.2f}")
    print(f"  Std Dev Maximum Load: {random_results['std_max_load']:.2f}")
    
    print("\nStrategy: Best of Two (k=2) - Power of Two Choices")
    print(f"  Average Maximum Load: {best_of_two_results['avg_max_load']:.2f}")
    print(f"  Std Dev Maximum Load: {best_of_two_results['std_max_load']:.2f}")
    
    improvement = ((random_results['avg_max_load'] - best_of_two_results['avg_max_load']) / 
                   random_results['avg_max_load'] * 100)
    print(f"  Improvement over Random: {improvement:.1f}%")
    
    print("\n" + "="*60)
    print("Max Load Comparison for Different k Values:")
    print("-"*60)
    for k in range(1, max_k + 1):
        print(f"k={k}: Avg Max Load = {k_results[k]['avg_max_load']:.2f} "
              f"(±{k_results[k]['std_max_load']:.2f})")
    
    # Create probability distribution: ball count vs probability for k=1,2,3,5
    plt.figure(figsize=(14, 7))
    
    # Expected average: num_balls / num_bins
    expected_avg = num_balls / num_bins
    
    # Define x-axis range: center ± 10
    x_min = max(0, int(expected_avg - 10))
    x_max = int(expected_avg + 10) + 1
    bins_range = range(x_min, x_max + 1)
    
    # Strategies to plot
    strategies = [
        (1, k_results[1], 'Random (k=1)', 'blue', 'lightblue'),
        (2, k_results[2], 'Best of 2 (k=2)', 'red', 'lightcoral'),
        (3, k_results[3], 'Best of 3 (k=3)', 'green', 'lightgreen'),
        (5, k_results[5], 'Best of 5 (k=5)', 'purple', 'plum')
    ]
    
    bar_width = 0.2
    x_positions = np.arange(x_min, x_max)
    
    for idx, (k, results, label, edge_color, face_color) in enumerate(strategies):
        # Calculate probability distribution
        flat_data = np.concatenate(results['load_distributions'])
        counts, _ = np.histogram(flat_data, bins=bins_range, density=True)
        
        # Plot bars with offset
        offset = (idx - 1.5) * bar_width
        plt.bar(x_positions + offset, counts, width=bar_width, alpha=0.7, 
                label=label, edgecolor=edge_color, color=face_color)
    
    # Add vertical line at expected average
    plt.axvline(expected_avg, color='black', linestyle='--', linewidth=2, 
                label=f'Expected Avg ({expected_avg:.1f})')
    
    plt.xlabel('Ball Count per Bin', fontsize=12)
    plt.ylabel('Probability Density', fontsize=12)
    plt.title(f'Probability Distribution of Ball Counts\n(Bins={num_bins}, Balls={num_balls}, Trials={num_trials})', 
              fontsize=14)
    plt.legend(fontsize=10, loc='upper right')
    plt.grid(True, alpha=0.3, axis='y')
    plt.xlim(x_min - 0.5, x_max - 0.5)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
