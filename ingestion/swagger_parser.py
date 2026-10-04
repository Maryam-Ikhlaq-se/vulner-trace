"""
Layer: Ingestion
Responsibility: Parse OpenAPI/Swagger specification files.
Extracts endpoints, HTTP methods, and parameters into a clean structure.
This module has no knowledge of fuzzing, LLM, or output layers.
"""

import json
import yaml
import requests


def load_swagger(source: str) -> dict:
    """
    Loads a Swagger/OpenAPI spec from a file path or URL.

    Args:
        source (str): File path (.json/.yaml) or URL to swagger spec

    Returns:
        dict: Raw parsed swagger specification
    """

    # URL se load karo
    if source.startswith("http"):
        response = requests.get(source, timeout=10)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch swagger: {response.status_code}")
        if "yaml" in source or "yml" in source:
            return yaml.safe_load(response.text)
        return response.json()

    # Local file se load karo
    with open(source, 'r', encoding='utf-8') as f:
        if source.endswith(".yaml") or source.endswith(".yml"):
            return yaml.safe_load(f)
        return json.load(f)


def extract_parameters(method_data: dict) -> list[str]:
    """
    Extracts all parameter names from a single endpoint method.
    Handles query params, path params, and request body properties.

    Args:
        method_data (dict): Single method data from swagger paths

    Returns:
        list[str]: List of parameter names
    """

    parameters = []

    # Query aur path parameters
    for param in method_data.get("parameters", []):
        if "name" in param:
            parameters.append(param["name"])

    # Request body parameters
    request_body = method_data.get("requestBody", {})
    content      = request_body.get("content", {})

    for content_type, content_data in content.items():
        schema     = content_data.get("schema", {})
        properties = schema.get("properties", {})
        parameters.extend(properties.keys())

    return parameters


def parse_endpoints(swagger: dict) -> list[dict]:
    """
    Parses all endpoints from a swagger spec into a clean list.

    Args:
        swagger (dict): Raw swagger specification

    Returns:
        list[dict]: List of endpoint dicts, each containing:
                    - 'path'       (str) : Endpoint path e.g. /api/login
                    - 'method'     (str) : HTTP method e.g. POST
                    - 'summary'    (str) : Short description
                    - 'parameters' (list): Parameter names
    """

    endpoints = []
    paths     = swagger.get("paths", {})

    for path, path_data in paths.items():
        for method, method_data in path_data.items():

            # Skip non-method keys
            if method not in ["get", "post", "put", "delete", "patch"]:
                continue

            endpoints.append({
                "path":       path,
                "method":     method.upper(),
                "summary":    method_data.get("summary", "No description"),
                "parameters": extract_parameters(method_data)
            })

    return endpoints


def load_and_parse(source: str) -> list[dict]:
    """
    Main function — loads swagger and returns clean endpoint list.

    Args:
        source (str): File path or URL to swagger spec

    Returns:
        list[dict]: Parsed endpoints ready for fuzzing
    """

    swagger   = load_swagger(source)
    endpoints = parse_endpoints(swagger)
    return endpoints