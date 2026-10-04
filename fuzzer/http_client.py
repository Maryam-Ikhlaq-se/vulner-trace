"""
Layer: Fuzzer
Responsibility: Send adversarial HTTP requests to target API endpoints.
Takes generated payloads and returns raw responses for analysis.
Has no knowledge of payload generation, scoring, or output formatting.
"""

import requests
import time


# Default headers for all requests
DEFAULT_HEADERS = {
    "Content-Type":  "application/json",
    "User-Agent":    "VulnerTrace-Security-Scanner/1.0"
}


def send_request(
    base_url:   str,
    endpoint:   dict,
    payload:    dict,
    timeout:    int = 10
) -> dict:
    """
    Sends a single HTTP request with an adversarial payload.

    Args:
        base_url  (str) : Target API base URL e.g. https://api.example.com
        endpoint  (dict): Endpoint dict from swagger_parser
        payload   (dict): Single payload to send {param_name: value}
        timeout   (int) : Request timeout in seconds

    Returns:
        dict: {
            "status_code"    (int) : HTTP response code
            "response_body"  (str) : Response text
            "response_time"  (float): Time taken in seconds
            "payload_sent"   (dict): The payload that was sent
            "endpoint"       (dict): The endpoint that was tested
        }
    """

    url    = base_url.rstrip('/') + endpoint['path']
    method = endpoint['method'].upper()

    start_time = time.time()

    try:
        if method == "GET":
            response = requests.get(
                url,
                params=payload,
                headers=DEFAULT_HEADERS,
                timeout=timeout
            )
        elif method == "POST":
            response = requests.post(
                url,
                json=payload,
                headers=DEFAULT_HEADERS,
                timeout=timeout
            )
        elif method == "PUT":
            response = requests.put(
                url,
                json=payload,
                headers=DEFAULT_HEADERS,
                timeout=timeout
            )
        elif method == "DELETE":
            response = requests.delete(
                url,
                headers=DEFAULT_HEADERS,
                timeout=timeout
            )
        else:
            response = requests.request(
                method,
                url,
                json=payload,
                headers=DEFAULT_HEADERS,
                timeout=timeout
            )

        return {
            "status_code":   response.status_code,
            "response_body": response.text[:2000],  # Limit to 2000 chars
            "response_time": round(time.time() - start_time, 3),
            "payload_sent":  payload,
            "endpoint":      endpoint,
            "error":         None
        }

    except requests.exceptions.Timeout:
        return {
            "status_code":   0,
            "response_body": "Request timed out",
            "response_time": timeout,
            "payload_sent":  payload,
            "endpoint":      endpoint,
            "error":         "timeout"
        }

    except requests.exceptions.ConnectionError:
        return {
            "status_code":   0,
            "response_body": "Connection failed",
            "response_time": 0,
            "payload_sent":  payload,
            "endpoint":      endpoint,
            "error":         "connection_error"
        }


def fuzz_endpoint(
    base_url:        str,
    endpoint_data:   dict
) -> list[dict]:
    """
    Sends all generated payloads against a single endpoint.

    Args:
        base_url       (str) : Target API base URL
        endpoint_data  (dict): Output from attack_generator.generate_payloads()
                               Contains endpoint + payloads

    Returns:
        list[dict]: All HTTP responses for this endpoint
    """

    endpoint = endpoint_data['endpoint']
    payloads = endpoint_data['payloads']
    results  = []

    for param_name, attack_categories in payloads.items():
        for attack_type, payload_list in attack_categories.items():
            for payload_value in payload_list:

                # Build payload dict
                payload = {param_name: payload_value}

                result = send_request(base_url, endpoint, payload)
                result['attack_type'] = attack_type
                result['param_name']  = param_name

                results.append(result)

    return results


def fuzz_all_endpoints(
    base_url:       str,
    all_payloads:   list[dict]
) -> list[dict]:
    """
    Fuzzes all endpoints with all generated payloads.

    Args:
        base_url      (str)      : Target API base URL
        all_payloads  (list[dict]): Output from attack_generator.generate_all_payloads()

    Returns:
        list[dict]: All HTTP responses across all endpoints
    """

    all_results = []

    for endpoint_data in all_payloads:
        endpoint = endpoint_data['endpoint']
        print(f"  Fuzzing: {endpoint['method']} {endpoint['path']}")
        results = fuzz_endpoint(base_url, endpoint_data)
        all_results.extend(results)

    return all_results