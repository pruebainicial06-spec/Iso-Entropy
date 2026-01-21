# constraints.py - FIXED
"""
Hard Rules & Physical Constraints
=================================

CRITICAL CHANGE: No longer throws an exception for I > 1.5*K.
That is exactly the type of system the agent should DIAGNOSE,
not reject.

Instead:
- Warning log
- "Critical situation" flag
- Let the agent try (or determine it's unrecoverable)
"""

from typing import Dict


class HardConstraintViolation(Exception):
    """Critical physics error: the system cannot operate."""
    pass


def apply_hard_rules(
    *,
    volatility: str,
    rigidity: str,
    buffer_months: int,
    params: Dict[str, float]
) -> Dict[str, float]:
    """
    Applies physical rules BUT ALLOWS CRITICAL SYSTEMS.

    - Adjusts invalid parameters
    - MARKS critical situation (does not throw an exception)
    - Let the agent diagnose
    """

    I = params.get("I", 1.0)
    K = params.get("K", 1.0)
    liquidity = params.get("liquidity", 0.5)

    adjustments = []
    warnings = []

    # ------------------------------------------------------------------
    # 1️⃣ MINIMUM ENTROPY ACCORDING TO VOLATILITY
    # ------------------------------------------------------------------
    if volatility == "High (Chaotic)":
        if I < 4.5:
            I = 4.5
            adjustments.append("I adjusted to physical minimum (4.5) for high volatility")

    elif volatility == "Medium (Seasonal)":
        if I < 1.0:
            I = 1.0
            adjustments.append("I adjusted to physical minimum (1.0) for medium volatility")

    elif volatility == "Low (Stable)":
        if I < 0.5:
            I = 0.5
            adjustments.append("I adjusted to physical minimum (0.5) for low volatility")

    # ------------------------------------------------------------------
    # 2️⃣ INITIAL CAPACITY ACCORDING TO RIGIDITY
    # ------------------------------------------------------------------
    if rigidity == "High (Manual/Bureaucratic)":
        if K > 3.0:
            K = 3.0
            adjustments.append("K limited to 3.0 for manual/bureaucratic rigidity")

    # ------------------------------------------------------------------
    # 3️⃣ LOW LIQUIDITY → MORE AGGRESSIVE K GROWTH
    # ------------------------------------------------------------------
    if liquidity < 0.5:
        params["low_liquidity_penalty"] = True
        warnings.append("⚠️ Low liquidity: K adjustments will be less effective")

    # ------------------------------------------------------------------
    # 4️⃣ CRITICALITY DETECTION (but allow)
    # ------------------------------------------------------------------
    # CHANGE: Instead of throwing an exception, we mark and warn
    if I > K * 2.0:
        warnings.append(
            f"⚠️ STRUCTURAL CRITICALITY: I ({I:.2f}) >> 2.0 × K ({K:.2f}). "
            "The system is at extreme risk. The agent will attempt to diagnose."
        )
        params["critical_structural_warning"] = True
    
    elif I > K * 1.5:
        warnings.append(
            f"⚠️ MARGINAL SITUATION: I ({I:.2f}) > 1.5 × K ({K:.2f}). "
            "Fragile system. Requires urgent intervention."
        )
        params["marginal_situation"] = True

    # ------------------------------------------------------------------
    # 5️⃣ FINAL ABSOLUTE CLAMP
    # ------------------------------------------------------------------
    I = max(0.1, min(10.0, I))
    K = max(0.1, min(10.0, K))
    liquidity = max(0.0, min(1.0, liquidity))

    # ------------------------------------------------------------------
    # 6️⃣ ZERO DIVISION PREVENTION
    # ------------------------------------------------------------------
    if K == 0:
        K = 0.1
        warnings.append("K clamped to 0.1 to prevent zero division")

    params.update({
        "I": I,
        "K": K,
        "liquidity": liquidity,
        "adjustments": adjustments,
        "warnings": warnings
    })

    return params