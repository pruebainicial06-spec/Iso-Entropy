---

### REPORTE TÉCNICO DE INCIDENCIA: ANÁLISIS DE FALLO ESTRUCTURAL EN ISO-ENTROPY V2.3

#### 1. Resumen de la Crisis de Ejecución
El sistema **Iso-Entropy v2.3**, diseñado como un Agente Autónomo de Auditoría Forense basado en la arquitectura **Gemini 3**, está experimentando un fallo crítico de cascada. Este fallo se manifiesta en tres dimensiones: **agotamiento de cuota de API (Rate Limiting)**, **corrupción de la integridad de datos en el historial de experimentos (KeyError)** y **fallo en la extracción de razonamiento latente (Thinking Process)**. A pesar de los intentos previos de mitigación mediante retardos (`time.sleep`), el agente opera a una velocidad de procesamiento que desincroniza el estado de la interfaz de usuario (Streamlit) con las capacidades reales del Tier gratuito de Gemini 3 Flash.

#### 2. Dimensión 1: El Cuello de Botella del Rate Limit (RPM)
El núcleo del problema reside en el límite de frecuencia de la API de **Gemini 3 Flash**. Según los logs de AI Studio, el modelo tiene un límite estricto de **5 Solicitudes por Minuto (RPM)**. La lógica actual del agente es "agéntica", lo que significa que el bucle de razonamiento intenta iterar rápidamente entre las fases de `ORIENT`, `VALIDATE` y `STRESS` para encontrar el punto de equilibrio de entropía. 

En un escenario de éxito (como el caso LEGO), el agente requiere al menos 5 o 6 interacciones para concluir. Debido a la baja latencia de respuesta de Gemini 3 Flash, estas 6 peticiones ocurren en menos de 45 segundos. Al intentar disparar la sexta petición (usualmente el reporte final en la fase `CONCLUDE`), la API devuelve un error `429: Too Many Requests`. El sistema no tiene una lógica de "Backoff" o de gestión de colas, lo que resulta en una terminación abrupta del proceso de auditoría antes de generar valor para el usuario.

#### 3. Dimensión 2: Corrupción de la Memoria Episódica y Colapso de UI (KeyError)
El error más visible para el usuario es el `❌ Error Crítico: 'resultado'`. Este es un fallo de **Integridad de Datos** en la estructura del `experiment_log`. 
- **Mecánica del fallo:** El historial de experimentos (`experiment_log`) es una lista de diccionarios. El código de la interfaz en `app.py` y la lógica de señales en `telemetry.py` asumen que cada entrada en esta lista es un experimento exitoso que contiene la clave `resultado` (la cual guarda los datos de la simulación Monte Carlo).
- **Inyección de basura:** Cuando la API de Gemini falla por Rate Limit o por error de red, el agente añade una entrada incompleta o nula al log, o simplemente detiene la ejecución dejando el log en un estado inconsistente. 
- **Fallo de Indexación:** Al final de la ejecución, Streamlit intenta renderizar métricas y gráficas recorriendo el `experiment_log`. Al encontrar una entrada donde la clave `resultado` no existe (porque la simulación nunca se disparó debido al error previo de la IA), Python lanza un `KeyError`. El código actual no es defensivo; no valida la existencia de la data antes de intentar procesarla, lo que bloquea toda la visualización de resultados.

#### 4. Dimensión 3: Fallo en la Capacidad de "Thinking" (SDK v1.0 Mismatch)
Uno de los pilares del Hackathon es el uso de **Thought Signatures** y **Thinking Level**. En los logs actuales, la sección "Gemini Thinking" muestra el valor booleano `True` en lugar del texto del razonamiento.
- **Causa Raíz:** Existe una desconexión entre la configuración de generación y la extracción de partes del mensaje. En el nuevo SDK de Gemini 3, la respuesta no es un string simple, sino una estructura de candidatos con múltiples partes. 
- **Objeto vs. Atributo:** El código está capturando el atributo de configuración (`include_thoughts=True`) o interpretando erróneamente el objeto `thought` del SDK como un booleano. La documentación de Gemini 3 especifica que el "pensamiento" es una parte del contenido (`part.thought`) que debe ser iterada y extraída como texto. Al fallar esta extracción, el usuario pierde la visibilidad del "Cerebro" del agente, reduciendo la innovación del proyecto a una simple llamada de texto tradicional.

