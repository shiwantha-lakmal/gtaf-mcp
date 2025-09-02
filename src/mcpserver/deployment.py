from mcp.server.fastmcp import FastMCP

mcp = FastMCP("deployment")

@mcp.tool()
# add 2 digit and return the result
def add(digit1: int, digit2: int) -> int:
    """Add 2 digit and return the result"""
    return digit1 + digit2

@mcp.tool()
def get_projects() -> str:
    """Get all projects by calling API"""
    import requests
    import json
    
    url = "https://dev-portal.ordino.ai/api/v1/project-external"
    headers = {
        "Ordino-Key": "ztjEFessWESzKfkaMRZiJHcQ+UY19N6tHW5GKj7QfS4="
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    return json.dumps(response.json(), indent=2)
    