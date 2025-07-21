from typing import Dict, Any
from services.api_client import APIClient
from config.settings import settings

class PostcodeService:
    def __init__(self):
        self.api_client = APIClient()
    
    def validate_postcode(self, postcode: str) -> Dict[str, Any]:
        """Validate if postcode is serviceable"""
        try:
            endpoint = settings.ENDPOINTS['VALIDATE_POSTCODE']
            params = {
                'isGetData': 'true',
                'code': postcode,
                'culture': 'en-IN'
            }
            
            response = self.api_client.get(endpoint, params=params)
            
            if response.get('error'):
                return {
                    'success': False,
                    'message': 'Unable to validate postcode',
                    'error': response.get('message', 'Unknown error')
                }
            
            # Check if postcode is valid based on API response
            if response.get('isSuccess') and response.get('statusCode') == 1:
                return {
                    'success': True,
                    'is_valid': True,
                    'message': 'We are serving in your area! 🎉',
                    'data': response.get('data')
                }
            else:
                return {
                    'success': True,
                    'is_valid': False,
                    'message': 'Sorry, we are not serving in your area yet. 😔',
                    'data': None
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': 'Postcode validation failed',
                'error': str(e)
            }