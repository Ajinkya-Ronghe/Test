import json
import random
import string
import time
import concurrent.futures
import requests
from datetime import datetime
import logging

# Configuration
ENDPOINT = "http://localhost:8081/api/sendrequest"
REQUESTS_PER_SECOND = 400
REQUEST_SECONDS = 1  # Total simulation time in seconds
TOTAL_REQUESTS = REQUESTS_PER_SECOND * REQUEST_SECONDS
DATA_PER_MINUTE_MB = 200
DATA_PER_SECOND_MB = DATA_PER_MINUTE_MB / 60
DATA_PER_REQUEST_MB = DATA_PER_SECOND_MB / REQUESTS_PER_SECOND
DATA_PER_REQUEST_BYTES = DATA_PER_REQUEST_MB * 1024 * 1024
NUM_CONNECTIONS = 50  # Number of different connections

# Setup logging
logging.basicConfig(
    filename='simulation.log',
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

# Generate random JSON payload
def generate_random_json(size_in_bytes):
    payload = {
        "data": "".join(random.choices(string.ascii_letters + string.digits, k=size_in_bytes - 30))
    }
    return json.dumps(payload)

# Simulate a single request
def send_request(session, request_id):
    type_value = ''.join(random.choices(string.ascii_lowercase, k=10))
    url = f"{ENDPOINT}?type={type_value}&id={request_id}"
    payload = generate_random_json(int(DATA_PER_REQUEST_BYTES))
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_BEARER_TOKEN'
    }
    
    request_details = {
        "request_id": request_id,
        "url": url,
        "payload_size": len(payload),
        "status": "no_response",
        "status_code": None,
        "exception": None
    }

    logging.debug(f"Request ID: {request_id}, URL: {url}, Payload Size: {len(payload)} bytes")
    
    try:
        response = session.post(url, data=payload, headers=headers, timeout=5)
        request_details["status_code"] = response.status_code
        if response.status_code == 200:
            logging.info(f"Request ID: {request_id} - Success")
            request_details["status"] = "success"
        else:
            logging.error(f"Request ID: {request_id} - Failure, Status Code: {response.status_code}")
            request_details["status"] = "failure"
    except requests.RequestException as e:
        logging.error(f"Request ID: {request_id} - Failure, Exception: {e}")
        request_details["status"] = "failure"
        request_details["exception"] = str(e)
    
    return request_details

# Monitor and run the simulation
def run_simulation():
    results = {
        "success": 0,
        "failure": 0,
        "no_response": 0,
        "details": []
    }
    
    sessions = [requests.Session() for _ in range(NUM_CONNECTIONS)]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=REQUESTS_PER_SECOND) as executor:
        future_to_request = {executor.submit(send_request, random.choice(sessions), i): i for i in range(TOTAL_REQUESTS)}
        for future in concurrent.futures.as_completed(future_to_request):
            request_details = future.result()
            results["details"].append(request_details)
            results[request_details["status"]] += 1
    
    return results

# Run and print the results
start_time = datetime.now()
results = run_simulation()
end_time = datetime.now()

duration = (end_time - start_time).total_seconds()

report = f"""
Simulation Report:
==================
Total Requests: {TOTAL_REQUESTS}
Success: {results['success']}
Failure: {results['failure']}
No Response: {results['no_response']}
Duration: {duration:.2f} seconds
"""

print(report)

# Save the report to a file
with open("simulation_report.txt", "w") as report_file:
    report_file.write(report)

# Save detailed request logs to a separate file
with open("detailed_requests_report.txt", "w") as detailed_report_file:
    for detail in results["details"]:
        detailed_report_file.write(f"{json.dumps(detail)}\n")

logging.info(report)
