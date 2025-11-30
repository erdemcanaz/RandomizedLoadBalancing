import random
from typing import List, Dict, Callable
import matplotlib.pyplot as plt


def poly_value(x: float, coeffs: List[float]) -> float:
    """Evaluate polynomial p(x) = a0 + a1 x + ... at x."""
    return sum(a * (x ** i) for i, a in enumerate(coeffs))


def poly_normalization_constant(coeffs: List[float]) -> float:
    """
    Compute Z = ∫_0^1 p(x) dx analytically for polynomial p(x).
    If p(x) = Σ a_i x^i, then ∫_0^1 p(x) dx = Σ a_i / (i+1).
    """
    return sum(a / (i + 1) for i, a in enumerate(coeffs))


def make_polynomial_sampler(
    coeffs: List[float],
    grid_points: int = 1000
) -> Callable[[], float]:
    """
    Create a sampler for a 1D PDF on [0,1] defined by an unnormalized polynomial.

    P(server has load in [x, x+dx]) ∝ p(x), where p(x) >= 0 on [0,1].
    We:
      - compute normalization constant Z = ∫_0^1 p(x) dx
      - estimate max p(x) on a grid to use for rejection sampling
    Returns:
      A function sample() that draws a single x ~ normalized p(x)/Z.
    """

    Z = poly_normalization_constant(coeffs)
    if Z <= 0:
        raise ValueError("Polynomial integral over [0,1] must be positive.")

    # Estimate max p(x) on [0,1] using a grid
    max_val = 0.0
    for i in range(grid_points + 1):
        x = i / grid_points
        val = poly_value(x, coeffs)
        if val < -1e-12:
            raise ValueError(
                f"Polynomial must be non-negative on [0,1], got {val} at x={x}"
            )
        if val > max_val:
            max_val = val

    if max_val <= 0:
        raise ValueError("Polynomial appears to be zero on [0,1].")

    # Rejection sampling using unnormalized p(x). Normalization Z is not
    # needed for the accept/reject logic, but we computed it for completeness.
    def sample() -> float:
        while True:
            x = random.random()          # Uniform in [0,1]
            u = random.random() * max_val
            if u <= poly_value(x, coeffs):
                return x

    return sample


def run_simulation_with_poly_loads(
    num_servers: int = 1000,
    max_k: int = 10,
    num_trials: int = 10000,
    poly_coeffs: List[float] = None,
) -> Dict[int, float]:
    """
    Monte Carlo simulation of randomized load balancing with
    server loads drawn from a polynomial PDF on [0,1].

    poly_coeffs defines an unnormalized polynomial:
        p(x) = a0 + a1 x + a2 x^2 + ...
    which is normalized internally to form a proper PDF.
    """

    if poly_coeffs is None:
        # Example: p(x) ∝ 2x (i.e. more mass near 1), i.e. [0, 2]
        poly_coeffs = [0.0, 2.0]

    sampler = make_polynomial_sampler(poly_coeffs)

    totals = {k: 0.0 for k in range(1, max_k + 1)}
    indices = list(range(num_servers))

    for _ in range(num_trials):
        # Sample loads for each server according to polynomial PDF
        loads = [sampler() for _ in range(num_servers)]

        for k in range(1, max_k + 1):
            sampled_indices = random.sample(indices, k)
            chosen_load = min(loads[i] for i in sampled_indices)
            totals[k] += chosen_load

    expectations = {k: totals[k] / num_trials for k in totals}
    return expectations


def main():
    num_servers = 10000
    max_k = 10
    num_trials = 100

    # Example polynomial: p(x) = 0.02 x^2 + 0.15 x + 1
    poly_coeffs = [0.02 , 0.15, 1]

    results = run_simulation_with_poly_loads(
        num_servers=num_servers,
        max_k=max_k,
        num_trials=num_trials,
        poly_coeffs=poly_coeffs,
    )

    print("Polynomial coefficients (unnormalized):", poly_coeffs)
    print(f"Simulation with N={num_servers}, K<= {max_k}, T={num_trials}")
    print("k\tExpected chosen load")
    for k in sorted(results.keys()):
        print(f"{k}\t{results[k]:.4f}")
    
    # Plot the results
    k_values = sorted(results.keys())
    expected_loads = [results[k] for k in k_values]
    
    plt.figure(figsize=(10, 6))
    plt.plot(k_values, expected_loads, marker='o', linewidth=2, markersize=6)
    plt.xlabel('k (number of servers sampled)', fontsize=12)
    plt.ylabel('Expected chosen load', fontsize=12)
    plt.title(f'Non-uniform Load Balancing (N={num_servers}, Trials={num_trials})\nPolynomial: {poly_coeffs}', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

