#app.py

import streamlit as st
import time
import sys
from io import StringIO
from contextlib import redirect_stdout

# Manejo de importación defensivo
try:
    import sys
    from pathlib import Path
    # Agregar directorio raíz al path
    root_dir = Path(__file__).parent.parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    from src.core.agent import IsoEntropyAgent
except ImportError as e:
    st.error(f"""
    ❌ **Error de Importación**
    
    No se pudo cargar `src.core.agent`. Verifica:
    - Estructura de directorio correcta
    - `pip install -r requirements.txt`
    - Ejecuta: streamlit run src/ui/app.py desde directorio raíz
    
    Error técnico: {e}
    """)
    st.stop()

def main():
    st.set_page_config(
        page_title="Iso-Entropy: Autonomous Auditor",
        page_icon="⚡",
        layout="wide"
    )
    
    # Header
    st.title("⚡ Iso-Entropy: Auditor de Resiliencia Autónomo")
    st.markdown("""
    **Powered by Gemini 3 Pro Preview (Agentic Reasoning)**
    
    Este NO es un chatbot. Es un **Agente Científico Autónomo** que diseña y ejecuta 
    experimentos de termodinámica para encontrar el punto de quiebre de tu sistema.
    
    > *"En la Era de la Acción, los agentes planifican y ejecutan sin supervisión humana."*
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración del Entorno")

        api_key = st.text_input(
            "Clave API de Gemini",
            type="password",
            help="Ingresa tu clave API de Google Gemini. Si no se proporciona, el agente funcionará en modo mock.",
            placeholder="AIzaSy..."
        )

        volatilidad = st.selectbox(
            "Volatilidad de Mercado (Entropía I)",
            ["Baja (Estable)", "Media (Estacional)", "Alta (Caótica)"],
            index=1
        )

        rigidez = st.selectbox(
            "Rigidez Operativa (Capacidad K)",
            ["Baja (Automatizada)", "Media (Estándar)", "Alta (Manual/Burocrático)"],
            index=2
        )

        colchon = st.slider(
            "Colchón Financiero (Meses)",
            min_value=1, max_value=24, value=6,
            help="Define el Umbral de Colapso (Theta_max)."
        )

        st.info("ℹ️ **Grounding:** Estos datos anclan al agente en la realidad física, evitando alucinaciones.")

        with st.expander("📚 Casos de Referencia"):
            st.markdown("""
            **Frágil (JIT):** Alta volatilidad + Alta rigidez + 2 meses → ~50% colapso

            **Resiliente:** Media volatilidad + Baja rigidez + 12 meses → ~2% colapso
            """)
    
    # Área principal
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1️⃣ Contexto del Sistema")
        user_input = st.text_area(
            "Describe tu operación:",
            height=150,
            placeholder="Ej: Startup logística con crecimiento explosivo. Procesos manuales, un solo proveedor crítico..."
        )
        
        start_btn = st.button("🚀 Iniciar Auditoría Autónoma", type="primary")
    
    # Ejecución
    if start_btn:
        if not user_input.strip():
            st.warning("⚠️ Por favor, describe tu empresa primero.")
            return
        
        # Inicializar agente
        logs_acumulados = []
        
        def capturar_log(mensaje):
            """Callback para logs en tiempo real."""
            logs_acumulados.append(mensaje)
        
        agent = IsoEntropyAgent(log_callback=capturar_log, api_key=api_key if api_key else None)
        
        # Área de visualización
        with col2:
            st.subheader("2️⃣ Cerebro del Agente (En Vivo)")
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_display = st.empty()
        
        # Contenedor para resultado
        resultado = {"reporte": None, "error": None, "completo": False}
        
        def ejecutar_agente():
            """Ejecuta el agente en background."""
            try:
                resultado["reporte"] = agent.audit_system(
                    user_input, volatilidad, colchon, rigidez
                )
            except Exception as e:
                resultado["error"] = str(e)
            finally:
                resultado["completo"] = True
        
        # Lanzar en thread
        import threading
        thread = threading.Thread(target=ejecutar_agente, daemon=True)
        thread.start()
        
        # Simulación de progreso + actualización de logs
        max_wait = 120  # 2 minutos máximo
        intervalo = 0.5  # Actualizar cada 0.5s
        iteraciones = int(max_wait / intervalo)
        
        for i in range(iteraciones):
            if resultado["completo"]:
                progress_bar.progress(100)
                status_text.success("✅ Auditoría completada")
                break
            
            # Actualizar progreso (estimación falsa pero tranquiliza al usuario)
            progreso = min(95, int((i / iteraciones) * 100))
            progress_bar.progress(progreso)
            
            # Actualizar logs si hay nuevos
            if logs_acumulados:
                log_display.code("\n".join(logs_acumulados), language="text")
            
            # Mostrar estado
            ciclo_actual = len([l for l in logs_acumulados if "CICLO" in l])
            status_text.info(f"🧠 Agente pensando... (Ciclo {ciclo_actual}/10 estimado)")
            
            time.sleep(intervalo)
        
        # Esperar a que termine
        thread.join(timeout=5)
        
        # Mostrar resultados
        if resultado["error"]:
            st.error(f"❌ **Error Crítico**\n\n{resultado['error']}")
        elif resultado["reporte"]:
            st.divider()
            st.subheader("3️⃣ Informe Forense Final")
            st.markdown(resultado["reporte"])

            # Indicador de Insolvencia Informacional
            if agent.experiment_log:
                ii_values = [exp.get("insolvencia_informacional", 0) for exp in agent.experiment_log if "insolvencia_informacional" in exp]
                if ii_values:
                    ii_avg = sum(ii_values) / len(ii_values)
                    estado = "Solvente" if ii_avg <= 1 else "Insolvente"
                    delta = "Estable" if ii_avg <= 1 else "Crítico"
                    st.metric(
                        label="Estado de Insolvencia Informacional (II)",
                        value=f"{estado} (II = {ii_avg:.2f})",
                        delta=delta
                    )
                    with st.expander("ℹ️ Explicación de la Ley de Ashby"):
                        st.markdown("""
                        **Ley de Ashby (Requisito de Variedad):** Un sistema debe tener al menos tanta variedad (capacidad K) como la variedad del entorno (entropía I) para ser viable.

                        - **II = I/K**: Si II ≤ 1, el sistema es solvente (puede absorber la entropía).
                        - **II > 1**: Insolvencia informacional - el sistema es insuficiente y acumula deuda entrópica.
                        """)

            # Indicador de Fragilidad
            if agent.experiment_log:
                ii_max = max([exp.get("insolvencia_informacional", 0) for exp in agent.experiment_log if "insolvencia_informacional" in exp] or [0])
                if ii_max > 1:
                    st.warning("🚨 **Sistema FRÁGIL**: Insolvencia informacional persistente detectada. El sistema acumula deuda entrópica y es vulnerable al colapso.")

            # Botón de descarga
            st.download_button(
                label="📥 Descargar Reporte",
                data=resultado["reporte"],
                file_name=f"iso_entropy_{time.strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
            
            # Telemetría
            with st.expander("📊 Ver Telemetría de Experimentos (JSON)"):
                st.json(agent.experiment_log)
                
                # Gráfica de exploración
                if agent.experiment_log:
                    try:
                        import pandas as pd
                        import plotly.express as px
                        
                        df = pd.DataFrame([
                            {
                                "Ciclo": exp["ciclo"],
                                "K": exp["hipotesis"]["K"],
                                "Colapso (%)": exp["resultado"]["tasa_de_colapso"] * 100
                            }
                            for exp in agent.experiment_log
                            if "resultado" in exp
                        ])
                        
                        if not df.empty:
                            fig = px.line(
                                df, x="K", y="Colapso (%)",
                                markers=True,
                                title="Exploración del Espacio de Parámetros"
                            )
                            fig.add_hline(y=5, line_dash="dash", line_color="red")
                            st.plotly_chart(fig, width='stretch')

                        # Nueva gráfica para Deuda Entrópica Residual (D_e)
                        df_de = pd.DataFrame([
                            {
                                "Ciclo": exp["ciclo"],
                                "Deuda Entrópica Residual (D_e)": exp.get("deuda_entropica_residual", 0)
                            }
                            for exp in agent.experiment_log
                            if "deuda_entropica_residual" in exp
                        ])

                        if not df_de.empty:
                            fig_de = px.line(
                                df_de, x="Ciclo", y="Deuda Entrópica Residual (D_e)",
                                markers=True,
                                title="Acumulación de Deuda Entrópica Residual a lo Largo del Tiempo"
                            )
                            st.plotly_chart(fig_de, width='stretch')

                        # Tabla actualizada con II y D_e
                        df_full = pd.DataFrame([
                            {
                                "Ciclo": exp["ciclo"],
                                "K": exp["hipotesis"]["K"],
                                "Colapso (%)": exp["resultado"]["tasa_de_colapso"] * 100,
                                "Insolvencia Informacional (II)": exp.get("insolvencia_informacional", 0),
                                "Deuda Entrópica Residual (D_e)": exp.get("deuda_entropica_residual", 0)
                            }
                            for exp in agent.experiment_log
                            if "resultado" in exp
                        ])

                        if not df_full.empty:
                            st.dataframe(df_full)

                    except ImportError:
                        st.info("Instala `plotly` para ver gráficas: `pip install plotly`")
        else:
            st.warning("⚠️ El agente no devolvió reporte. Revisa los logs.")

if __name__ == "__main__":
    main()