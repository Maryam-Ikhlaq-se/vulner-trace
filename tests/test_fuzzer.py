"""
Test: Fuzzer Layer
Tests payload generation and HTTP fuzzing on a public test API.
Target: Petstore API — safe, public, designed for testing.
"""

from ingestion.swagger_parser import load_and_parse
from fuzzer.attack_generator import generate_payloads
from fuzzer.http_client import fuzz_endpoint

# Public test API
SWAGGER_URL = "https://petstore.swagger.io/v2/swagger.json"
BASE_URL    = "https://petstore.swagger.io/v2"


def test_fuzzer():

    # Step 1: Parse swagger
    print("\nParsing swagger...")
    endpoints = load_and_parse(SWAGGER_URL)

    # Test on first endpoint that has parameters
    target = None
    for ep in endpoints:
        if ep['parameters']:
            target = ep
            break

    print(f"Testing endpoint: {target['method']} {target['path']}")
    print(f"Parameters: {target['parameters']}")

    # Step 2: Generate payloads
    print("\nGenerating adversarial payloads...")
    payload_data = generate_payloads(target)
    print(f"Payloads generated for: {list(payload_data['payloads'].keys())}")

    # Step 3: Fuzz endpoint
    print("\nFuzzing endpoint...")
    results = fuzz_endpoint(BASE_URL, payload_data)
    print(f"Total requests sent: {len(results)}")

    # Show sample results
    print("\nSample responses:")
    for r in results[:3]:
        print(f"  Attack: {r['attack_type']}")
        print(f"  Payload: {r['payload_sent']}")
        print(f"  Status: {r['status_code']}")
        print(f"  Time: {r['response_time']}s")
        print()


if __name__ == "__main__":
    test_fuzzer()