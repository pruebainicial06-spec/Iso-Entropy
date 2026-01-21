# grounding.py
# ============================================
# COMPONENT 2 — Physical Grounding
# Converts structured human inputs
# into canonical physical variables.
# ============================================

from typing import Dict


def clamp(value: float, min_v: float, max_v: float) -> float:
    return max(min_v, min(max_v, value))


def ground_inputs(volatility: str, rigidity: str, buffer_months: int) -> Dict[str, float]:
    """
    Deterministic physical grounding.
    CALIBRATED FOR DEMO: Values adjusted to generate narrative tension.
    """

    # 1. EXTERNAL ENTROPY (I) - The "Chaos"
    # High = 5.0 (Dangerous but survivable if the agent is smart)
    volatility_map = {
        "Low (Stable)": 0.6,
        "Medium (Seasonal)": 1.5,
        "High (Chaotic)": 5.0
    }
    # If key not found, default to 5.0
    I = volatility_map.get(volatility, 5.0)

    # 2. INITIAL CAPACITY (K0) - The "Response"
    # High Rigidity = Low K (0.8). Ratio I/K = 5.0/0.8 = 6.25 (CRITICAL)
    rigidity_map = {
        "Low (Automated)": 3.0,
        "Medium (Standard)": 1.5,
        "High (Manual/Bureaucratic)": 0.8
    }
    K0 = rigidity_map.get(rigidity, 0.8)

    # 3. PHYSICAL BUFFER (STOCK)
    # Normalize months to a ratio (e.g., 6 months = 0.25)
    stock = clamp(buffer_months / 24.0, 0.05, 1.0)

    # 4. LIQUIDITY (Friction)
    # High rigidity often implies low operational liquidity
    if "High" in rigidity:
        liquidity = 0.3
    elif "Medium" in rigidity:
        liquidity = 0.6
    else:
        liquidity = 0.9

    # 5. CAPITAL (Base value)
    capital = 1.0

    return {
        "I": I,
        "K0": K0,
        "stock": stock,
        "liquidity": liquidity,
        "capital": capital
    }