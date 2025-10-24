import pandas as pd
from difflib import SequenceMatcher
import re
from urllib.parse import urlparse

def get_levenshtein_ratio(s1, s2):
    """Calculates the Levenshtein Ratio (similarity score) on base domains."""
    # Preprocessing: Convert to lower and remove TLD
    s1 = s1.lower().split('.')[0]
    s2 = s2.lower().split('.')[0]
    
    # SequenceMatcher is used to calculate the ratio based on edit distance
    return SequenceMatcher(None, s1, s2).ratio()

def extract_url_features(url):
    """Extracts features from the full URL string based on Annexure A."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path
    query = parsed_url.query
    
    # URL-BASED FEATURES
    url_length = len(url)
    num_slashes = url.count('/') - 2 # Exclude http(s)://
    num_underscores = url.count('_')
    num_question_marks = url.count('?')
    num_equal_signs = url.count('=')
    
    # SPECIAL CHARACTERS count (e.g., @, !, $, %, &, |)
    special_chars_count = len(re.findall(r'[!@#$%^&*()|]', url))
    
    # PATH-BASED FEATURES
    path_length = len(path)
    has_query = bool(query)
    
    # SUBDOMAIN FEATURES
    # Simple check for number of subdomains (dots in the domain name minus 1 for the TLD)
    subdomain_parts = domain.split('.')
    num_dots_in_domain = len(subdomain_parts) - 1
    num_subdomains = len(subdomain_parts[:-2])
    
    # DOMAIN FEATURES
    domain_length = len(domain)
    num_hyphens_in_domain = domain.count('-')
    
    # Calculate domain age here, but the actual value comes from external_lookups
    # This feature is just a placeholder for the model input
    
    return {
        'URL_Length': url_length,
        'Num_Slashes': num_slashes,
        'Num_Underscores': num_underscores,
        'Num_Question_Marks': num_question_marks,
        'Num_Equal_Signs': num_equal_signs,
        'Special_Chars_Count': special_chars_count,
        'Path_Length': path_length,
        'Has_Query': int(has_query),
        'Num_Subdomains': num_subdomains,
        'Domain_Length': domain_length,
        'Num_Dots': num_dots_in_domain,
        'Num_Hyphens': num_hyphens_in_domain,
        # The 'Domain_Age_Days' feature will be filled with its corresponding value
        # from the WHOIS lookup before the model runs (handled in app.py)
        'Domain_Age_Days': 0 
    }

def create_model_input_features(identified_url, cse_domain, cse_name, domain_age_days):
    """
    Generates all required features for the trained AI pipeline, incorporating
    typosquatting, lexical, URL-based, and network (age) features.

    Args:
        identified_url (str): The suspicious URL being classified.
        cse_domain (str): The genuine CSE domain.
        cse_name (str): The Critical Sector Entity name.
        domain_age_days (int): The age of the domain in days (from WHOIS lookup).

    Returns:
        pandas.DataFrame: A single-row DataFrame ready for model prediction.
    """
    
    # --- 1. Typosquatting Features ---
    # Use the domain part of the URL for ratio calculation
    identified_domain = urlparse(identified_url).netloc
    
    ratio = get_levenshtein_ratio(identified_domain, cse_domain)
    
    # Length Difference on base domain names
    len1 = len(identified_domain.lower().split('.')[0])
    len2 = len(cse_domain.lower().split('.')[0])
    len_diff = abs(len1 - len2)
    
    # --- 2. URL and Lexical Features ---
    url_features = extract_url_features(identified_url)
    
    # --- 3. Compile Input DataFrame ---
    data = {
        'Levenshtein_Ratio': [ratio],
        'Length_Difference': [len_diff],
        'Critical Sector Entity Name': [cse_name],
        # Update Domain_Age_Days with the actual WHOIS value
        'Domain_Age_Days': [domain_age_days], 
        **url_features # Unpack all URL/Lexical features
    }
    
    return pd.DataFrame(data)