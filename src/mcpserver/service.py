from mcp.server.fastmcp import FastMCP
from .facade import OrdinoResultClient, LightweightKnowledgeDB

mcp = FastMCP("service")

# Initialize result client
result_client = OrdinoResultClient()

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
    return result_client.get_projects()
    
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
    - Slowness/Network issues or framework errors 
    
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
    return result_client.get_test_failures()

@mcp.tool()
def save_failure_to_db(test_case: str, error: str, stack_trace: str = "", file_path: str = "", failed_step: str = "") -> str:
    """
    Save a test failure to the knowledge database for tracking and analysis.
    
    This function allows manual saving of test failures to build historical knowledge:
    - Tracks recurring failures and patterns
    - Builds failure frequency statistics
    - Enables pattern recognition for similar issues
    - Provides historical context for debugging
    
    Args:
        test_case: Name/description of the failed test case
        error: Error message or exception details
        stack_trace: Full stack trace (optional)
        file_path: Path to the test file (optional)
        failed_step: Specific step that failed (optional)
    
    Returns:
        JSON string with failure ID and database statistics
        
    Example Usage:
        save_failure_to_db(
            test_case="Login form validation test",
            error="Element not found: #login-button",
            stack_trace="ElementNotFound: Unable to locate element...",
            file_path="tests/auth/login.test.js",
            failed_step="click('#login-button')"
        )
    """
    import json
    
    # Call the result client method
    response = result_client.save_failure_to_db(test_case, error, stack_trace, file_path, failed_step)
    
    return json.dumps(response, indent=2)

@mcp.tool()
def process_and_save_all_failures() -> str:
    """
    Get all current test failures from the main API and save them to the knowledge database.
    
    This function:
    - Fetches the latest test failures from the dataplatform-reporting project
    - Processes each failure and saves it to the knowledge database
    - Provides summary statistics and insights
    - Identifies recurring and similar failure patterns
    
    Use cases:
    - Bulk import of current test failures into knowledge database
    - Historical tracking of test suite stability
    - Pattern analysis for recurring issues
    - Building failure knowledge base for debugging
    
    Returns:
        JSON string with processing summary and database statistics
    """
    import json
    
    # Call the result client method
    processing_summary = result_client.process_and_save_all_failures()
    
    return json.dumps(processing_summary, indent=2)
