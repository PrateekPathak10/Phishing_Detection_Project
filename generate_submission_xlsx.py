import pandas as pd
import json
import os
from datetime import datetime
from urllib.parse import urlparse
import random


from external_lookups import mock_whois_lookup, mock_dns_geoip_lookup
from reporting_engine import generate_full_detection_report, LABEL_MAP


APPLICATION_ID = "PS02-AIGR-S68411" 
OUTPUT_FILENAME = f"PS-02_{APPLICATION_ID}_Submission_Set.xlsx"


def mock_classify_domain(identified_url, cse_domain, cse_name):
    """
    Simulates the model prediction and report generation steps.
    (Content is identical to the version provided in the previous response)
    """
    if 'legit' in identified_url:
        prediction_id = 0
        confidence = [0.9, 0.05, 0.05]
    elif 'suspected' in identified_url or identified_url.endswith('.club'):
        prediction_id = 1
        confidence = [0.1, 0.75, 0.15]
    else: 
        prediction_id = 2
        confidence = [0.05, 0.1, 0.85]
        
    report_json_string = generate_full_detection_report(
        identified_url=identified_url,
        cse_domain=cse_domain,
        cse_name=cse_name,
        model_prediction_id=prediction_id,
        model_confidence_scores=confidence,
        application_id=APPLICATION_ID 
    )
    return json.loads(report_json_string)

def load_and_run_shortlisting_data():
    """
    Simulates loading the shortlisting data and running the classification.
    (Content is identical to the version provided in the previous response)
    """
    shortlisting_data = [
        {'url': 'https://sbi-login-safe.top/auth', 'cse_domain': 'onlinesbi.co.in', 'cse_name': 'State Bank of India (SBI)'},
        {'url': 'http://icicicard-logins.xyz/secure/verify.php', 'cse_domain': 'icicibank.com', 'cse_name': 'ICICI Bank'},
        {'url': 'https://airtelrechargemobile.club', 'cse_domain': 'airtel.in', 'cse_name': 'Airtel'},
        {'url': 'http://nic-government-suspected.app', 'cse_domain': 'nic.in', 'cse_name': 'National Informatics Centre (NIC)'},
        {'url': 'https://www.hdfcbank.com/personal', 'cse_domain': 'hdfcbank.com', 'cse_name': 'HDFC Bank'},
    ]
    
    all_reports = []
    for entry in shortlisting_data:
        report = mock_classify_domain(entry['url'], entry['cse_domain'], entry['cse_name'])
        if report.get('classification_id') in [1, 2]:
            all_reports.append(report)
            
    return all_reports


OFFICIAL_HEADERS = [
    'Application_ID',
    'Source of detection',
    'Identified Phishing/Suspected Domain Name',
    'Corresponding CSE Domain Name',
    'Critical Sector Entity Name',
    'Phishing/Suspected Domains (i.e. Class Label)',
    'Domain Registration Date',
    'Registrar Name',
    'Registrant Name or Registrant Organisation',
    'Registrant Country',
    'Name Servers',
    'Hosting IP',
    'Hosting ISP',
    'Hosting Country',
    'DNS Records (if any)',
    'Evidence file name',
    'Date of detection (DD-MM-YYYY)',
    'Time of detection (HH-MM-SS)',
    'Date of Post (If detection is from Source: social media)',
    'Remarks (If any)'
]

def create_submission_xlsx(raw_reports):
    """
    Formats the raw JSON reports into the exact Annexure B Excel structure,
    ensuring all 20 columns exist and are in the correct order.
    """
    submission_list = []
    
    
    if not raw_reports:
        print("\n⚠️ No Phishing or Suspected domains were detected. Creating an empty file.")
        df = pd.DataFrame(columns=OFFICIAL_HEADERS)
        df.to_excel(OUTPUT_FILENAME, index=False)
        return

    for report in raw_reports:
        submission_data = report.get('submission_data', {})
        
        
        row = {}
        
       
        row['Application_ID'] = submission_data.get('application_id')
        row['Source of detection'] = submission_data.get('source_of_detection')
        row['Identified Phishing/Suspected Domain Name'] = submission_data.get('identified_domain_name')
        row['Corresponding CSE Domain Name'] = submission_data.get('corresponding_cse_domain_name')
        row['Critical Sector Entity Name'] = submission_data.get('critical_sector_entity')
        row['Phishing/Suspected Domains (i.e. Class Label)'] = submission_data.get('phishing_suspected_domains_class_label')
        row['Domain Registration Date'] = submission_data.get('domain_registration_date')
        row['Registrar Name'] = submission_data.get('registrar_name')
        row['Registrant Name or Registrant Organisation'] = submission_data.get('registrant_name_org')
        row['Registrant Country'] = submission_data.get('registrant_country')
        row['Name Servers'] = submission_data.get('name_servers')
        row['Hosting IP'] = submission_data.get('hosting_ip')
        row['Hosting ISP'] = submission_data.get('hosting_isp')
        row['Hosting Country'] = submission_data.get('hosting_country')
        row['DNS Records (if any)'] = submission_data.get('dns_records')
        row['Evidence file name'] = submission_data.get('evidence_file_name')
        row['Date of detection (DD-MM-YYYY)'] = submission_data.get('date_of_detection')
        row['Time of detection (HH-MM-SS)'] = submission_data.get('time_of_detection')
        row['Date of Post (If detection is from Source: social media)'] = submission_data.get('date_of_post')
        row['Remarks (If any)'] = submission_data.get('remarks')
        
        submission_list.append(row)

    
    df = pd.DataFrame(submission_list)

    
    df = df[OFFICIAL_HEADERS] 
    
    
    df.to_excel(OUTPUT_FILENAME, index=False)
    print(f"\n Successfully created submission file: {OUTPUT_FILENAME}")
    print(f"Total entries logged: {len(df)}")
    

if __name__ == '__main__':
    print(f"--- Starting PS-02 Submission Set Generation for ID: {APPLICATION_ID} ---")
    
    detected_reports = load_and_run_shortlisting_data()
    create_submission_xlsx(detected_reports)