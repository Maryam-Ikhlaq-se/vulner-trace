"""
Layer: Fuzzer
Responsibility: Generate adversarial test payloads using Gemini AI.
Takes endpoint details and returns attack payloads per parameter.
Has no knowledge of HTTP requests, scoring, or output formatting.
"""

from llm.gemini_client import get_structured_response


# OWASP attack categories to test
ATTACK_CATEGORIES = [
    "sql_injection",
    "xss",
    "auth_bypass",
    "input_validation",
    "sensitive_data"
]


def generate_payloads(endpoint: dict) -> dict:
    """
    Generates adversarial payloads for all parameters of an endpoint.

    Args:
        endpoint (dict): Single endpoint dict from swagger_parser
                         Must contain: path, method, parameters

    Returns:
        dict: {
            "endpoint": endpoint,
            "payloads": {
                "username": {
                    "sql_injection": ["admin'--", "' OR 1=1"],
                    "xss": ["<script>alert(1)</script>"],
                    ...
                },
                "password": {...}
            }
        }
    """

    # Skip endpoints with no parameters
    if not endpoint["parameters"]:
        return {
            "endpoint":  endpoint,
            "payloads":  {}
        }

    prompt = f"""
You are a software quality engineer writing automated test cases for API validation testing.

API Endpoint Details:
- Path:       {endpoint['path']}
- Method:     {endpoint['method']}
- Summary:    {endpoint['summary']}
- Parameters: {endpoint['parameters']}

Generate boundary and edge case test inputs for each parameter to verify input validation:
1. SQL special characters (for testing sanitization)
2. HTML special characters (for testing encoding)
3. Empty and null values (for testing required field validation)
4. Extremely long strings (for testing length limits)
5. Special characters and unicode (for testing encoding)

Return ONLY this exact JSON format, no explanation, no markdown:
{{
    "parameter_name": {{
        "sql_injection":    ["test1", "test2", "test3"],
        "xss":              ["test1", "test2"],
        "auth_bypass":      ["test1", "test2"],
        "input_validation": ["test1", "test2"],
        "sensitive_data":   ["test1", "test2"]
    }}
}}

Generate for ALL parameters: {endpoint['parameters']}
"""

    return {
        "endpoint": endpoint,
        "payloads": get_structured_response(prompt)
    }


def generate_all_payloads(endpoints: list[dict]) -> list[dict]:
    """
    Generates payloads for all endpoints.

    Args:
        endpoints (list[dict]): Output from swagger_parser.load_and_parse()

    Returns:
        list[dict]: Each endpoint with its generated payloads
    """

    results = []

    for endpoint in endpoints:
        print(f"  Generating payloads: {endpoint['method']} {endpoint['path']}")
        result = generate_payloads(endpoint)
        results.append(result)

    return results