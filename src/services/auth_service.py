from typing import Dict, Any, Optional
from services.api_client import APIClient
from models.customer import Customer, CustomerLoginRequest, LoginResponse
from config.settings import settings

class AuthService:
    def __init__(self):
        self.api_client = APIClient()
    
    def register_customer(self, customer_data: Customer) -> Dict[str, Any]:
        """Register a new customer"""
        try:
            endpoint = settings.ENDPOINTS['INSERT_CUSTOMER']
            data = customer_data.model_dump()
            
            response = self.api_client.post(endpoint, data)
            
            if response.get('error'):
                return {
                    'success': False,
                    'message': response.get('message', 'Registration failed'),
                    'error': response.get('message', 'Unknown error')
                }
            
            return {
                'success': True,
                'message': 'Customer registered successfully',
                'data': response
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': 'Registration failed',
                'error': str(e)
            }
    
    def login_customer(self, login_data: CustomerLoginRequest) -> Dict[str, Any]:
        """Login customer and get token"""
        try:
            endpoint = settings.ENDPOINTS['LOGIN']
            data = login_data.model_dump()
            
            response = self.api_client.post(endpoint, data)
            
            if response.get('error'):
                return {
                    'success': False,
                    'message': response.get('message', 'Login failed'),
                    'error': response.get('message', 'Unknown error')
                }
            
            # Parse the response
            if response.get('isSuccess') and response.get('statusCode') == 1:
                login_response = LoginResponse(**response)
                return {
                    'success': True,
                    'message': 'Login successful',
                    'token': login_response.data1,
                    'customer_data': login_response.data2,
                    'customer_id': login_response.data2.id
                }
            else:
                return {
                    'success': False,
                    'message': response.get('message', 'Login failed'),
                    'error': 'Invalid credentials'
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': 'Login failed',
                'error': str(e)
            }
    
    def auto_login(self, customer_data: Customer) -> Dict[str, Any]:
        """Auto login after registration"""
        login_request = CustomerLoginRequest(
            username=customer_data.loginDetails.username,
            password=customer_data.loginDetails.password
        )
        return self.login_customer(login_request)