#### 5. Dimensión 4: Calibración Física y Agresividad del Agente
Existe una discrepancia entre la **Física del Mundo** y la **Inteligencia del Agente**. 
- **Letalidad del Escenario:** En configuraciones de alta volatilidad, el valor de entropía ($I$) es tan alto que la simulación Monte Carlo arroja un colapso del 100% en todos los casos. 
- **Estancamiento del Agente:** El agente actual no tiene la "agresividad" necesaria para proponer saltos grandes en la capacidad ($K$). Si el sistema colapsa al 100%, el agente intenta subir $K$ en incrementos mínimos (ej. $+0.5$). Al ver que sigue colapsando, la FSM (Máquina de Estados) decide que no hay solución y termina. 
- **El Resultado:** En lugar de una auditoría profunda de 10 ciclos, obtenemos una "muerte súbita" en 3 ciclos, lo cual no cumple el objetivo de mostrar una evolución de la resiliencia en la demo del Hackathon.

#### 6. Conclusión del Problema
El sistema **Iso-Entropy** está "ahogado" por su propia velocidad y por una arquitectura de datos frágil. Para que funcione, necesita una reingeniería que lo haga **respetuoso de los tiempos de la API**, **defensivo ante la ausencia de datos** y **capaz de extraer el razonamiento profundo** que Gemini 3 está generando pero que el código actual es incapaz de mostrar.


---

### BASE DE CONOCIMIENTO: DOCUMENTACIÓN OFICIAL Y ESPECIFICACIONES DE GEMINI 3

#### 1. Arquitectura Central y Modelos
Este módulo define la naturaleza del modelo utilizado en el Hackathon. Es vital para que Claude entienda que estamos operando en la frontera de los modelos de razonamiento (Reasoning Models).

*   **Gemini 3 Overview:** https://ai.google.dev/gemini-api/docs/gemini-3
    *   *Uso:* Define las capacidades nativas de Gemini 3 Flash, incluyendo el procesamiento de razonamiento multietapa y la optimización de latencia.
*   **Migrating to Gemini 3:** https://ai.google.dev/gemini-api/docs/migrating_from_other_models
    *   *Uso:* Crucial para entender cambios en los esquemas de respuesta de candidatos y partes del mensaje respecto a Gemini 1.5 o 2.0.

#### 2. Capacidades de Razonamiento (Thinking & Reasoning)
Este es el punto de fallo actual (el error del booleano "True"). Estas URLs contienen la estructura exacta que el código debe navegar para extraer los pensamientos del modelo.

*   **Thinking Documentation:** https://ai.google.dev/gemini-api/docs/thinking
    *   *Uso:* Explica el parámetro `include_thoughts` dentro de `GenerateContentConfig`. Define que el razonamiento ocurre "antes" de la respuesta final.
*   **Thought Signatures:** https://ai.google.dev/gemini-api/docs/thought-signatures
    *   *Uso:* Detalla la firma criptográfica y la estructura de datos del objeto `thought`. Es la fuente definitiva para corregir el acceso a `part.thought` o `part.text` dentro de un candidato de respuesta.
*   **Thinking Level API:** https://ai.google.dev/gemini-api/docs/gemini-3#thinking_level
    *   *Uso:* Especifica los niveles (`low`, `medium`, `high`) para controlar la profundidad del razonamiento analítico.

#### 3. Configuración de Generación y Salidas Estructuradas
Para evitar el `KeyError: 'resultado'`, el sistema debe garantizar que Gemini devuelva JSON válido y que el SDK lo parsee correctamente.

*   **Text Generation Guide:** https://ai.google.dev/gemini-api/docs/text-generation
    *   *Uso:* Referencia general sobre cómo configurar `temperature`, `top_p` y `max_output_tokens` en el nuevo SDK.
*   **Structured Outputs with Tools:** https://ai.google.dev/gemini-api/docs/gemini-3#structured_outputs_with_tools
    *   *Uso:* Cómo forzar al modelo a seguir un esquema JSON estricto sin preámbulos de texto que rompan el parseo en Python.
