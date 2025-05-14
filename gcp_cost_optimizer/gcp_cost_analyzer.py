import os
import subprocess
import json
import datetime
import sys

os.makedirs('../reports', exist_ok=True)
TODAY = datetime.datetime.now().strftime('%Y-%m-%d')
REPORT_FILE = f"../reports/gcp_cost_report_{TODAY}.txt"

def run_gcloud(args):
    command = ["gcloud"] + args
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command)}")
        print(f"Error: {e.stderr}")
        return None

def get_project_info():
    print("Getting project information...")
    project_info = run_gcloud(["config", "list", "--format=json"])
    if project_info:
        return json.loads(project_info)
    return None

def analyze_compute_instances():
    print("Analyzing Compute Engine instances...")
    instances = run_gcloud(["compute", "instances", "list", "--format=json"])
    
    if not instances:
        return "No Compute Engine instances found or error retrieving data."
    
    try:
        instances_data = json.loads(instances)
    except json.JSONDecodeError:
        return "Error parsing Compute Engine data."
    
    # Analyze instance usage
    report = "COMPUTE ENGINE OPTIMIZATION RECOMMENDATIONS:\n"
    report += "=" * 50 + "\n\n"
    
    if not instances_data:
        return report + "No Compute Engine instances found.\n"
    
    # Count instances by machine type
    machine_types = {}
    for instance in instances_data:
        machine_type = instance['machineType'].split('/')[-1]
        if machine_type not in machine_types:
            machine_types[machine_type] = 0
        machine_types[machine_type] += 1
    
    report += "Instance Types Summary:\n"
    for machine_type, count in machine_types.items():
        report += f"  - {machine_type}: {count} instances\n"
    
    # Check for optimization opportunities
    report += "\nOptimization Opportunities:\n"
    
    # Check for stopped instances
    stopped_instances = [i for i in instances_data if i['status'] == 'TERMINATED']
    if stopped_instances:
        report += f"\n1. You have {len(stopped_instances)} stopped instances that are still incurring storage costs:\n"
        for instance in stopped_instances:
            report += f"   - {instance['name']} (Zone: {instance['zone'].split('/')[-1]})\n"
        report += "   Recommendation: Delete unused instances to avoid storage charges.\n"
    
    # Check for oversized instances
    large_instances = [i for i in instances_data if any(large_type in i['machineType'] 
                                                      for large_type in ['n1-standard-8', 'n1-standard-16', 
                                                                        'n2-standard-8', 'n2-standard-16',
                                                                        'e2-standard-8', 'e2-standard-16'])]
    if large_instances:
        report += f"\n2. You have {len(large_instances)} large instances that might be oversized:\n"
        for instance in large_instances:
            machine_type = instance['machineType'].split('/')[-1]
            report += f"   - {instance['name']} (Type: {machine_type}, Zone: {instance['zone'].split('/')[-1]})\n"
        report += "   Recommendation: Monitor CPU and memory usage and consider downsizing if utilization is low.\n"
    
    # Check for instances without sustained use discounts
    report += "\n3. Sustained Use Discount Opportunities:\n"
    report += "   - Instances running continuously for a month automatically receive sustained use discounts.\n"
    report += "   - Consider converting eligible workloads to committed use contracts for 1-3 year terms to save 20-60%.\n"
    
    # Check for instances that could use preemptible VMs
    report += "\n4. Preemptible VM Opportunities:\n"
    report += "   - For fault-tolerant, batch processing workloads, consider using preemptible VMs to save up to 80%.\n"
    
    return report

