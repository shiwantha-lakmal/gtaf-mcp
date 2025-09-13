import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from mcpserver.facade import OrdinoResultClient

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
def get_projects(mode: str = "summary") -> str:
    """
    Get all active projects from testing platform.
    
    Args:
        mode: Control level of detail returned
            - "summary": Return only ID and name (default)
            - "full": Return extended technical details
    
    Returns:
        Summary mode: Minimal project metadata for LLM consumption
        Full mode: Complete project data for debugging
    """
    import json
    
    raw = result_client.get_projects()
    if mode == "summary":
        summary_data = [{"id": p["id"], "name": p["name"]} for p in raw]
        return json.dumps(summary_data, indent=2)
    return json.dumps(raw, indent=2)
    
@mcp.tool()
def get_failures_by_project(project_name: str, mode: str = "summary") -> str:
    """
    Get test failure details for a specific project by name.
    
    Args:
        project_name: Name of the project to get failure details for
        mode: Control level of detail returned
            - "summary": Return essential failure info to understand situation (default)
            - "full": Return detailed root cause analysis with complete stack traces
    
    Returns:
        Summary mode: Essential test failure details for quick understanding
        Full mode: Complete failure analysis with stack traces and root cause info
    """
    import json
    
    if mode == "summary":
        data = result_client.get_failures_summary(project_name)
    else:
        data = result_client.get_failures_full(project_name)
    
    return json.dumps(data, indent=2)
    

@mcp.tool()
def get_knowledge_db_documents(partial_testcase_name: str) -> str:
    """
    Fetch documents from knowledge database using partial test case name matching.
    
    Args:
        partial_testcase_name: Partial or full test case name to search for
    
    Returns JSON array with:
    - Matched test case documents from knowledge database
    - Test failure history and occurrence details
    - Bug classification status and tester notes
    - Statistical information about failures
    """
    import json
    
    # Initialize knowledge database
    from mcpserver.facade.knowledge_db import LightweightKnowledgeDB
    knowledge_db = LightweightKnowledgeDB()
    
    # Search for matching test cases
    matching_documents = []
    
    try:
        # Get all testcase files
        testcases_path = knowledge_db.testcases_path
        
        if not testcases_path.exists():
            return json.dumps({
                "success": False,
                "message": "Knowledge database testcases directory not found",
                "matched_documents": []
            })
        
        # Search through all JSON files
        for json_file in testcases_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    document = json.load(f)
                
                # Get test case name from document
                test_case_name = document.get("testCase", "")
                
                # Check for partial match (case-insensitive)
                if partial_testcase_name.lower() in test_case_name.lower():
                    # Add file information
                    document["source_file"] = json_file.name
                    document["matched_on"] = test_case_name
                    matching_documents.append(document)
                    
            except (json.JSONDecodeError, IOError) as e:
                # Skip files that can't be read or parsed
                continue
        
        # Sort by last_updated (most recent first)
        matching_documents.sort(
            key=lambda x: x.get("last_updated", ""), 
            reverse=True
        )
        
        return json.dumps({
            "success": True,
            "search_term": partial_testcase_name,
            "total_matches": len(matching_documents),
            "matched_documents": matching_documents
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "search_term": partial_testcase_name,
            "matched_documents": []
        })

@mcp.tool()
def process_and_save_all_failures(project_name: str = "") -> str:
    """
    Fetch and save test failures to knowledge database for specific project.
    
    Process: ["fetch", "get", "summarize", "analysis"] # ✅ failure data processing
    Save: ["caches", "store", "persist", "knowledgebase"] # ✅ knowledge database storage
    Project: ["partial", "name", "match", "dynamic", "lookup"] # ✅ flexible project selection
    
    Args:
        project_name: Project name or partial name (e.g. "portal", "reporting"). If empty, processes all projects.
    
    Returns: Success confirmation with case counts and processed projects.
    """
    import json
    
    # Call the result client method with optional project name
    project_filter = project_name.strip() if project_name and project_name.strip() else None
    processing_summary = result_client.process_and_save_all_failures(project_filter)
    
    # Optimize for LLM consumption - return required info in compact format
    optimized_result = {
        "success": processing_summary.get("success", False),
        "message": f"Processed {processing_summary.get('total_cases_saved', 0)} cases" if processing_summary.get("success") else "Processing failed",
        "projects_processed": processing_summary.get("projects_processed", []),
        "total_cases_saved": processing_summary.get("total_cases_saved", 0),
        "available_projects": processing_summary.get("available_projects", [])
    }
    
    return json.dumps(optimized_result, indent=2)

@mcp.tool()
def get_latest_result_analysis(project_name: str, mode: str = "summary") -> str:
    """
    Get latest test result analysis from test report with summary and full detail modes.
    
    Args:
        project_name: Project name or keyword to find matching test setup
        mode: Analysis mode - "summary" for key metrics or "full" for complete details
    
    Analysis: ["test", "results", "metrics", "failures", "report"] # ✅ test execution analysis
    Summary: ["overview", "stats", "highlights", "brief", "key"] # ✅ concise metrics & insights
    
    Returns: JSON with test metrics, pass rates, failure highlights - optimized for low LLM consumption
    """
    import json
    
    if mode == "summary":
        data = result_client.get_latest_summary(project_name)
        # Save summary stats to knowledge database
        if "error" not in data:  # Only save if no error occurred
            saved_path = result_client.save_analysis_to_knowledge_db(project_name, data)
            data["_saved_to_knowledge_db"] = saved_path
    else:
        data = result_client.get_latest_full(project_name)
    
    return json.dumps(data, indent=2)


@mcp.tool()
def cleanup_knowledge_database() -> str:
    """
    Fully clean knowledge database - removes all testcases, analysis files & directories.
    
    Clean: ["remove", "delete", "clear", "purge", "reset"] # ✅ complete cleanup operation
    Database: ["testcases", "analysis", "files", "dirs", "knowledge"] # ✅ all stored data
    
    WARNING: Irreversible action - permanently deletes all knowledge database content.
    
    Returns: Success confirmation with removal counts only.
    """
    import json
    from mcpserver.facade.knowledge_db import LightweightKnowledgeDB
    
    knowledge_db = LightweightKnowledgeDB()
    cleanup_results = knowledge_db.cleanup_knowledge_db_fully()
    
    # Optimize for LLM consumption - return only essential info
    optimized_result = {
        "success": cleanup_results.get("success", False),
        "testcases_removed": cleanup_results.get("testcases_removed", 0),
        "analysis_files_removed": cleanup_results.get("analysis_files_removed", 0),
        "analysis_dirs_removed": cleanup_results.get("analysis_directories_removed", 0),
        "status": "completed" if cleanup_results.get("success") else "failed"
    }
    
    # Only include errors if they exist
    if cleanup_results.get("errors"):
        optimized_result["error_count"] = len(cleanup_results["errors"])
    
    return json.dumps(optimized_result, indent=2)