*   **JSON Mode & Schema:** https://ai.google.dev/gemini-api/docs/text-generation#json
    *   *Uso:* Instrucciones para el parámetro `response_mime_type: "application/json"`.

#### 4. Límites de Frecuencia y Gestión de Cuotas (Rate Limits)
Este módulo es la base para resolver el error `6 / 5 RPM`. Define la "paciencia" que el código debe tener.

*   **Rate Limits Official Table:** https://ai.google.dev/gemini-api/docs/rate-limits
    *   *Uso:* Confirma que Gemini 3 Flash tiene un límite de **5 RPM** y **2,000 RPD** (Requests Per Day) en el tier gratuito. Claude debe usar esta información para implementar una lógica de `sleep` o un "Rate Limiter" preventivo.

#### 5. Capacidades Avanzadas de Agente (Tool Use)
Iso-Entropy aspira a ser un agente autónomo. Estas URLs describen cómo Gemini puede llamar a las funciones de `physics.py`.

*   **Function Calling Guide:** https://ai.google.dev/gemini-api/docs/function-calling
    *   *Uso:* Cómo registrar funciones de Python como herramientas (`tools`) para que Gemini las llame directamente en lugar de "sugerir" parámetros.
*   **Parallel Function Calling:** https://ai.google.dev/gemini-api/docs/gemini-3#parallel-function
    *   *Uso:* Describe cómo Gemini 3 puede ejecutar múltiples simulaciones Monte Carlo en una sola llamada si el escenario lo requiere.
*   **Multi-step Reasoning:** https://ai.google.dev/gemini-api/docs/gemini-3#multi-step
    *   *Uso:* Explica el proceso de bucle interno del modelo para tareas complejas como la auditoría forense.

#### 6. Herramientas de Desarrollo y SDK
Referencia para la sintaxis exacta de las librerías instaladas en `requirements.txt`.

*   **Python SDK Reference (google-genai):** https://github.com/google/generative-ai-python
    *   *Uso:* Claude debe indexar esta repo para conocer los nombres de las clases (`types.GenerateContentConfig`, `types.ThinkingConfig`) que han cambiado en la v1.0.
*   **Batch API (Optimización de Costos/Límites):** https://ai.google.dev/gemini-api/docs/batch-api
    *   *Uso:* Alternativa si se requiere procesar múltiples escenarios históricos sin chocar con el límite de RPM de tiempo real.

---

#### Nota Técnica para la Indexación de Claude:
Pon especial atención a la estructura del objeto **Candidate**. En Gemini 3, el pensamiento (`thought`) reside en una parte del contenido que es distinta a la parte del texto final. El código actual falla porque intenta tratar el objeto completo como un booleano o no itera correctamente sobre la lista de `parts`. 

Debes notar que la latencia de Gemini 3 Flash es significativamente menor que la de Pro, lo que hace que los 12-15 segundos de espera entre peticiones sean **críticos y no opcionales** para la estabilidad del sistema.

---

### ESTATUTO DE OBJETIVOS ESTRATÉGICOS: ISO-ENTROPY V2.3 (AGENTIC FORENSIC AUDITOR)

#### 1. Visión de Éxito: La Auditoría de "Caja de Cristal"
El objetivo supremo de Iso-Entropy es transformar la auditoría de riesgos de una "opinión subjetiva" a una "auditoría científica transparente". El sistema no debe comportarse como un oráculo que da respuestas, sino como un **Agente Científico** que demuestra su proceso de razonamiento. El éxito se define cuando un usuario técnico puede abrir el log de telemetría y entender la cadena lógica que llevó de un bit de entropía a una recomendación de inversión millonaria.

#### 2. Objetivo de Integridad: Grounding Físico-Semántico Bidireccional
El sistema debe alcanzar una sincronización perfecta entre dos mundos que normalmente están desconectados:
*   **De la Historia a la Física:** El agente debe ser capaz de traducir una descripción narrativa (ej. "huelgas sindicales") en un valor numérico de Entropía Externa ($I$) fundamentado en la realidad de ese mercado.
*   **De la Física a la Estrategia:** El agente debe traducir los resultados de una simulación de Monte Carlo (ej. "tasa de colapso 22%") en consecuencias de negocio específicas para el contexto del usuario (ej. "riesgo de pérdida de contratos con el sector público por incumplimiento de plazos").
*   **Métrica de éxito:** Los resultados de la auditoría deben variar de forma coherente y sensible cuando el usuario altera los parámetros de entrada (Volatilidad, Rigidez, Colchón).

