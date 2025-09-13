import requests
import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from .knowledge_db import LightweightKnowledgeDB


class OrdinoResultClient:
    """Client for interacting with Ordino API endpoints."""
    
    BASE_URL = "https://dev-portal.ordino.ai/api/v1"
    
    def __init__(self):
        self.headers = {}
        self.knowledge_db = LightweightKnowledgeDB()
    
    def _make_request(self, endpoint: str, api_key: str) -> Dict[Any, Any]:
        """Make HTTP request to Ordino API endpoint."""
        headers = {"Ordino-Key": api_key}
        url = f"{self.BASE_URL}{endpoint}"
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Retrieve all active projects from the GrubTech testing platform."""
        api_key = "ztjEFessWESzKfkaMRZiJHcQ+UY19N6tHW5GKj7QfS4="
        endpoint = "/project-external"
        
        data = self._make_request(endpoint, api_key)
        return data
    
    def get_test_failures(self, project_id: str = "0a180944-8df0-4fc5-9f38-98a36bfda85c") -> str:
        """Retrieve comprehensive test failure analysis for a specific project."""
        api_key = "YoXGKROxf/p43uOoTMhUVWusceS1Y+5VoaQP54sJU+I="
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
    
    def process_and_save_all_failures(self) -> Dict[Any, Any]:
        """
        Get all current test failures from the main API and save them to the knowledge database.
        
        This function:
        - Fetches the latest test failures from the dataplatform-reporting project
        - Processes each failure and saves it to the knowledge database
        - Returns a simple success message with project names and case counts
        
        Returns:
            Dictionary with success message, project names, and case counts
        """
        # Get all projects to identify project names
        projects = self.get_projects()
        project_names = [p.get("name", "Unknown") for p in projects]
        
        # Get current failures from API (using default project)
        failures_json = self.get_test_failures()
        failures_data = json.loads(failures_json)
        
        if failures_data.get("isSuccess") and failures_data.get("extraInfo"):
            total_cases = 0
            
            for failure in failures_data["extraInfo"]:
                # Extract failure details
                test_case = failure.get("testCase", "Unknown Test")
                error = failure.get("error", "Unknown Error")
                stack_trace = failure.get("stackTrace", "")
                file_path = failure.get("filePath", "")
                failed_step = failure.get("failedStep", "")
                
                # Save to knowledge database
                self.knowledge_db.save_failure({
                    "testCase": test_case,
                    "status": failure.get("status", "failed"),
                    "error": error,
                    "stackTrace": stack_trace,
                    "filePath": file_path,
                    "failedStep": failed_step
                })
                
                total_cases += 1
            
            # Return simple success message
            return {
                "success": True,
                "message": f"Successfully processed and saved {total_cases} test failure cases to knowledge database",
                "projects_processed": ["dataplatform-reporting"],  # Default project
                "total_cases_saved": total_cases,
                "available_projects": project_names
            }
            
        else:
            return {
                "success": False,
                "message": "No failure data available or API call failed",
                "projects_processed": [],
                "total_cases_saved": 0,
                "available_projects": project_names
            }
    
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
