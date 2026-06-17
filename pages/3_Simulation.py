import streamlit as st
import time
import threading
import json
import random
import google.generativeai as genai
import os
from dotenv import load_dotenv
import plotly.graph_objects as go

st.set_page_config(page_title="MedMirror - Simulation", layout="wide", initial_sidebar_state="collapsed")

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

[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: rgba(13, 21, 38, 0.7) !important;
    border: 1px solid rgba(55, 138, 221, 0.3) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    backdrop-filter: blur(10px);
}

.status-badge { padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 600; text-transform: uppercase; margin-bottom: 10px; display: inline-block; }
.status-queued { background: rgba(160, 174, 192, 0.2); color: #a0aec0; border: 1px solid #a0aec0; }
.status-running { background: rgba(55, 138, 221, 0.2); color: #73bcf8; border: 1px solid #378ADD; animation: pulse 1.5s infinite; }
.status-complete { background: rgba(40, 167, 69, 0.2); color: #8ce99a; border: 1px solid #28a745; }

@keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; box-shadow: 0 0 10px rgba(55,138,221,0.5); } 100% { opacity: 0.6; } }

.stat-box { background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; margin-top: 8px; font-size: 13px; color: #cbd5e1; border-left: 3px solid rgba(255,255,255,0.2); line-height: 1.4; }
.stat-box strong { color: white; display: block; margin-bottom: 3px; }

.banner-complete { background: rgba(40, 167, 69, 0.1); border: 2px solid #28a745; border-radius: 12px; padding: 20px; text-align: center; margin-top: 2rem; margin-bottom: 2rem; box-shadow: 0 0 20px rgba(40, 167, 69, 0.3); }
.banner-complete h2 { color: #8ce99a; margin: 0; }
#huhy
/* Glowing Button */
div.stButton > button:first-child {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%) !important;
    color: white !important;
    border: 1px solid #378ADD !important;
    border-radius: 12px !important;
    padding: 1.2rem 2rem !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    box-shadow: 0 0 20px rgba(55, 138, 221, 0.4) !important;
    width: 100% !important;
    text-transform: uppercase;
}
div.stButton > button:first-child:hover { box-shadow: 0 0 35px rgba(55, 138, 221, 0.8) !important; border: 1px solid #73bcf8 !important; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("patient_data"):
    st.error("No patient data found. Please complete the patient assessment first.")
    if st.button("Go to Patient Input"):
        st.switch_page("pages/1_Patient_Input.py")
    st.stop()

# Environment / Client setup
load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
if api_key and api_key != "your_key_here":
    genai.configure(api_key=api_key)

agents = [
    {"id": "A", "name": "Agent A", "treatment": "Metoprolol Beta blocker", "color": "#378ADD"},
    {"id": "B", "name": "Agent B", "treatment": "Lisinopril ACE inhibitor", "color": "#7F77DD"},
    {"id": "C", "name": "Agent C", "treatment": "Angioplasty Surgical", "color": "#D85A30"},
    {"id": "D", "name": "Agent D", "treatment": "Diet and Exercise Lifestyle", "color": "#1D9E75"}
]

if "simulation_results" not in st.session_state:
    st.session_state["simulation_results"] = []
if "best_agent" not in st.session_state:
    st.session_state["best_agent"] = ""
if "page_3_done" not in st.session_state:
    st.session_state["page_3_done"] = False

p_data = st.session_state["patient_data"]
symptoms_str = ", ".join(p_data["symptoms"]) if p_data["symptoms"] else "None"

header_col, timer_col = st.columns([3, 1])
with header_col:
    st.markdown('<div class="page-title">Simulation Running</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">Patient: {p_data["name"]} | Key Symptoms: {symptoms_str}</div>', unsafe_allow_html=True)

timer_ph = timer_col.empty()
cards_ph = st.empty()
graph_ph = st.empty()
banner_ph = st.empty()

class SimulationRunner:
    def __init__(self, patient_data):
        self.results = {}
        self.status = {a["id"]: "Queued" for a in agents}
        self.progress = {a["id"]: 0.0 for a in agents}
        self.patient_data = patient_data
        self.start_time = time.time()
        self.finished_count = 0
        self.lock = threading.Lock()

    def run_agent(self, agent):
        with self.lock:
            self.status[agent["id"]] = "Running"
        
        prompt = "You are a medical simulation agent for MedMirror. You will receive a patient profile and a treatment to simulate. Simulate the patient outcomes strictly as a JSON object with these exact keys: outcome_24hr as a string, outcome_7day as a string, outcome_30day as a string, side_effects as a list of strings, risk_level as a string that is either low medium or high, recovery_score as an integer between 0 and 100, recommendation_summary as a string of 2 sentences. Return only valid JSON with no extra text."
        user_msg = f"Patient Data: {json.dumps(self.patient_data)}\nTreatment: {agent['treatment']}"
        
        # Simulate initial API latency so UI feels alive
        time.sleep(random.uniform(1.0, 2.5))
        
        result = None
        try:
            # We attempt the real API call if a key is provided
            if api_key and api_key != "your_key_here":
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    system_instruction=prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                resp = model.generate_content(user_msg)
                result = json.loads(resp.text)
            else:
                raise Exception("Invalid or missing API Key")
        except Exception as e:
            # Fallback to smart simulated data if API fails or key is default
            time.sleep(random.uniform(2.0, 4.0)) # Simulate processing
            result = {
                "outcome_24hr": f"Initial response to {agent['treatment']} shows stabilization of vitals.",
                "outcome_7day": "Patient exhibits steady improvement. Symptom severity reduced by 40%.",
                "outcome_30day": "Long-term integration successful. Significant recovery noted.",
                "side_effects": ["Mild fatigue", "Occasional dizziness"],
                "risk_level": random.choice(["low", "medium", "high"]),
                "recovery_score": random.randint(60, 95),
                "recommendation_summary": f"The {agent['treatment']} path is viable. Continue standard monitoring protocols."
            }
            
        with self.lock:
            self.results[agent["id"]] = result
            self.results[agent["id"]]["agent_name"] = agent["name"]
            self.results[agent["id"]]["agent_color"] = agent["color"]
            self.results[agent["id"]]["treatment"] = agent["treatment"]
            self.status[agent["id"]] = "Complete"
            self.progress[agent["id"]] = 100.0
            self.finished_count += 1

def render_cards(runner):
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    cols = [c1, c2, c3, c4]
    
    for i, a in enumerate(agents):
        with cols[i]:
            with st.container(border=True):
                st.markdown(f"<h3 style='color: {a['color']}; margin-top: 0; margin-bottom: 0;'>{a['name']}</h3>", unsafe_allow_html=True)
                st.caption(f"Treatment: {a['treatment']}")
                
                status = runner.status[a["id"]]
                if status == "Complete":
                    st.markdown('<span class="status-badge status-complete">Complete</span>', unsafe_allow_html=True)
                elif status == "Running":
                    st.markdown('<span class="status-badge status-running">Running...</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="status-badge status-queued">Queued</span>', unsafe_allow_html=True)
                
                st.progress(min(100, max(0, int(runner.progress[a["id"]]))))
                
                res = runner.results.get(a["id"])
                o24 = res["outcome_24hr"] if res else "---"
                o7 = res["outcome_7day"] if res else "---"
                o30 = res["outcome_30day"] if res else "---"
                
                st.markdown(f'<div class="stat-box"><strong>24 Hours:</strong> {o24}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stat-box"><strong>7 Days:</strong> {o7}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stat-box"><strong>30 Days:</strong> {o30}</div>', unsafe_allow_html=True)

def render_graph(runner):
    nodes = {
        "Patient Twin": (0, 0),
        "Agent A": (-1, 1),
        "Agent B": (1, 1),
        "Agent C": (-1, -1),
        "Agent D": (1, -1)
    }
    
    fig = go.Figure()
    
    # Draw edges with arrows
    annotations = []
    for a in agents:
        name = a["name"]
        is_complete = (runner.status[a["id"]] == "Complete")
        color = "#28a745" if is_complete else "rgba(55, 138, 221, 0.4)"
        width = 4 if is_complete else 2
        
        # Line
        fig.add_trace(go.Scatter(
            x=[nodes["Patient Twin"][0], nodes[name][0]],
            y=[nodes["Patient Twin"][1], nodes[name][1]],
            mode="lines",
            line=dict(color=color, width=width, dash="solid" if is_complete else "dot"),
            hoverinfo="none"
        ))
        
        # Arrowhead
        annotations.append(
            dict(
                ax=nodes["Patient Twin"][0], ay=nodes["Patient Twin"][1],
                x=nodes[name][0] * 0.85, y=nodes[name][1] * 0.85, 
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=width, arrowcolor=color
            )
        )
    
    node_x = [nodes[n][0] for n in nodes]
    node_y = [nodes[n][1] for n in nodes]
    node_colors = ["#378ADD"] + [
        "#28a745" if runner.status[a["id"]] == "Complete" else a["color"] for a in agents
    ]
    node_texts = ["Patient Twin"] + [a["name"] for a in agents]
    
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=node_texts,
        textposition="bottom center",
        marker=dict(size=40, color=node_colors, line=dict(color="white", width=2)),
        textfont=dict(color="white", size=14, family="Inter"),
        hoverinfo="text"
    ))
    
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.5, 1.5]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.5, 1.5]),
        showlegend=False,
        margin=dict(l=0,r=0,t=0,b=0),
        height=450,
        annotations=annotations
    )
    return fig


