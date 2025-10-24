import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS 
import pandas as pd
import numpy as np
import datetime
import os
import json 
from urllib.parse import urlparse

# --- Import Utilities ---
from feature_engineer import create_model_input_features 
from external_lookups import mock_whois_lookup
from reporting_engine import generate_full_detection_report 

# --- CONFIGURATION ---
MODEL_PATH = 'model/final_phishing_model_pipeline.joblib' 
LABEL_MAP = {0: 'Legitimate', 1: 'Suspected', 2: 'Phishing'}
APPLICATION_ID = os.environ.get('APP_ID', 'PS02-AIGR-XXXXXX') # Read ID from environment or use placeholder

app = Flask(__name__)
CORS(app) 

# --- Load Model ---
FINAL_MODEL_PIPELINE = None
# ... (Model Loading Logic remains the same, omitted for brevity) ...

try:
    if os.path.exists(MODEL_PATH):
        FINAL_MODEL_PIPELINE = joblib.load(MODEL_PATH) 
        print(f"AI Model loaded successfully from {MODEL_PATH}.")
    else:
        FALLBACK_PATH = 'final_phishing_model_pipeline.joblib'
        FINAL_MODEL_PIPELINE = joblib.load(FALLBACK_PATH) 
        print(f"AI Model loaded successfully from {FALLBACK_PATH} (FALLBACK).")
        
except Exception as e:
    print(f"\nFATAL ERROR: Could not load model pipeline. Prediction will fail.")
    print(f"Details: {e}")
    
# --- END Model Loading Logic ---

@app.route('/api/classify', methods=['POST'])
def classify_domain():
    """
    Endpoint to classify a new URL/domain and generate the complete detection report.
    Expected Input: {"url": "http://suspicious.in/login", "cse_domain": "airtel.in", "cse_name": "Airtel"}
    """
    if not FINAL_MODEL_PIPELINE:
        return jsonify({"error": "AI Model is not initialized. Check server logs."}), 503

    try:
        data = request.get_json()
        identified_url = data.get('url') # Input is now the full URL
        cse_domain = data.get('cse_domain')
        cse_name = data.get('cse_name')

        if not identified_url or not cse_domain or not cse_name:
             return jsonify({"error": "Missing one or more required inputs (url, cse_domain, cse_name)."}), 400

        # Extract domain from URL for external lookups
        identified_domain = urlparse(identified_url).netloc
        
        # 1. Fetch WHOIS data to get Domain Age (needed for Feature Engineering)
        whois_mock_result = mock_whois_lookup(identified_domain)
        domain_age_days = whois_mock_result["domain_age_days"]
        
        # 2. Feature Engineering
        input_df = create_model_input_features(
            identified_url, 
            cse_domain, 
            cse_name, 
            domain_age_days # Pass the WHOIS feature
        )

        # 3. Prediction
        prediction_id = FINAL_MODEL_PIPELINE.predict(input_df)[0]
        prediction_id = int(prediction_id) # Convert numpy.int64 to native Python int
        prediction_proba = FINAL_MODEL_PIPELINE.predict_proba(input_df)[0].tolist()

        # 4. Generate Full Report (Requirement 3.4 & Annexure B)
        report_json_string = generate_full_detection_report(
            identified_url=identified_url,
            cse_domain=cse_domain,
            cse_name=cse_name,
            model_prediction_id=prediction_id,
            model_confidence_scores=prediction_proba,
            application_id=APPLICATION_ID # Pass Application ID
        )
        
        report_data = json.loads(report_json_string) 

        # 5. Compile API Response
        response = {
            'prediction_id': prediction_id, 
            'label': LABEL_MAP.get(prediction_id),
            'report_data': report_data # Includes the full Annexure B data under 'submission_data'
        }
        
        # --- NOTE ---
        # The 'report_data["submission_data"]' structure can be used to generate
        # the required Excel file upon submission completion.
        
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
    print("\n--- Starting Flask AI Backend ---")
    print("API is available at http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)