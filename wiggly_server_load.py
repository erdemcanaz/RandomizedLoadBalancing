import random
from typing import List, Dict, Callable

import numpy as np
import matplotlib.pyplot as plt


# ---------- Random smooth PDF on [0, 1] ----------

def make_random_pdf(num_ctrl_points: int = 10) -> (Callable[[np.ndarray], np.ndarray],
                                                   Callable[[], float],
                                                   np.ndarray,
                                                   np.ndarray
    ):
    """
    Create a random 'smooth-ish' PDF on [0,1].

    - Draw random control-point heights.
    - Smooth them with a moving average.
    - Normalize area to 1 (PDF).
    - Return:
        pdf(x_array) -> array of values,
        sample() -> single x ~ pdf,
        xs_ctrl, pdf_ctrl for plotting.
    """
    # Control points on [0,1]
    xs = np.linspace(0.0, 1.0, num_ctrl_points)

    # Random positive heights, then smooth with moving average
    raw = np.abs(np.random.randn(num_ctrl_points)) + 0.1  # ensure strictly > 0

    # Simple smoothing: moving average with window size 3
    kernel = np.array([1.0, 2.0, 1.0])
    smoothed = np.convolve(raw, kernel, mode="same")
    smoothed = np.maximum(smoothed, 1e-6)  # avoid zero

    # Normalize to get a proper PDF over [0,1]
    area = np.trapz(smoothed, xs)
    pdf_ctrl = smoothed / area

    pdf_max = pdf_ctrl.max()

    def pdf(x: np.ndarray) -> np.ndarray:
        """Evaluate PDF at x in [0,1] using linear interpolation."""
        return np.interp(x, xs, pdf_ctrl)

    def sample() -> float:
        """Rejection sampling from the PDF on [0,1]."""
        while True:
            x = random.random()                # proposal ~ Uniform(0,1)
            u = random.random() * pdf_max      # vertical coordinate
            if u <= pdf(np.array([x]))[0]:
                return x

    return pdf, sample, xs, pdf_ctrl


# ---------- Load balancing simulation ----------

def run_simulation_with_random_pdf(
    num_servers: int = 1000,
    max_k: int = 10,
    num_trials: int = 5000,
) -> (Dict[int, float], Callable[[np.ndarray], np.ndarray], np.ndarray, np.ndarray):
    """
    Monte Carlo simulation of randomized load balancing with
    server loads drawn from a random continuous PDF on [0,1].
    """
    pdf, sampler, xs_ctrl, pdf_ctrl = make_random_pdf()

    totals = {k: 0.0 for k in range(1, max_k + 1)}
    indices = list(range(num_servers))

    for _ in range(num_trials):
        loads = [sampler() for _ in range(num_servers)]

        for k in range(1, max_k + 1):
            sampled_indices = random.sample(indices, k)
            chosen_load = min(loads[i] for i in sampled_indices)
            totals[k] += chosen_load

    expectations = {k: totals[k] / num_trials for k in totals}
    return expectations, pdf, xs_ctrl, pdf_ctrl


# ---------- Main + plotting ----------

def main():
    # For reproducibility, you can set seeds here
    random.seed(48)
    np.random.seed(48)

    num_servers = 10000
    max_k = 10
    num_trials = 200

    results, pdf, xs_ctrl, pdf_ctrl = run_simulation_with_random_pdf(
        num_servers=num_servers,
        max_k=max_k,
        num_trials=num_trials,
    )

    # Prepare data for plotting the PDF
    x_dense = np.linspace(0.0, 1.0, 500)
    pdf_dense = pdf(x_dense)

    # Prepare results for plotting
    ks = np.array(sorted(results.keys()))
    expected_loads = np.array([results[k] for k in ks])

    # ---- Plot: PDF + results in same figure (two subplots) ----
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Left: random PDF
    ax_pdf = axes[0]
    ax_pdf.plot(x_dense, pdf_dense, label="Random PDF")
    ax_pdf.scatter(xs_ctrl, pdf_ctrl, s=15, alpha=0.6, label="Control points")
    ax_pdf.set_title("Random Continuous PDF over Load x ∈ [0,1]")
    ax_pdf.set_xlabel("Load x")
    ax_pdf.set_ylabel("p(x)")
    ax_pdf.legend()

    # Right: expected chosen load vs k with reduction overlay
    ax_res = axes[1]
    
    # Plot expected load
    color1 = 'tab:blue'
    ax_res.plot(ks, expected_loads, marker="o", color=color1, label="Expected Load")
    ax_res.set_xlabel("k (number of random candidates)")
    ax_res.set_ylabel("E[chosen load]", color=color1)
    ax_res.tick_params(axis='y', labelcolor=color1)
    ax_res.grid(True, alpha=0.3)
    
    # Create secondary y-axis for reduction percentage
    ax_reduction = ax_res.twinx()
    
    # Calculate reduction relative to k=1
    baseline_load = expected_loads[0]  # k=1 load
    reduction_percent = ((baseline_load - expected_loads) / baseline_load) * 100
    
    color2 = 'tab:red'
    ax_reduction.plot(ks, reduction_percent, marker="s", linestyle="--", 
                     color=color2, alpha=0.7, label="Reduction vs k=1")
    ax_reduction.set_ylabel("Reduction from k=1 (%)", color=color2)
    ax_reduction.tick_params(axis='y', labelcolor=color2)
    
    ax_res.set_title(f"Expected Load vs k with Reduction\n(N={num_servers:,}, Trials={num_trials})")
    
    # Add legends
    lines1, labels1 = ax_res.get_legend_handles_labels()
    lines2, labels2 = ax_reduction.get_legend_handles_labels()
    ax_res.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    fig.suptitle(
        f"Random PDF + Load Balancing Results (N={num_servers}, T={num_trials})",
        y=1.02,
    )
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
