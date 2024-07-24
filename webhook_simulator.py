import http.client
import json
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# Status counters
status_counts = {
    "successful": 0,
    "failed": 0,
    "no_response": 0
}

def generate_random_data():
    sources = [
        {
            "source": "Source1",
            "data": [
                {"key1": "value1", "key2": random.randint(1, 100)},
                {"key1": "value2", "key2": random.randint(1, 100)}
            ]
        },
        {
            "source": "Source2",
            "data": [
                {"paramA": random.choice(["A", "B", "C"]), "paramB": random.random()},
                {"paramA": random.choice(["D", "E", "F"]), "paramB": random.random()}
            ]
        },
        {
            "source": "Source3",
            "metrics": [
                {"metric1": random.uniform(0, 10), "metric2": random.uniform(0, 10)},
                {"metric1": random.uniform(10, 20), "metric2": random.uniform(10, 20)}
            ]
        },
        {
            "source": "Source4",
            "logs": [
                {"timestamp": time.time(), "message": "Log message 1"},
                {"timestamp": time.time(), "message": "Log message 2"}
            ]
        },
        {
            "source": "Source5",
            "events": [
                {"eventId": random.randint(1000, 2000), "eventType": "type1"},
                {"eventId": random.randint(2000, 3000), "eventType": "type2"}
            ]
        },
        {
            "source": "Source6",
            "details": [
                {"name": "Item1", "quantity": random.randint(1, 50)},
                {"name": "Item2", "quantity": random.randint(1, 50)}
            ]
        },
        {
            "source": "Source7",
            "info": [
                {"info1": "data1", "info2": random.choice(["X", "Y", "Z"])},
                {"info1": "data2", "info2": random.choice(["A", "B", "C"])}
            ]
        },
        {
            "source": "Source8",
            "attributes": [
                {"attr1": random.choice([True, False]), "attr2": random.randint(0, 10)},
                {"attr1": random.choice([True, False]), "attr2": random.randint(10, 20)}
            ]
        },
        {
            "source": "Source9",
            "measurements": [
                {"measure1": random.uniform(100, 200), "measure2": random.uniform(200, 300)},
                {"measure1": random.uniform(300, 400), "measure2": random.uniform(400, 500)}
            ]
        },
        {
            "source": "Source10",
            "entries": [
                {"entryId": random.randint(5000, 6000), "entryValue": "valueA"},
                {"entryId": random.randint(6000, 7000), "entryValue": "valueB"}
            ]
        }
    ]
    return random.choice(sources)

def send_request(url, endpoint, data):
    conn = http.client.HTTPConnection(url)
    headers = {
        'Authorization': 'Bearer dummy_token',
        'Content-Type': 'application/json'
    }
    json_data = json.dumps(data)
    try:
        conn.request('POST', endpoint, body=json_data, headers=headers)
        response = conn.getresponse()
        if response.status == 200:
            status_counts["successful"] += 1
        else:
            status_counts["failed"] += 1
        result = response.read().decode()
        conn.close()
        return result
    except Exception as exc:
        status_counts["no_response"] += 1
        return str(exc)

def main(url, endpoint, total_requests, rate_per_second):
    with open("request_results.txt", "w") as log_file:
        with ThreadPoolExecutor(max_workers=rate_per_second) as executor:
            future_to_request = {
                executor.submit(send_request, url, endpoint, generate_random_data()): i for i in range(total_requests)
            }
            start_time = time.time()
            for future in as_completed(future_to_request):
                try:
                    result = future.result()
                    log_file.write(result + "\n")
                except Exception as exc:
                    log_file.write(f'Generated an exception: {exc}\n')
                # Maintain the rate of requests per second
                if len(future_to_request) % rate_per_second == 0:
                    time.sleep(1)
            end_time = time.time()
        
        # Print summary
        log_file.write("\nSummary:\n")
        log_file.write(f"Total requests: {total_requests}\n")
        log_file.write(f"Successful requests: {status_counts['successful']}\n")
        log_file.write(f"Failed requests: {status_counts['failed']}\n")
        log_file.write(f"No response: {status_counts['no_response']}\n")
        log_file.write(f"Total time taken: {end_time - start_time:.2f} seconds\n")

if __name__ == "__main__":
    url = "localhost:8080"  # Replace with your actual webhook URL (without the http:// prefix)
    endpoint = "/sap/getFolderPath"  # Replace with the actual endpoint if needed
    total_requests = 4000  # Total number of requests to be sent (400 requests per second * 10 seconds)
    rate_per_second = 400  # Requests per second

    main(url, endpoint, total_requests, rate_per_second)
