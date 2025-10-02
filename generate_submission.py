import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000"
BENCHMARK_FILE = os.path.join("DB_Dataset", "benchmark_queries.json")
OUTPUT_FILE = "submission.json"

def generate_submission():
    """Reads a list of benchmark queries, calls the API, and generates the submission.json file."""
    try:
        with open(BENCHMARK_FILE, 'r') as f:
            benchmark_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Benchmark file not found at '{BENCHMARK_FILE}'")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{BENCHMARK_FILE}'")
        return

    submission_results = {}
    print("--- Generating submission.json ---")

    # The actual queries are in a list under the "tests" key.
    queries_to_run = benchmark_data.get("tests", [])

    # We loop directly through the list. Each item in the list is a dictionary.
    for test_case in queries_to_run:
        try:
            # We access the details from the dictionary by key.
            query_id = test_case["id"]
            search_type = test_case["type"]
            query = test_case["query"]
        except (KeyError, TypeError) as e:
            print(f"  - Skipping malformed test case: {test_case}. Error: {e}")
            continue
        
        url = f"{BASE_URL}/search/{search_type}?q={query}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            results_list = response.json().get("results", [])
            submission_results[query_id] = results_list
            print(f"  - Processed query ID {query_id}: Found {len(results_list)} results.")

        except requests.exceptions.RequestException as e:
            print(f"Error querying {url}: {e}")
            submission_results[query_id] = []

    final_submission = {"results": submission_results}

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(final_submission, f, indent=2)

    print(f"\nSuccessfully created '{OUTPUT_FILE}'!")

if __name__ == "__main__":
    print("Make sure your FastAPI server is running before executing this script.")
    generate_submission()