def analyze_storage():
    print("Analyzing storage resources...")
    
    # Get Cloud Storage buckets
    buckets = run_gcloud(["storage", "ls", "--format=json"])
    
    # Get persistent disks
    disks = run_gcloud(["compute", "disks", "list", "--format=json"])
    
    report = "STORAGE OPTIMIZATION RECOMMENDATIONS:\n"
    report += "=" * 50 + "\n\n"
    
    # Analyze Cloud Storage
    report += "Cloud Storage Optimization:\n"
    if buckets:
        try:
            buckets_data = json.loads(buckets)
            report += f"1. You have {len(buckets_data)} Cloud Storage buckets.\n"
        except json.JSONDecodeError:
            report += "1. You have Cloud Storage buckets, but couldn't parse the data.\n"
        
        report += "   Storage Class Recommendations:\n"
        report += "   - Standard Storage: Use for frequently accessed data (multiple times a month)\n"
        report += "   - Nearline Storage: Use for data accessed less than once a month (20% cheaper)\n"
        report += "   - Coldline Storage: Use for data accessed less than once a quarter (50% cheaper)\n"
        report += "   - Archive Storage: Use for data accessed less than once a year (90% cheaper)\n"
        report += "   Recommendation: Set up Object Lifecycle Management to automatically transition objects to cheaper storage classes.\n"
    else:
        report += "No Cloud Storage buckets found or error retrieving data.\n"
    
    # Analyze Persistent Disks
    report += "\nPersistent Disk Optimization:\n"
    if disks:
        try:
            disks_data = json.loads(disks)
            
            # Check for unattached disks
            unattached_disks = [d for d in disks_data if 'users' not in d or not d['users']]
            if unattached_disks:
                report += f"1. You have {len(unattached_disks)} unattached persistent disks that are incurring costs:\n"
                total_size_gb = sum(int(d['sizeGb']) for d in unattached_disks)
                for disk in unattached_disks:
                    report += f"   - {disk['name']} (Size: {disk['sizeGb']} GB, Type: {disk['type'].split('/')[-1]})\n"
                report += f"   Total unattached disk space: {total_size_gb} GB\n"
                report += "   Recommendation: Delete unattached disks or create snapshots before deletion if the data is needed.\n"
            
            # Check for SSD vs Standard disks
            ssd_disks = [d for d in disks_data if 'ssd' in d['type'].lower()]
            if ssd_disks:
                report += f"\n2. You have {len(ssd_disks)} SSD persistent disks:\n"
                report += "   Recommendation: For non-performance-critical workloads, consider using Standard persistent disks to reduce costs.\n"
        except json.JSONDecodeError:
            report += "Error parsing disk data.\n"
    else:
        report += "No persistent disks found or error retrieving data.\n"
    
    return report

def analyze_network():
    print("Analyzing networking resources...")
    
    # Get external IP addresses
    addresses = run_gcloud(["compute", "addresses", "list", "--format=json"])
    
    # Get forwarding rules (load balancers)
    forwarding_rules = run_gcloud(["compute", "forwarding-rules", "list", "--format=json"])
    
    report = "NETWORKING OPTIMIZATION RECOMMENDATIONS:\n"
    report += "=" * 50 + "\n\n"
    
    # Analyze External IP Addresses
    report += "External IP Address Optimization:\n"
    if addresses:
        try:
            addresses_data = json.loads(addresses)
            if addresses_data:
                static_ips = [a for a in addresses_data if a['status'] == 'RESERVED']
                if static_ips:
                    report += f"1. You have {len(static_ips)} reserved static external IP addresses:\n"
                    for ip in static_ips:
                        in_use = 'users' in ip and ip['users']
                        status = "In use" if in_use else "Not in use"
                        report += f"   - {ip['address']} (Name: {ip['name']}, Status: {status})\n"
                    report += "   Recommendation: Delete unused static IPs as they incur charges even when not attached to resources.\n"
        except json.JSONDecodeError:
            report += "Error parsing IP address data.\n"
    else:
        report += "No external IP addresses found or error retrieving data.\n"
    
    # Analyze Load Balancers
    report += "\nLoad Balancer Optimization:\n"
    if forwarding_rules:
        try:
            rules_data = json.loads(forwarding_rules)
            if rules_data:
                report += f"1. You have {len(rules_data)} load balancer forwarding rules:\n"
                for rule in rules_data:
                    report += f"   - {rule['name']} (IP: {rule.get('IPAddress', 'N/A')}, Target: {rule.get('target', 'N/A').split('/')[-1]})\n"
                report += "   Recommendation: Load balancers incur hourly charges. Consider consolidating load balancers where possible.\n"
        except json.JSONDecodeError:
            report += "Error parsing forwarding rules data.\n"
    else:
        report += "No load balancers found or error retrieving data.\n"
    
    return report

