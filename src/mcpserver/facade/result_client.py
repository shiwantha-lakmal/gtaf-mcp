import requests
import json
from typing import Dict, Any


class OrdinoResultClient:
    """Client for interacting with Ordino API endpoints."""
    
    BASE_URL = "https://dev-portal.ordino.ai/api/v1"
    
    def __init__(self):
        self.headers = {}
    
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
        return json.dumps(data, indent=2)
