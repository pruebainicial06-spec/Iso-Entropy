# telemetry.py
from typing import List, Dict, Optional


def build_llm_signal(experiment_log: List[Dict]) -> Dict:
    """
    Builds a summary signal for the LLM (Context Pruning).
    Summarizes the full history into key statistics to avoid context overload.
    Handles compressed states.
    """

    if not experiment_log:
        return {
            "experiments": 0,
            "trend": "none"
        }

    # Check if compressed
    if len(experiment_log) == 1 and experiment_log[0].get("compressed"):
        summary = experiment_log[0]["summary"]
        if isinstance(summary, dict):
            return {
                "experiments": "compressed",
                "compressed_summary": summary.get("executive_summary", "Compressed"),
                "entropy_debt": summary.get("accumulated_entropy_debt", 0.0),
                "system_uncertainty": summary.get("system_uncertainty", 0.0),
                "current_state": summary.get("current_state", "Unknown"),
                "trends": summary.get("trends", "N/A"),
                "recommendations": summary.get("recommendations", "N/A")
            }
        else:
            return {
                "experiments": "compressed",
                "compressed_summary": str(summary)
            }

    # Filter invalid entries (no result or no hypothesis)
    valid_experiments = [
        exp for exp in experiment_log 
        if exp.get("result") and exp.get("hypothesis")
    ]
    
    if not valid_experiments:
        return {
            "experiments": len(experiment_log),
            "min_collapse_rate": 0.0,
            "max_collapse_rate": 0.0,
            "avg_collapse_rate": 0.0,
            "last_collapse_rate": 0.0,
            "last_K": 0.0,
            "k_range": "0.00 - 0.00",
            "theta_max_range": "0.00 - 0.00",
            "entropy_debt_accumulated": 0.0,
            "last_theta_max": 0.0,
            "overall_trend": "none"
        }
    
    # Extract collapse rates with defensive validation
    collapse_rates = [
        exp.get("result", {}).get("collapse_rate", 0.0) 
        for exp in valid_experiments
    ]
    k_values = [
        exp.get("hypothesis", {}).get("K", 0.0) 
        for exp in valid_experiments
    ]
    theta_max_values = [
        exp.get("full_parameters", {}).get("theta_max", 0.0) 
        for exp in valid_experiments 
        if exp.get("full_parameters")
    ]
    
    # Calculate accumulated entropy debt (undissipated I - K)
    entropy_debt = 0.0
    for exp in valid_experiments:
        I = exp.get("hypothesis", {}).get("I", 0.0)
        K = exp.get("hypothesis", {}).get("K", 0.0)
        collapse_rate = exp.get("result", {}).get("collapse_rate", 0.0)
        if I > K:
            entropy_debt += (I - K) * collapse_rate  # Weighted by collapse probability

    # Summary statistics
    signal = {
        "experiments": len(valid_experiments),
        "min_collapse_rate": min(collapse_rates),
        "max_collapse_rate": max(collapse_rates),
        "avg_collapse_rate": sum(collapse_rates) / len(collapse_rates),
        "last_collapse_rate": collapse_rates[-1],
        "last_K": k_values[-1],
        "k_range": f"{min(k_values):.2f} - {max(k_values):.2f}",
        "theta_max_range": f"{min(theta_max_values) if theta_max_values else 0.0:.2f} - {max(theta_max_values) if theta_max_values else 0.0:.2f}",
        "entropy_debt_accumulated": entropy_debt,
        "last_theta_max": theta_max_values[-1] if theta_max_values else 0.0
    }

    # Overall trend
    if len(collapse_rates) >= 2:
        first_half = collapse_rates[:len(collapse_rates)//2]
        second_half = collapse_rates[len(collapse_rates)//2:]
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        delta = avg_first - avg_second
        signal["overall_trend"] = (
            "improving" if delta > 0.01
            else "worsening" if delta < -0.01
            else "stable"
        )

    return signal
