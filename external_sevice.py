from external_lookups import mock_whois_lookup, mock_dns_geoip_lookup
import json
from datetime import datetime

# NOTE: This function's sole purpose is to gather and return the raw report data, 
# simulating real API calls (WHOIS, DNS, etc.)

def get_full_domain_report(identified_domain):
    """
    Gathers all external network and registration attributes needed for the final report.
    This replaces actual calls to WHOIS and GeoIP APIs with mock functions.
    """
    
    whois_data = mock_whois_lookup(identified_domain)
    dns_data = mock_dns_geoip_lookup(identified_domain)
    
    report_attributes = {
        "domain_creation_date": whois_data["domain_creation_date"],
        "registrar_info": whois_data["registrar_info"],
        "is_privacy_protected": whois_data["is_privacy_protected"],
        "ip_address": dns_data["ip_address"],
        "subnet_info": dns_data["subnet_info"],
        "geo_location": dns_data["geo_location"],
        "ip_reputation_score": dns_data["ip_reputation_score"],
        "report_generated_at": datetime.now().isoformat()
    }
    
    return report_attributes
