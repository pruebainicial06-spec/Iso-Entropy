# Copilot Instructions for ISO-ENTROPÍA

## Overview
ISO-ENTROPÍA es un sistema de auditoría científica para detectar fragilidad estructural en empresas, basado en termodinámica de información y simulación Monte Carlo. El código está organizado en capas inteligentes y sigue flujos de trabajo científicos y reproducibles.

## Arquitectura y Componentes Clave
- **src/core/**: Motor científico
  - `agent.py`: Orquestador autónomo, gestiona fases y lógica principal
  - `physics.py`: Simulación Monte Carlo (500 runs, distribución gaussiana, acumulación no-lineal)
  - `fsm.py`: Máquina de estados finitos (ORIENT, VALIDATE, STRESS, CONCLUDE)
  - `constraints.py`: Pre-control y validaciones duras
  - `grounding.py`: Traducción de inputs humanos a parámetros físicos
  - `telemetry.py`: Señales y métricas para LLM
  - `prompt_templates.py`: Prompts inteligentes por fase
- **src/ui/app.py**: Interfaz Streamlit para uso visual
- **docs/**: Documentación completa, guías rápidas y casos de uso
- **config/.env.example**: Plantilla de configuración de entorno

## Flujos de Trabajo Esenciales
- **Ejecución UI:**
  ```bash
  streamlit run src/ui/app.py
  ```
- **Ejecución directa:**
  ```python
  from src.core.agent import IsoEntropyAgent
  agent = IsoEntropyAgent(api_key="tu-api-key")
  report = agent.audit_system(...)
  ```
- **Modo Mock (sin API):**
  ```python
  agent = IsoEntropyAgent(is_mock_mode=True)
  report = agent.audit_system(...)
  ```
- **Configuración:**
  - Copia `.env.example` a `.env` y agrega tu `GEMINI_API_KEY`.
  - Variables clave: `GEMINI_API_KEY`, `ISO_MOCK_MODE`, `ISO_MAX_ITERATIONS`.

## Patrones y Convenciones Específicas
- **Fases FSM:** Cada fase tiene lógica y criterios de éxito claros (ver README y `fsm.py`).
- **Simulación:** 500 runs, precisión ±2%, distribución gaussiana, acumulación no-lineal.
- **Inputs UI:** Volatilidad, rigidez y colchón se traducen a parámetros físicos en `grounding.py`.
- **Prompts:** Definidos por fase en `prompt_templates.py`.
- **Testing:** Usa `is_mock_mode=True` para pruebas sin API externa.

## Ejemplos de Uso
- Ver [docs/examples/CASO_USO_INNOVASTORE.md] CASO_USO_INNOVASTORE.md para un flujo completo.
- Ver [docs/technical/README_V2_3.md] README_V2_3.md para detalles técnicos.

## Integraciones y Dependencias
- **Gemini 3 Flash API** (opcional, configurable por entorno)
- **Streamlit** para UI
- **Python 3.10+**
- Dependencias en `requirements.txt`

## Reglas para Agentes AI
- Mantén la lógica de fases y validaciones duras.
- No modifiques la estructura FSM sin actualizar prompts y criterios de éxito.
- Sincroniza cambios entre UI, grounding y physics para robustez.
- Documenta cualquier nuevo parámetro o flujo en la documentación técnica.

---
Para dudas, consulta la documentación en `docs/` o los ejemplos de uso.
