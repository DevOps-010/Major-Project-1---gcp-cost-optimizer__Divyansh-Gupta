# GCP Cost Optimizer

A collection of tools to analyze and optimize Google Cloud Platform costs.

## Overview

This project provides scripts to help you identify cost optimization opportunities in your GCP environment. It analyzes your resources and provides recommendations for reducing costs.

## Prerequisites

- Google Cloud SDK installed
- Python 3.6+
- Authenticated with GCP (`gcloud auth login`)
- Appropriate permissions to view resources and billing data

## Tools Included

### 1. Cost Analyzer

Analyzes your GCP resources and provides cost optimization recommendations.

```bash
cd scripts
./run_cost_analyzer.sh
```

The report will be generated in the reports directory.

### 2. Idle Resource Cleanup
Identifies idle or unused resources that can be deleted to save costs.
```bash
cd scripts
./cleanup_idle_resources.sh
```
### 3. VM Scheduler
Sets up automatic schedules to shut down non-production VMs during off-hours.
```bash
cd scripts
./schedule_vm_shutdowns.sh
```

## Cost Optimization Strategies

### Resource Rightsizing
- Use appropriate machine types for your workloads
- Downsize over-provisioned resources

### Committed Use Discounts
- Purchase committed use contracts for steady-state workloads
- Save up to 57% compared to on-demand pricing

### Preemptible VMs
- Use for fault-tolerant, batch processing workloads
- Save up to 80% compared to regular instances

### Storage Optimization
- Use appropriate storage classes based on access frequency
- Delete unattached disks and old snapshots

### Networking Optimization
- Avoid using external IPs for internal communication
- Delete unused static IPs

### Scheduled Resources
- Shut down non-production resources during off-hours
- Implement instance scheduling

### Billing Export and Analysis
- Export billing data to BigQuery for detailed analysis
- Create custom dashboards to track spending by project, service, and label

### Budgets and Alerts
- Set up budget alerts to notify you when spending approaches predefined thresholds
- Use GCP's Cost Explorer to identify cost trends and anomalies

## Installation

1. Clone this repository:
```bash
git https://github.com/DevOps-010/Major-Project-1---gcp-cost-optimizer__Divyansh-Gupta.git
cd gcp-cost-optimizer
```

2. Ensure you have the required dependencies:
```bash
pip install -r requirements.txt
```

3. Authenticate with GCP:
```bash
gcloud auth login
```

4. Set your project:
```bash
gcloud config set project YOUR_PROJECT_ID
```

## Usage
Navigate to the scripts directory and run the desired tool:
```bash
cd scripts
./run_cost_analyzer.sh
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
MIT License

Copyright (c) 2025 Divyansh Gupta

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## How to Test Locally

1. Authenticate with Google Cloud:
```bash
gcloud auth login
```

2. Set your project ID:
```bash
gcloud config set project YOUR_PROJECT_ID
```

3. Navigate to the gcp_cost_optimizer directory:
```bash
cd gcp_cost_optimizer
```

4. Run the cost analyzer script:
```bash
cd scripts
./run_cost_analyzer.sh
```

5. Check the generated report:
```bash
cat ../reports/gcp_cost_report_$(date +%Y-%m-%d).txt
```

6. Test the idle resource cleanup script:
```bash
./cleanup_idle_resources.sh
```

7. Check the cleanup report:
```bash
cat ../reports/cleanup_report_$(date +%Y-%m-%d).txt
```