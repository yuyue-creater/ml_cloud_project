# load_test.py
import requests
import time
import json
import argparse
from concurrent.futures import ThreadPoolExecutor

# Endpoints
container_url = "https://iris-container-api-x76cce2eva-uc.a.run.app/predict"
serverless_url = "https://iris-predict-fn-x76cce2eva-uc.a.run.app"  # replace if different

# Test data
test_inputs = [
    {"features": [5.1, 3.5, 1.4, 0.2]},
    {"features": [6.2, 3.4, 5.4, 2.3]},
    {"features": [5.9, 3.0, 5.1, 1.8]}
]

# Function to send POST request and record latency
def send_request(url, data):
    start = time.time()
    try:
        response = requests.post(url, json=data)
        latency = time.time() - start
        return {
            "input": data,
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "latency_sec": latency
        }
    except Exception as e:
        return {"input": data, "error": str(e)}

# Function to test endpoint with concurrency
def run_load_test(url, requests_per_endpoint=50, concurrent_workers=10):
    results = []
    with ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
        futures = [executor.submit(send_request, url, test_inputs[i % len(test_inputs)]) for i in range(requests_per_endpoint)]
        for future in futures:
            results.append(future.result())
    return results
def measure_single_request(url, data):
    return send_request(url, data)

def print_single_result(result, deployment_name):
    if "latency_sec" in result:
        print(f"{deployment_name} Single Request Test:")
        print(f"  Status Code: {result.get('status_code')}")
        print(f"  Latency: {result['latency_sec']:.3f} sec\n")
    else:
        print(f"{deployment_name} Single Request Test Error:")
        print(f"  Error: {result.get('error')}\n")

# Print summary
def print_summary(results, deployment_name):
    latencies = [r["latency_sec"] for r in results if "latency_sec" in r]
    if latencies:
        print(f"{deployment_name} Summary:")
        print(f"  Total Requests: {len(results)}")
        print(f"  Average Latency: {sum(latencies)/len(latencies):.3f} sec")
        print(f"  Max Latency: {max(latencies):.3f} sec")
        print(f"  Min Latency: {min(latencies):.3f} sec\n")


def main():
    parser = argparse.ArgumentParser(description="Load test for container and serverless deployments.")
    parser.add_argument(
        "--requests",
        type=int,
        default=20,
        help="Number of requests per endpoint for the warm/longer-run test.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of concurrent workers for the warm/longer-run test.",
    )
    args = parser.parse_args()

    # Run tests
    container_cold_result = measure_single_request(container_url, test_inputs[0])
    serverless_cold_result = measure_single_request(serverless_url, test_inputs[0])

    container_results = run_load_test(
        container_url,
        requests_per_endpoint=args.requests,
        concurrent_workers=args.workers,
    )
    serverless_results = run_load_test(
        serverless_url,
        requests_per_endpoint=args.requests,
        concurrent_workers=args.workers,
    )

    print_single_result(container_cold_result, "Container Deployment")
    print_single_result(serverless_cold_result, "Serverless Deployment")

    # Save results to JSON files
    with open("container_results.json", "w") as f:
        json.dump(container_results, f, indent=2)

    with open("serverless_results.json", "w") as f:
        json.dump(serverless_results, f, indent=2)

    print_summary(container_results, "Container Deployment")
    print_summary(serverless_results, "Serverless Deployment")


if __name__ == "__main__":
    main()