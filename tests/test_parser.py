"""
Test: Swagger Parser
Layer: Ingestion
Tests that swagger spec is correctly loaded and endpoints extracted.
"""

from ingestion.swagger_parser import load_and_parse

# Public test API swagger URL
SWAGGER_URL = "https://petstore.swagger.io/v2/swagger.json"


def test_parser():
    print("\nLoading swagger spec...")
    endpoints = load_and_parse(SWAGGER_URL)

    print(f"Total endpoints found: {len(endpoints)}")
    print("\nFirst 5 endpoints:")

    for ep in endpoints[:5]:
        print(f"  {ep['method']} {ep['path']}")
        print(f"  Summary:    {ep['summary']}")
        print(f"  Parameters: {ep['parameters']}")
        print()


if __name__ == "__main__":
    test_parser()