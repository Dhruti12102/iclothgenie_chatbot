import requests
import json
from typing import Dict, Any, Optional
from config.settings import settings

class APIClient:
    def __init__(self):
        self.base_url = settings.API_BASE_URL
        self.timeout = settings.API_TIMEOUT
        self.session = requests.Session()
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, 
                     params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        default_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if headers:
            default_headers.update(headers)
            
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=default_headers,
                timeout=self.timeout
            )
            
            
            try:
                response.raise_for_status()
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {
                        'error': True,
                        'message': response.text or 'Invalid response format',
                        'status_code': response.status_code
                    }
            except requests.exceptions.RequestException as e:
                return {
                    'error': True,
                    'message': f'API request failed: {str(e)}',
                    'status_code': getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
                }

            
            # response.raise_for_status()
            # return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                'error': True,
                'message': f'API request failed: {str(e)}',
                'status_code': getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
            }
        except json.JSONDecodeError:
            return {
                'error': True,
                'message': 'Invalid JSON response',
                'status_code': 500
            }
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make GET request"""
        return self._make_request('GET', endpoint, params=params, headers=headers)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, 
             headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make POST request"""
        return self._make_request('POST', endpoint, data=data, headers=headers)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make PUT request"""
        return self._make_request('PUT', endpoint, data=data, headers=headers)
    
    def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None, 
              headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make PATCH request"""
        return self._make_request('PATCH', endpoint, data=data, headers=headers)
    
    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make DELETE request"""
        return self._make_request('DELETE', endpoint, headers=headers)
    
    def close(self):
        """Close the session"""
        self.session.close()