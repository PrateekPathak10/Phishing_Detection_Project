from external_lookups import mock_whois_lookup, mock_dns_geoip_lookup
import json
from datetime import datetime

# Define the label map for human-readable output
LABEL_MAP = {0: 'Legitimate', 1: 'Suspected', 2: 'Phishing'}

def generate_full_detection_report(
    identified_domain, 
    cse_domain, 
    cse_name, 
    model_prediction_id, 
    model_confidence_scores,
    reclassification_data=None # Used if domain was moved from Suspected to Phishing
):
    """
    Compiles all required information into a comprehensive report (Requirement 3.4).

    Args:
        identified_domain (str): The suspicious domain being checked.
        cse_domain (str): The genuine domain of the target CSE.
        cse_name (str): The name of the Critical Sector Entity.
        model_prediction_id (int): The final label (0, 1, or 2).
        model_confidence_scores (list): Probabilities for [0, 1, 2].
        reclassification_data (dict, optional): Details if the domain was reclassified.

    Returns:
        str: A JSON formatted string containing the complete report.
    """
    
    # --- 1. Fetch External Data ---
    whois_data = mock_whois_lookup(identified_domain)
    dns_data = mock_dns_geoip_lookup(identified_domain)
    
    # --- 2. Compile Report Structure ---
    report = {
        "report_id": f"REPORT-{int(datetime.now().timestamp())}",
        "analysis_timestamp": datetime.now().isoformat(),
        
        # Mapping (Requirement 3.2)
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
            "reclassification_details": reclassification_data if reclassification_data else "N/A"
        },
        
        # Attributes (Requirement 3.4)
        "domain_attributes": {
            "identified_domain": identified_domain,
            "creation_date_time": whois_data["domain_creation_date"],
            "registrar_info": whois_data["registrar_info"],
            "is_privacy_protected": whois_data["is_privacy_protected"]
        },
        
        "network_attributes": {
            "ip_address": dns_data["ip_address"],
            "subnet_info": dns_data["subnet_info"],
            "geo_location": dns_data["geo_location"],
            "ip_reputation_score": dns_data["ip_reputation_score"]
        }
    }
    
    # Return the report as a neatly formatted JSON string
    return json.dumps(report, indent=4)
