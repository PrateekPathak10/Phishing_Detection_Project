from external_lookups import mock_dynamic_content_check
from reporting_engine import generate_full_detection_report
import time
from datetime import datetime

class SuspectedDomainMonitor:
    def __init__(self, monitor_duration_days=90):
        self.monitoring_queue = {}
        self.duration = monitor_duration_days
        self.alerts = [] 

    def add_to_queue(self, domain, cse_domain, cse_name, initial_confidence):
        """Adds a domain classified as 'Suspected' (Label 1) to the queue."""
        if domain not in self.monitoring_queue:
            self.monitoring_queue[domain] = {
                'cse_domain': cse_domain,
                'cse_name': cse_name,
                'initial_confidence': initial_confidence,
                'start_time': time.time(),
                'status': 'Monitoring'
            }
            print(f"-> Added {domain} to monitoring queue for {self.duration} days.")

    def run_monitoring_cycle(self):
        """Iterates through the queue, performs content checks, and re-classifies."""
        print(f"\n--- Running Monitoring Cycle ({datetime.now().isoformat()}) ---")
        
        domains_to_remove = []

        for domain, data in list(self.monitoring_queue.items()):
            
            time_elapsed = (time.time() - data['start_time']) / (60 * 60 * 24)
            
            # 1. Check Duration Limit
            if time_elapsed >= self.duration:
                print(f"-> Monitoring finished for {domain}. Status: Safe (Timed out).")
                domains_to_remove.append(domain)
                continue
            
            # 2. Perform Dynamic Content Check
            content_check_result = mock_dynamic_content_check(domain, data['cse_domain'])
            
            if content_check_result['reclassified_as_phishing']:
                # 3. Trigger Re-classification and Alert
                reclassification_data = {
                    "monitoring_days_elapsed": int(time_elapsed) + 1,
                    "trigger_type": "Content Change",
                    "visual_similarity_score": content_check_result["visual_similarity_score"],
                    "detection_reason": content_check_result["reason"]
                }
                
                # Assume initial confidence score for Phishing (Label 2) was low, 
                # we now assign a very high confidence for the alert
                mock_new_confidence = [0.01, 0.02, 0.97] 
                
                # Generate the full report immediately
                full_report_json = generate_full_detection_report(
                    domain, 
                    data['cse_domain'], 
                    data['cse_name'], 
                    model_prediction_id=2, # Force to Phishing
                    model_confidence_scores=mock_new_confidence,
                    reclassification_data=reclassification_data
                )

                self.alerts.append(full_report_json)
                print(f"\n!!! URGENT ALERT: {domain} RE-CLASSIFIED as PHISHING !!!")
                print(f"Report Generated (See alerts list).")
                domains_to_remove.append(domain)
                
        # Update queue
        for domain in domains_to_remove:
            self.monitoring_queue.pop(domain, None)
            
        print(f"Monitoring cycle finished. {len(self.monitoring_queue)} domains remaining in queue.")
        return self.alerts


if __name__ == '__main__':
    # Initialize Monitor (set to 5 days for easy testing)
    monitor = SuspectedDomainMonitor(monitor_duration_days=5) 

    # Mock initial classification results (from your final model pipeline)
    # The domain 'airtel-suspected.in' was flagged as Suspected (1)
    monitor.add_to_queue(
        domain='airtel-suspected.in', 
        cse_domain='airtel.in', 
        cse_name='Airtel', 
        initial_confidence=[0.1, 0.85, 0.05] # Model was confident it was Suspected (1)
    )
    
    # Run monitoring cycle until an alert is generated or it times out
    for day in range(1, 6):
        print(f"\n--- SIMULATION DAY {day} ---")
        alerts = monitor.run_monitoring_cycle()
        if alerts:
            print("\n" + "="*50)
            print("REPORT PREVIEW FOR RE-CLASSIFIED DOMAIN:")
            print(alerts[0])
            print("="*50)
            break
        time.sleep(0.1) # Simulate time passing

    if not alerts:
        print("\nMonitoring timed out without re-classification.")
