from typing import Dict, Any, List
from services.api_client import APIClient
from models.order import OrderRequest, OrderUpdateRequest
from models.service import Service, ServiceResponse
from config.settings import settings

class OrderService:
    def __init__(self):
        self.api_client = APIClient()
    
    def get_all_services(self) -> Dict[str, Any]:
        """Get all available services"""
        try:
            endpoint = settings.ENDPOINTS['GET_ALL_SERVICES']
            
            response = self.api_client.get(endpoint)
            
            # Debug: Print the raw response
            print(f"DEBUG: Raw API response: {response}")
            
            if response.get('error'):
                return {
                    'success': False,
                    'message': 'Unable to fetch services',
                    'error': response.get('message', 'Unknown error')
                }
            
            # Check if the response is successful
            if response.get('isSuccess') and response.get('statusCode') == 1:
                # Extract services data - try different possible field names
                services_data = response.get('data', [])
                
                # Debug: Print services data
                print(f"DEBUG: Services data from API: {services_data}")
                print(f"DEBUG: Type of services data: {type(services_data)}")
                
                # If services_data is None or empty, try other possible field names
                if not services_data:
                    # Try alternative field names that might contain services
                    # Based on your debug output, the API uses 'data1' for services
                    alternative_fields = ['data1', 'services', 'result', 'items', 'list', 'data2', 'data3', 'data4']
                    for field in alternative_fields:
                        if field in response and response[field]:
                            services_data = response[field]
                            print(f"DEBUG: Found services in field '{field}': {services_data}")
                            break
                
                # If still no data, check if the response structure is different
                if not services_data:
                    print(f"DEBUG: No services data found. Full response keys: {list(response.keys())}")
                    return {
                        'success': False,
                        'message': 'No services data found in API response',
                        'error': f'Response structure: {list(response.keys())}'
                    }
                
                return {
                    'success': True,
                    'message': 'Services retrieved successfully',
                    'services': services_data
                }
            else:
                error_message = response.get('message', 'API returned unsuccessful response')
                return {
                    'success': False,
                    'message': 'Unable to fetch services',
                    'error': error_message
                }
        
        except Exception as e:
            print(f"DEBUG: Exception in get_all_services: {str(e)}")
            return {
                'success': False,
                'message': 'Failed to fetch services',
                'error': str(e)
            }
    
    def create_order(self, order_data: OrderRequest, token: str) -> Dict[str, Any]:
        """Create a new order"""
        try:
            endpoint = settings.ENDPOINTS['INSERT_ORDER']
            data = order_data.model_dump()
            
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            response = self.api_client.post(endpoint, data, headers=headers)
            
            if response.get('error'):
                return {
                    'success': False,
                    'message': 'Unable to create order',
                    'error': response.get('message', 'Unknown error')
                }
            
            if response.get('isSuccess') and response.get('statusCode') == 1:
                return {
                    'success': True,
                    'message': 'Order placed successfully! 🎉',
                    'order_id': response.get('data', {}).get('id'),
                    'data': response.get('data')
                }
            else:
                return {
                    'success': False,
                    'message': 'Unable to create order',
                    'error': response.get('message', 'Order creation failed')
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': 'Order creation failed',
                'error': str(e)
            }
    
    def update_order(self, order_data: OrderUpdateRequest, token: str) -> Dict[str, Any]:
        """Update an existing order with multiple endpoint attempts"""
        try:
            # Try different possible endpoints for order update
            possible_endpoints = [
                '/Order/UpdateOrder'
            ]
            
            data = order_data.model_dump()
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Debug: Print request details
            print(f"DEBUG: Update order data: {data}")
            print(f"DEBUG: Update order headers: {headers}")
            
            # Try each endpoint with different HTTP methods
            for endpoint in possible_endpoints:
                print(f"DEBUG: Trying endpoint: {endpoint}")
                
                # Try PUT method first (RESTful standard for updates)
                try:
                    response = self.api_client.put(endpoint, data, headers=headers)
                    print(f"DEBUG: PUT response for {endpoint}: {response}")
                    
                    # Check if we got a successful response (not 404)
                    if not response.get('error') or response.get('status_code') != 404:
                        result = self._process_update_response(response, endpoint, 'PUT')
                        if result['success'] or 'not found' not in result.get('error', '').lower():
                            return result
                except Exception as e:
                    print(f"DEBUG: PUT failed for {endpoint}: {str(e)}")
                
                # Try POST method (some APIs use POST for updates)
                try:
                    response = self.api_client.post(endpoint, data, headers=headers)
                    print(f"DEBUG: POST response for {endpoint}: {response}")
                    
                    # Check if we got a successful response (not 404)
                    if not response.get('error') or response.get('status_code') != 404:
                        result = self._process_update_response(response, endpoint, 'POST')
                        if result['success'] or 'not found' not in result.get('error', '').lower():
                            return result
                except Exception as e:
                    print(f"DEBUG: POST failed for {endpoint}: {str(e)}")
                
                # Try PATCH method (partial updates)
                try:
                    response = self.api_client.patch(endpoint, data, headers=headers)
                    print(f"DEBUG: PATCH response for {endpoint}: {response}")
                    
                    # Check if we got a successful response (not 404)
                    if not response.get('error') or response.get('status_code') != 404:
                        result = self._process_update_response(response, endpoint, 'PATCH')
                        if result['success'] or 'not found' not in result.get('error', '').lower():
                            return result
                except Exception as e:
                    print(f"DEBUG: PATCH failed for {endpoint}: {str(e)}")
            
            # If all endpoints failed
            return {
                'success': False,
                'message': 'Unable to update order - no valid endpoint found',
                'error': f'All attempted endpoints failed. Tried: {", ".join(possible_endpoints)}'
            }
        
        except Exception as e:
            print(f"DEBUG: Exception in update_order: {str(e)}")
            return {
                'success': False,
                'message': 'Order update failed',
                'error': f"Exception: {str(e)}"
            }
    
    def _process_update_response(self, response: Dict[str, Any], endpoint: str, method: str) -> Dict[str, Any]:
        """Process the update response from API"""
        if response.get('error'):
            error_message = response.get('message', 'Unknown API error')
            print(f"DEBUG: {method} {endpoint} returned error: {error_message}")
            return {
                'success': False,
                'message': 'Unable to update order',
                'error': error_message
            }
        
        # Check for different success indicators
        is_success = (
            response.get('isSuccess') == True or 
            response.get('success') == True or
            response.get('statusCode') == 1 or
            response.get('status') == 'success' or
            response.get('code') == 200
        )
        
        if is_success:
            print(f"DEBUG: {method} {endpoint} succeeded!")
            return {
                'success': True,
                'message': 'Order updated successfully! ✅',
                'data': response.get('data', {}),
                'endpoint_used': f"{method} {endpoint}"
            }
        else:
            # Get detailed error information
            error_message = (
                response.get('message') or 
                response.get('error') or 
                response.get('errorMessage') or
                'Order update failed - no specific error message'
            )
            
            status_code = response.get('statusCode', response.get('status_code', 'unknown'))
            
            print(f"DEBUG: {method} {endpoint} failed - Status: {status_code}, Message: {error_message}")
            
            return {
                'success': False,
                'message': 'Unable to update order',
                'error': f"Status: {status_code}, Error: {error_message}"
            }
    
    def validate_order_for_update(self, order_id: int, customer_id: int, token: str) -> Dict[str, Any]:
        """Validate if an order exists and can be updated"""
        try:
            # Get customer orders first
            orders_result = self.get_order_detail(customer_id, token)
            
            if not orders_result['success']:
                return {
                    'success': False,
                    'message': 'Unable to fetch orders for validation',
                    'error': orders_result['error']
                }
            
            # Find the order
            target_order = None
            for order in orders_result['orders']:
                order_id_field = order.get('id') or order.get('ID') or order.get('orderId')
                if order_id_field == order_id:
                    target_order = order
                    break
            
            if not target_order:
                return {
                    'success': False,
                    'message': f'Order with ID {order_id} not found',
                    'error': 'Order not found'
                }
            
            # Check if order can be updated (add your business logic here)
            order_status = target_order.get('orderStatus', target_order.get('status', '')).lower()
            if order_status in ['completed', 'cancelled', 'delivered']:
                return {
                    'success': False,
                    'message': f'Cannot update order with status: {order_status}',
                    'error': f'Order status is {order_status}'
                }
            
            return {
                'success': True,
                'message': 'Order can be updated',
                'order': target_order
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': 'Error validating order',
                'error': str(e)
            }
        
    def get_order_detail(self, customer_id: int, token: str) -> Dict[str, Any]:
        """Get order details for a customer"""
        try:
            endpoint = settings.ENDPOINTS['GET_ORDER_DETAIL']
            params = {'customerId': customer_id}
            
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            print(f"DEBUG: Fetching orders with params: {params}")
            
            response = self.api_client.get(endpoint, params=params, headers=headers)
            
            print(f"DEBUG: Get orders response: {response}")
            
            if response.get('error'):
                return {
                    'success': False,
                    'message': 'Unable to fetch order details',
                    'error': response.get('message', 'Unknown error')
                }
            
            if response.get('isSuccess') and response.get('statusCode') == 1:
                orders_data = response.get('data', [])
                
                # Try alternative field names if 'data' is empty
                if not orders_data:
                    alternative_fields = ['data1', 'orders', 'result', 'items', 'list']
                    for field in alternative_fields:
                        if field in response and response[field]:
                            orders_data = response[field]
                            break
                
                return {
                    'success': True,
                    'message': 'Order details retrieved successfully',
                    'orders': orders_data
                }
            else:
                return {
                    'success': False,
                    'message': 'Unable to fetch order details',
                    'error': response.get('message', 'No orders found')
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': 'Failed to fetch order details',
                'error': str(e)
            }