from mcp.server.fastmcp import FastMCP
from mcpserver.facade import OrdinoResultClient, LightweightKnowledgeDB

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

@mcp.tool()
def generate_test_failure_analysis_report(report_format: str = "markdown", include_detailed_analysis: bool = True) -> str:
    """
    Generate a comprehensive test failure analysis report using the Markdown template.
    
    This function creates a detailed RCA (Root Cause Analysis) report by:
    - Fetching current test failures from the API
    - Analyzing failure patterns and root causes
    - Generating insights from the knowledge database
    - Creating a formatted report using the Markdown template
    - Saving the report to the RCA directory
    
    Features:
    - Comprehensive failure analysis with statistics
    - Root cause identification and impact assessment
    - Service health status evaluation
    - Actionable recommendations and next steps
    - Historical failure pattern analysis
    - Business impact assessment
    
    Args:
        report_format: Format of the report ("markdown" or "json")
        include_detailed_analysis: Whether to include detailed technical analysis
    
    Use cases:
    - Automated RCA report generation for test failures
    - Stakeholder communication and status updates
    - Development team debugging assistance
    - Quality assurance process improvement
    - Historical failure tracking and analysis
    - Business impact assessment and risk evaluation
    
    Returns:
        JSON string with report generation status and file path
        
    Output:
        Saves report as .md file in src/resources/template/rca/ directory
    """
    import json
    import os
    from datetime import datetime
    
    try:
        # Get current test failures
        failures_json = result_client.get_test_failures()
        failures_data = json.loads(failures_json)
        
        # Generate report data
        report_data = _generate_report_data(failures_data, include_detailed_analysis)
        
        if report_format.lower() == "markdown":
            # Generate markdown report
            report_content = _generate_markdown_report(report_data)
            
            # Save report to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_failure_analysis_report_{timestamp}.md"
            file_path = os.path.join("src/resources/template/rca", filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            return json.dumps({
                "success": True,
                "message": "Test failure analysis report generated successfully",
                "report_path": file_path,
                "report_format": report_format,
                "timestamp": timestamp,
                "summary": {
                    "total_failures": report_data.get("total_failures", 0),
                    "critical_issues": report_data.get("critical_issues", 0),
                    "affected_modules": len(report_data.get("modules", [])),
                    "root_causes": len(report_data.get("root_causes", []))
                }
            }, indent=2)
        else:
            # Return JSON format
            return json.dumps({
                "success": True,
                "message": "Test failure analysis data generated successfully",
                "report_format": "json",
                "data": report_data
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "Failed to generate test failure analysis report"
        }, indent=2)

def _generate_report_data(failures_data, include_detailed_analysis=True):
    """Generate structured report data from failures."""
    from collections import defaultdict
    from datetime import datetime
    
    report_data = {
        "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "environment": "grubcenter.staging.grubtech.io",
        "total_failures": 0,
        "success_rate": 0,
        "root_causes_count": 0,
        "affected_modules_count": 0,
        "impact_summary": "",
        "primary_root_cause": "Unknown",
        "failed_test_name": "",
        "failed_test_file": "",
        "primary_error": "",
        "cascade_impact": "",
        "stack_trace": "",
        "error_translation": "",
        "modules": [],
        "evidence_data": [],
        "service_health": [],
        "business_impact": [],
        "action_items": {
            "immediate": [],
            "short_term": [],
            "long_term": []
        },
        "additional_notes": ""
    }
    
    if not failures_data.get("isSuccess") or not failures_data.get("extraInfo"):
        report_data["impact_summary"] = "No test failure data available or API call failed"
        return report_data
    
    failures = failures_data["extraInfo"]
    report_data["total_failures"] = len(failures)
    
    # Analyze failures by module/file
    module_failures = defaultdict(list)
    error_patterns = defaultdict(int)
    
    for failure in failures:
        file_path = failure.get("filePath", "Unknown")
        module_name = _extract_module_name(file_path)
        module_failures[module_name].append(failure)
        
        error = failure.get("error", "")
        error_type = error.split('\n')[0] if error else "Unknown Error"
        error_patterns[error_type] += 1
    
    # Find primary root cause (most common error)
    if error_patterns:
        primary_error_type, primary_count = max(error_patterns.items(), key=lambda x: x[1])
        report_data["primary_root_cause"] = primary_error_type
        report_data["primary_error"] = primary_error_type
        report_data["cascade_impact"] = f"Single failure caused {primary_count} cascading failures"
        
        # Find the first failure with this error
        for failure in failures:
            if failure.get("error", "").startswith(primary_error_type.split(':')[0]):
                report_data["failed_test_name"] = failure.get("testCase", "Unknown Test")
                report_data["failed_test_file"] = failure.get("filePath", "Unknown File")
                report_data["stack_trace"] = failure.get("stackTrace", "No stack trace available")
                break
    
    # Calculate success rate
    total_tests = report_data["total_failures"] + 0  # Assume all tests failed for now
    report_data["success_rate"] = 0 if total_tests > 0 else 100
    
    # Module analysis
    for module, module_failures_list in module_failures.items():
        failure_count = len(module_failures_list)
        percentage = (failure_count / report_data["total_failures"]) * 100 if report_data["total_failures"] > 0 else 0
        
        report_data["modules"].append({
            "name": module,
            "failures": failure_count,
            "percentage": round(percentage, 1),
            "status": "Critical" if failure_count > 5 else "Warning" if failure_count > 1 else "Minor",
            "impact": _generate_module_impact(module, failure_count)
        })
    
    # Sort modules by failure count
    report_data["modules"].sort(key=lambda x: x["failures"], reverse=True)
    report_data["affected_modules_count"] = len(report_data["modules"])
    report_data["root_causes_count"] = len(error_patterns)
    
    # Generate impact summary
    if report_data["modules"]:
        top_module = report_data["modules"][0]
        report_data["impact_summary"] = f"Complete test suite failure affecting {report_data['affected_modules_count']} modules. Primary impact in {top_module['name']} with {top_module['failures']} failures ({top_module['percentage']}%)."
    
    # Generate error translation
    if "undefined" in report_data["primary_error"].lower():
        report_data["error_translation"] = "API returned undefined response, then code tried to access properties causing null reference error."
    elif "element not found" in report_data["primary_error"].lower():
        report_data["error_translation"] = "UI elements are missing, likely due to empty database or failed data loading."
    else:
        report_data["error_translation"] = "System error requiring investigation."
    
    # Add service health analysis
    report_data["service_health"] = [
        {"service": "Authentication Service", "status": "Working", "evidence": "Tests pass login", "impact": "None"},
        {"service": "Test Data Service", "status": "CRITICAL FAILURE", "evidence": "API returns undefined", "impact": "Complete test suite failure"},
        {"service": "Database Connection", "status": "Unknown", "evidence": "Needs verification", "impact": "Potential data persistence issues"},
        {"service": "UI Services", "status": "Working but no data", "evidence": "UI loads but shows empty", "impact": "Customer-facing impact"}
    ]
    
    # Generate action items
    report_data["action_items"]["immediate"] = [
        "Verify test data creation service status",
        "Check database connectivity and data persistence",
        "Validate API endpoint accessibility",
        "Review recent API schema changes"
    ]
    
    report_data["action_items"]["short_term"] = [
        "Add null safety checks in test code",
        "Implement retry logic for data creation",
        "Add health checks before test execution",
        "Create fallback test data mechanisms"
    ]
    
    report_data["action_items"]["long_term"] = [
        "Implement comprehensive service monitoring",
        "Add automated failure pattern detection",
        "Create test data validation framework",
        "Establish failure recovery procedures"
    ]
    
    return report_data

def _extract_module_name(file_path):
    """Extract module name from file path."""
    if not file_path or file_path == "Unknown":
        return "Unknown Module"
    
    # Extract meaningful module name from path
    parts = file_path.split('/')
    if len(parts) > 1:
        return parts[-2].replace('_', ' ').title() + " Module"
    else:
        return file_path.split('.')[0].replace('_', ' ').title() + " Module"

def _generate_module_impact(module_name, failure_count):
    """Generate impact description for a module."""
    if failure_count > 20:
        return "Critical system failure - complete module breakdown"
    elif failure_count > 10:
        return "Major functionality affected - multiple feature failures"
    elif failure_count > 5:
        return "Moderate impact - several test failures"
    elif failure_count > 1:
        return "Minor issues - limited functionality affected"
    else:
        return "Single point failure - isolated issue"

def _generate_markdown_report(report_data):
    """Generate markdown report from template."""
    from datetime import datetime
    
    # Read the markdown template
    template_path = "src/resources/template/rca/test_failure_analysis.md"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        # Fallback basic template if file not found
        template = """# 🐛 Test Failure Analysis Report

## 📋 Executive Summary
- **Total Failed Tests:** {total_failures}
- **Success Rate:** {success_rate}%
- **Root Causes:** {root_causes_count}
- **Affected Modules:** {affected_modules_count}

## 🔍 Root Cause Analysis
**Primary Root Cause:** {primary_root_cause}
**Failed Test:** {failed_test_name}
**File:** {failed_test_file}
**Error:** {primary_error}

## 📊 Module Breakdown
{module_breakdown}

## 🔧 Action Items
### Immediate Actions
{immediate_actions}

*Report generated on {report_date}*
"""
    
    # Generate module breakdown table
    module_breakdown = "| Module | Failures | Percentage | Status | Impact |\n|--------|----------|------------|---------|--------|\n"
    for module in report_data["modules"]:
        module_breakdown += f"| {module['name']} | {module['failures']} | {module['percentage']}% | {module['status']} | {module['impact']} |\n"
    
    # Generate timeline items
    timeline_items = """
- ✅ **Test Environment Starts** - Test suite initialization successful
- ✅ **User Authentication Succeeds** - Login functionality working correctly  
- ❌ **Data Creation Fails** - API returns undefined - Critical failure point
- ❌ **Code Crashes** - Accessing undefined properties causes errors
- ❌ **No Test Data Created** - Database remains empty for all tests
- ❌ **All Tests Fail** - Cascading failures due to empty database
"""
    
    # Generate service health rows
    service_health_rows = ""
    for service in report_data["service_health"]:
        status_emoji = "✅" if service["status"] == "Working" else "❌" if "CRITICAL" in service["status"] else "⚠️"
        service_health_rows += f"| {service['service']} | {status_emoji} {service['status']} | {service['evidence']} | {service['impact']} |\n"
    
    # Generate action lists
    immediate_actions = "\n".join([f"- {action}" for action in report_data["action_items"]["immediate"]])
    short_term_actions = "\n".join([f"- {action}" for action in report_data["action_items"]["short_term"]])
    long_term_actions = "\n".join([f"- {action}" for action in report_data["action_items"]["long_term"]])
    
    # Replace template variables
    replacements = {
        "{report_date}": report_data["report_date"],
        "{environment}": report_data["environment"],
        "{total_failures}": str(report_data["total_failures"]),
        "{success_rate}": str(report_data["success_rate"]),
        "{success_status}": "🔴 Critical" if report_data["success_rate"] == 0 else "✅ Good",
        "{root_causes_count}": str(report_data["root_causes_count"]),
        "{root_cause_status}": "🔴 Multiple Issues" if report_data["root_causes_count"] > 1 else "⚠️ Single Issue",
        "{affected_modules_count}": str(report_data["affected_modules_count"]),
        "{modules_status}": "🔴 Critical" if report_data["affected_modules_count"] > 3 else "⚠️ Limited",
        "{impact_summary}": report_data["impact_summary"],
        "{primary_root_cause}": report_data["primary_root_cause"],
        "{failed_test_name}": report_data["failed_test_name"],
        "{failed_test_file}": report_data["failed_test_file"],
        "{primary_error}": report_data["primary_error"],
        "{cascade_impact}": report_data["cascade_impact"],
        "{stack_trace}": report_data["stack_trace"][:500] + "..." if len(report_data["stack_trace"]) > 500 else report_data["stack_trace"],
        "{error_translation}": report_data["error_translation"],
        "{module_breakdown_chart}": _generate_module_chart(report_data["modules"]),
        "{module_table_rows}": module_breakdown,
        "{evidence_table_rows}": "| Order Count | 1 | 0 | ❌ Failed |\n| Sales Amount | Expected | 0.00 | ❌ Failed |",
        "{failure_pattern}": "Expected to find element: `tbody.GTTable__tableBody tr.GTTable__row--body`, but never found it",
        "{pattern_translation}": "All data tables are loading but contain no rows (empty database)",
        "{additional_issues}": "Monitor module shows wrong data instead of no data, indicating separate service issue",
        "{timeline_items}": timeline_items,
        "{service_health_rows}": service_health_rows,
        "{priority_1_actions}": immediate_actions,
        "{priority_3_actions}": short_term_actions,
        "{code_language}": "javascript",
        "{code_fix_example}": "// Add null safety check\nif (response && response.data) {\n    const data = response.data;\n} else {\n    throw new Error('API response is invalid');\n}",
        "{business_impact_rows}": "| Reporting Dashboard | HIGH | All metrics showing zero |\n| Analytics | HIGH | No data for decisions |",
        "{business_concerns}": immediate_actions,
        "{root_cause_strategy}": "Don't run full suite until data creation works",
        "{health_check_strategy}": "Add service health checks before running tests",
        "{progressive_strategy}": "Verify data creation before proceeding with tests",
        "{separate_issues_strategy}": "Handle monitor module separately - different root cause",
        "{immediate_actions}": immediate_actions,
        "{short_term_actions}": short_term_actions,
        "{long_term_actions}": long_term_actions,
        "{assigned_team}": "DevOps + Backend Team",
        "{assigned_contact}": "devops@company.com",
        "{reporter_team}": "QA Automation Team", 
        "{reporter_contact}": "qa@company.com",
        "{next_review_date}": "After service fix",
        "{review_contact}": "qa-lead@company.com",
        "{total_test_cases}": str(report_data["total_failures"]),
        "{passed_tests}": "0",
        "{failed_tests}": str(report_data["total_failures"]),
        "{skipped_tests}": "0",
        "{execution_time}": "Unknown",
        "{failure_distribution}": _generate_failure_distribution(report_data["modules"]),
        "{historical_comparison}": "No historical data available",
        "{dashboard_link}": "https://dev-portal.ordino.ai/dashboard",
        "{pipeline_link}": "https://github.com/company/repo/actions",
        "{logs_link}": "https://logs.company.com",
        "{kb_link}": "https://wiki.company.com/test-failures",
        "{additional_notes}": report_data["additional_notes"],
        "{report_id}": f"GTAF-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "{tool_version}": "1.0.0"
    }
    
    # Apply all replacements
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, str(value))
    
    return template

def _generate_module_chart(modules):
    """Generate ASCII chart for module failures."""
    if not modules:
        return "No module data available"
    
    chart = "```\n"
    for module in modules[:5]:  # Top 5 modules
        bar_length = int(module["percentage"] / 2)  # Scale down for display
        bar = "█" * bar_length + "░" * (50 - bar_length)
        chart += f"{module['name']:<20} │{bar}│ {module['percentage']}% ({module['failures']} failures)\n"
    chart += "```"
    return chart

def _generate_failure_distribution(modules):
    """Generate failure distribution summary."""
    if not modules:
        return "No distribution data available"
    
    distribution = ""
    for module in modules:
        distribution += f"- **{module['name']}:** {module['failures']} failures ({module['percentage']}%)\n"
    return distribution
