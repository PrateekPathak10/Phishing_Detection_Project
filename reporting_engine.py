from external_lookups import mock_whois_lookup, mock_dns_geoip_lookup
import json
from datetime import datetime
from urllib.parse import urlparse # Make sure this import is present

# Define the label map for human-readable output
LABEL_MAP = {0: 'Legitimate', 1: 'Suspected', 2: 'Phishing'}

def generate_full_detection_report(
    identified_url, 
    cse_domain, 
    cse_name, 
    model_prediction_id, 
    model_confidence_scores,
    reclassification_data=None, # Accepts None for initial classification
    application_id="PS02-AIGR-XXXXXX" 
):
    """
    Compiles all required information into a comprehensive report (Requirement 3.4 & Annexure B).
    """
    
    # Extract domain from URL
    identified_domain = urlparse(identified_url).netloc
    
    # --- 1. Fetch External Data ---
    whois_data = mock_whois_lookup(identified_domain)
    dns_data = mock_dns_geoip_lookup(identified_domain)
    
    detection_date = datetime.now()
    
    # --- 2. Create a SAFE dictionary for reclassification details ---
    # This prevents calling .get() on None later in the code.
    safe_reclassification = reclassification_data if isinstance(reclassification_data, dict) else {}
    
    # --- 3. Compile Report Structure (Aligned with Annexure B columns) ---
    report = {
        "report_id": f"REPORT-{int(detection_date.timestamp())}",
        "analysis_timestamp": detection_date.isoformat(),
        
        "critical_sector_entity": cse_name, 
        "genuine_cse_domain": cse_domain, 
        
        # Classification Result
        "final_classification": LABEL_MAP[model_prediction_id],
        "classification_id": model_prediction_id,
        "maliciousness_information": {
            "model_confidence": {
                "legitimate_score": f"{model_confidence_scores[0]:.4f}",
                "suspected_score": f"{model_confidence_scores[1]:.4f}",
                "phishing_score": f"{model_confidence_scores[2]:.4f}"
            },
            # Use the original reclassification_data for the report structure
            "reclassification_details": reclassification_data if reclassification_data else "N/A"
        },
        
        # NOTE: Include domain_attributes structure for the frontend's safety checks (Privacy Protected)
        "domain_attributes": {
            "identified_domain": identified_domain,
            "is_privacy_protected": whois_data["is_privacy_protected"]
        },
        
        # --- Annexure B Columns (Data for Excel Submission) ---
        "submission_data": {
            "application_id": application_id, 
            # Use safe_reclassification to call .get() safely
            "source_of_detection": safe_reclassification.get("source_of_detection", "AI Model"),
            "identified_domain_name": identified_domain, 
            "corresponding_cse_domain_name": cse_domain, 
            "critical_sector_entity": cse_name, 
            "phishing_suspected_domains_class_label": LABEL_MAP[model_prediction_id],
            
            # WHOIS Data
            "domain_registration_date": whois_data["domain_creation_date"], 
            "registrar_name": whois_data["registrar_name"], 
            "registrant_name_org": whois_data["registrant_name_org"], 
            "registrant_country": whois_data["registrant_country"], 
            
            # DNS/Hosting Data
            "name_servers": ", ".join(dns_data["name_servers"]), 
            "hosting_ip": dns_data["ip_address"], 
            "hosting_isp": dns_data["hosting_isp"], 
            "hosting_country": dns_data["geo_location"].split(', ')[-1], 
            "dns_records": json.dumps(dns_data["dns_records"]), 
            
            # Detection Details
            "evidence_file_name": f"{cse_name}_{identified_domain}_SNo.pdf", 
            "date_of_detection": detection_date.strftime("%d-%m-%Y"), 
            "time_of_detection": detection_date.strftime("%H-%M-%S"), 
            # Use safe_reclassification here
            "date_of_post": safe_reclassification.get("date_of_post", "N/A"), 
            # Use safe_reclassification here
            "remarks": safe_reclassification.get("detection_reason", "Initial Classification/N/A")
        }
    }
    
    # Return the report as a neatly formatted JSON string
    return json.dumps(report, indent=4)