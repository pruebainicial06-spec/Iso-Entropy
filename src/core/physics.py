#physics.py
import math
import random

def calculate_collapse_threshold(stock_ratio: float, capital_ratio: float, liquidity: float) -> float:
    """
    Calculates the Collapse Threshold (Theta_max) using the logarithmic formula.
    θ_max = log₂(1 + Stock Ratio) + log₂(1 + Capital Ratio) + log₂(1 + Liquidity)
    
    This value represents the maximum uncertainty absorption capacity
    of the system before collapsing.

    Args:
        stock_ratio (float): Safety Stock Ratio (e.g., inventory days).
        capital_ratio (float): Working Capital Ratio (e.g., financial survival days).
        liquidity (float): Liquidity Ratio.
        
    Returns:
        float: The value of Theta_max in bits.
    """
    if not all(isinstance(i, (int, float)) and i >= 0 for i in [stock_ratio, capital_ratio, liquidity]):
        raise ValueError("All ratios must be non-negative numbers.")
        
    term_stock = math.log2(1 + stock_ratio)
    term_capital = math.log2(1 + capital_ratio)
    term_liquidity = math.log2(1 + liquidity)
    
    return term_stock + term_capital + term_liquidity

def run_simulation(I: float, K: float, theta_max: float, runs: int = 500, time_steps: int = 52, alpha: float = 0.15):
    """
    Runs a Monte Carlo simulation of entropy debt accumulation.
    
    ⚠️ IMPROVED FOR RELIABILITY:
    - runs increased to 500 for robust statistics
    - alpha improved to 0.15 for more realistic dissipation
    - Normal distribution for more realistic disturbances

    Args:
        I (float): Average Input Entropy.
        K (float): Average Response Capacity.
        theta_max (float): Collapse threshold in bits.
        runs (int): Number of iterations (complete simulations) to run.
        time_steps (int): Time steps (e.g., weeks) in each simulation.
        alpha (float): Rate of debt dissipation when K > I.

    Returns:
        dict: A dictionary with numerical results, including 'collapse_rate',
              'average_collapse_time', 'informational_insolvency' and 'residual_entropy_debt'.
    """
    if not all(isinstance(i, (int, float)) and i >= 0 for i in [I, K, theta_max, runs, time_steps, alpha]):
        raise ValueError("All input parameters must be non-negative numbers.")

    import statistics
    collapses = 0
    collapse_times_list = []
    ratios_list = []
    residual_debts = []
    
    # Realistic volatility
    volatility_i = 0.4  # 40% volatility (real markets)
    volatility_k = 0.08  # 8% volatility (more stable operations)

    for _ in range(runs):
        trajectory = [] if _ == runs - 1 else None
        entropy_debt = 0.0
        run_ratios = []
        collapsed = False
        for t in range(1, time_steps + 1):
            # Use normal distribution instead of uniform (more realistic)
            input_entropy = random.gauss(I, I * volatility_i)
            response_capacity = random.gauss(K, K * volatility_k)
            
            # Ensure values are not negative
            input_entropy = max(0.01, input_entropy)
            response_capacity = max(0.01, response_capacity)

            # I/K Ratio (instantaneous Informational Insolvency)
            ratio = input_entropy / response_capacity if response_capacity > 0 else float('inf')
            run_ratios.append(ratio)
            
            # Dynamic equation: If I > K chronically, collapse is inevitable.
            # Increasing K (if still < I) only reduces the accumulation speed.
            if ratio > 1.0:  # Overloaded system (Ashby's Law violation)
                # Non-linear accumulation: damage grows exponentially with the ratio
                accumulation = (input_entropy - response_capacity) * (1 + (ratio - 1) ** 0.5)
            else:
                accumulation = 0
            
            dissipation = alpha * max(0, response_capacity - input_entropy)
            entropy_debt = max(0, entropy_debt + accumulation - dissipation)

            if trajectory is not None:
                trajectory.append(entropy_debt)

            # Check if the system collapses
            if entropy_debt >= theta_max:
                collapses += 1
                collapse_times_list.append(t)
                residual_debts.append(entropy_debt)
                collapsed = True
                break
        
        if not collapsed:
            residual_debts.append(entropy_debt)
        
        if run_ratios:
            ratios_list.append(statistics.mean(run_ratios))
    
    collapse_rate = collapses / runs if runs > 0 else 0
    average_collapse_time = statistics.mean(collapse_times_list) if collapse_times_list else float('inf')
    avg_insolvency = statistics.mean(ratios_list) if ratios_list else (I / K if K > 0 else float('inf'))
    avg_residual_debt = statistics.mean(residual_debts) if residual_debts else 0.0

    return {
        "collapse_rate": collapse_rate,
        "average_collapse_time": average_collapse_time,
        "informational_insolvency": avg_insolvency,
        "residual_entropy_debt": avg_residual_debt,
        "total_collapses": collapses,
        "runs": runs,
        "trajectory": trajectory if trajectory else []
    }

if __name__ == '__main__':
    # --- Example of simulation usage ---

    # Scenario 1: "Fragile" System (Just-In-Time)
    # Low shock absorption capacity.
    theta_max_fragile = calculate_collapse_threshold(
        stock_ratio=0.5,
        capital_ratio=1.0,
        liquidity=0.2
    )
    # The environment's entropy (I) is greater than the response capacity (K).
    fragile_results = run_simulation(
        I=1.5,
        K=1.0,
        theta_max=theta_max_fragile,
        runs=1000  # More runs for a more robust statistical result
    )
    print("--- Fragile Scenario (JIT) ---")
    print(f"Collapse Threshold (θ_max): {theta_max_fragile:.2f} bits")
    print(f"Collapse Rate: {fragile_results['collapse_rate']:.2%}")
    print(f"Average Collapse Time: {fragile_results['average_collapse_time']:.2f} weeks")
    print(f"Informational Insolvency (I/K): {fragile_results['informational_insolvency']:.2f}")
    print(f"Residual Entropy Debt: {fragile_results['residual_entropy_debt']:.2f}")
    print("-" * 30)

    # Scenario 2: "Resilient" System
    # High absorption capacity (large buffers).
    theta_max_resilient = calculate_collapse_threshold(
        stock_ratio=5.0,
        capital_ratio=10.0,
        liquidity=4.0
    )
    # The response capacity (K) is significantly greater than the environment's entropy (I).
    resilient_results = run_simulation(
        I=1.5,
        K=2.5,
        theta_max=theta_max_resilient,
        runs=1000
    )
    print("--- Resilient Scenario ---")
    print(f"Collapse Threshold (θ_max): {theta_max_resilient:.2f} bits")
    print(f"Collapse Rate: {resilient_results['collapse_rate']:.2%}")
    print(f"Average Collapse Time: {resilient_results['average_collapse_time']:.2f} weeks")
    print(f"Informational Insolvency (I/K): {resilient_results['informational_insolvency']:.2f}")
    print(f"Residual Entropy Debt: {resilient_results['residual_entropy_debt']:.2f}")
    print("-" * 30)
