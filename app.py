import streamlit as st
import os

# Page config
st.set_page_config(
    page_title="MedMirror",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS Injection
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Backgrounds */
.stApp {
    background-color: #0a0f1e;
    color: white;
}

[data-testid="stSidebar"] {
    background-color: #0d1526;
}

/* Hide default streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Button Styling (Targets st.button) */
div.stButton {
    display: flex;
    justify-content: center;
}

div.stButton > button:first-child {
    background-color: rgba(55, 138, 221, 0.1) !important;
    color: white !important;
    border: 1px solid #378ADD !important;
    border-radius: 8px !important;
    padding: 0.75rem 2rem !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 10px rgba(55, 138, 221, 0.2) !important;
    width: 300px !important;
}

div.stButton > button:first-child:hover {
    background-color: rgba(55, 138, 221, 0.2) !important;
    box-shadow: 0 0 20px rgba(55, 138, 221, 0.6) !important;
    transform: translateY(-2px) !important;
    border: 1px solid #5ab0ff !important;
}
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'patient_data' not in st.session_state:
    st.session_state['patient_data'] = {}
if 'simulation_results' not in st.session_state:
    st.session_state['simulation_results'] = []
if 'best_agent' not in st.session_state:
    st.session_state['best_agent'] = ""
if 'page_1_done' not in st.session_state:
    st.session_state['page_1_done'] = False
if 'page_2_done' not in st.session_state:
    st.session_state['page_2_done'] = False
if 'page_3_done' not in st.session_state:
    st.session_state['page_3_done'] = False

# --- UI LAYOUT ---

# Top & Middle Section (HTML/CSS)
st.markdown("""
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-top: 4rem;">
    <!-- Top Section: Pulsing Circle -->
    <style>
        .pulse-circle {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            font-weight: 700;
            color: white;
            margin-bottom: 2rem;
            position: relative;
            box-shadow: 0 0 0 0 rgba(55, 138, 221, 0.7);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(55, 138, 221, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 25px rgba(55, 138, 221, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(55, 138, 221, 0); }
        }
        
        .main-title {
            font-size: 64px;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: -webkit-linear-gradient(#ffffff, #b0c4de);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .subtitle {
            font-size: 18px;
            color: #a0aec0;
            font-weight: 300;
            letter-spacing: 1px;
            margin-bottom: 1.5rem;
        }
        
        .divider {
            width: 60px;
            height: 4px;
            background-color: #378ADD;
            border-radius: 2px;
            margin-bottom: 1.5rem;
        }
        
        .description {
            font-size: 14px;
            color: #718096;
            max-width: 600px;
            line-height: 1.6;
            margin-bottom: 2.5rem;
        }
    </style>
    
    <div class="pulse-circle">M</div>
    
    <!-- Middle Section: Text -->
    <div class="main-title">MedMirror</div>
    <div class="subtitle">AI-Powered Clinical Decision Simulation</div>
    <div class="divider"></div>
    <div class="description">
        MedMirror creates a digital mirror world of your patient. Four AI agents simultaneously test different treatment paths and simulate outcomes — so you know the best decision before making it in the real world.
    </div>
</div>
""", unsafe_allow_html=True)

# Bottom Section: Button and Stats
# The button is auto-centered via our custom CSS on div.stButton
if st.button("Begin Patient Assessment"):
    # Streamlit requires the file to exist to use switch_page
    try:
        st.switch_page("pages/1_Patient_Input.py")
    except Exception as e:
        st.error("Page not created yet! Wait for step 2.")

# Stat Cards
st.markdown("""
<style>
    .stats-container {
        display: flex;
        gap: 2rem;
        justify-content: center;
        margin-top: 3rem;
        margin-bottom: 4rem;
    }

    .stat-card {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        width: 220px;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }

    .stat-card:hover {
        transform: translateY(-5px);
        border-color: rgba(55, 138, 221, 0.4);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2), 0 0 15px rgba(55, 138, 221, 0.1);
    }

    .stat-value {
        font-size: 16px;
        font-weight: 600;
        color: white;
        letter-spacing: 0.5px;
    }
</style>

<div class="stats-container">
    <div class="stat-card">
        <div class="stat-value">4 Parallel Agents</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">30-Day Simulation</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">AI-Powered Report</div>
    </div>
</div>
""", unsafe_allow_html=True)
