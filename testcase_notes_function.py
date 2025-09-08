@mcp.tool()
def get_testcase_tester_notes(test_case_name: str) -> str:
    """
    Get all tester notes and classification history for a specific test case.
    
    This function retrieves the complete tester note history for all failures in a test case:
    - All tester notes with timestamps for each failure type
    - Classification changes over time per failure
    - Complete audit trail of tester decisions for the test case
    - Summary of bug classifications across all failure types
    
    Args:
        test_case_name: Name of the test case to get notes for
    
    Returns:
        JSON string with complete tester note history for the test case
        
    Example Usage:
        get_testcase_tester_notes("Grubtech Menu Item Report - Verify Menu Items Report Table")
    """
    import json
    
    knowledge_db = result_client.knowledge_db
    testcase_data = knowledge_db.get_testcase_history(test_case_name)
    
    if testcase_data:
        # Process all failures and their tester notes
        failures_with_notes = []
        total_notes = 0
        bug_classifications = {"bugs": 0, "not_bugs": 0, "pending": 0}
        
        for failure in testcase_data.get("failure_history", []):
            failure_notes = failure.get("tester_notes", [])
            total_notes += len(failure_notes)
            
            # Count classifications
            is_bug = failure.get("isBug")
            if is_bug is True:
                bug_classifications["bugs"] += 1
            elif is_bug is False:
                bug_classifications["not_bugs"] += 1
            else:
                bug_classifications["pending"] += 1
            
            # Add failure info if it has notes or classification
            if failure_notes or is_bug is not None:
                failures_with_notes.append({
                    "failure_id": failure.get("failure_id"),
                    "first_seen": failure.get("first_seen"),
                    "last_seen": failure.get("last_seen"),
                    "occurrence_count": failure.get("occurrence_count", 0),
                    "current_classification": {
                        "is_bug": is_bug,
                        "last_updated": failure.get("bug_status_updated")
                    },
                    "tester_notes": failure_notes,
                    "notes_count": len(failure_notes),
                    "latest_error": failure.get("recent_occurrences", [{}])[-1].get("error", "")[:100] + "..." if failure.get("recent_occurrences") and len(failure.get("recent_occurrences", [{}])[-1].get("error", "")) > 100 else failure.get("recent_occurrences", [{}])[-1].get("error", "") if failure.get("recent_occurrences") else "No recent error"
                })
        
        response = {
            "success": True,
            "test_case": test_case_name,
            "testcase_summary": {
                "created": testcase_data.get("created"),
                "last_updated": testcase_data.get("last_updated"),
                "total_failures": testcase_data.get("total_failures", 0),
                "unique_errors": testcase_data.get("unique_errors", 0)
            },
            "tester_activity": {
                "total_notes": total_notes,
                "failures_with_activity": len(failures_with_notes),
                "bug_classifications": bug_classifications
            },
            "failures_with_notes": failures_with_notes
        }
    else:
        response = {
            "success": False,
            "message": f"Test case '{test_case_name}' not found in knowledge database",
            "test_case": test_case_name
        }
    
    return json.dumps(response, indent=2)
