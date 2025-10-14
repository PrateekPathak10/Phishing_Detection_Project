import pandas as pd
from difflib import SequenceMatcher

def get_levenshtein_ratio(s1, s2):
    """Calculates the Levenshtein Ratio (similarity score)."""
    # Preprocessing: Convert to lower and remove TLD
    s1 = s1.lower().split('.')[0]
    s2 = s2.lower().split('.')[0]
    
    # SequenceMatcher is used to calculate the ratio based on edit distance
    return SequenceMatcher(None, s1, s2).ratio()

def create_model_input_features(identified_domain, cse_domain, cse_name):
    """
    Generates all required features for the trained AI pipeline.

    Args:
        identified_domain (str): The suspicious domain being classified.
        cse_domain (str): The genuine CSE domain.
        cse_name (str): The Critical Sector Entity name (for one-hot encoding).

    Returns:
        pandas.DataFrame: A single-row DataFrame ready for model prediction.
    """
    
    # --- 1. Typosquatting Features ---
    ratio = get_levenshtein_ratio(identified_domain, cse_domain)
    
    len1 = len(identified_domain.lower().split('.')[0])
    len2 = len(cse_domain.lower().split('.')[0])
    len_diff = abs(len1 - len2)
    
    # --- 2. Lexical Features ---
    domain_length = len(identified_domain)
    num_dots = identified_domain.count('.')
    num_hyphens = identified_domain.count('-')
    
    # --- 3. Compile Input DataFrame ---
    data = {
        'Levenshtein_Ratio': [ratio],
        'Length_Difference': [len_diff],
        'Domain_Length': [domain_length],
        'Num_Dots': [num_dots],
        'Num_Hyphens': [num_hyphens],
        'Critical Sector Entity Name': [cse_name] # Categorical feature
    }
    
    return pd.DataFrame(data)
