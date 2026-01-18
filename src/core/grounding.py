# grounding.py
# ============================================
# COMPONENTE 2 — Grounding Físico
# Convierte inputs humanos estructurados
# en variables físicas canónicas.
# ============================================

from typing import Dict


def clamp(value: float, min_v: float, max_v: float) -> float:
    return max(min_v, min(max_v, value))


def ground_inputs(volatilidad, rigidez, colchon_meses):
    # 1. Mapeo de Volatilidad (Entropía de Entrada - I)
    # Ajustado para que "Alta" sea peligrosa pero no mortal instantánea
    volatilidad_map = {
        "Baja (Estable)": 0.6,
        "Media (Estacional)": 1.2,
        "Alta (Caótica)": 5.0  # ANTES ERA 10.0 (Demasiado alto)
    }
    # Si no encuentra la clave, usa 5.0 por defecto
    I = volatilidad_map.get(volatilidad, 5.0)

    # 2. Mapeo de Rigidez (Capacidad Inicial - K0)
    # Baja rigidez = Alta capacidad de respuesta
    rigidez_map = {
        "Baja (Automatizada)": 2.5,
        "Media (Estándar)": 1.5,
        "Alta (Manual/Burocrático)": 0.8
    }
    K0 = rigidez_map.get(rigidez, 0.8)

    # 3. Buffer Físico (Stock)
    # Normalizamos meses a un ratio (ej: 6 meses = 0.25)
    stock = max(0.05, min(1.0, colchon_meses / 24.0))

    # 4. Liquidez (Inversa a la rigidez para este modelo)
    # Baja rigidez suele implicar mejor flujo de liquidez operativa
    liquidity = 0.8 if "Baja" in rigidez else (0.5 if "Media" in rigidez else 0.2)

    # 5. Capital (Valor base)
    capital = 1.0

    return {
        "I": I,
        "K0": K0,
        "stock": stock,
        "liquidity": liquidity,
        "capital": capital
    }