def analyze_billing():
    print("Analyzing billing data...")
    
    report = "BILLING OPTIMIZATION RECOMMENDATIONS:\n"
    report += "=" * 50 + "\n\n"
    
    report += "1. Set up Budget Alerts:\n"
    report += "   - Create budget alerts to notify you when spending approaches predefined thresholds\n"
    report += "   - Use the following command to create a budget alert:\n"
    report += "     gcloud billing budgets create --billing-account=ACCOUNT_ID --display-name=BUDGET_NAME --budget-amount=1000USD --threshold-rules=percent=80\n\n"
    
    report += "2. Export Billing Data to BigQuery:\n"
    report += "   - Export your billing data to BigQuery for detailed analysis\n"
    report += "   - Create custom dashboards to track spending by project, service, and label\n"
    report += "   - Use Data Studio to visualize your spending patterns\n\n"
    
    report += "3. Use Labels for Cost Allocation:\n"
    report += "   - Apply consistent labels to all resources for better cost tracking\n"
    report += "   - Example labels: environment (prod, dev, test), team, project, application\n"
    
    return report

def generate_cost_recommendations():
    """Generate general cost optimization recommendations"""
    recommendations = """
GENERAL COST OPTIMIZATION RECOMMENDATIONS:
=========================================

1. Resource Rightsizing:
   - Regularly review and rightsize your resources based on actual usage patterns
   - Use GCP's Recommender API to get automatic rightsizing recommendations

2. Committed Use Discounts:
   - Purchase committed use contracts for steady-state workloads to save up to 57%
   - Analyze your usage patterns to determine optimal commitment levels

3. Sustained Use Discounts:
   - GCP automatically applies sustained use discounts for resources used for significant portions of the month
   - Consolidate workloads to maximize these discounts

4. Preemptible VMs:
   - Use preemptible VMs for fault-tolerant, batch processing workloads to save up to 80%
   - Ensure your applications can handle interruptions

5. Storage Optimization:
   - Use appropriate storage classes based on access frequency
   - Implement lifecycle policies to automatically transition objects to cheaper storage classes
   - Delete unnecessary snapshots and unattached persistent disks

6. Networking Optimization:
   - Avoid using external IPs for internal communication
   - Use Cloud NAT for outbound traffic instead of assigning external IPs to each instance
   - Delete unused static external IPs

7. Budgets and Alerts:
   - Set up budget alerts to notify you when spending approaches predefined thresholds
   - Use GCP's Cost Explorer to identify cost trends and anomalies

8. Scheduled Resources:
   - Schedule non-production resources to shut down during off-hours
   - Use Cloud Scheduler and Cloud Functions to automate resource management

9. Containerization:
   - Consider using Google Kubernetes Engine (GKE) to optimize resource utilization
   - Use GKE Autopilot to let Google manage capacity provisioning

10. Billing Export:
    - Export billing data to BigQuery for detailed analysis
    - Create custom dashboards to track spending by project, service, and label
"""
    return recommendations

def main():
    print("GCP Cost Optimization Tool")
    print("=========================")
    
    # Get project info
    project_info = get_project_info()
    if not project_info:
        print("Error: Unable to get project information. Make sure you're authenticated with GCP.")
        print("Run 'gcloud auth login' to authenticate.")
        return
    
    # Start building the report
    with open(REPORT_FILE, 'w') as f:
        f.write(f"GCP COST OPTIMIZATION REPORT - {TODAY}\n")
        f.write("=" * 50 + "\n\n")
        
        if 'core' in project_info and 'project' in project_info['core']:
            f.write(f"Project: {project_info['core']['project']}\n\n")
        
        # Analyze Compute Engine
        compute_report = analyze_compute_instances()
        f.write(compute_report + "\n\n")
        
        # Analyze Storage
        storage_report = analyze_storage()
        f.write(storage_report + "\n\n")
        
        # Analyze Networking
        network_report = analyze_network()
        f.write(network_report + "\n\n")
        
        # Analyze Billing
        billing_report = analyze_billing()
        f.write(billing_report + "\n\n")
        
        # General recommendations
        f.write(generate_cost_recommendations())
    
    print(f"Report generated: {REPORT_FILE}")
    print("To view the report, open it in a text editor.")
if __name__ == "__main__":
    main()
