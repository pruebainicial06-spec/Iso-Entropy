import math
import random

def calculate_collapse_threshold(stock_ratio: float, capital_ratio: float, liquidity: float) -> float:
    """
    Calcula el Umbral de Colapso (Theta_max) usando la fórmula logarítmica.
    θ_max = log₂(1 + Ratio Stock) + log₂(1 + Ratio Capital) + log₂(1 + Liquidez)
    
    Este valor representa la capacidad máxima de absorción de incertidumbre
    del sistema antes de colapsar.

    Args:
        stock_ratio (float): Ratio de Stock de Seguridad (ej. días de inventario).
        capital_ratio (float): Ratio de Capital de Trabajo (ej. días de supervivencia financiera).
        liquidity (float): Ratio de Liquidez.
        
    Returns:
        float: El valor de Theta_max en bits.
    """
    if not all(isinstance(i, (int, float)) and i >= 0 for i in [stock_ratio, capital_ratio, liquidity]):
        raise ValueError("Todos los ratios deben ser números no negativos.")
        
    term_stock = math.log2(1 + stock_ratio)
    term_capital = math.log2(1 + capital_ratio)
    term_liquidity = math.log2(1 + liquidity)
    
    return term_stock + term_capital + term_liquidity

def run_simulation(I: float, K: float, theta_max: float, runs: int = 500, time_steps: int = 52, alpha: float = 0.15):
    """
    Ejecuta una simulación Monte Carlo de acumulación de deuda de entropía.
    
    ⚠️ MEJORADO PARA FIABILIDAD:
    - runs aumentado a 500 para estadística robusta
    - alpha mejorado a 0.15 para disipación más realista
    - Distribución normal para perturbaciones más realistas

    Args:
        I (float): Entropía de Entrada promedio.
        K (float): Capacidad de Respuesta promedio.
        theta_max (float): Umbral de colapso en bits.
        runs (int): Número de iteraciones (simulaciones completas) a ejecutar.
        time_steps (int): Pasos de tiempo (e.g., semanas) en cada simulación.
        alpha (float): Tasa de disipación de la deuda cuando K > I.

    Returns:
        dict: Un diccionario con resultados numéricos, incluyendo 'tasa_de_colapso'
              y 'tiempo_promedio_colapso'.
    """
    if not all(isinstance(i, (int, float)) and i >= 0 for i in [I, K, theta_max, runs, time_steps, alpha]):
        raise ValueError("Todos los parámetros de entrada deben ser números no negativos.")

    collapses = 0
    total_collapse_time = 0
    collapse_times_list = []
    
    # Volatilidad realista
    volatility_i = 0.4  # 40% de volatilidad (mercados reales)
    volatility_k = 0.08  # 8% de volatilidad (operaciones más estables)

    for _ in range(runs):
        entropy_debt = 0.0
        for t in range(1, time_steps + 1):
            # Usar distribución normal en lugar de uniforme (más realista)
            # Normal distribution centrada en I y K con desviación estándar proporcional
            import statistics
            input_entropy = random.gauss(I, I * volatility_i)
            response_capacity = random.gauss(K, K * volatility_k)
            
            # Asegurar que los valores no sean negativos
            input_entropy = max(0.01, input_entropy)  # Min 0.01 para evitar valores nulos
            response_capacity = max(0.01, response_capacity)

            # Ecuación dinámica mejorada de la Deuda de Entropía
            # Considera la relación I/K explícitamente
            ratio = input_entropy / response_capacity if response_capacity > 0 else float('inf')
            
            if ratio > 1.0:  # Sistema sobrecargado
                accumulation = (input_entropy - response_capacity) * (1 + (ratio - 1) ** 0.5)  # Acumulación no-lineal
            else:
                accumulation = max(0, input_entropy - response_capacity)
            
            dissipation = alpha * max(0, response_capacity - input_entropy)
            entropy_debt = max(0, entropy_debt + accumulation - dissipation)

            # Comprobar si el sistema colapsa
            if entropy_debt >= theta_max:
                collapses += 1
                total_collapse_time += t
                collapse_times_list.append(t)
                break  # Termina esta simulación y pasa a la siguiente
    
    collapse_rate = collapses / runs if runs > 0 else 0
    # El tiempo promedio se calcula solo sobre las simulaciones que colapsaron
    average_collapse_time = statistics.mean(collapse_times_list) if collapse_times_list else float('inf')

    return {
        "tasa_de_colapso": collapse_rate,
        "tiempo_promedio_colapso": average_collapse_time,
        "collapses_total": collapses,
        "runs": runs
    }

if __name__ == '__main__':
    # --- Ejemplo de uso de la simulación ---

    # Escenario 1: Sistema "Frágil" (Just-In-Time)
    # Poca capacidad de absorción de shocks.
    theta_max_fragil = calculate_collapse_threshold(
        stock_ratio=0.5,
        capital_ratio=1.0,
        liquidity=0.2
    )
    # La entropía del entorno (I) es mayor que la capacidad de respuesta (K).
    resultados_fragil = run_simulation(
        I=1.5,
        K=1.0,
        theta_max=theta_max_fragil,
        runs=1000  # Más runs para un resultado estadístico más robusto
    )
    print("--- Escenario Frágil (JIT) ---")
    print(f"Umbral de Colapso (θ_max): {theta_max_fragil:.2f} bits")
    print(f"Tasa de Colapso: {resultados_fragil['tasa_de_colapso']:.2%}")
    print(f"Tiempo Promedio de Colapso: {resultados_fragil['tiempo_promedio_colapso']:.2f} semanas")
    print("-" * 30)

    # Escenario 2: Sistema "Resiliente"
    # Alta capacidad de absorción (buffers grandes).
    theta_max_resiliente = calculate_collapse_threshold(
        stock_ratio=5.0,
        capital_ratio=10.0,
        liquidity=4.0
    )
    # La capacidad de respuesta (K) es significativamente mayor que la entropía del entorno (I).
    resultados_resiliente = run_simulation(
        I=1.5,
        K=2.5,
        theta_max=theta_max_resiliente,
        runs=1000
    )
    print("--- Escenario Resiliente ---")
    print(f"Umbral de Colapso (θ_max): {theta_max_resiliente:.2f} bits")
    print(f"Tasa de Colapso: {resultados_resiliente['tasa_de_colapso']:.2%}")
    print(f"Tiempo Promedio de Colapso: {resultados_resiliente['tiempo_promedio_colapso']:.2f} semanas")
    print("-" * 30)