import random
from datetime import datetime, timedelta

# --- MOCK WHOIS LOOKUP ---
def mock_whois_lookup(domain):
    """
    Simulates fetching Domain Registration (WHOIS) data.
    In a real app, this would use the 'python-whois' library or a dedicated API.
    """
    if 'legit' in domain:
        creation_date = datetime.now() - timedelta(days=random.randint(2000, 5000))
        registrar = "Google LLC"
    elif 'suspected' in domain:
        # Suspected/parked domains are often new
        creation_date = datetime.now() - timedelta(days=random.randint(10, 90))
        registrar = random.choice(["Namecheap", "GoDaddy", "PublicDomainRegistry"])
    else:
        # Phishing domains are usually very new
        creation_date = datetime.now() - timedelta(days=random.randint(1, 15))
        registrar = random.choice(["CheapDomains", "PrivacyProtect"])
        
    return {
        "domain_creation_date": creation_date.strftime("%Y-%m-%d %H:%M:%S"),
        "registrar_info": registrar,
        "is_privacy_protected": random.choice([True, False]),
    }

# --- MOCK DNS AND GEO-IP LOOKUP ---
def mock_dns_geoip_lookup(domain):
    """
    Simulates fetching IP and Geo-location information.
    In a real app, this would use the 'dns' library and a Geo-IP database (e.g., MaxMind).
    """
    if 'vercel.app' in domain:
        ip = "76.76.21.21" # Common Vercel IP
        subnet = "76.76.0.0/16"
        geo = "San Francisco, US (Hosting/Tunneling Service)"
    elif 'suspected' in domain:
        ip = f"192.168.1.{random.randint(100, 200)}" # Placeholder IP
        subnet = "192.168.0.0/16"
        geo = random.choice(["Mumbai, IN (VPS)", "Frankfurt, DE (Cloud)"])
    else:
        # Standard IPs
        ip = f"104.22.{random.randint(0, 255)}.{random.randint(0, 255)}"
        subnet = "104.22.0.0/16"
        geo = random.choice(["Singapore, SG", "London, UK"])
        
    return {
        "ip_address": ip,
        "subnet_info": subnet,
        "geo_location": geo,
        "ip_reputation_score": round(random.uniform(0.1, 0.9), 2) # Mock score
    }

# --- MOCK DYNAMIC CONTENT CHECK ---
def mock_dynamic_content_check(identified_domain, cse_domain):
    """
    Simulates checking if a suspected domain has started hosting lookalike content.
    In a real app, this would involve web scraping and image hashing.
    """
    # 5% chance the domain becomes malicious on any given check
    if random.random() < 0.05:
        # High similarity found (e.g., a login page resembling the CSE)
        visual_similarity = round(random.uniform(0.85, 0.98), 2)
        return {
            "is_content_hosted": True,
            "visual_similarity_score": visual_similarity,
            "reason": "High visual similarity to CSE login page detected.",
            "reclassified_as_phishing": True
        }
    else:
        # Domain is still parked or harmless
        return {
            "is_content_hosted": False,
            "visual_similarity_score": round(random.uniform(0.05, 0.25), 2),
            "reason": "Domain still parked or content is non-CSE specific.",
            "reclassified_as_phishing": False 
        }
