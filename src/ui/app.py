# src/ui/app.py - Streamlit UI for Iso-Entropy Autonomous Auditor

import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd                 
from datetime import datetime       

# ============================================================================
# INITIAL CONFIGURATION
# ============================================================================

# Load environment variables
load_dotenv()

# Page configuration (MUST BE THE FIRST THING)
st.set_page_config(
    page_title="Iso-Entropy | Autonomous Audit",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/RogelioAlcantarRangel/Iso-Entropy",
        "Report a bug": "https://github.com/RogelioAlcantarRangel/Iso-Entropy/issues",
        "About": "ISO-ENTROPY v2.3 - Structural Fragility Auditor"
    }
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
    <style>
    /* Professional dark theme */
    .main {
        background-color: #0E1117;
        color: #E6EDF3;
    }
    
    /* Titles */
    h1, h2, h3 {
        color: #FAFAFA;
        font-weight: 700;
    }
    
    /* Metrics */
    .stMetric {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #41444C;
    }
    
    /* Success boxes */
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #1c4f2e;
        color: #aaffaa;
        border: 1px solid #2e7d32;
    }
    
    /* Warning boxes */
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #4a3a1a;
        color: #ffcc99;
        border: 1px solid #8b6f47;
    }
    
    /* Divider */
    hr {
        border: 1px solid #41444C;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #262730;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# IMPORT AGENT
# ============================================================================

try:
    root_dir = Path(__file__).parent.parent.parent
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    
    from src.core.agent import IsoEntropyAgent
except ImportError as e:
    st.error(f"❌ Import error: {e}")
    st.stop()

# ============================================================================
# SIDEBAR - CONFIGURATION
# ============================================================================

with st.sidebar:
    # Logo and title
    st.image(
        "https://img.icons8.com/fluency/96/system-diagnostic.png",
        width=80
    )
    st.title("ISO-ENTROPY")
    st.caption("v2.3 - Autonomous Auditor")
    
    st.markdown("---")

     # --- RESTORED API KEY INPUT ---
    api_key_input = st.text_input(
        "🔑 Gemini API Key",
        type="password",
        placeholder="Paste AIzaSy... here",
        help="If left empty, the key from the .env file will be used",
        value="" 
    )
    # -----------------------------------
    
    # SYSTEM PARAMETERS
    st.subheader("⚙️ System Parameters")
    
    volatility = st.selectbox(
        "🌪️ Volatility (External Entropy I)",
        options=[
            "Low (Stable)",
            "Medium (Seasonal)",
            "High (Chaotic)"
        ],
        index=1,
        help="Level of chaos and uncertainty in the system's environment. Directly affects I (External Entropy)."
    )
    
    rigidity = st.selectbox(
        "🧱 Operational Rigidity (Capacity K)",
        options=[
            "Low (Automated)",
            "Medium (Standard)",
            "High (Manual/Bureaucratic)"
        ],
        index=1,
        help="System's ability to adapt and process information. Directly affects K (Response Capacity)."
    )
    
    buffer = st.slider(
        "💰 Financial Buffer (Months)",
        min_value=1,
        max_value=24,
        value=6,
        step=1,
        help="Time buffer before collapse. Defines the Collapse Threshold (θ_max)."
    )
    
    st.markdown("---")

    # ADVANCED SETTINGS
    st.subheader("🔧 Advanced Options")
    
    advanced_options = st.expander("Show advanced options", expanded=False)
    
    with advanced_options:
        mock_mode = st.checkbox(
            "🎭 Mock Mode (no API)",
            value=False,
            help="Activates simulation mode without consuming API quota. Useful for testing and development."
        )
        
        verbose = st.checkbox(
            "📝 Verbose Mode",
            value=True,
            help="Displays detailed logs for each agent iteration."
        )
        
        max_iterations = st.slider(
            "🔄 Maximum Iterations",
            min_value=1,
            max_value=20,
            value=10,
            help="Maximum number of iterations the FSM can execute."
        )
    
    st.markdown("---")
    
    # INFO
    st.info(
        "**Powered by:**\n"
        "- google-genai SDK\n"
        "- Gemini 3 Flash\n"
        "- Information Thermodynamics",
        icon="ℹ️"
    )
    
    st.caption(
        "ISO-ENTROPY v2.3 | "
        "[GitHub](https://github.com/RogelioAlcantarRangel/Iso-Entropy) | "
        "[Hackathon](https://gemini3.devpost.com/)"
    )

# ============================================================================
# MAIN CONTENT - HERO SECTION
# ============================================================================

col_logo, col_title = st.columns([1, 5])

with col_logo:
    st.markdown("# ⚡")

with col_title:
    st.markdown("# ISO-ENTROPY")
    st.markdown("### Structural Fragility Audit & Business Collapse Detection")

st.markdown("""
    <div style='background-color: #181a20; padding: 15px; border-radius: 10px; border-left: 5px solid #FF4B4B;'>
        <strong>🤖 Autonomous Auditor:</strong> Uses <strong>Information Thermodynamics</strong> + 
        <strong>AI Reasoning (Gemini 3)</strong> to detect invisible breaking points in your 
        operation <strong>6-12 months before</strong> they occur.
    </div>
""", unsafe_allow_html=True)

st.write("")  # Spacer

# ============================================================================
# SECTION 1: SYSTEM DESCRIPTION
# ============================================================================

st.subheader("1️⃣ Describe your Operating System")

user_input = st.text_area(
    "Operational context (include challenges, recent changes, constraints):",
    height=150,
    placeholder=(
        "Example: High-specialty private hospital. "
        "Emergency demand grew 40% in 12 months. "
        "Shortage of specialized personnel. "
        "IT systems show intermittent failures. "
        "Tight financial margins. "
        "Any technological interruption generates a cascade of effects."
    ),
    label_visibility="collapsed"
)

st.write("")  # Spacer

# ============================================================================
# SECTION 2: CONTROL BUTTONS
# ============================================================================

st.subheader("2️⃣ Start Audit")

col_btn1, col_btn2, col_spacer = st.columns([2, 1, 2])

with col_btn1:
    start_btn = st.button(
        "🚀 RUN AUTONOMOUS AUDIT",
        type="primary",
        use_container_width=True,
        help="Starts the complete audit with FSM, simulations, and analysis."
    )

with col_btn2:
    clear_btn = st.button(
        "🗑️ Clear",
        use_container_width=True,
        help="Clears the cache history."
    )

if clear_btn:
    st.session_state.clear()
    st.rerun()

st.write("")  # Spacer

# ============================================================================
# AUDIT EXECUTION
# ============================================================================

if start_btn:
    # KEY VALIDATIONS AND PRIORITY LOGIC
    env_key = os.getenv("GEMINI_API_KEY")
    final_api_key = api_key_input.strip() if api_key_input else env_key
    
    if not user_input.strip():
        st.error("⚠️ Please describe your operating system first")
        st.stop()
    
    if not final_api_key and not mock_mode:
        st.warning(
            "⚠️ GEMINI_API_KEY not found. "
            "Activating Mock Mode automatically for demonstration."
        )
        mock_mode = True
    
    # INITIALIZE AGENT
    try:
        agent = IsoEntropyAgent(
            api_key=final_api_key if not mock_mode else None,
            mock_mode=mock_mode,
            verbose=verbose,
            max_iterations=max_iterations
        )
    except Exception as e:
        st.error(f"❌ Error initializing agent: {e}")
        st.stop()
    
    # RUN AUDIT
    status_placeholder = st.status(
        "🔄 Starting autonomous audit...",
        expanded=True
    )
    
    with status_placeholder:
        try:
            # Create container for logs
            logs_container = st.empty()
            
            # Capture output
            import io
            from contextlib import redirect_stdout
            
            log_capture = io.StringIO()
            
            with redirect_stdout(log_capture):
                result = agent.audit_system(
                    user_input=user_input,
                    volatility=volatility,
                    rigidity=rigidity,
                    buffer=buffer
                )
            
            # Show logs
            logs = log_capture.getvalue()
            if logs:
                with st.expander("📋 Execution Logs"):
                    st.code(logs, language="text")
            
            status_placeholder.update(
                label="✅ Audit completed",
                state="complete"
            )
        
        except Exception as e:
            status_placeholder.update(
                label=f"❌ Error during audit",
                state="error"
            )
            st.error(f"Error: {str(e)}")
            st.stop()
    
    # ========================================================================
    # SHOW RESULTS
    # ========================================================================
    
    st.divider()
    st.subheader("3️⃣ Analysis Results")
    st.write("")
    
    # KPIs
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    
    with col_kpi1:
        st.metric(
            "Experiments",
            len(agent.experiment_log),
            help="Number of simulations run by the FSM"
        )
    
    with col_kpi2:
        mode_text = "🎭 Mock" if mock_mode else "🚀 Production"
        st.metric(
            "Mode",
            mode_text,
            help="Execution mode"
        )
    
    with col_kpi3:
        current_phase = agent.fsm.phase_name()
        st.metric(
            "Final Phase",
            current_phase,
            help="Last completed phase of the FSM"
        )
    
    with col_kpi4:
        st.metric(
            "Status",
            "✅ OK",
            help="Audit status"
        )
    
    st.write("")
    
    # MAIN REPORT
    st.subheader("📄 Complete Executive Report")
    st.markdown(result)

    # VISUALIZATION
    if agent.experiment_log:
        last_result = agent.experiment_log[-1]['result']
        trajectory = last_result.get('trajectory', [])
        if trajectory:
            # Calculate theta_max
            from src.core.grounding import ground_inputs
            from src.core.physics import calculate_collapse_threshold
            params = ground_inputs(volatility, rigidity, buffer)
            theta_max = calculate_collapse_threshold(params['stock'], params['capital'], params['liquidity'])

            st.subheader("📈 Entropy Debt Trajectory")
            df = pd.DataFrame({
                'Time Step': range(1, len(trajectory) + 1),
                'Entropy Debt': trajectory,
                'Collapse Threshold': [theta_max] * len(trajectory)
            })
            st.line_chart(df.set_index('Time Step')[['Entropy Debt', 'Collapse Threshold']])

    # AUDIT EVOLUTION TIME SERIES
    if len(agent.experiment_log) > 1:
        st.subheader("📊 Evolución del Audit")
        cycles = [exp['cycle'] for exp in agent.experiment_log]
        k_values = [exp['hypothesis']['K'] for exp in agent.experiment_log]
        collapse_rates = [exp['result']['collapse_rate'] for exp in agent.experiment_log]
        df_evolution = pd.DataFrame({
            'Cycle': cycles,
            'K (Capacity)': k_values,
            'Collapse Rate': collapse_rates
        })
        st.line_chart(df_evolution.set_index('Cycle'))

    # DOWNLOAD
    st.download_button(
        label="📥 Download Report (Markdown)",
        data=result,
        file_name=f"iso_entropy_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown"
    )
    
    # TECHNICAL INFORMATION
    with st.expander("🔬 Technical Details"):
        col_tech1, col_tech2 = st.columns(2)
        
        with col_tech1:
            st.write("**Physical Parameters:**")
            st.json({
                "volatility": volatility,
                "rigidity": rigidity,
                "buffer_months": buffer,
                "mock_mode": mock_mode
            })
        
        with col_tech2:
            st.write("**FSM History:**")
            if agent.experiment_log:
                hist_data = []
                for exp in agent.experiment_log:
                    hist_data.append({
                        "Cycle": exp['cycle'],
                        "Phase": exp['phase'],
                        "K": f"{exp['hypothesis']['K']:.2f}",
                        "Collapse": f"{exp['result']['collapse_rate']:.1%}"
                    })
                
                df = pd.DataFrame(hist_data)
                # Use use_container_width to make it look good
                st.dataframe(df, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.caption("**ISO-ENTROPY v2.3**")

with col_footer2:
    st.caption("*Powered by Gemini 3 Flash*")

with col_footer3:
    st.caption("[GitHub](https://github.com/RogelioAlcantarRangel/Iso-Entropy)")