#### 3. Objetivo de Transparencia: Exposición del Razonamiento Latente (Thinking)
Aprovechando las capacidades nativas de **Gemini 3**, el sistema tiene como objetivo eliminar el misterio de la "IA como caja negra". 
*   **Thought Signatures:** El sistema debe extraer y mostrar el proceso de pensamiento (`thought`) generado por el modelo antes de cada decisión.
*   **Visibilidad de Intención:** El usuario debe ver en tiempo real cómo el agente planea el siguiente experimento (ej. "Voy a subir K a 1.5 para probar si la automatización compensa el caos climático detectado").
*   **Métrica de éxito:** El 100% de los ciclos de pensamiento deben mostrar el razonamiento interno en la interfaz de usuario, diferenciándolo claramente de la respuesta final estructurada.

#### 4. Objetivo de Estabilidad: Autorregulación Agéntica (Tier Management)
Dado que el sistema opera en un entorno de recursos limitados (Free Tier/Preview de 5 RPM), el agente debe poseer conciencia de sus propios límites operativos.
*   **Homeostasis de Cuota:** El sistema debe gestionar su ritmo de ejecución para nunca exceder el límite de frecuencia de la API, garantizando que una auditoría compleja de 10 ciclos se complete sin errores de conexión.
*   **Persistencia de Memoria Episódica:** El historial de experimentos (`experiment_log`) debe mantenerse íntegro y libre de corrupción, incluso si una llamada individual a la API falla. El sistema debe ser capaz de recuperarse y presentar los datos parciales de forma defensiva.
*   **Métrica de éxito:** Lograr una tasa de finalización de auditoría del 100% en los escenarios de prueba LEGO, Blockbuster y AHMSA, sin disparar errores de `KeyError` o `RateLimit`.

#### 5. Objetivo de Análisis: Detección Temprana de Insolvencia Informacional
El sistema debe cumplir su promesa de valor: detectar el colapso **antes** de que los indicadores financieros tradicionales lo hagan.
*   **Análisis Forense Cuantitativo:** Identificar con precisión el punto crítico donde la Entropía ($I$) supera la Capacidad ($K$) de forma irreversible, consumiendo el colchón financiero ($\theta_{max}$).
*   **Mitigación Específica:** El reporte final (`CONCLUDE`) no debe dar consejos genéricos. Debe proponer acciones que alteren directamente la física del sistema: reducir $I$ (filtrado de ruido) o aumentar $K$ (procesamiento de variedad).
*   **Métrica de éxito:** El horizonte de supervivencia estimado en el reporte debe basarse matemáticamente en la tasa de acumulación de deuda de entropía observada en los ciclos de simulación.

#### 6. Objetivo de Innovación (Criterio Hackathon): Uso de Gemini 3 como Orquestador
El proyecto debe demostrar que Gemini 3 no es solo un motor de texto, sino el "Cerebro Central" de una arquitectura neuro-simbólica.
*   **Decisión de Parámetros:** Gemini 3 debe tener autonomía para decidir qué valores de $K$ probar, basándose en los resultados de los ciclos anteriores (Búsqueda Inteligente).
*   **Interpretación Multimodal de Datos:** El modelo debe analizar la tabla de experimentos como un todo, detectando patrones de fragilidad que un algoritmo estático pasaría por alto.
*   **Métrica de éxito:** El sistema debe demostrar que la intervención de Gemini 3 reduce la cantidad de iteraciones necesarias para encontrar la región estable del sistema en comparación con una búsqueda aleatoria.

#### 7. Resumen de Requerimientos para Claude/Cursor (Instrucción Final)
Al procesar el código, Claude debe priorizar la **robustez del dato** y la **claridad del pensamiento**. No se aceptarán soluciones que "truquen" los resultados. El código debe ser una implementación honesta de las Leyes de Ashby mediada por la inteligencia de Gemini 3. La interfaz debe ser digna de una herramienta de nivel ejecutivo (C-Level Suite), proyectando autoridad técnica y rigor científico.

---