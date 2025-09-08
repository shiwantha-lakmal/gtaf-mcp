import requests
import json
from typing import Dict, Any
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
    
    def get_projects(self) -> str:
        """Retrieve all active projects from the GrubTech testing platform."""
        api_key = "ztjEFessWESzKfkaMRZiJHcQ+UY19N6tHW5GKj7QfS4="
        endpoint = "/project-external"
        
        data = self._make_request(endpoint, api_key)
        return json.dumps(data, indent=2)
    
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
    
    def save_failure_to_db(self, test_case: str, error: str, stack_trace: str = "", file_path: str = "", failed_step: str = "") -> Dict[Any, Any]:
        """
        Save a test failure to the knowledge database for tracking and analysis.
        
        Args:
            test_case: Name/description of the failed test case
            error: Error message or exception details
            stack_trace: Full stack trace (optional)
            file_path: Path to the test file (optional)
            failed_step: Specific step that failed (optional)
        
        Returns:
            Dictionary with failure ID and database statistics
        """
        # Prepare failure data
        failure_data = {
            "testCase": test_case,
            "status": "failed",
            "error": error,
            "stackTrace": stack_trace,
            "filePath": file_path,
            "failedStep": failed_step
        }
        
        # Save to knowledge database
        failure_id = self.knowledge_db.save_failure(failure_data)
        
        # Get failure history and similar failures
        failure_history = self.knowledge_db.get_failure_history(failure_id)
        similar_failures = self.knowledge_db.find_similar_failures(test_case, error)
        db_stats = self.knowledge_db.get_failure_stats()
        
        # Prepare response
        response = {
            "success": True,
            "failure_id": failure_id,
            "message": f"Failure saved successfully with ID: {failure_id}",
            "failure_details": {
                "occurrence_count": failure_history.get("occurrence_count", 1) if failure_history else 1,
                "is_recurring": failure_history.get("occurrence_count", 1) > 1 if failure_history else False,
                "similar_failures_found": len(similar_failures),
                "first_seen": failure_history.get("timestamp") if failure_history else None,
                "last_seen": failure_history.get("last_seen") if failure_history else None
            },
            "knowledge_db_stats": db_stats
        }
        
        return response
    
    def process_and_save_all_failures(self) -> Dict[Any, Any]:
        """
        Get all current test failures from the main API and save them to the knowledge database.
        
        This function:
        - Fetches the latest test failures from the dataplatform-reporting project
        - Processes each failure and saves it to the knowledge database
        - Provides summary statistics and insights
        - Identifies recurring and similar failure patterns
        
        Returns:
            Dictionary with processing summary and database statistics
        """
        # Get current failures from API
        failures_json = self.get_test_failures()
        failures_data = json.loads(failures_json)
        
        processing_summary = {
            "success": True,
            "processed_failures": [],
            "statistics": {
                "total_failures_processed": 0,
                "new_failures": 0,
                "recurring_failures": 0,
                "similar_patterns_found": 0
            },
            "insights": []
        }
        
        if failures_data.get("isSuccess") and failures_data.get("extraInfo"):
            for failure in failures_data["extraInfo"]:
                # Extract failure details
                test_case = failure.get("testCase", "Unknown Test")
                error = failure.get("error", "Unknown Error")
                stack_trace = failure.get("stackTrace", "")
                file_path = failure.get("filePath", "")
                failed_step = failure.get("failedStep", "")
                
                # Save to knowledge database
                failure_id = self.knowledge_db.save_failure({
                    "testCase": test_case,
                    "status": failure.get("status", "failed"),
                    "error": error,
                    "stackTrace": stack_trace,
                    "filePath": file_path,
                    "failedStep": failed_step
                })
                
                # Get failure history
                failure_history = self.knowledge_db.get_failure_history(failure_id)
                similar_failures = self.knowledge_db.find_similar_failures(test_case, error)
                
                # Determine if this is new or recurring
                is_new = failure_history.get("occurrence_count", 1) == 1
                is_recurring = failure_history.get("occurrence_count", 1) > 1
                
                # Update statistics
                processing_summary["statistics"]["total_failures_processed"] += 1
                if is_new:
                    processing_summary["statistics"]["new_failures"] += 1
                if is_recurring:
                    processing_summary["statistics"]["recurring_failures"] += 1
                if len(similar_failures) > 1:
                    processing_summary["statistics"]["similar_patterns_found"] += 1
                
                # Add to processed failures
                processed_failure = {
                    "failure_id": failure_id,
                    "test_case": test_case[:100] + "..." if len(test_case) > 100 else test_case,
                    "file_path": file_path,
                    "occurrence_count": failure_history.get("occurrence_count", 1),
                    "is_new": is_new,
                    "is_recurring": is_recurring,
                    "similar_failures_count": len(similar_failures),
                    "error_type": error.split('\n')[0][:100] if error else "Unknown"
                }
                processing_summary["processed_failures"].append(processed_failure)
            
            # Generate insights
            total_processed = processing_summary["statistics"]["total_failures_processed"]
            recurring_count = processing_summary["statistics"]["recurring_failures"]
            similar_patterns = processing_summary["statistics"]["similar_patterns_found"]
            
            if recurring_count > 0:
                processing_summary["insights"].append(
                    f"Found {recurring_count} recurring failures that need immediate attention"
                )
            
            if similar_patterns > 0:
                processing_summary["insights"].append(
                    f"Identified {similar_patterns} failures with similar patterns - potential systemic issues"
                )
            
            if total_processed > 0:
                recurring_percentage = (recurring_count / total_processed) * 100
                processing_summary["insights"].append(
                    f"Recurring failure rate: {recurring_percentage:.1f}% ({recurring_count}/{total_processed})"
                )
            
            # Add overall database statistics
            processing_summary["knowledge_db_stats"] = self.knowledge_db.get_failure_stats()
            
        else:
            processing_summary["success"] = False
            processing_summary["message"] = "No failure data available or API call failed"
        
        return processing_summary
