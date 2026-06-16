from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import os
import json
import time
import random
import threading
from dotenv import load_dotenv
import google.generativeai as genai
import plotly.graph_objects as go
from fpdf import FPDF

# Load environment variables
load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
if api_key and api_key != "your_key_here":
    genai.configure(api_key=api_key)

# In-memory thread-safe simulation storage
SIMULATIONS = {}
SIMULATIONS_LOCK = threading.Lock()

AGENTS = [
    {"id": "A", "name": "Agent A", "treatment": "Metoprolol Beta blocker", "color": "#378ADD"},
    {"id": "B", "name": "Agent B", "treatment": "Lisinopril ACE inhibitor", "color": "#7F77DD"},
    {"id": "C", "name": "Agent C", "treatment": "Angioplasty Surgical", "color": "#D85A30"},
    {"id": "D", "name": "Agent D", "treatment": "Diet and Exercise Lifestyle", "color": "#1D9E75"}
]

def landing_view(request):
    return render(request, 'medmirror/landing.html')

def patient_input_view(request):
    errors = []
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        age = int(request.POST.get('age', 50))
        gender = request.POST.get('gender', 'Male')
        symptoms = request.POST.getlist('symptoms')
        diabetes = request.POST.get('diabetes', 'No')
        sys_bp = int(request.POST.get('sys_bp', 120))
        dia_bp = int(request.POST.get('dia_bp', 80))
        conditions = request.POST.getlist('conditions')
        meds = request.POST.get('medications', '').strip()

        if not name:
            errors.append("Validation Error: Patient Name cannot be empty.")
        if not symptoms:
            errors.append("Validation Error: At least one symptom must be selected.")

        if not errors:
            request.session['patient_data'] = {
                "name": name, "age": age, "gender": gender, "symptoms": symptoms,
                "sys_bp": sys_bp, "dia_bp": dia_bp, "diabetes": diabetes, 
                "conditions": conditions, "medications": meds
            }
            # Clear previous simulation state
            if 'simulation_results' in request.session:
                del request.session['simulation_results']
            if 'best_agent' in request.session:
                del request.session['best_agent']
            return redirect('medmirror:mirror_world')

    # Default options for multiselects
    symptom_options = ["Chest Pain", "Shortness of Breath", "High Fever", "Fatigue", "Dizziness", "Nausea", "Severe Headache", "Abdominal Pain"]
    condition_options = ["Heart Disease", "Kidney Disease", "Liver Disease", "Asthma", "None"]

    return render(request, 'medmirror/patient_input.html', {
        'symptom_options': symptom_options,
        'condition_options': condition_options,
        'errors': errors
    })

def mirror_world_view(request):
    patient_data = request.session.get('patient_data')
    if not patient_data:
        return redirect('medmirror:patient_input')

    # Calculate risk profile
    risks = []
    if patient_data.get("diabetes") == "Yes":
        risks.append("Metabolic risk elevated")
    if "Chest Pain" in patient_data.get("symptoms", []):
        risks.append("Cardiac event risk detected")
    if patient_data.get("sys_bp", 120) > 140:
        risks.append("Hypertension risk flagged")
    if "Heart Disease" in patient_data.get("conditions", []):
        risks.append("Cardiovascular complication risk")

    return render(request, 'medmirror/mirror_world.html', {
        'patient_data': patient_data,
        'symptoms_str': ", ".join(patient_data.get("symptoms", [])),
        'conditions_str': ", ".join(patient_data.get("conditions", [])) if patient_data.get("conditions") else "None",
        'bp_str': f"{patient_data.get('sys_bp')} / {patient_data.get('dia_bp')} mmHg",
        'meds_str': patient_data.get("medications") if patient_data.get("medications") else "None",
        'risks': risks
    })

def run_agent_simulation(session_key, agent, patient_data):
    # Set agent to running
    with SIMULATIONS_LOCK:
        if session_key in SIMULATIONS:
            SIMULATIONS[session_key]['status'][agent['id']] = 'Running'
            SIMULATIONS[session_key]['progress'][agent['id']] = 10.0

    # Simulate latency
    time.sleep(random.uniform(1.5, 3.0))

    prompt = "You are a medical simulation agent for MedMirror. You will receive a patient profile and a treatment to simulate. Simulate the patient outcomes strictly as a JSON object with these exact keys: outcome_24hr as a string, outcome_7day as a string, outcome_30day as a string, side_effects as a list of strings, risk_level as a string that is either low medium or high, recovery_score as an integer between 0 and 100, recommendation_summary as a string of 2 sentences. Return only valid JSON with no extra text."
    user_msg = f"Patient Data: {json.dumps(patient_data)}\nTreatment: {agent['treatment']}"

    result = None
    try:
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
        # Fallback to simulated data
        time.sleep(random.uniform(2.0, 3.5))
        result = {
            "outcome_24hr": f"Initial response to {agent['treatment']} shows stabilization of vitals.",
            "outcome_7day": "Patient exhibits steady improvement. Symptom severity reduced by 40%.",
            "outcome_30day": "Long-term integration successful. Significant recovery noted.",
            "side_effects": ["Mild fatigue", "Occasional dizziness"],
            "risk_level": random.choice(["low", "medium", "high"]),
            "recovery_score": random.randint(60, 95),
            "recommendation_summary": f"The {agent['treatment']} path is viable. Continue standard monitoring protocols."
        }

    # Store results
    with SIMULATIONS_LOCK:
        if session_key in SIMULATIONS:
            result["agent_name"] = agent["name"]
            result["agent_color"] = agent["color"]
            result["treatment"] = agent["treatment"]
            
            SIMULATIONS[session_key]['results'][agent['id']] = result
            SIMULATIONS[session_key]['status'][agent['id']] = 'Complete'
            SIMULATIONS[session_key]['progress'][agent['id']] = 100.0
            SIMULATIONS[session_key]['finished_count'] += 1

