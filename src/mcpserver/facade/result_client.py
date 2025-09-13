import requests
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from .knowledge_db import LightweightKnowledgeDB


class OrdinoResultClient:
    """Client for interacting with Ordino API endpoints."""
    
    BASE_URL = "https://dev-portal.ordino.ai/api/v1"
    
    def __init__(self):
        self.knowledge_db = LightweightKnowledgeDB()
    
    def _make_request(self, endpoint: str, api_key: str) -> Dict[Any, Any]:
        """Make HTTP request to Ordino API endpoint."""
        headers = {"Ordino-Key": api_key}
        url = f"{self.BASE_URL}{endpoint}"
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Retrieve all active projects from the testing platform."""
        api_key = os.getenv("ORDINO_CLI_API_KEY")
        if not api_key:
            raise ValueError("ORDINO_CLI_API_KEY environment variable is required")
        endpoint = "/project-external"
        
        data = self._make_request(endpoint, api_key)
        return data
    
    def get_test_failures(self, project_id: str) -> str:
        """Retrieve comprehensive test failure analysis for a specific project."""
        api_key = os.getenv("ORDINO_SYSTEM_API_KEY")
        if not api_key:
            raise ValueError("ORDINO_SYSTEM_API_KEY environment variable is required")
        endpoint = f"/public/test-report/failed-test-cases/{project_id}"
        
        data = self._make_request(endpoint, api_key)
        
        # Save failures to knowledge database and enhance with historical data
        if data.get("isSuccess") and data.get("extraInfo"):
            enhanced_failures = []
            
            for failure in data["extraInfo"]:
                # Save failure to knowledge DB
                failure_id = self.knowledge_db.save_failure(failure)
                
                # Get failure history
                failure_history = self.knowledge_db.get_failure_history(failure_id)
                
                # Find similar failures
                similar_failures = self.knowledge_db.find_similar_failures(
                    failure.get("testCase", ""), 
                    failure.get("error", "")
                )
                
                # Enhance failure data with knowledge DB info
                enhanced_failure = failure.copy()
                enhanced_failure["knowledgeDB"] = {
                    "failure_id": failure_id,
                    "occurrence_count": failure_history.get("occurrence_count", 1) if failure_history else 1,
                    "first_seen": failure_history.get("timestamp") if failure_history else None,
                    "last_seen": failure_history.get("last_seen") if failure_history else None,
                    "similar_failures_count": len(similar_failures),
                    "is_recurring": failure_history.get("occurrence_count", 1) > 1 if failure_history else False
                }
                
                enhanced_failures.append(enhanced_failure)
            
            # Update data with enhanced failures
            data["extraInfo"] = enhanced_failures
            
            # Add knowledge DB statistics
            data["knowledgeDBStats"] = self.knowledge_db.get_failure_stats()
        
        return json.dumps(data, indent=2)
    
    def process_and_save_all_failures(self, project_name: str = None) -> Dict[Any, Any]:
        """
        Get test failures and save them to the knowledge database.
        
        This function:
        - If project_name provided: Fetches failures from specific project using partial name matching
        - If no project_name: Fetches failures from all available projects
        - Processes each failure and saves it to the knowledge database
        - Returns success message with processed project names and case counts
        
        Args:
            project_name: Optional partial project name to filter specific project
            
        Returns:
            Dictionary with success message, project names, and case counts
        """
        # Get all projects for reference
        all_projects = self.get_projects()
        all_project_names = [p.get("name", "Unknown") for p in all_projects]
        
        total_cases = 0
        processed_projects = []
        failed_projects = []
        
        # Determine which projects to process
        if project_name:
            # Find specific project by partial name
            project_info = self.find_project_by_name(project_name)
            if not project_info["found"]:
                return {
                    "success": False,
                    "error": project_info["error"],
                    "projects_processed": [],
                    "total_cases_saved": 0,
                    "available_projects": all_project_names
                }
            
            # Process only the found project
            projects_to_process = [{
                "id": project_info["project_id"],
                "name": project_info["project_name"]
            }]
        else:
            # Process all projects
            projects_to_process = all_projects
        
        # Process failures from selected projects
        for project in projects_to_process:
            result = self._process_single_project(project, processed_projects, failed_projects)
            if result:
                total_cases += result
        
        # Return results
        if processed_projects or total_cases > 0:
            return {
                "success": True,
                "projects_processed": processed_projects,
                "total_cases_saved": total_cases,
                "available_projects": all_project_names
            }
        else:
            return {
                "success": False,
                "projects_processed": failed_projects,
                "total_cases_saved": 0,
                "available_projects": all_project_names
            }
    
    def _process_single_project(self, project: Dict[str, Any], processed_projects: List[str], failed_projects: List[str]) -> int:
        """Process failures for a single project. Returns number of cases processed."""
        project_id = project.get("id")
        project_name = project.get("name", "Unknown")
        
        if not project_id:
            return 0
            
        try:
            failures_json = self.get_test_failures(project_id)
            failures_data = json.loads(failures_json)
            
            if failures_data.get("isSuccess") and failures_data.get("extraInfo"):
                cases_saved = self._save_project_failures(failures_data["extraInfo"], project_name, project_id)
                if cases_saved > 0:
                    processed_projects.append(project_name)
                return cases_saved
            elif failures_data.get("isSuccess"):
                # Project has no failures (success case)
                processed_projects.append(project_name)
                return 0
                
        except Exception:
            failed_projects.append(project_name)
            
        return 0
    
    def _save_project_failures(self, failures: List[Dict], project_name: str, project_id: str) -> int:
        """Save failures for a project to knowledge database. Returns count of saved failures."""
        saved_count = 0
        
        for failure in failures:
            failure_data = {
                "testCase": failure.get("testCase", "Unknown Test"),
                "status": failure.get("status", "failed"),
                "error": failure.get("error", "Unknown Error"),
                "stackTrace": failure.get("stackTrace", ""),
                "filePath": failure.get("filePath", ""),
                "failedStep": failure.get("failedStep", ""),
                "project_name": project_name,
                "project_id": project_id
            }
            
            self.knowledge_db.save_failure(failure_data)
            saved_count += 1
            
        return saved_count
    
    def get_latest_result_analysis(self, project_id: str) -> Dict[str, Any]:
        """Get latest test result analysis from test report endpoint using project ID."""
        api_key = os.getenv("ORDINO_SYSTEM_API_KEY")
        if not api_key:
            raise ValueError("ORDINO_SYSTEM_API_KEY environment variable is required")
        endpoint = f"/public/test-report/test-setup/{project_id}"
        
        try:
            data = self._make_request(endpoint, api_key)
            return data
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "project_id": project_id
            }
    
    def get_latest_result_summary(self, project_id: str) -> Dict[str, Any]:
        """Get summarized latest test result analysis optimized for LLM consumption."""
        raw_data = self.get_latest_result_analysis(project_id)
        
        if not raw_data.get("success", True):
            return raw_data
        
        # Extract key metrics for summary - optimized for low LLM consumption
        summary = {
            "setup_id": project_id,
            "total": 0,
            "passed": 0,
            "failed": 0,
            "pass_rate": 0.0,
            "failures": []  # Top 3 failures only for minimal token usage
        }
        
        # Simplified flat processing approach
        def process_test_node(node, summary, failures_list):
            """Process a single test node and update summary."""
            if "testDetails" not in node or not isinstance(node["testDetails"], list):
                return
                
            for test in node["testDetails"]:
                summary["total"] += 1
                state = test.get("state")
                
                if state == "passed":
                    summary["passed"] += 1
                elif state == "failed":
                    summary["failed"] += 1
                    # Add failure if under limit
                    if len(failures_list) < 3:
                        error_msg = test.get("errorMessage", "No error message")
                        if error_msg and len(error_msg) > 100:
                            error_msg = error_msg.split('\n')[0][:100] + "..."
                        
                        failures_list.append({
                            "name": test.get("testTitle", "Unknown")[:50],
                            "error": error_msg,
                            "duration": test.get("duration")
                        })
        
        def traverse_tree(node, summary, failures_list):
            """Traverse the test tree and collect results."""
            process_test_node(node, summary, failures_list)
            
            # Process children
            for child in node.get("children", []):
                traverse_tree(child, summary, failures_list)
        
        # Process tests from the root level
        if "label" in raw_data:  # This is the hierarchical test structure
            failures_list = []
            traverse_tree(raw_data, summary, failures_list)
            summary["failures"] = failures_list
            
            # Calculate pass rate
            if summary["total"] > 0:
                summary["pass_rate"] = round((summary["passed"] / summary["total"]) * 100, 1)  # 1 decimal for brevity
        
        return summary
    
    def get_latest_result_full(self, project_id: str) -> Dict[str, Any]:
        """Get complete latest test result analysis with full details."""
        return self.get_latest_result_analysis(project_id)
    
    def get_latest_summary(self, project_name: str) -> Dict[str, Any]:
        """Get summarized latest test result analysis for a project."""
        # Find project
        project_info = self.find_project_by_name(project_name)
        if not project_info["found"]:
            return {
                "error": project_info["error"],
                "message": "Available projects:",
                "available_projects": project_info["available_projects"],
                "suggestion": "Use exact or partial project names from the list above"
            }
        
        # Use project ID for test setup
        project_id = project_info["project_id"]
        summary_data = self.get_latest_result_summary(project_id)
        
        # Add project context
        summary_data["matched_project"] = project_info["project_name"]
        summary_data["search_term"] = project_name
        
        return summary_data
    
    def get_latest_full(self, project_name: str) -> Dict[str, Any]:
        """Get complete latest test result analysis for a project."""
        # Find project
        project_info = self.find_project_by_name(project_name)
        if not project_info["found"]:
            return {
                "error": project_info["error"],
                "message": "Available projects:",
                "available_projects": project_info["available_projects"],
                "suggestion": "Use exact or partial project names from the list above"
            }
        
        # Use project ID for test setup
        project_id = project_info["project_id"]
        full_data = self.get_latest_result_full(project_id)
        
        # Add project context
        full_data["matched_project"] = project_info["project_name"]
        full_data["search_term"] = project_name
        
        return full_data
    
    def save_analysis_to_knowledge_db(self, project_name: str, analysis_data: Dict[str, Any]) -> str:
        """Save analysis results to knowledge database under analysis/{project_name}/ directory."""
        knowledge_db = LightweightKnowledgeDB()
        return knowledge_db.save_project_analysis(project_name, analysis_data)

    def find_project_by_name(self, project_name: str) -> Dict[str, Any]:
        """Find project by name with partial matching support."""
        projects = self.get_projects()
        
        # Find project by partial name match (case-insensitive)
        for project in projects:
            project_full_name = project.get("name", "")
            # Check for exact match first, then partial match
            if project_full_name.lower() == project_name.lower():
                return {
                    "found": True,
                    "project_id": project.get("id"),
                    "project_name": project_full_name
                }
            elif project_name.lower() in project_full_name.lower():
                return {
                    "found": True,
                    "project_id": project.get("id"),
                    "project_name": project_full_name
                }
        
        # Project not found
        project_list = [p.get("name") for p in projects]
        return {
            "found": False,
            "error": f"Project '{project_name}' not found",
            "available_projects": project_list
        }
    
    def get_failures_summary(self, project_name: str) -> Dict[str, Any]:
        """Get summarized failure information for a project."""
        # Find project
        project_info = self.find_project_by_name(project_name)
        if not project_info["found"]:
            return {
                "error": project_info["error"],
                "message": "Available projects:",
                "available_projects": project_info["available_projects"],
                "suggestion": "Use exact or partial project names from the list above"
            }
        
        # Get failures
        result = self.get_test_failures(project_info["project_id"])
        result_data = json.loads(result)
        
        # Create summary
        summary_data = {
            "matched_project": project_info["project_name"],
            "total_failures": len(result_data.get("extraInfo", [])),
            "success": result_data.get("isSuccess", False),
            "failures": []
        }
        
        # Extract essential failure info
        for failure in result_data.get("extraInfo", []):
            summary_failure = {
                "test_case": failure.get("testCase", "Unknown"),
                "status": failure.get("status", "failed"),
                "error": failure.get("error", "").split('\n')[0] if failure.get("error") else "No error message",
                "file_path": failure.get("filePath", "Unknown"),
                "failed_step": failure.get("failedStep", "Unknown")
            }
            
            # Add knowledge DB info if available
            if "knowledgeDB" in failure:
                kb_info = failure["knowledgeDB"]
                summary_failure["occurrence_count"] = kb_info.get("occurrence_count", 1)
                summary_failure["is_recurring"] = kb_info.get("is_recurring", False)
            
            summary_data["failures"].append(summary_failure)
        
        return summary_data
    
    def get_failures_full(self, project_name: str) -> Dict[str, Any]:
        """Get complete failure information for a project."""
        # Find project
        project_info = self.find_project_by_name(project_name)
        if not project_info["found"]:
            return {
                "error": project_info["error"],
                "message": "Available projects:",
                "available_projects": project_info["available_projects"],
                "suggestion": "Use exact or partial project names from the list above"
            }
        
        # Get failures
        result = self.get_test_failures(project_info["project_id"])
        result_data = json.loads(result)
        result_data["matched_project"] = project_info["project_name"]
        
        return result_data
