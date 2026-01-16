# grounding.py
# ============================================
# COMPONENTE 2 — Grounding Físico
# Convierte inputs humanos estructurados
# en variables físicas canónicas.
# ============================================

from typing import Dict


def clamp(value: float, min_v: float, max_v: float) -> float:
    return max(min_v, min(max_v, value))


def ground_inputs(
    volatilidad: str,
    rigidez: str,
    colchon_meses: int
) -> Dict[str, float]:
    """
    Grounding físico determinista.
    
    INPUTS (desde UI, NO texto libre):
    - volatilidad: enum
    - rigidez: enum
    - colchon_meses: int

    OUTPUT:
    Estado físico base del sistema.
    """

    # -------------------------------
    # 1️⃣ ENTROPÍA EXTERNA (I)
    # Mapeo: Volatilidad UI → Valor físico
    # -------------------------------
    volatilidad_map = {
        "Baja (Estable)": 0.6,
        "Media (Estacional)": 1.2,
        "Alta (Caótica)": 4.5
    }
    if volatilidad not in volatilidad_map:
        raise ValueError(f"Volatilidad no reconocida: {volatilidad}. Opciones válidas: {list(volatilidad_map.keys())}")
    I = volatilidad_map[volatilidad]

    # -------------------------------
    # 2️⃣ FRICCIÓN ORGANIZACIONAL (Liquidez)
    # Mapeo: Rigidez UI → Valor físico
    # -------------------------------
    rigidez_map = {
        "Baja (Automatizada)": 0.85,
        "Media (Estándar)": 0.6,
        "Alta (Manual/Burocrático)": 0.4
    }
    if rigidez not in rigidez_map:
        raise ValueError(f"Rigidez no reconocida: {rigidez}. Opciones válidas: {list(rigidez_map.keys())}")
    liquidity = rigidez_map[rigidez]

    # -------------------------------
    # 3️⃣ BUFFER FÍSICO (STOCK)
    # Normalización lineal
    # -------------------------------
    stock = clamp(colchon_meses / 24.0, 0.05, 1.0)

    # -------------------------------
    # 4️⃣ CAPACIDAD INICIAL (K₀)
    # SIEMPRE sub-crítica
    # -------------------------------
    K0 = max(I * 0.6, 0.5)

    return {
        "I": I,
        "K0": K0,
        "stock": stock,
        "liquidity": liquidity
    }