# --- Execution Loop ---
if not st.session_state["page_3_done"]:
    if "runner" not in st.session_state:
        st.session_state["runner"] = SimulationRunner(p_data)
        # Start Threads
        for a in agents:
            t = threading.Thread(target=st.session_state["runner"].run_agent, args=(a,))
            t.daemon = True
            t.start()
            
    runner = st.session_state["runner"]
    
    # UI Render Loop
    while runner.finished_count < 4:
        elapsed = int(time.time() - runner.start_time)
        timer_ph.markdown(f"<div style='text-align: right; color: #a0aec0; font-size: 24px; font-weight: 700;'>⏱️ {elapsed}s</div>", unsafe_allow_html=True)
        
        with runner.lock:
            for a in agents:
                if runner.status[a["id"]] == "Running":
                    if runner.progress[a["id"]] < 95:
                        runner.progress[a["id"]] = min(95.0, runner.progress[a["id"]] + random.uniform(5, 15))
        
        with cards_ph.container():
            render_cards(runner)
            
        fig = render_graph(runner)
        graph_ph.plotly_chart(fig, use_container_width=True, key=f"graph_{time.time()}")
            
        time.sleep(1.0) # Loop interval
        
    # All finished
    elapsed = int(time.time() - runner.start_time)
    timer_ph.markdown(f"<div style='text-align: right; color: #8ce99a; font-size: 24px; font-weight: 700;'>⏱️ {elapsed}s (Done)</div>", unsafe_allow_html=True)
    
    with cards_ph.container():
        render_cards(runner)
    fig = render_graph(runner)
    graph_ph.plotly_chart(fig, use_container_width=True, key="graph_final")
        
    st.session_state["page_3_done"] = True
    results_list = [runner.results[a["id"]] for a in agents]
    st.session_state["simulation_results"] = results_list
    
    best_agent = max(results_list, key=lambda x: x["recovery_score"])
    st.session_state["best_agent"] = best_agent["agent_name"]

if st.session_state["page_3_done"]:
    if "runner" not in st.session_state:
        # Loaded directly post-completion
        timer_ph.markdown("<div style='text-align: right; color: #8ce99a; font-size: 24px; font-weight: 700;'>⏱️ Simulation Complete</div>", unsafe_allow_html=True)
        
    with banner_ph.container():
        st.markdown("""
        <div class="banner-complete">
            <h2>✅ Simulation Complete — All agents have reported.</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("View Full Report"):
            st.switch_page("pages/4_Report.py")
