from mcp.server.fastmcp import FastMCP
from openai import OpenAI
from dotenv import load_dotenv
import os
import tempfile
import time
import json
from pathlib import Path

mcp = FastMCP("service")

@mcp.tool()
def add(digit1: int, digit2: int) -> int:
    """
    Performs mathematical addition of two integers.
    
    This utility function can be used for:
    - Basic arithmetic calculations
    - Test case counting and summation
    - Numerical data processing
    - Validation of computational workflows
    
    Args:
        digit1: First integer operand
        digit2: Second integer operand
        
    Returns:
        Sum of the two input integers
        
    Example:
        add(5, 3) -> 8
    """
    return digit1 + digit2

@mcp.tool()
def get_projects() -> str:
    """
    Retrieves all active projects from the GrubTech testing platform.
    
    This function provides comprehensive project information including:
    - Project metadata (ID, name, partner/team associations)
    - Testing configuration (platform, GUI, API, mobile capabilities)
    - Repository integration details
    - Feature flags and example ordino dev portal project settings
    
    Use cases:
    - Organization level projects discovery
    - Team level project listing
    - Project level identity management
    - Project information search
    - Project active status monitoring
    - Configuration auditing and compliance checks
    - Integration setup validation
    - Test environment preparation & Ordino Dev Portal Settings
    
    Returns:
        JSON string containing array of project objects with full configuration details
        
    API Endpoint: 
        GET /api/v1/project-external
        
    Authentication:
        Requires valid Ordino-Key header for API access
    """
    import requests
    import json
    
    url = "https://dev-portal.ordino.ai/api/v1/project-external"
    headers = {
        "Ordino-Key": "ztjEFessWESzKfkaMRZiJHcQ+UY19N6tHW5GKj7QfS4="
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    return json.dumps(response.json(), indent=2)
    
@mcp.tool()
def get_failures_by_project() -> str:
    """
    Retrieves comprehensive test failure analysis for the dataplatform-reporting project.
    
    This function provides detailed failure diagnostics including:
    - Complete test case identification and status
    - Full error messages with Cypress/Playwright testing framework details
    - Stack traces for debugging and root cause analysis
    - File paths and specific test step failures
    - UI interaction issues and element accessibility problems
    
    Key failure categories analyzed:
    - UI overlay DOM diff comparison analysis
    - Element interaction timeouts/accessibility or serve side errors
    - Data validation mismatches and assertion errors
    - Missing DOM elements and selector failures
    - Cross-browser compatibility problems or framework errors 
    
    Use cases:
    - Test failure triage and prioritization
    - Quality assurance reporting and metrics
    - Development debugging and issue resolution
    - Regression analysis and trend monitoring
    - Test failure investigation & root cause analysis
    - Test infrastructure health monitoring
    
    Returns:
        JSON string containing detailed failure report with:
        - Test execution status and success indicators
        - Json array of failed test cases with full diagnostic information
        - Error categorization for efficient debugging workflows
        - Suggested fixes and mitigation strategies based on the test failure history analysis
        - Is same testcase failed before or not if failed before then provide the fail history of the testcase
        
    API Endpoint:
        GET /api/v1/public/test-report/failed-test-cases/{project_id}
        
    Project Scope:
        dataplatform-reporting (ID: 0a180944-8df0-4fc5-9f38-98a36bfda85c)
        
    Authentication:
        Requires valid Ordino-Key with test report access permissions
    """
    import requests
    import json
    
    url = f"https://dev-portal.ordino.ai/api/v1/public/test-report/failed-test-cases/0a180944-8df0-4fc5-9f38-98a36bfda85c"
    headers = {
        "Ordino-Key": "YoXGKROxf/p43uOoTMhUVWusceS1Y+5VoaQP54sJU+I="
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    return json.dumps(response.json(), indent=2)