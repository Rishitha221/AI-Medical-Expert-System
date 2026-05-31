# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import random
from typing import Dict, List, Set, Tuple

app = Flask(__name__)
CORS(app)

class MedicalExpertSystem:
    def __init__(self):
        self.rules = [
            ({"fever", "cough", "fatigue"}, ("Common Cold", 0.7)),
            ({"fever", "cough", "shortness_of_breath"}, ("COVID-19", 0.8)),
            ({"fever", "headache", "stiff_neck"}, ("Meningitis", 0.9)),
            ({"fever", "rash", "joint_pain"}, ("Dengue Fever", 0.75)),
            ({"fever", "sore_throat", "swollen_lymph_nodes"}, ("Strep Throat", 0.8)),
            ({"cough", "wheezing", "shortness_of_breath"}, ("Asthma", 0.85)),
            ({"cough", "chest_pain", "fever"}, ("Pneumonia", 0.8)),
            ({"nausea", "vomiting", "diarrhea"}, ("Gastroenteritis", 0.8)),
            ({"abdominal_pain", "nausea", "fever"}, ("Appendicitis", 0.85)),
            ({"headache", "sensitivity_to_light", "nausea"}, ("Migraine", 0.8)),
            ({"dizziness", "nausea", "sweating"}, ("Vertigo", 0.75)),
            ({"fever", "cough", "body_aches"}, ("Influenza", 0.8)),
            ({"fatigue", "weight_loss", "increased_thirst"}, ("Diabetes", 0.7)),
            ({"chest_pain", "shortness_of_breath", "sweating"}, ("Heart Attack", 0.9)),
        ]
        
        self.symptoms_db = {
            "fever": "Elevated body temperature (>37.5°C)",
            "cough": "Sudden expulsion of air from lungs",
            "fatigue": "Extreme tiredness or lack of energy",
            "shortness_of_breath": "Difficulty breathing or feeling breathless",
            "headache": "Pain in any region of the head",
            "stiff_neck": "Difficulty moving the neck, especially bending forward",
            "rash": "Change in skin color or texture",
            "joint_pain": "Discomfort in one or more joints",
            "sore_throat": "Pain, scratchiness or irritation of the throat",
            "swollen_lymph_nodes": "Enlarged lymph nodes, usually in neck",
            "wheezing": "High-pitched whistling sound when breathing",
            "chest_pain": "Discomfort or pain in the chest area",
            "nausea": "Feeling of sickness with an inclination to vomit",
            "vomiting": "Forcible emptying of stomach contents",
            "diarrhea": "Loose, watery bowel movements",
            "abdominal_pain": "Pain in the belly region",
            "sensitivity_to_light": "Discomfort or pain in bright light",
            "dizziness": "Sensation of spinning or lightheadedness",
            "sweating": "Production of sweat beyond normal levels",
            "body_aches": "Generalized pain in muscles and joints",
            "weight_loss": "Unintentional reduction in body weight",
            "increased_thirst": "Feeling unusually thirsty",
        }
        
        self.treatments = {
            "Common Cold": "Rest, fluids, over-the-counter cold medication",
            "COVID-19": "Isolation, rest, medical consultation, possibly antiviral medication",
            "Meningitis": "Immediate medical attention, antibiotics, hospitalization",
            "Dengue Fever": "Rest, fluids, pain relievers (avoid aspirin), medical monitoring",
            "Strep Throat": "Antibiotics, rest, warm liquids, throat lozenges",
            "Asthma": "Bronchodilators, inhaled corticosteroids, avoiding triggers",
            "Pneumonia": "Antibiotics, rest, fluids, medical supervision",
            "Gastroenteritis": "Hydration, rest, bland diet, possibly antiemetics",
            "Appendicitis": "Immediate medical attention, usually surgery",
            "Migraine": "Rest in dark room, pain relievers, migraine-specific medication",
            "Vertigo": "Balance exercises, medication for nausea/dizziness",
            "Influenza": "Rest, fluids, antiviral medication if early",
            "Diabetes": "Blood sugar monitoring, insulin or oral medication, diet control",
            "Heart Attack": "Emergency medical care, aspirin, nitroglycerin",
        }

    def get_all_symptoms(self):
        return [{"id": symptom, "name": symptom.replace('_', ' ').title(), "description": desc} 
                for symptom, desc in self.symptoms_db.items()]

    def diagnose(self, patient_symptoms):
        possible_diagnoses = []
        
        for condition, (diagnosis, base_confidence) in self.rules:
            matched_symptoms = condition.intersection(set(patient_symptoms))
            match_ratio = len(matched_symptoms) / len(condition)
            
            if match_ratio >= 0.6:
                adjusted_confidence = base_confidence * match_ratio
                possible_diagnoses.append({
                    "diagnosis": diagnosis,
                    "confidence": round(adjusted_confidence, 2),
                    "matched_symptoms": list(matched_symptoms),
                    "total_symptoms_required": len(condition),
                    "match_ratio": round(match_ratio, 2)
                })
        
        possible_diagnoses.sort(key=lambda x: x["confidence"], reverse=True)
        return possible_diagnoses

    def explain_reasoning(self, diagnosis_result):
        diagnosis = diagnosis_result["diagnosis"]
        confidence = diagnosis_result["confidence"]
        matched = diagnosis_result["matched_symptoms"]
        total_required = diagnosis_result["total_symptoms_required"]
        
        explanation = {
            "diagnosis": diagnosis,
            "confidence": confidence,
            "matched_symptoms": [s.replace('_', ' ').title() for s in matched],
            "total_required": total_required,
            "match_percentage": diagnosis_result["match_ratio"] * 100
        }
        return explanation

    def get_treatment_plan(self, diagnosis):
        return self.treatments.get(diagnosis, "Consult a healthcare professional for specific treatment advice.")

expert_system = MedicalExpertSystem()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    return jsonify(expert_system.get_all_symptoms())

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    data = request.json
    symptoms = data.get('symptoms', [])
    
    if not symptoms:
        return jsonify({"error": "No symptoms provided"}), 400
    
    diagnoses = expert_system.diagnose(symptoms)
    
    # Add reasoning and treatment to each diagnosis
    for diagnosis in diagnoses:
        diagnosis['reasoning'] = expert_system.explain_reasoning(diagnosis)
        diagnosis['treatment'] = expert_system.get_treatment_plan(diagnosis['diagnosis'])
    
    return jsonify({
        "symptoms_entered": [s.replace('_', ' ').title() for s in symptoms],
        "diagnoses": diagnoses
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')