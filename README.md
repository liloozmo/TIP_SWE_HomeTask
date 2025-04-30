### TIP SWE HomeTask - Alert Ingestion and Enrichment System

### Overview

This command-line Python application simulates the flow of an alert through a SOAR (Security Orchestration, Automation, and Response) pipeline. It is composed of two main services:

1. Ingestion Service- pulls messages from a Google Cloud Pub/Sub subscription, each message containing a list of Ios (Indicators of Compromise), and transforms them into Alert objects.
2. Enrichment Service- queries the VirusTotal API for each IoC, determines whether it is malicious, calculates alert severity, and saves a report in json format.





###  Modules Overview
The main logic of the application is divided into the following modules inside the app/ directory:

- main.py – Entry point of the application. Controls the ingestion and enrichment loop.
- ingestion_service.py – Pulls Ioc messages from Pub/Sub and converts them into Alert objects.
- enrichment_service.py – Queries the VirusTotal API, analyzes Iocs, generates severity reports and save them to .json files.
- alert.py – Defines the Alert class structure used to pass IoCs through the pipeline.
- utils.py – Contains helper functions (e.g., timestamp generation, output directory handling).

###  Project Structure

```text
TIP_SWE_HomeTask/
│
├── app/                     
│   ├── __init__.py
│   ├── main.py
│   ├── alert.py
│   ├── ingestion_service.py
│   ├── enrichment_service.py
│   ├── utils.py
│   └── output/          # created on first report save
│
├── tests/                    
│   ├── __init__.py
│   ├── test_alert.py
│   ├── test_ingestion_service.py
│   ├── test_enrichment_service.py
│   └── test_utils.py
│
├── publisher_service/
│   ├── publisher.py
│   └── requirements.txt
│
├── requirements.txt         
├── .env                      
├── README.md 
```
              
### How to Run

### Step 1: Activate virtual environment and Install dependencies

```bash
# Run from project root (TIP_SWE_HomeTask)
python3 -m venv venv
source venv/bin/activate # Use venv\Scripts\activate on Windows
pip install -r requirements.txt
``` 
Requirements.txt in the root level covers all the dependencies, but to be on the safe side, download the requirements.txt of the publisher_service as well:

```bash
pip install -r publisher_service/requirements.txt
```

### Step 2: Run the Application

#### Open Terminal 1 – Run the Alert Ingestion & Enrichment Pipeline:
ACTIVATE YOUR VIRTUAL ENVIRONMENT IF NOT ACTIVATED:
```bash
source venv/bin/activate
```
THEN RUN:
```bash
python -m app.main
```
This will continuously:

1. Pull messages from Pub/Sub

2. Enrich each IoC using VirusTotal

3. Save a report to the output folder inside app (app/output) -output folder will be created with the first saved report.

#### Open Terminal 2- Run the publish simulator:
ACTIVATE YOUR VIRTUAL ENVIRONMENT IF NOT ACTIVATE:
```bash
source venv/bin/activate
```
THEN RUN:
```bash
python publisher_service/publisher.py
```
This publishes test IoCs to the Pub/Sub topic for ingestion and enrichment.




### Output Format

Each processed alert is saved as a timestamped .json file inside app/output/.

Example:
```json
{
  "AlertId": "a1b2c3d4",
  "Severity": 50,
  "IoCs": [
    { "IoC": "1.2.3.4", "IsMalicious": true },
    { "IoC": "5.6.7.8", "IsMalicious": false }
  ]
}
```


## Testing
To run the tests- use the following command line from the root directory (TIP_SWE_HomeTask):
```bash
python -m unittest discover -s tests
```