def simulation_view(request):
    patient_data = request.session.get('patient_data')
    if not patient_data:
        return redirect('medmirror:patient_input')

    # Save session to guarantee session key
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    # Initialize simulation states
    with SIMULATIONS_LOCK:
        SIMULATIONS[session_key] = {
            'status': {a['id']: 'Queued' for a in AGENTS},
            'progress': {a['id']: 0.0 for a in AGENTS},
            'results': {},
            'finished_count': 0,
            'started_time': time.time()
        }

    # Start simulation threads
    for agent in AGENTS:
        t = threading.Thread(target=run_agent_simulation, args=(session_key, agent, patient_data))
        t.daemon = True
        t.start()

    symptoms_str = ", ".join(patient_data.get("symptoms", []))
    return render(request, 'medmirror/simulation.html', {
        'patient_data': patient_data,
        'symptoms_str': symptoms_str,
        'agents': AGENTS
    })

def simulation_status_api(request):
    session_key = request.session.session_key
    if not session_key or session_key not in SIMULATIONS:
        return JsonResponse({'error': 'No simulation active'}, status=400)

    sim = SIMULATIONS[session_key]
    elapsed = int(time.time() - sim['started_time'])

    # Proactively increment progress on running agents to make the UI look alive
    with SIMULATIONS_LOCK:
        for a in AGENTS:
            a_id = a['id']
            if sim['status'][a_id] == 'Running':
                if sim['progress'][a_id] < 95.0:
                    sim['progress'][a_id] = min(95.0, sim['progress'][a_id] + random.uniform(5, 12))

    # Check if finished
    is_finished = (sim['finished_count'] == 4)

    if is_finished:
        # Save results to session
        results_list = [sim['results'][a['id']] for a in AGENTS]
        request.session['simulation_results'] = results_list
        best_agent = max(results_list, key=lambda x: x["recovery_score"])
        request.session['best_agent'] = best_agent["agent_name"]
        
        # Clean up in-memory simulation tracker
        # (Don't delete immediately to allow final poll return success)
        # We can clean it up after a delay, or just leave it since it's local

    return JsonResponse({
        'status': sim['status'],
        'progress': sim['progress'],
        'results': sim['results'],
        'finished_count': sim['finished_count'],
        'elapsed': elapsed,
        'is_finished': is_finished
    })

def report_view(request):
    patient_data = request.session.get('patient_data')
    results = request.session.get('simulation_results')
    best_name = request.session.get('best_agent')

    if not patient_data or not results or not best_name:
        return redirect('medmirror:patient_input')

    best_agent = next(r for r in results if r["agent_name"] == best_name)

    # Generate Plotly comparison chart
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
    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    # Setup colors for detailed items
    for r in results:
        r['risk_upper'] = r['risk_level'].upper()
        if r['risk_level'].lower() == 'low':
            r['risk_class'] = 'risk-low'
        elif r['risk_level'].lower() == 'medium':
            r['risk_class'] = 'risk-medium'
        else:
            r['risk_class'] = 'risk-high'

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    return render(request, 'medmirror/report.html', {
        'patient_data': patient_data,
        'results': results,
        'best_agent': best_agent,
        'chart_html': chart_html,
        'timestamp': timestamp
    })

def download_pdf_view(request):
    p_data = request.session.get('patient_data')
    results = request.session.get('simulation_results')
    best_name = request.session.get('best_agent')

    if not p_data or not results or not best_name:
        return HttpResponse("No report data found in session.", status=400)

    best_agent = next(r for r in results if r["agent_name"] == best_name)

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
        
    pdf_bytes = pdf.output(dest='S')
    # In newer fpdf2 versions, output(dest='S') returns a bytearray/bytes,
    # or output() directly returns bytes if no dest is provided. Let's make sure it handles bytes:
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin1')
    elif isinstance(pdf_bytes, bytearray):
        pdf_bytes = bytes(pdf_bytes)

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="MedMirror_Report_{p_data["name"].replace(" ", "_")}.pdf"'
    return response

def reset_view(request):
    request.session.clear()
    return redirect('medmirror:landing')
