# constraints.py
"""
Hard Rules & Physical Constraints
=================================

Este módulo implementa PRE-CONTROL.
Nada aquí es negociable por el LLM.
"""

from typing import Dict


class HardConstraintViolation(Exception):
    """Error crítico de física: el sistema no puede operar."""
    pass


def apply_hard_rules(
    *,
    volatilidad: str,
    rigidez: str,
    colchon_meses: int,
    params: Dict[str, float]
) -> Dict[str, float]:
    """
    Aplica reglas físicas absolutas ANTES del razonamiento del agente.

    - Ajusta parámetros inválidos
    - Detecta colapso inevitable
    - Nunca consulta al LLM
    """

    I = params.get("I", 1.0)
    K = params.get("K", 1.0)
    liquidity = params.get("liquidity", 0.5)

    adjustments = []

    # ------------------------------------------------------------------
    # 1️⃣ ENTROPÍA MÍNIMA SEGÚN VOLATILIDAD
    # ------------------------------------------------------------------
    if volatilidad == "Alta (Caótica)":
        if I < 4.5:
            I = 4.5
            adjustments.append("I ajustado a mínimo físico (4.5) por volatilidad alta")

    elif volatilidad == "Media (Estacional)":
        if I < 1.0:
            I = 1.0
            adjustments.append("I ajustado a mínimo físico (1.0) por volatilidad media")

    elif volatilidad == "Baja (Estable)":
        if I < 0.5:
            I = 0.5
            adjustments.append("I ajustado a mínimo físico (0.5) por volatilidad baja")

    # ------------------------------------------------------------------
    # 2️⃣ CAPACIDAD INICIAL SEGÚN RIGIDEZ
    # ------------------------------------------------------------------
    if rigidez == "Alta (Manual/Burocrático)":
        if K > 3.0:
            K = 3.0
            adjustments.append("K limitado a 3.0 por rigidez manual/burocrática")

    # ------------------------------------------------------------------
    # 3️⃣ LIQUIDEZ BAJA → CRECIMIENTO DE K MÁS AGRESIVO
    # ------------------------------------------------------------------
    if liquidity < 0.5:
        # No forzamos K aquí, pero marcamos penalización implícita
        params["low_liquidity_penalty"] = True

    # ------------------------------------------------------------------
    # 4️⃣ DETECCIÓN DE COLAPSO INEVITABLE
    # ------------------------------------------------------------------
    # Regla dura: si la entropía supera 1.5x la capacidad,
    # no hay régimen estable posible.
    if I > K * 1.5:
        raise HardConstraintViolation(
            f"Colapso inevitable: I ({I:.2f}) > 1.5 × K ({K:.2f})"
        )

    # ------------------------------------------------------------------
    # 5️⃣ CLAMP FINAL ABSOLUTO
    # ------------------------------------------------------------------
    I = max(0.1, min(10.0, I))
    K = max(0.1, min(10.0, K))
    liquidity = max(0.0, min(1.0, liquidity))

    params.update({
        "I": I,
        "K": K,
        "liquidity": liquidity,
        "adjustments": adjustments
    })

    return params
