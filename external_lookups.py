import random
from datetime import datetime, timedelta

# MOCK WHOIS LOOKUP 
def mock_whois_lookup(domain):
    """
    Simulates fetching Domain Registration (WHOIS) data, including
    Registrant Name, Organisation, and Country (Annexure B).
    Returns the domain age in days for the model input.
    """
    

    if 'legit' in domain:
        creation_date = datetime.now() - timedelta(days=random.randint(2000, 5000))
        registrar = "Google LLC"
        registrant_org = "Legit Corp"
        registrant_country = "US"
    elif 'suspected' in domain:
        creation_date = datetime.now() - timedelta(days=random.randint(10, 90))
        registrar = random.choice(["Namecheap", "GoDaddy", "PublicDomainRegistry"])
        registrant_org = "Domain Parked Service"
        registrant_country = random.choice(["IN", "DE"])
    else:
        creation_date = datetime.now() - timedelta(days=random.randint(1, 15))
        registrar = random.choice(["CheapDomains", "PrivacyProtect"])
        registrant_org = "Privacy Protected"
        registrant_country = random.choice(["PA", "RU"])
        
    domain_age = (datetime.now() - creation_date).days
        
    return {
        "domain_creation_date": creation_date.strftime("%Y-%m-%d %H:%M:%S"),
        "registrar_name": registrar, 
        "registrant_name_org": registrant_org, 
        "registrant_country": registrant_country, 
        "is_privacy_protected": random.choice([True, False]),
        "domain_age_days": domain_age 
    }


def mock_dns_geoip_lookup(domain):
    """
    Simulates fetching IP, Geo-location, and Hosting details (Annexure B).
    """
    if 'vercel.app' in domain:
        ip = "76.76.21.21"
        hosting_isp = "Vercel" 
        geo_location = "San Francisco, US" 
        name_servers = ["dns1.vercel-dns.com", "dns2.vercel-dns.com"] 
    elif 'suspected' in domain:
        ip = f"192.168.1.{random.randint(100, 200)}"
        hosting_isp = random.choice(["DigitalOcean", "Linode"])
        geo_location = random.choice(["Mumbai, IN", "Frankfurt, DE"])
        name_servers = ["ns1.hoster.com", "ns2.hoster.com"]
    else:
        ip = f"104.22.{random.randint(0, 255)}.{random.randint(0, 255)}"
        hosting_isp = random.choice(["Cloudflare", "Contabo"])
        geo_location = random.choice(["Singapore, SG", "London, UK"])
        name_servers = ["ns1.registrar.net", "ns2.registrar.net"]
        
    
    mock_dns_records = {
        "A": ip,
        "MX": f"mail.{domain}",
        "TXT": "v=spf1 include:spf.example.com ~all"
    }
        
    return {
        "ip_address": ip, 
        "hosting_isp": hosting_isp,
        "geo_location": geo_location,
        "ip_reputation_score": round(random.uniform(0.1, 0.9), 2),
        "name_servers": name_servers,
        "dns_records": mock_dns_records
    }


def mock_dynamic_content_check(identified_domain, cse_domain):
    """
    Simulates checking if a suspected domain has started hosting lookalike content.
    (No change needed here as it satisfies the conceptual content check for Req 3.3).
    """
    if random.random() < 0.05:
        visual_similarity = round(random.uniform(0.85, 0.98), 2)
        return {
            "is_content_hosted": True,
            "visual_similarity_score": visual_similarity,
            "reason": "High visual similarity to CSE login page detected.",
            "reclassified_as_phishing": True
        }
    else:
        return {
            "is_content_hosted": False,
            "visual_similarity_score": round(random.uniform(0.05, 0.25), 2),
            "reason": "Domain still parked or content is non-CSE specific.",
            "reclassified_as_phishing": False 
        }