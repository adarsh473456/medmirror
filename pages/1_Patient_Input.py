import streamlit as st
import time

# --- Page Config & CSS ---
st.set_page_config(page_title="MedMirror - Patient Assessment", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0a0f1e; color: white; }
[data-testid="stSidebar"] { background-color: #0d1526; }
#MainMenu, footer, header { visibility: hidden; }

.page-title { font-size: 42px; font-weight: 700; color: white; margin-top: 1rem; margin-bottom: 0.2rem; }
.page-subtitle { font-size: 16px; color: #a0aec0; font-weight: 300; margin-bottom: 2rem; }

/* Interactive Cards */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: rgba(13, 21, 38, 0.7) !important;
    border: 1px solid rgba(55, 138, 221, 0.3) !important;
    border-radius: 16px !important;
    padding: 24px !important;
    backdrop-filter: blur(10px);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    margin-bottom: 1.5rem;
    animation: fadeIn 0.8s ease-out forwards;
}

[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border: 1px solid #378ADD !important;
    box-shadow: 0 10px 30px rgba(55, 138, 221, 0.2) !important;
    transform: translateY(-4px) !important;
}

@keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

/* Inputs and Sliders */
.stTextInput label, .stSlider label, .stSelectbox label, .stMultiSelect label, .stTextArea label, .stRadio label {
    color: #e2e8f0 !important; font-weight: 600 !important; letter-spacing: 0.5px;
}

/* Custom interactive glowing button */
div.stButton > button:first-child {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%) !important;
    color: white !important;
    border: 1px solid #378ADD !important;
    border-radius: 12px !important;
    padding: 1.2rem 2rem !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 20px rgba(55, 138, 221, 0.4) !important;
    width: 100% !important;
    margin-top: 1rem !important;
    text-transform: uppercase;
    letter-spacing: 2px;
}
div.stButton > button:first-child:hover {
    box-shadow: 0 0 35px rgba(55, 138, 221, 0.8) !important;
    transform: scale(1.01) !important;
    border: 1px solid #73bcf8 !important;
}

/* AI insight badge */
.ai-insight {
    background: rgba(55, 138, 221, 0.1);
    border-left: 4px solid #378ADD;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    font-size: 14px;
    color: #a0aec0;
    margin-top: 8px;
    animation: slideIn 0.3s ease-out;
}
.ai-insight-warning {
    background: rgba(220, 53, 69, 0.1);
    border-left: 4px solid #dc3545;
    color: #ff8793;
}

@keyframes slideIn { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }

/* Progress bar styling */
.stProgress > div > div > div > div {
    background-color: #378ADD;
}
</style>
""", unsafe_allow_html=True)

# --- App Logic & Interactive UI ---
st.markdown('<div class="page-title">Patient Assessment</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Step 1 of 4 — Enter patient clinical data for the digital twin</div>', unsafe_allow_html=True)

# Progress bar container (will be filled at the bottom but visually stays top)
progress_placeholder = st.empty()

# Initialize variables
name = ""
age = 50
gender = "Male"
symptoms = []
sys_bp = 120
dia_bp = 80
diabetes = "No"
conditions = []
meds = ""

with st.container(border=True):
    st.subheader("👤 1. Patient Profile")
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        name = st.text_input("Patient Name", placeholder="e.g., Jane Doe")
    with col2:
        age = st.slider("Age", min_value=1, max_value=100, value=50, step=1)
    with col3:
        gender = st.radio("Gender", options=["Male", "Female", "Other"], horizontal=True)

with st.container(border=True):
    st.subheader("🩺 2. Symptoms and Vitals")
    col1, col2 = st.columns(2)
    with col1:
        symptoms = st.multiselect("Primary Symptoms", 
            options=["Chest Pain", "Shortness of Breath", "High Fever", "Fatigue", "Dizziness", "Nausea", "Severe Headache", "Abdominal Pain"]
        )
        diabetes = st.radio("Diabetes", options=["Yes", "No"], horizontal=True)
    with col2:
        sys_bp = st.slider("Systolic Blood Pressure (mmHg)", min_value=70, max_value=200, value=120)
        dia_bp = st.slider("Diastolic Blood Pressure (mmHg)", min_value=40, max_value=130, value=80)
        
        # INTERACTIVE WIDGET: Real-time AI Analysis based on slider movement!
        if sys_bp > 140 or dia_bp > 90:
            st.markdown('<div class="ai-insight ai-insight-warning">⚠️ <b>AI Note:</b> Stage 2 Hypertension detected. High risk profile. Agents A & B (Beta Blockers / ACE Inhibitors) will be prioritized in simulation.</div>', unsafe_allow_html=True)
        elif sys_bp > 120 or dia_bp > 80:
            st.markdown('<div class="ai-insight">🟡 <b>AI Note:</b> Elevated BP detected. Monitoring recommended.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="ai-insight">🟢 <b>AI Note:</b> Blood pressure is within optimal range.</div>', unsafe_allow_html=True)

with st.container(border=True):
    st.subheader("📋 3. Medical History")
    conditions = st.multiselect("Existing Conditions", 
        options=["Heart Disease", "Kidney Disease", "Liver Disease", "Asthma", "None"]
    )
    meds = st.text_input("Current Medications", placeholder="e.g. Aspirin, Metformin")

# Calculate completeness for progress bar
score = 0
if name.strip(): score += 25
if symptoms: score += 25
if conditions: score += 25
if meds.strip(): score += 25

with progress_placeholder.container():
    st.caption(f"Data Completeness: {score}%")
    st.progress(score / 100.0)

# Submit Button
error_placeholder = st.empty()

if st.button("🚀 INITIATE DIGITAL TWIN SIMULATION"):
    if not name.strip():
        error_placeholder.error("❌ Validation Error: Patient Name cannot be empty.")
    elif len(symptoms) == 0:
        error_placeholder.error("❌ Validation Error: At least one symptom must be selected.")
    else:
        st.session_state["patient_data"] = {
            "name": name, "age": age, "gender": gender, "symptoms": symptoms,
            "sys_bp": sys_bp, "dia_bp": dia_bp, "diabetes": diabetes, "conditions": conditions, "medications": meds
        }
        st.session_state["page_1_done"] = True
        st.switch_page("pages/2_Mirror_World.py")
#jjj
