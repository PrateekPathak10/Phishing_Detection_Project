import pandas as pd
from difflib import SequenceMatcher
import re
from urllib.parse import urlparse

def get_levenshtein_ratio(s1, s2):
    """Calculates the Levenshtein Ratio (similarity score) on base domains."""
    s1 = s1.lower().split('.')[0]
    s2 = s2.lower().split('.')[0]
    
    return SequenceMatcher(None, s1, s2).ratio()

def extract_url_features(url):
    """Extracts features from the full URL string based on Annexure A."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path
    query = parsed_url.query
    
    url_length = len(url)
    num_slashes = url.count('/') - 2 
    num_underscores = url.count('_')
    num_question_marks = url.count('?')
    num_equal_signs = url.count('=')
    
    
    special_chars_count = len(re.findall(r'[!@#$%^&*()|]', url))
    
    path_length = len(path)
    has_query = bool(query)
    
    subdomain_parts = domain.split('.')
    num_dots_in_domain = len(subdomain_parts) - 1
    num_subdomains = len(subdomain_parts[:-2])
    
    domain_length = len(domain)
    num_hyphens_in_domain = domain.count('-')
    
    
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
    
   
    identified_domain = urlparse(identified_url).netloc
    
    ratio = get_levenshtein_ratio(identified_domain, cse_domain)
    
    len1 = len(identified_domain.lower().split('.')[0])
    len2 = len(cse_domain.lower().split('.')[0])
    len_diff = abs(len1 - len2)
    
    url_features = extract_url_features(identified_url)
    
    data = {
        'Levenshtein_Ratio': [ratio],
        'Length_Difference': [len_diff],
        'Critical Sector Entity Name': [cse_name],
       
        'Domain_Age_Days': [domain_age_days], 
        **url_features 
    }
    
    return pd.DataFrame(data)