import streamlit as st
import time

st.set_page_config(page_title="MedMirror - Mirror World", layout="wide", initial_sidebar_state="collapsed")

# Shared Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0a0f1e; color: white; }
[data-testid="stSidebar"] { background-color: #0d1526; }
#MainMenu, footer, header { visibility: hidden; }

.page-title { font-size: 42px; font-weight: 700; color: white; margin-top: 1rem; margin-bottom: 0.2rem; }
.page-subtitle { font-size: 18px; color: #a0aec0; font-weight: 300; margin-bottom: 2rem; }

/* Interactive Cards */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: rgba(13, 21, 38, 0.7) !important;
    border: 1px solid rgba(55, 138, 221, 0.3) !important;
    border-radius: 16px !important;
    padding: 24px !important;
    backdrop-filter: blur(10px);
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border: 1px solid #378ADD !important;
    box-shadow: 0 10px 30px rgba(55, 138, 221, 0.2) !important;
}

/* Stat cards bottom */
.stat-card {
    background-color: rgba(13, 21, 38, 0.9);
    border: 1px solid rgba(55, 138, 221, 0.5);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 0 15px rgba(55, 138, 221, 0.2);
    transition: all 0.3s ease;
}
.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 0 25px rgba(55, 138, 221, 0.5);
    border-color: #5ab0ff;
}
.stat-value { font-size: 18px; font-weight: 600; color: white; }

/* Red/Green Badges */
.risk-badge {
    background: rgba(220, 53, 69, 0.1);
    border: 1px solid #dc3545;
    color: #ff8793;
    padding: 8px 16px;
    border-radius: 8px;
    display: inline-block;
    margin-right: 10px;
    margin-bottom: 10px;
    font-weight: 600;
    animation: fadeIn 0.5s ease-out;
}
.safe-badge {
    background: rgba(40, 167, 69, 0.1);
    border: 1px solid #28a745;
    color: #8ce99a;
    padding: 8px 16px;
    border-radius: 8px;
    display: inline-block;
    font-weight: 600;
    animation: fadeIn 0.5s ease-out;
}

