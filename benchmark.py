import asyncio
import time
import aiohttp
import logging
import os
from datetime import datetime

# Setup Logging 
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Create a unique log file name with a timestamp
log_filename = os.path.join(LOG_DIR, f"benchmark_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

# Configure the logger to write to both a file and the console
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s', # Keep the output clean
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

# Benchmark Configuration ---
BASE_URL = "http://127.0.0.1:8000"

QUERIES_TO_TEST = [
    {"type": "prefix", "query": "Ava"},
    {"type": "substring", "query": "Injection"},
    {"type": "fulltext", "query": "antibiotic"},
    {"type": "fussy", "query": "Avastn"},
]

TOTAL_REQUESTS = 100
CONCURRENCY = 10

async def test_endpoint(session, search_type, query):
    """Helper function to perform a single request and return its status and latency."""
    url = f"{BASE_URL}/search/{search_type}?q={query}"
    start_time = time.time()
    try:
        async with session.get(url) as response:
            await response.read()
            end_time = time.time()
            latency = (end_time - start_time) * 1000
            return response.status, latency
    except aiohttp.ClientError:
        return None, -1

async def main():
    """Main function to run all benchmark tests."""
    async with aiohttp.ClientSession() as session:
        
        logging.info("--- 1. Latency Test (Single Request Performance) ---")
        for test in QUERIES_TO_TEST:
            status, latency = await test_endpoint(session, test["type"], test["query"])
            if status == 200:
                logging.info(f"  - Endpoint: /search/{test['type']:<10} | Query: '{test['query']:<12}' | Latency: {latency:.2f} ms")
            else:
                logging.info(f"  - Endpoint: /search/{test['type']:<10} | Query: '{test['query']:<12}' | FAILED (Status: {status})")
        
        logging.info("\n--- 2. Throughput Test (Concurrent Performance) ---")
        for test in QUERIES_TO_TEST:
            logging.info(f"  - Testing Endpoint: /search/{test['type']} with query '{test['query']}'...")
            
            tasks = [test_endpoint(session, test['type'], test['query']) for _ in range(TOTAL_REQUESTS)]
            
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            total_time = end_time - start_time
            successful_requests = sum(1 for status, _ in results if status == 200)
            
            if total_time > 0:
                requests_per_second = successful_requests / total_time
                logging.info(f"    -> Completed {successful_requests}/{TOTAL_REQUESTS} requests in {total_time:.2f}s | Throughput: {requests_per_second:.2f} req/s")
            else:
                logging.info("    -> Completed requests too quickly to measure throughput.")

if __name__ == "__main__":
    logging.info("Make sure your FastAPI server is running before executing this script.")
    logging.info(f"Throughput test will run {TOTAL_REQUESTS} requests per endpoint with {CONCURRENCY} concurrent requests.\n")
    asyncio.run(main())