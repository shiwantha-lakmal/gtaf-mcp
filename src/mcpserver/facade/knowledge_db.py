import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class LightweightKnowledgeDB:
    """Lightweight file-based knowledge database for storing failure stack traces and analysis."""
    
    def __init__(self, db_path: str = "knowledge_db"):
        self.db_path = Path(db_path)
        self.testcases_path = self.db_path / "testcases"
        self.analysis_path = self.db_path / "analysis"
        
        # Create directories if they don't exist
        self.testcases_path.mkdir(parents=True, exist_ok=True)
        self.analysis_path.mkdir(parents=True, exist_ok=True)
    
    def _generate_testcase_filename(self, test_case: str) -> str:
        """Generate a safe filename for a test case."""
        # Remove special characters and limit length
        safe_name = "".join(c for c in test_case if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')[:200]  # Increased limit to 200 chars
        return f"{safe_name}.json"
    
    def _generate_failure_id(self, test_case: str, error: str) -> str:
        """Generate a unique ID for a failure based on test case and error."""
        content = f"{test_case}:{error}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def save_failure(self, failure_data: Dict[str, Any]) -> str:
        """Save a failure to the knowledge database organized by test case."""
        test_case = failure_data.get("testCase", "unknown")
        error = failure_data.get("error", "unknown")
        
        # Ensure directories exist
        self.testcases_path.mkdir(parents=True, exist_ok=True)
        self.analysis_path.mkdir(parents=True, exist_ok=True)
        
        failure_id = self._generate_failure_id(test_case, error)
        testcase_filename = self._generate_testcase_filename(test_case)
        testcase_file = self.testcases_path / testcase_filename
        
        # Prepare new failure entry
        new_failure_entry = {
            "failure_id": failure_id,
            "timestamp": datetime.now().isoformat(),
            "status": failure_data.get("status", "failed"),
            "filePath": failure_data.get("filePath", ""),
            "failedStep": failure_data.get("failedStep", "")
        }
        
        # Load existing testcase data or create new
        try:
            if testcase_file.exists():
                with open(testcase_file, 'r', encoding='utf-8') as f:
                    testcase_data = json.load(f)
            else:
                testcase_data = {
                    "testCase": test_case,
                    "created": datetime.now().isoformat(),
                    "total_failures": 0,
                    "unique_errors": 0,
                    "failure_history": []
                }
        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            # If file is corrupted or can't be read, create new data
            testcase_data = {
                "testCase": test_case,
                "created": datetime.now().isoformat(),
                "total_failures": 0,
                "unique_errors": 0,
                "failure_history": []
            }
        
        # Check if this exact failure already exists in history
        existing_failure = None
        for i, failure in enumerate(testcase_data["failure_history"]):
            if failure["failure_id"] == failure_id:
                existing_failure = failure
                current_time = datetime.now()
                
                # Check if this is truly a new occurrence (not seen in the last 5 minutes)
                recent_occurrences = existing_failure.get("recent_occurrences", [])
                is_new_occurrence = True
                
                if recent_occurrences:
                    # Get the most recent occurrence timestamp
                    latest_occurrence = max(recent_occurrences, key=lambda x: x.get("timestamp", ""))
                    latest_timestamp_str = latest_occurrence.get("timestamp", "")
                    
                    try:
                        latest_timestamp = datetime.fromisoformat(latest_timestamp_str.replace("Z", "+00:00"))
                        time_diff = (current_time - latest_timestamp.replace(tzinfo=None)).total_seconds()
                        
                        # Only add as new occurrence if more than 5 minutes have passed
                        # or if the error/stackTrace is different
                        if (time_diff < 300 and  # 5 minutes = 300 seconds
                            latest_occurrence.get("error", "") == error and
                            latest_occurrence.get("stackTrace", "") == failure_data.get("stackTrace", "")):
                            is_new_occurrence = False
                    except (ValueError, AttributeError):
                        # If timestamp parsing fails, treat as new occurrence
                        is_new_occurrence = True
                
                if is_new_occurrence:
                    existing_failure["occurrence_count"] = existing_failure.get("occurrence_count", 1) + 1
                    existing_failure["last_seen"] = current_time.isoformat()
                    existing_failure["recent_occurrences"].append({
                        "timestamp": current_time.isoformat(),
                        "error": error,
                        "stackTrace": failure_data.get("stackTrace", ""),
                        "isBug": None,
                        "tester_notes": []
                    })
                    # Keep only last 10 occurrences
                    existing_failure["recent_occurrences"] = existing_failure["recent_occurrences"][-10:]
                else:
                    # Just update the last_seen timestamp without adding new occurrence
                    existing_failure["last_seen"] = current_time.isoformat()
                
                break
        
        # If not found, add as new failure
        if not existing_failure:
            new_failure_entry.update({
                "first_seen": datetime.now().isoformat(),
                "occurrence_count": 1,
                "recent_occurrences": [{
                    "timestamp": datetime.now().isoformat(),
                    "error": error,
                    "stackTrace": failure_data.get("stackTrace", ""),
                    "isBug": None,
                    "tester_notes": []
                }]
            })
            testcase_data["failure_history"].append(new_failure_entry)
            testcase_data["unique_errors"] += 1
        
        # Update summary statistics
        testcase_data["total_failures"] += 1
        testcase_data["last_updated"] = datetime.now().isoformat()
        
        # Sort failure history by most recent first
        testcase_data["failure_history"].sort(key=lambda x: x.get("last_seen", x.get("first_seen", "")), reverse=True)
        
        # Save updated testcase data
        try:
            with open(testcase_file, 'w', encoding='utf-8') as f:
                json.dump(testcase_data, f, indent=2, ensure_ascii=False)
        except (OSError, IOError) as e:
            # If we can't write the file, at least return the failure_id
            print(f"Warning: Could not save testcase data to {testcase_file}: {e}")
        
        return failure_id
    
    def get_failure_history(self, failure_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve failure history by ID from testcase files."""
        # Ensure testcases directory exists
        if not self.testcases_path.exists():
            return None
            
        # Search through all testcase files to find the failure
        for testcase_file in self.testcases_path.glob("*.json"):
            try:
                with open(testcase_file, 'r', encoding='utf-8') as f:
                    testcase_data = json.load(f)
                
                for failure in testcase_data.get("failure_history", []):
                    if failure.get("failure_id") == failure_id:
                        return failure
            except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
                # Skip corrupted or inaccessible files
                continue
        return None
    
    def get_testcase_history(self, test_case: str) -> Optional[Dict[str, Any]]:
        """Retrieve complete history for a specific test case."""
        testcase_filename = self._generate_testcase_filename(test_case)
        testcase_file = self.testcases_path / testcase_filename
        
        try:
            if testcase_file.exists():
                with open(testcase_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            # Return None if file is corrupted or inaccessible
            pass
        return None
    
    def find_similar_failures(self, test_case: str, error: str) -> List[Dict[str, Any]]:
        """Find similar failures based on test case or error patterns."""
        similar_failures = []
        
        for testcase_file in self.testcases_path.glob("*.json"):
            with open(testcase_file, 'r') as f:
                testcase_data = json.load(f)
            
            # Check for similarity in test case name or errors in failure history
            for failure in testcase_data.get("failure_history", []):
                if (test_case.lower() in testcase_data.get("testCase", "").lower() or 
                    any(keyword in failure.get("error", "").lower() 
                        for keyword in error.lower().split()[:3])):  # Use first 3 words for matching
                    similar_failures.append({
                        "testCase": testcase_data.get("testCase"),
                        "failure": failure
                    })
        
        # Sort by occurrence count (most frequent first)
        similar_failures.sort(key=lambda x: x["failure"].get("occurrence_count", 0), reverse=True)
        return similar_failures
    
    def save_analysis(self, failure_id: str, analysis: Dict[str, Any]) -> None:
        """Save analysis for a specific failure."""
        analysis_record = {
            "failure_id": failure_id,
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis
        }
        
        analysis_file = self.analysis_path / f"{failure_id}_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis_record, f, indent=2)
    
    def save_project_analysis(self, project_name: str, analysis_data: Dict[str, Any]) -> str:
        """Save project-level analysis results to knowledge database."""
        try:
            # Create project-specific analysis directory
            project_analysis_path = self.analysis_path / project_name.replace(" ", "_").replace("-", "_")
            project_analysis_path.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_analysis_{timestamp}.json"
            file_path = project_analysis_path / filename
            
            # Prepare analysis record
            analysis_record = {
                "project_name": project_name,
                "timestamp": datetime.now().isoformat(),
                "analysis_type": "latest_result_analysis",
                "data": analysis_data
            }
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_record, f, indent=2, ensure_ascii=False)
            
            return str(file_path)
            
        except Exception as e:
            return f"Error saving project analysis: {str(e)}"
    
    def get_failure_stats(self) -> Dict[str, Any]:
        """Get statistics about failures in the database."""
        total_testcases = len(list(self.testcases_path.glob("*.json")))
        total_failures = 0
        total_unique_errors = 0
        
        failure_types = {}
        most_common_errors = {}
        testcase_stats = {}
        
        for testcase_file in self.testcases_path.glob("*.json"):
            with open(testcase_file, 'r') as f:
                testcase_data = json.load(f)
            
            testcase_name = testcase_data.get("testCase", "unknown")
            testcase_total_failures = testcase_data.get("total_failures", 0)
            testcase_unique_errors = testcase_data.get("unique_errors", 0)
            
            total_failures += testcase_total_failures
            total_unique_errors += testcase_unique_errors
            
            # Store testcase stats
            testcase_stats[testcase_name] = {
                "total_failures": testcase_total_failures,
                "unique_errors": testcase_unique_errors
            }
            
            # Count by file path (test suite) from failure history
            for failure in testcase_data.get("failure_history", []):
                file_path = failure.get("filePath", "unknown")
                failure_types[file_path] = failure_types.get(file_path, 0) + failure.get("occurrence_count", 1)
                
                # Count common error patterns
                error = failure.get("error", "")
                error_key = error.split('\n')[0][:100]  # First line, max 100 chars
                most_common_errors[error_key] = most_common_errors.get(error_key, 0) + failure.get("occurrence_count", 1)
        
        return {
            "total_testcases": total_testcases,
            "total_failures": total_failures,
            "total_unique_errors": total_unique_errors,
            "failure_types": dict(sorted(failure_types.items(), key=lambda x: x[1], reverse=True)[:10]),
            "most_common_errors": dict(sorted(most_common_errors.items(), key=lambda x: x[1], reverse=True)[:5]),
            "top_failing_testcases": dict(sorted(testcase_stats.items(), key=lambda x: x[1]["total_failures"], reverse=True)[:10])
        }
    
    def cleanup_old_failures(self, days_old: int = 30) -> int:
        """Clean up testcase files older than specified days."""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        cleaned_count = 0
        
        for testcase_file in self.testcases_path.glob("*.json"):
            if testcase_file.stat().st_mtime < cutoff_date:
                testcase_file.unlink()
                cleaned_count += 1
        
        # Also clean up old analysis files
        for analysis_file in self.analysis_path.glob("*.json"):
            if analysis_file.stat().st_mtime < cutoff_date:
                analysis_file.unlink()
        
        return cleaned_count
    
    def update_failure_bug_status(self, test_case_name: str, is_bug: bool, tester_notes: str = "", failure_index: int = 0) -> bool:
        """Update the isBug status for a specific test case's failure after manual tester sign-off.
        
        Args:
            test_case_name: Name of the test case to update
            is_bug: True if this is a confirmed bug, False if not a bug
            tester_notes: Optional notes from the tester explaining the classification
            failure_index: Index of the failure to update (0 = most recent, default)
            
        Returns:
            bool: True if update was successful, False if test case not found
        """
        # First try: Use generated filename
        testcase_filename = self._generate_testcase_filename(test_case_name)
        testcase_file = self.testcases_path / testcase_filename
        
        # Second try: If file doesn't exist, search through all files to find matching test case
        if not testcase_file.exists():
            testcase_file = None
            for file_path in self.testcases_path.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if data.get("testCase") == test_case_name:
                            testcase_file = file_path
                            break
                except (json.JSONDecodeError, OSError):
                    continue
            
            if not testcase_file:
                return False
        
        try:
            with open(testcase_file, 'r', encoding='utf-8') as f:
                testcase_data = json.load(f)
            
            failure_history = testcase_data.get("failure_history", [])
            if not failure_history or failure_index >= len(failure_history):
                return False
            
            # Get the failure to update (default to most recent)
            failure = failure_history[failure_index]
            
            # Update the most recent occurrence's bug status
            recent_occurrences = failure.get("recent_occurrences", [])
            if recent_occurrences:
                # Update the most recent occurrence
                recent_occurrences[-1]["isBug"] = is_bug
                recent_occurrences[-1]["bug_status_updated"] = datetime.now().isoformat()
            
            # Add new tester note to the most recent occurrence if provided
            if tester_notes and recent_occurrences:
                latest_occurrence = recent_occurrences[-1]
                
                # Initialize tester_notes as array if it doesn't exist in the occurrence
                if "tester_notes" not in latest_occurrence:
                    latest_occurrence["tester_notes"] = []
                
                note_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "note": tester_notes,
                    "classification": "bug" if is_bug else "not_bug"
                }
                latest_occurrence["tester_notes"].append(note_entry)
            
            # Save the updated testcase data
            with open(testcase_file, 'w', encoding='utf-8') as f:
                json.dump(testcase_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            return False
    
    def get_bug_statistics(self) -> Dict[str, Any]:
        """Get statistics about bug classifications."""
        stats = {
            "total_failures": 0,
            "classified_as_bugs": 0,
            "classified_as_not_bugs": 0,
            "pending_classification": 0,
            "bug_classification_rate": 0.0,
            "testcases_with_bugs": [],
            "testcases_without_bugs": []
        }
        
        for testcase_file in self.testcases_path.glob("*.json"):
            with open(testcase_file, 'r') as f:
                testcase_data = json.load(f)
            
            testcase_name = testcase_data.get("testCase", "unknown")
            testcase_bugs = 0
            testcase_non_bugs = 0
            testcase_pending = 0
            
            for failure in testcase_data.get("failure_history", []):
                stats["total_failures"] += 1
                
                # Check isBug status in recent occurrences
                recent_occurrences = failure.get("recent_occurrences", [])
                is_bug = None
                if recent_occurrences:
                    # Get the most recent occurrence's bug status
                    is_bug = recent_occurrences[-1].get("isBug")
                
                if is_bug is True:
                    stats["classified_as_bugs"] += 1
                    testcase_bugs += 1
                elif is_bug is False:
                    stats["classified_as_not_bugs"] += 1
                    testcase_non_bugs += 1
                else:
                    stats["pending_classification"] += 1
                    testcase_pending += 1
            
            # Categorize testcases
            if testcase_bugs > 0:
                stats["testcases_with_bugs"].append({
                    "testCase": testcase_name,
                    "bugs": testcase_bugs,
                    "non_bugs": testcase_non_bugs,
                    "pending": testcase_pending
                })
            elif testcase_non_bugs > 0:
                stats["testcases_without_bugs"].append({
                    "testCase": testcase_name,
                    "non_bugs": testcase_non_bugs,
                    "pending": testcase_pending
                })
        
        # Calculate classification rate
        classified_total = stats["classified_as_bugs"] + stats["classified_as_not_bugs"]
        if stats["total_failures"] > 0:
            stats["bug_classification_rate"] = (classified_total / stats["total_failures"]) * 100
        
        return stats
    
    def cleanup_knowledge_db_fully(self) -> Dict[str, Any]:
        """Completely clean up the knowledge database by removing all files and directories.
        
        Returns:
            Dict with cleanup statistics and results
        """
        cleanup_stats = {
            "testcases_removed": 0,
            "analysis_files_removed": 0,
            "analysis_directories_removed": 0,
            "errors": [],
            "success": True
        }
        
        try:
            # Clean up testcases directory
            if self.testcases_path.exists():
                testcase_files = list(self.testcases_path.glob("*.json"))
                cleanup_stats["testcases_removed"] = len(testcase_files)
                
                for testcase_file in testcase_files:
                    try:
                        testcase_file.unlink()
                    except Exception as e:
                        cleanup_stats["errors"].append(f"Failed to remove testcase file {testcase_file}: {str(e)}")
                        cleanup_stats["success"] = False
            
            # Clean up analysis directory (including subdirectories)
            if self.analysis_path.exists():
                # Count analysis files first
                analysis_files = list(self.analysis_path.rglob("*.json"))
                cleanup_stats["analysis_files_removed"] = len(analysis_files)
                
                # Count subdirectories (project directories)
                analysis_dirs = [d for d in self.analysis_path.iterdir() if d.is_dir()]
                cleanup_stats["analysis_directories_removed"] = len(analysis_dirs)
                
                # Remove all files first
                for item in self.analysis_path.rglob("*"):
                    try:
                        if item.is_file():
                            item.unlink()
                    except Exception as e:
                        cleanup_stats["errors"].append(f"Failed to remove file {item}: {str(e)}")
                        cleanup_stats["success"] = False
                
                # Then remove directories (deepest first)
                for item in sorted(self.analysis_path.rglob("*"), key=lambda p: len(p.parts), reverse=True):
                    try:
                        if item.is_dir() and item != self.analysis_path:
                            item.rmdir()
                    except Exception as e:
                        cleanup_stats["errors"].append(f"Failed to remove directory {item}: {str(e)}")
                        cleanup_stats["success"] = False
            
            # Recreate empty directories to maintain structure
            try:
                self.testcases_path.mkdir(parents=True, exist_ok=True)
                self.analysis_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                cleanup_stats["errors"].append(f"Failed to recreate directories: {str(e)}")
                cleanup_stats["success"] = False
            
            cleanup_stats["message"] = "Knowledge database cleanup completed successfully" if cleanup_stats["success"] else "Knowledge database cleanup completed with errors"
            
        except Exception as e:
            cleanup_stats["success"] = False
            cleanup_stats["errors"].append(f"General cleanup error: {str(e)}")
            cleanup_stats["message"] = f"Knowledge database cleanup failed: {str(e)}"
        
        return cleanup_stats