/* Glowing Green Button */
div.stButton > button:first-child {
    background: linear-gradient(90deg, #1e5631 0%, #4c9a2a 100%) !important;
    color: white !important;
    border: 1px solid #639922 !important;
    border-radius: 12px !important;
    padding: 1.2rem 2rem !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    box-shadow: 0 0 20px rgba(99, 153, 34, 0.4) !important;
    width: 100% !important;
    text-transform: uppercase;
    letter-spacing: 2px;
    transition: all 0.3s ease !important;
}
div.stButton > button:first-child:hover {
    box-shadow: 0 0 35px rgba(99, 153, 34, 0.8) !important;
    transform: scale(1.02) !important;
    border: 1px solid #8be836 !important;
}

/* Data summary table layout */
.label-col { color: #a0aec0; font-size: 16px; margin-bottom: 12px; }
.value-col { color: white; font-size: 16px; font-weight: 600; margin-bottom: 12px; }

/* Animation card */
.anim-card {
    background-color: rgba(13, 21, 38, 0.9);
    border: 1px solid #378ADD;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 10px;
    box-shadow: 0 0 15px rgba(55, 138, 221, 0.3);
    color: white;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 15px;
    animation: slideDown 0.3s ease-out;
}
.spinner {
    width: 20px; height: 20px;
    border: 3px solid rgba(55,138,221,0.3);
    border-radius: 50%;
    border-top-color: #378ADD;
    animation: spin 1s ease-in-out infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

</style>
""", unsafe_allow_html=True)

if not st.session_state.get("patient_data"):
    st.error("No patient data found. Please complete the patient assessment first.")
    if st.button("Go to Patient Input"):
        st.switch_page("pages/1_Patient_Input.py")
    st.stop()

st.markdown('<div class="page-title">Mirror World</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Building your patient\'s digital twin...</div>', unsafe_allow_html=True)

steps = [
    "Extracting patient biomarkers...",
    "Mapping disease progression model...",
    "Loading drug interaction database...",
    "Generating physiological twin...",
    "Calibrating immune response model...",
    "Mirror world construction complete."
]

# Animation sequence logic
if not st.session_state.get('mirror_animation_done', False):
    anim_placeholder = st.empty()
    html_content = ""
    
    for step in steps:
        # Show step with spinner
        current_html = html_content + f'<div class="anim-card"><div class="spinner"></div>{step}</div>'
        anim_placeholder.markdown(current_html, unsafe_allow_html=True)
        time.sleep(0.8)
        
        # Replace spinner with checkmark
        html_content += f'<div class="anim-card">✅ {step}</div>'
        anim_placeholder.markdown(html_content, unsafe_allow_html=True)
        
        # Small delay before next step
        if step != steps[-1]:
            time.sleep(0.4)
            
    time.sleep(1.0)
    anim_placeholder.empty()  # Clear animation
    st.session_state['mirror_animation_done'] = True

# --- Main Content Post-Animation ---
p_data = st.session_state["patient_data"]

col1, col2 = st.columns([1.2, 1])

with col1:
    with st.container(border=True):
        st.subheader("🧬 Digital Twin — Patient Model")
        st.markdown("<hr style='border-color: rgba(55,138,221,0.2); margin-top: 0; margin-bottom: 1rem;'>", unsafe_allow_html=True)
        
        d_col1, d_col2 = st.columns([1, 1.5])
        
        labels = ["Name", "Age", "Gender", "Symptoms", "Blood Pressure", "Diabetes", "Existing Conditions", "Current Medications"]
        
        symptoms_str = ", ".join(p_data["symptoms"]) if p_data["symptoms"] else "None"
        conditions_str = ", ".join(p_data["conditions"]) if p_data["conditions"] else "None"
        bp_str = f"{p_data['sys_bp']} / {p_data['dia_bp']} mmHg"
        meds_str = p_data["medications"] if p_data["medications"].strip() else "None"
        
        values = [
            p_data["name"], 
            str(p_data["age"]), 
            p_data["gender"], 
            symptoms_str, 
            bp_str, 
            p_data["diabetes"], 
            conditions_str, 
            meds_str
        ]
        
        for lbl, val in zip(labels, values):
            with d_col1:
                st.markdown(f'<div class="label-col">{lbl}</div>', unsafe_allow_html=True)
            with d_col2:
                st.markdown(f'<div class="value-col">{val}</div>', unsafe_allow_html=True)

with col2:
    with st.container(border=True):
        st.subheader("⚠️ Risk Profile Analysis")
        st.markdown("<hr style='border-color: rgba(55,138,221,0.2); margin-top: 0; margin-bottom: 1rem;'>", unsafe_allow_html=True)
        
        risks = []
        if p_data["diabetes"] == "Yes":
            risks.append("Metabolic risk elevated")
        if "Chest Pain" in p_data["symptoms"]:
            risks.append("Cardiac event risk detected")
        if p_data["sys_bp"] > 140:
            risks.append("Hypertension risk flagged")
        if "Heart Disease" in p_data["conditions"]:
            risks.append("Cardiovascular complication risk")
            
        if not risks:
            st.markdown('<div class="safe-badge">🟢 No critical risk factors detected</div>', unsafe_allow_html=True)
        else:
            for risk in risks:
                st.markdown(f'<div class="risk-badge">🚨 {risk}</div>', unsafe_allow_html=True)

# Stat Cards
st.markdown("""
<div style="display: flex; gap: 2rem; justify-content: space-between; margin-top: 2rem; margin-bottom: 3rem;">
    <div class="stat-card" style="flex: 1;">
        <div class="stat-value">🤖 4 Agents Ready</div>
    </div>
    <div class="stat-card" style="flex: 1;">
        <div class="stat-value">⏱️ 30-Day Simulation</div>
    </div>
    <div class="stat-card" style="flex: 1;">
        <div class="stat-value">🧠 AI Analysis Active</div>
    </div>
</div>
""", unsafe_allow_html=True)

if st.button("🚀 Launch Simulation"):
    st.session_state["page_2_done"] = True
    st.switch_page("pages/3_Simulation.py")
