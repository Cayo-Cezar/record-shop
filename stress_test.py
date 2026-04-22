import concurrent.futures
import urllib.request
import urllib.error
import json
import time

URL = "http://localhost:8000/pedidos"
TOTAL_REQUESTS = 500
CONCURRENCY = 50

# Use the IDs we fetched from the running database
CLIENTE_ID = 512
DISCO_ID = 1368  # We Are Reactive (500 units in stock)

PAYLOAD = json.dumps({
    "cliente_id": CLIENTE_ID,
    "itens": [
        {"disco_id": DISCO_ID, "quantidade": 1}
    ]
}).encode('utf-8')

HEADERS = {
    'Content-Type': 'application/json'
}

def send_request(req_id: int) -> int | str:
    req = urllib.request.Request(URL, data=PAYLOAD, headers=HEADERS, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            return response.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return str(e)

def main():
    print(f"Starting stress test: {TOTAL_REQUESTS} requests, {CONCURRENCY} concurrency.")
    start_time = time.time()
    
    status_codes = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [executor.submit(send_request, i) for i in range(TOTAL_REQUESTS)]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            status_codes[res] = status_codes.get(res, 0) + 1
            
    elapsed = time.time() - start_time
    print(f"\nCompleted in {elapsed:.2f} seconds.")
    print("Status code distribution:")
    for code, count in status_codes.items():
        print(f"  HTTP {code}: {count}")

if __name__ == "__main__":
    main()
