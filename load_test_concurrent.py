# load_test_concurrent.py
import requests
import time
from concurrent.futures import ThreadPoolExecutor

container_url = "https://iris-container-api-x76cce2eva-uc.a.run.app/predict"
serverless_url = "https://iris-predict-fn-x76cce2eva-uc.a.run.app"

payloads = [
    {"features": [5.1, 3.5, 1.4, 0.2]},
    {"features": [6.2, 3.4, 5.4, 2.3]},
    {"features": [5.9, 3.0, 5.1, 1.8]},
    {"features": [4.7, 3.2, 1.3, 0.2]},
] * 5  # simulate 20 requests

def send_post(url, payload):
    start = time.time()
    try:
        r = requests.post(url, json=payload)
        latency = time.time() - start
        return latency, r.status_code
    except Exception:
        latency = time.time() - start
        return latency, None

def run_load_test(url):
    latencies = []
    statuses = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(lambda p: send_post(url, p), payloads)
        for latency, status in results:
            latencies.append(latency)
            statuses.append(status)
    return latencies, statuses

# Container deployment load test
c_latencies, c_statuses = run_load_test(container_url)
print("Container Deployment Concurrent Test:")
print(f"  Total Requests: {len(c_latencies)}")
print(f"  Average Latency: {sum(c_latencies)/len(c_latencies):.3f} sec")
print(f"  Max Latency: {max(c_latencies):.3f} sec")
print(f"  Min Latency: {min(c_latencies):.3f} sec")
print(f"  Successful Responses: {c_statuses.count(200)}")

# Serverless deployment load test
s_latencies, s_statuses = run_load_test(serverless_url)
print("\nServerless Deployment Concurrent Test:")
print(f"  Total Requests: {len(s_latencies)}")
print(f"  Average Latency: {sum(s_latencies)/len(s_latencies):.3f} sec")
print(f"  Max Latency: {max(s_latencies):.3f} sec")
print(f"  Min Latency: {min(s_latencies):.3f} sec")
print(f"  Successful Responses: {s_statuses.count(200)}")