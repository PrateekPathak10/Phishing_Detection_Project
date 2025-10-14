import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS 
import pandas as pd
import numpy as np
import datetime
import os
import json # <-- Added this import, though it might be present in your local file

# --- Import Utilities ---
from feature_engineer import create_model_input_features 
from external_lookups import mock_whois_lookup, mock_dns_geoip_lookup
from reporting_engine import generate_full_detection_report # Imports the report generation logic

# --- CONFIGURATION ---
# Assumes the model is saved in a 'model' subdirectory. Adjust path if necessary.
MODEL_PATH = 'model/final_phishing_model_pipeline.joblib' 
LABEL_MAP = {0: 'Legitimate', 1: 'Suspected', 2: 'Phishing'}

app = Flask(__name__)
# Enable CORS for local development to allow the React frontend to communicate with this API
CORS(app) 

# --- Load Model ---
# The model pipeline must be loaded once when the application starts
FINAL_MODEL_PIPELINE = None
try:
    # Look for the model file in the current working directory or subdirectories
    if os.path.exists(MODEL_PATH):
        FINAL_MODEL_PIPELINE = joblib.load(MODEL_PATH) 
        print(f"AI Model loaded successfully from {MODEL_PATH}.")
    else:
        # Fallback for local testing if model isn't in 'model/'
        FALLBACK_PATH = 'final_phishing_model_pipeline.joblib'
        FINAL_MODEL_PIPELINE = joblib.load(FALLBACK_PATH) 
        print(f"AI Model loaded successfully from {FALLBACK_PATH} (FALLBACK).")
        
except Exception as e:
    print(f"\nFATAL ERROR: Could not load model pipeline. Prediction will fail.")
    print(f"Details: {e}")


@app.route('/api/classify', methods=['POST'])
def classify_domain():
    """
    Endpoint to classify a new domain and generate the complete detection report.
    This fulfills the core AI/ML engine and reporting requirements (3.1 & 3.4).
    """
    if not FINAL_MODEL_PIPELINE:
        return jsonify({"error": "AI Model is not initialized. Check server logs."}), 503

    try:
        # Expected input: {"domain": "suspicious.in", "cse_domain": "airtel.in", "cse_name": "Airtel"}
        data = request.get_json()
        identified_domain = data.get('domain')
        cse_domain = data.get('cse_domain')
        cse_name = data.get('cse_name')

        if not identified_domain or not cse_domain or not cse_name:
             return jsonify({"error": "Missing one or more required inputs (domain, cse_domain, cse_name)."}), 400

        # 1. Feature Engineering
        input_df = create_model_input_features(identified_domain, cse_domain, cse_name)

        # 2. Prediction
        prediction_id = FINAL_MODEL_PIPELINE.predict(input_df)[0]
        
        # --- FIX: Convert numpy.int64 to native Python int ---
        prediction_id = int(prediction_id) # <-- CRITICAL FIX

        # Convert numpy array of probabilities to a native Python list
        prediction_proba = FINAL_MODEL_PIPELINE.predict_proba(input_df)[0].tolist()

        # 3. Generate Full Report (Requirement 3.4)
        # This function fetches all mock external data (WHOIS, DNS) and formats the final JSON string.
        report_json_string = generate_full_detection_report(
            identified_domain=identified_domain,
            cse_domain=cse_domain,
            cse_name=cse_name,
            model_prediction_id=prediction_id,
            model_confidence_scores=prediction_proba
        )
        
        # Parse the JSON string back into a Python object for the final API response
        report_data = json.loads(report_json_string) 

        # 4. Compile API Response for the Frontend
        # The 'prediction_id' here is already a native int due to the fix above
        response = {
            # Core Prediction Results
            'prediction_id': prediction_id, 
            'label': LABEL_MAP.get(prediction_id),
            
            # Detailed Report (Including all external attributes)
            'report_data': report_data
        }
        
        return jsonify(response)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to process request due to internal server error: {str(e)}"}), 500


@app.route('/', methods=['GET'])
def server_status():
    """Simple status check endpoint."""
    return jsonify({"status": "AI Backend Service Running", "model_loaded": FINAL_MODEL_PIPELINE is not None})


if __name__ == '__main__':
    # Flask startup command for local testing.
    # The frontend will call this endpoint (e.g., http://127.0.0.1:5000/api/classify)
    print("\n--- Starting Flask AI Backend ---")
    print("API is available at http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
