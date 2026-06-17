import streamlit as st
import datetime
import plotly.graph_objects as go
from fpdf import FPDF

st.set_page_config(page_title="MedMirror - Report", layout="wide", initial_sidebar_state="collapsed")
#dfr
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0a0f1e; color: white; }
[data-testid="stSidebar"] { background-color: #0d1526; }
#MainMenu, footer, header { visibility: hidden; }

.page-title { font-size: 42px; font-weight: 700; color: white; margin-top: 1rem; margin-bottom: 0.2rem; }
.page-subtitle { font-size: 16px; color: #a0aec0; font-weight: 300; margin-bottom: 2rem; }

/* Recommended Banner */
.best-banner {
    background: rgba(40, 167, 69, 0.1);
    border: 2px solid #639922;
    border-radius: 16px;
    padding: 30px;
    margin-bottom: 3rem;
    box-shadow: 0 0 30px rgba(99, 153, 34, 0.2);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.banner-left { flex: 3; }
.banner-right { flex: 1; text-align: right; }
.best-banner-title { color: #8ce99a; font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;}
.best-banner-agent { color: white; font-size: 36px; font-weight: 700; margin-bottom: 5px; }
.best-summary { color: #e2e8f0; font-size: 16px; line-height: 1.6; border-left: 3px solid #639922; padding-left: 15px; margin-top: 15px; }
.best-score-label { color: #a0aec0; font-size: 14px; text-transform: uppercase; font-weight: 600; letter-spacing: 1px; }
.best-score-value { color: #8ce99a; font-size: 64px; font-weight: 800; line-height: 1; text-shadow: 0 0 20px rgba(140, 233, 154, 0.4); }

/* Column Cards */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: rgba(13, 21, 38, 0.7) !important;
    border: 1px solid rgba(55, 138, 221, 0.3) !important;
    border-radius: 12px !important;
    padding: 15px !important;
    backdrop-filter: blur(10px);
    height: 100%;
}
.col-card-title { font-size: 20px; font-weight: 700; margin-bottom: 0px; }
.col-card-subtitle { font-size: 12px; color: #a0aec0; margin-bottom: 15px; display: block; text-transform: uppercase; }
.col-score-green { font-size: 42px; font-weight: 800; color: #8ce99a; text-align: center; margin-top: 10px;}
.col-score-white { font-size: 42px; font-weight: 800; color: white; text-align: center; margin-top: 10px;}
.score-label-small { font-size: 12px; color: #a0aec0; text-align: center; text-transform: uppercase; margin-bottom: 15px; display: block; font-weight: 600;}

/* Risk Badges */
.risk-low { background: rgba(40,167,69,0.15); color: #8ce99a; border: 1px solid #28a745; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; display: inline-block; margin-bottom: 10px;}
.risk-medium { background: rgba(255,193,7,0.15); color: #ffd8a8; border: 1px solid #ffc107; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; display: inline-block; margin-bottom: 10px;}
.risk-high { background: rgba(220,53,69,0.15); color: #ff8793; border: 1px solid #dc3545; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; display: inline-block; margin-bottom: 10px;}

/* Outcome boxes */
.outcome-box { background: rgba(255,255,255,0.03); padding: 10px; border-radius: 6px; margin-top: 8px; font-size: 13px; color: #cbd5e1; border-left: 2px solid rgba(55,138,221,0.5); line-height: 1.4; }
.outcome-box strong { color: white; display: block; margin-bottom: 2px; font-size: 12px; text-transform: uppercase; color: #73bcf8;}

/* Side effects */
.se-title { font-size: 12px; font-weight: 700; color: #a0aec0; margin-top: 20px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px;}
.se-list { font-size: 13px; color: #94a3b8; padding-left: 20px; margin-top: 5px; line-height: 1.5;}

/* Reset Button */
.reset-btn div.stButton > button:first-child { 
    background: transparent !important;
    border: 1px solid #dc3545 !important; 
    color: #ff8793 !important; 
    border-radius: 8px !important;
    padding: 0.8rem 2rem !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    width: 100% !important;
    transition: all 0.3s ease;
}
.reset-btn div.stButton > button:first-child:hover { background: rgba(220,53,69,0.1) !important; box-shadow: 0 0 15px rgba(220,53,69,0.3) !important; }

/* Download btn */
.download-btn div.stDownloadButton > button:first-child {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%) !important;
    color: white !important;
    border: 1px solid #378ADD !important;
    border-radius: 8px !important;
    padding: 0.8rem 2rem !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    width: 100% !important;
    transition: all 0.3s ease;
}
.download-btn div.stDownloadButton > button:first-child:hover { box-shadow: 0 0 20px rgba(55, 138, 221, 0.6) !important; transform: translateY(-2px); }

/* Expander Overrides */
.streamlit-expanderHeader { color: white !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("simulation_results"):
    st.error("No simulation results found. Please run the simulation first.")
    if st.button("Go to Simulation"):
        st.switch_page("pages/3_Simulation.py")
    st.stop()

results = st.session_state["simulation_results"]
best_name = st.session_state["best_agent"]
p_data = st.session_state["patient_data"]
best_agent = next(r for r in results if r["agent_name"] == best_name)
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.markdown('<div class="page-title">Clinical Decision Report</div>', unsafe_allow_html=True)
st.markdown(f'<div class="page-subtitle">Patient: {p_data["name"]} | Generated: {timestamp}</div>', unsafe_allow_html=True)

# Glowing Green Banner
st.markdown(f"""
<div class="best-banner">
    <div class="banner-left">
        <div class="best-banner-title">✨ Recommended Treatment Path</div>
        <div class="best-banner-agent">{best_agent["agent_name"]} — {best_agent["treatment"]}</div>
        <div class="best-summary">{best_agent["recommendation_summary"]}</div>
    </div>
    <div class="banner-right">
        <div class="best-score-value">{best_agent["recovery_score"]}</div>
        <div class="best-score-label">Recovery Score</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### Treatment Comparison")

cols = st.columns(4)
for i, r in enumerate(results):
    is_best = (r["agent_name"] == best_name)
    score_class = "col-score-green" if is_best else "col-score-white"
    
    risk = r["risk_level"].lower()
    if risk == "low": risk_class = "risk-low"
    elif risk == "medium": risk_class = "risk-medium"
    else: risk_class = "risk-high"
    
    se_html = "".join([f"<li>{se}</li>" for se in r["side_effects"]])
    
    with cols[i]:
        with st.container(border=True):
            st.markdown(f"<div class='col-card-title' style='color: {r['agent_color']};'>{r['agent_name']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='col-card-subtitle'>{r['treatment']}</div>", unsafe_allow_html=True)
            
            st.markdown(f"<div class='{risk_class}'>Risk: {risk.upper()}</div>", unsafe_allow_html=True)
            
            st.markdown(f"<div class='{score_class}'>{r['recovery_score']}</div>", unsafe_allow_html=True)
            st.markdown("<div class='score-label-small'>Recovery Score</div>", unsafe_allow_html=True)
            
            st.markdown(f"<div class='outcome-box'><strong>24 Hours</strong>{r['outcome_24hr']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='outcome-box'><strong>7 Days</strong>{r['outcome_7day']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='outcome-box'><strong>30 Days</strong>{r['outcome_30day']}</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='se-title'>Side Effects</div>", unsafe_allow_html=True)
            st.markdown(f"<ul class='se-list'>{se_html}</ul>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Bar Chart
agent_names = [r["agent_name"] for r in results]
scores = [r["recovery_score"] for r in results]
colors = ["#639922" if r["agent_name"] == best_name else "#378ADD" for r in results]

fig = go.Figure(data=[
    go.Bar(
        x=agent_names, 
        y=scores, 
        marker_color=colors,
        text=scores,
        textposition='auto',
        textfont=dict(color='white', size=16, family="Inter")
    )
])
fig.update_layout(
    title="Recovery Score Comparison",
    title_font=dict(color="white", size=20, family="Inter"),
    plot_bgcolor="#0a0f1e",
    paper_bgcolor="#0a0f1e",
    xaxis=dict(tickfont=dict(color="white", size=14, family="Inter"), showgrid=False),
    yaxis=dict(title="Recovery Score", title_font=dict(color="white"), tickfont=dict(color="white"), range=[0, 100], gridcolor="rgba(255,255,255,0.1)"),
    margin=dict(t=60, b=30, l=30, r=30)
)
st.plotly_chart(fig, use_container_width=True, key="report_bar_chart")

st.markdown("### Detailed Agent Analysis")
for r in results:
    with st.expander(f"{r['agent_name']} — {r['treatment']} (Score: {r['recovery_score']})"):
        st.write("**Recommendation Summary:**")
        st.write(r["recommendation_summary"])
        st.write("**Reported Side Effects:**")
        for se in r["side_effects"]:
            st.write(f"- {se}")

# PDF Generation Function
def create_pdf(p_data, results, best_agent):
    pdf = FPDF()
    pdf.set_margins(10, 10, 10)
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 15, "MedMirror Clinical Decision Report", ln=True, align='C')
    pdf.ln(5)
    
    # Patient Data
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Patient Profile", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Name: {str(p_data['name'])} | Age: {str(p_data['age'])} | Gender: {str(p_data['gender'])}", ln=True)
    
    symptoms = ", ".join(p_data['symptoms']) if p_data['symptoms'] else "None"
    pdf.multi_cell(190, 8, f"Symptoms: {str(symptoms)}")
    
    conditions = ", ".join(p_data['conditions']) if p_data['conditions'] else "None"
    pdf.multi_cell(190, 8, f"Conditions: {str(conditions)}")
    
    pdf.cell(0, 8, f"Blood Pressure: {str(p_data['sys_bp'])}/{str(p_data['dia_bp'])} mmHg | Diabetes: {str(p_data['diabetes'])}", ln=True)
    pdf.ln(5)
    
    # Recommended Treatment
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Recommended Treatment: {str(best_agent['agent_name'])} - {str(best_agent['treatment'])}", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Recovery Score: {str(best_agent['recovery_score'])}/100", ln=True)
    pdf.multi_cell(190, 8, f"Summary: {str(best_agent['recommendation_summary'])}")
    pdf.ln(5)
    
    # All Agents
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Detailed Agent Analysis", ln=True)
    for r in results:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, f"{str(r['agent_name'])} ({str(r['treatment'])}) - Score: {str(r['recovery_score'])}", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(190, 6, f"24h: {str(r['outcome_24hr'])}")
        pdf.multi_cell(190, 6, f"7d: {str(r['outcome_7day'])}")
        pdf.multi_cell(190, 6, f"30d: {str(r['outcome_30day'])}")
        pdf.cell(0, 6, f"Risk Level: {str(r['risk_level'].upper())}", ln=True)
        pdf.ln(3)
        
    return bytes(pdf.output())

st.markdown("<hr style='border-color: rgba(55,138,221,0.2); margin-top: 2rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)

col_left, col_right = st.columns(2)
with col_left:
    st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
    if st.button("🔄 Run New Simulation", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    pdf_bytes = create_pdf(p_data, results, best_agent)
    st.markdown('<div class="download-btn">', unsafe_allow_html=True)
    st.download_button(
        label="📥 Download Report as PDF",
        data=pdf_bytes,
        file_name=f"MedMirror_Report_{p_data['name'].replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
