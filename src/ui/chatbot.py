import gradio as gr
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from services.auth_service import AuthService
from services.order_service import OrderService
from services.postcode_service import PostcodeService
from models.customer import Customer, LoginDetails
from models.order import OrderRequest, OrderUpdateRequest, OrderAddress
from utils.validators import (
    validate_email, validate_mobile, validate_postcode, 
    validate_date, validate_future_date, validate_name
)
from utils.formatters import (
    format_services_list, format_order_summary, format_order_list,
    format_customer_info, format_error_message, format_success_message,format_selected_services
)
from config.settings import settings

class ChatbotSession:
    def __init__(self):
        self.reset_session()
    
    def reset_session(self):
        self.state = "start"
        self.customer_data = {}
        self.order_data = {}
        self.token = None
        self.customer_id = None
        self.services = []
        self.pending_update = {}
        self.current_orders = []

class LaundryServiceChatbot:
    def __init__(self):
        self.auth_service = AuthService()
        self.order_service = OrderService()
        self.postcode_service = PostcodeService()
        self.session = ChatbotSession()
        
        # Also update the main process_message method to handle the new state
    def process_message(self, message: str, history: List[List[str]]) -> str:
        """Process user message and return response"""
        message_lower = message.strip().lower()
        
        # Handle different conversation states
        if self.session.state == "start":
            return self.handle_start_state(message_lower)
        elif self.session.state == "awaiting_postcode":
            return self.handle_postcode_validation(message)
        elif self.session.state == "awaiting_customer_details":
            return self.handle_customer_registration(message)
        elif self.session.state == "authenticated":
            return self.handle_authenticated_menu(message_lower)
        elif self.session.state == "placing_order":
            return self.handle_order_placement(message)
        elif self.session.state == "updating_order":
            return self.handle_order_update(message)
        elif self.session.state == "awaiting_service_selection":
            return self.handle_service_selection(message)
        elif self.session.state == "awaiting_order_details":
            return self.handle_order_details(message)
        elif self.session.state == "awaiting_address_details":
            return self.handle_address_details(message)
        elif self.session.state == "awaiting_update_selection":
            return self.handle_update_selection(message)
        elif self.session.state == "awaiting_update_value":
            return self.handle_update_value(message_lower)
        elif self.session.state == "awaiting_update_input":  # Add this new state
            return self.handle_update_input(message)
        else:
            return "I'm sorry, something went wrong. Let's start over. Please type 'start' to begin."
    
    def handle_start_state(self, message: str) -> str:
        """Handle initial conversation state"""
        self.session.reset_session()
        
        response = """🧺 Welcome to our Laundry Service Chatbot! 

I can help you with:
• Register as a new customer
• Place laundry orders
• Update existing orders
• View order summaries

To get started, I'll need to check if we serve your area. Please provide your postcode:"""
        
        self.session.state = "awaiting_postcode"
        return response
    
    def handle_postcode_validation(self, message: str) -> str:
        """Handle postcode validation"""
        postcode = message.strip().upper()
        
        if not validate_postcode(postcode):
            return "❌ Please enter a valid postcode."
        
        # Validate postcode with API
        result = self.postcode_service.validate_postcode(postcode)
        
        if not result['success']:
            return f"❌ {result['message']}"
        
        if result['is_valid']:
            self.session.customer_data['postcode'] = postcode
            self.session.state = "awaiting_customer_details"
            return f"""✅ {result['message']}

Now, let's register you as a customer. Please provide your details in the following format:

**First Name:** Your first name
**Last Name:** Your last name  
**Mobile:** Your 10-digit mobile number
**Email:** Your email address
**Password:** A strong password

Example:
First Name: John
Last Name: Doe
Mobile: 1234567890
Email: john@example.com
Password: MySecure123!"""
        else:
            return f"❌ {result['message']}\n\nPlease try with a different postcode or contact us for more information."
    
    def handle_customer_registration(self, message: str) -> str:
        """Handle customer registration"""
        lines = message.strip().split('\n')
        
        try:
            # Parse customer details
            details = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    details[key] = value
            
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'mobile', 'email', 'password']
            missing_fields = [field for field in required_fields if field not in details]
            
            if missing_fields:
                return f"❌ Missing required fields: {', '.join(missing_fields)}\n\nPlease provide all required information."
            
            # Validate each field
            if not validate_name(details['first_name']):
                return "❌ Please enter a valid first name."
            
            if not validate_name(details['last_name']):
                return "❌ Please enter a valid last name."
            
            if not validate_mobile(details['mobile']):
                return "❌ Please enter a valid 10-digit mobile number."
            
            if not validate_email(details['email']):
                return "❌ Please enter a valid email address."
            
            # password_validation = validate_password(details['password'])
            # if not password_validation['is_valid']:
            #     return f"❌ Password validation failed:\n" + '\n'.join(password_validation['errors'])
            
            # Create customer object
            customer = Customer(
                firstname=details['first_name'],
                lastname=details['last_name'],
                mobileNo=details['mobile'],
                email=details['email'],
                loginDetails=LoginDetails(
                    username=details['email'],
                    password=details['password']
                )
            )
            
            # Register customer
            registration_result = self.auth_service.register_customer(customer)
            
            if not registration_result['success']:
                return f"❌ Registration failed: {registration_result['message']}"
            
            # Auto-login after registration
            login_result = self.auth_service.auto_login(customer)
            
            if not login_result['success']:
                return f"❌ Auto-login failed: {login_result['message']}"
            
            # Store session data
            self.session.token = login_result['token']
            self.session.customer_id = login_result['customer_id']
            self.session.customer_data = login_result['customer_data']
            self.session.state = "authenticated"
            
            return f"""✅ Registration successful! Welcome {details['first_name']}!

You are now logged in. Here's what you can do:

1️⃣ **Place Order** - Create a new laundry order
2️⃣ **Update Order** - Modify an existing order
3️⃣ **View Orders** - See your order history
4️⃣ **Profile** - View your profile information

Please type the number or name of the option you'd like to choose."""
        
        except Exception as e:
            return f"❌ Error processing your details: {str(e)}\n\nPlease try again with the correct format."
    
    def handle_authenticated_menu(self, message: str) -> str:
        """Handle authenticated user menu"""
        if message in ['1', 'place order', 'place', 'order']:
            return self.start_order_placement()
        elif message in ['2', 'update order', 'update']:
            return self.start_order_update()
        elif message in ['3', 'view orders', 'view', 'orders']:
            return self.show_orders()
        elif message in ['4', 'profile', 'info']:
            return self.show_profile()
        else:
            return """Please choose one of the following options:

1️⃣ **Place Order** - Create a new laundry order
2️⃣ **Update Order** - Modify an existing order  
3️⃣ **View Orders** - See your order history
4️⃣ **Profile** - View your profile information

Type the number or name of the option."""
    
    def start_order_placement(self) -> str:
        """Start order placement process"""
        try:
            # Get available services
            services_result = self.order_service.get_all_services()
            
            if not services_result['success']:
                return f"❌ Unable to load services: {services_result['message']}"
            
            # Debug: Check the full API response structure
            print(f"DEBUG: Full services API response: {services_result}")
            
            # Extract services data
            services_data = services_result.get('services', [])
            
            if not services_data:
                return "❌ No services available at the moment. Please try again later."
            
            # Debug: Print services data structure
            print(f"DEBUG: Services data: {services_data}")
            print(f"DEBUG: First service structure: {services_data[0] if services_data else 'No services'}")
            
            # Store services
            self.session.services = services_data
            self.session.state = "awaiting_service_selection"
            
            # Format services for display
            services_text = format_services_list(self.session.services)
            
            # Create service selection instructions
            service_ids = []
            for service in self.session.services:
                if isinstance(service, dict):
                    service_id = service.get('id') or service.get('ID') or service.get('serviceId')
                    if service_id is not None:
                        service_ids.append(str(service_id))
            
            if not service_ids:
                return "❌ Unable to extract service IDs from the API response. Please contact support."
            
            return f"""🧺 Let's place your order!

    {services_text}

    Please select the services you want by typing the service IDs (comma-separated).

    Available service IDs: {', '.join(service_ids)}

    For example: {','.join(service_ids[:2]) if len(service_ids) >= 2 else service_ids[0]}"""
            
        except Exception as e:
            return f"❌ Error starting order placement: {str(e)}\n\nPlease try again later."

    
    # In handle_service_selection method, replace the service ID validation section:
    def handle_service_selection(self, message: str) -> str:
        try:
            # Parse selected service IDs
            service_ids = [id.strip() for id in message.split(',') if id.strip()]
            
            if not service_ids:
                return "❌ Please provide valid service IDs separated by commas."
            
            # Get available service IDs - handle different possible data structures
            available_services = {}  # Map of ID to service object
            for service in self.session.services:
                if isinstance(service, dict):
                    # Try different field names for service ID
                    service_id = service.get('serviceId') or service.get('id') or service.get('ID')
                    if service_id is not None:
                        available_services[str(service_id)] = service
            
            # Validate service IDs
            invalid_ids = [id for id in service_ids if id not in available_services]
            
            if invalid_ids:
                return f"""❌ Invalid service IDs: {', '.join(invalid_ids)}

    Available service IDs: {', '.join(available_services.keys())}

    Please select from the available services."""
            
            # Get selected services details
            selected_services = [available_services[id] for id in service_ids]
            
            # Store order data
            self.session.order_data['services'] = ','.join(service_ids)
            self.session.order_data['sub_services'] = "3"  # Default sub-service
            self.session.state = "awaiting_order_details"
            
            # Format selected services for display
            selected_services_text = format_selected_services(selected_services)
            
            return f"""✅ Services selected successfully!

    {selected_services_text}

    Now, please provide your order details:

    **Pickup Date:** YYYY-MM-DD
    **Pickup Time:** (choose from available slots)
    **Drop-off Date:** YYYY-MM-DD  
    **Drop-off Time:** (choose from available slots)
    **Collection Option:** Driver collects from you / Drop off at store
    **Delivery Option:** Driver delivers to you / Collect from store

    Available time slots:
    """ + '\n'.join([f"• {slot}" for slot in settings.TIME_SLOTS]) + """

    Example:
    Pickup Date: 2025-07-19
    Pickup Time: 09:00 AM - 11:00 AM
    Drop-off Date: 2025-07-21
    Drop-off Time: 03:00 PM - 05:00 PM
    Collection Option: Driver collects from you
    Delivery Option: Driver delivers to you"""
            
        except Exception as e:
            return f"❌ Error processing service selection: {str(e)}\n\nPlease try again or type 'Place Order' to restart."
        
    def handle_order_details(self, message: str) -> str:
        """Handle order details input"""
        try:
            lines = message.strip().split('\n')
            details = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    details[key] = value
            
            # Validate required fields
            required_fields = ['pickup_date', 'pickup_time', 'drop-off_date', 'drop-off_time', 'collection_option', 'delivery_option']
            missing_fields = [field for field in required_fields if field not in details]
            
            if missing_fields:
                return f"❌ Missing required fields: {', '.join(missing_fields)}"
            
            # Validate dates
            if not validate_date(details['pickup_date']):
                return "❌ Invalid pickup date format. Please use YYYY-MM-DD."
            
            if not validate_date(details['drop-off_date']):
                return "❌ Invalid drop-off date format. Please use YYYY-MM-DD."
            
            if not validate_future_date(details['pickup_date']):
                return "❌ Pickup date must be in the future."
            
            if not validate_future_date(details['drop-off_date']):
                return "❌ Drop-off date must be in the future."
            
           
            self.session.order_data.update(details)
            self.session.state = "awaiting_address_details"
            
            return """✅ Order details saved!

Now, please provide the delivery address details:

**First Name:** Recipient's first name
**Last Name:** Recipient's last name
**Email:** Recipient's email
**Contact Number:** 10-digit contact number
**Address Line 1:** Street address
**Address Line 2:** Apartment, suite, etc. (optional)
**Postcode:** Delivery postcode

Example:
First Name: Jane
Last Name: Smith
Email: jane@example.com
Contact Number: 9876543210
Address Line 1: 123 Main Street
Address Line 2: Apt 4B
Postcode: BR20XZ"""
        
        except Exception as e:
            return f"❌ Error processing order details: {str(e)}"
    
    def handle_address_details(self, message: str) -> str:
        """Handle address details and place order"""
        try:
            lines = message.strip().split('\n')
            details = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    details[key] = value
            
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'email', 'contact_number', 'address_line_1', 'postcode']
            missing_fields = [field for field in required_fields if field not in details]
            
            if missing_fields:
                return f"❌ Missing required fields: {', '.join(missing_fields)}"
            
            # Validate fields
            if not validate_name(details['first_name']):
                return "❌ Please enter a valid first name."
            
            if not validate_name(details['last_name']):
                return "❌ Please enter a valid last name."
            
            if not validate_email(details['email']):
                return "❌ Please enter a valid email address."
            
            if not validate_mobile(details['contact_number']):
                return "❌ Please enter a valid 10-digit contact number."
            
            if not validate_postcode(details['postcode']):
                return "❌ Please enter a valid postcode."
            
            # Create order request
            order_address = OrderAddress(
                firstname=details['first_name'],
                lastname=details['last_name'],
                email=details['email'],
                contactNo=details['contact_number'],
                postCode=details['postcode'],
                addressLine1=details['address_line_1'],
                addressLine2=details.get('address_line_2', '')
            )
            
            order_request = OrderRequest(
                customerId=self.session.customer_id,
                pickupDate=self.session.order_data['pickup_date'],
                pickupTime=self.session.order_data['pickup_time'],
                dropOffDate=self.session.order_data['drop-off_date'],
                dropOffTime=self.session.order_data['drop-off_time'],
                Services=self.session.order_data['services'],
                SubServices=self.session.order_data['sub_services'],
                collectionOption=self.session.order_data['collection_option'],
                deliveryOption=self.session.order_data['delivery_option'],
                orderAddress=order_address,
                offerCode=""
            )
            
            # Place order
            order_result = self.order_service.create_order(order_request, self.session.token)
            
            if not order_result['success']:
                return f"❌ Order placement failed: {order_result['message']}"
            
            # Get order summary
            summary = format_order_summary(order_request.model_dump(), self.session.customer_data.model_dump())
            
            self.session.state = "authenticated"
            
            return f"""✅ {order_result['message']}

{summary}

What would you like to do next?

1️⃣ **Place Order** - Create another order
2️⃣ **Update Order** - Modify an existing order
3️⃣ **View Orders** - See your order history
4️⃣ **Profile** - View your profile information"""
        
        except Exception as e:
            return f"❌ Error processing address details: {str(e)}"
    
    def start_order_update(self) -> str:
        """Start order update process"""
        # Get customer orders
        orders_result = self.order_service.get_order_detail(self.session.customer_id, self.session.token)
        
        if not orders_result['success']:
            return f"❌ Unable to load orders: {orders_result['message']}"
        
        if not orders_result['orders']:
            return "❌ No orders found. Please place an order first."
        
        self.session.current_orders = orders_result['orders']
        self.session.state = "awaiting_update_selection"
        
        orders_text = format_order_list(self.session.current_orders)
        
        return f"""{orders_text}

Please select which order you want to update (enter the order number):"""
    
    def handle_update_selection(self, message: str) -> str:
        """Handle order selection for update"""
        try:
            order_number = int(message.strip())
            
            if order_number < 1 or order_number > len(self.session.current_orders):
                return f"❌ Invalid order number. Please select between 1 and {len(self.session.current_orders)}."
            
            selected_order = self.session.current_orders[order_number - 1]
            self.session.pending_update = selected_order
            self.session.state = "awaiting_update_value"
            
            return """✅ Order selected for update!

What would you like to update?

1️⃣ **Pickup Date**
2️⃣ **Pickup Time**
3️⃣ **Drop-off Date**
4️⃣ **Drop-off Time**
5️⃣ **Collection Option**
6️⃣ **Delivery Option**

Please type the number or name of what you want to update:"""
        
        except ValueError:
            return "❌ Please enter a valid order number."
        except Exception as e:
            return f"❌ Error selecting order: {str(e)}"
        

# Fixed chatbot.py - Order Update Section

    def handle_update_value(self, message: str) -> str:
        """Handle update value input"""
        message = message.strip().lower()
        
        if message in ['1', 'pickup date']:
            return self.handle_date_update('pickup_date', 'pickup date')
        elif message in ['2', 'pickup time']:
            return self.handle_time_update('pickup_time', 'pickup time')
        elif message in ['3', 'drop-off date', 'dropoff date']:
            return self.handle_date_update('dropoff_date', 'drop-off date')
        elif message in ['4', 'drop-off time', 'dropoff time']:
            return self.handle_time_update('dropoff_time', 'drop-off time')
        elif message in ['5', 'collection option', 'collection']:
            return self.handle_option_update('collection_option', 'collection option', settings.COLLECTION_OPTIONS)
        elif message in ['6', 'delivery option', 'delivery']:
            return self.handle_option_update('delivery_option', 'delivery option', settings.DELIVERY_OPTIONS)
        else:
            # Check if this is an actual update value (when update_field is already set)
            if hasattr(self.session, 'update_field') and self.session.update_field:
                return self.handle_update_input(message.strip())
            
            return """Please select what you want to update:

    1️⃣ **Pickup Date**
    2️⃣ **Pickup Time**
    3️⃣ **Drop-off Date**
    4️⃣ **Drop-off Time**
    5️⃣ **Collection Option**
    6️⃣ **Delivery Option**

    Type the number or name of what you want to update:"""

    def handle_date_update(self, field: str, field_name: str) -> str:
        """Handle date update"""
        self.session.update_field = field
        self.session.state = "awaiting_update_input"  # Add this state
        return f"""Please enter the new {field_name} in YYYY-MM-DD format:
        
    Example: 2025-07-22

    Note: The date must be in the future."""

    def handle_time_update(self, field: str, field_name: str) -> str:
        """Handle time update"""
        self.session.update_field = field
        self.session.state = "awaiting_update_input"  # Add this state
        
        time_slots = '\n'.join([f"• {slot}" for slot in settings.TIME_SLOTS])
        
        return f"""Please select the new {field_name} from the available slots:

    {time_slots}

    Type the exact time slot you want:"""

    def handle_option_update(self, field: str, field_name: str, options: List[str]) -> str:
        """Handle option update"""
        self.session.update_field = field
        self.session.state = "awaiting_update_input"  # Add this state
        
        options_text = '\n'.join([f"• {option}" for option in options])
        
        return f"""Please select the new {field_name}:

    {options_text}

    Type the exact option you want:"""

    def handle_update_input(self, message: str) -> str:
        """Handle the actual update input"""
        try:
            field = self.session.update_field
            value = message.strip()
            
            print(f"DEBUG: Updating field '{field}' with value '{value}'")
            print(f"DEBUG: Current order to update: {self.session.pending_update}")
            
            # Validate input based on field type
            if field in ['pickup_date', 'dropoff_date']:
                if not validate_date(value):
                    return "❌ Invalid date format. Please use YYYY-MM-DD."
                
                if not validate_future_date(value):
                    return "❌ Date must be in the future."
            
            elif field in ['pickup_time', 'dropoff_time']:
                if value not in settings.TIME_SLOTS:
                    return f"❌ Invalid time slot. Please choose from: {', '.join(settings.TIME_SLOTS)}"
            
            elif field == 'collection_option':
                if value not in [opt.lower() for opt in settings.COLLECTION_OPTIONS]:
                    return f"❌ Invalid collection option. Please choose from: {', '.join(settings.COLLECTION_OPTIONS)}"
            
            elif field == 'delivery_option':
                if value not in [opt.lower() for opt in settings.DELIVERY_OPTIONS]:
                    return f"❌ Invalid delivery option. Please choose from: {', '.join(settings.DELIVERY_OPTIONS)}"
            
            # Get current order data with proper field mapping
            current_order = self.session.pending_update
            
            # Create update request with current values as defaults
            order_update_data = {
                'id': current_order.get('id') or current_order.get('ID') or current_order.get('orderId'),
                'customerId': self.session.customer_id,
                'pickupDate': current_order.get('pickupDate', ''),
                'pickupTime': current_order.get('pickupTime', ''),
                'collectionOption': current_order.get('collectionOption', ''),
                'dropOffDate': current_order.get('dropOffDate', ''),
                'dropOffTime': current_order.get('dropOffTime', ''),
                'deliveryOption': current_order.get('deliveryOption', '')
            }
            
            # Update the specific field
            if field == 'pickup_date':
                order_update_data['pickupDate'] = value
            elif field == 'pickup_time':
                order_update_data['pickupTime'] = value
            elif field == 'dropoff_date':
                order_update_data['dropOffDate'] = value
            elif field == 'dropoff_time':
                order_update_data['dropOffTime'] = value
            elif field == 'collection_option':
                # Find the exact match from settings (case-insensitive)
                for option in settings.COLLECTION_OPTIONS:
                    if option.lower() == value.lower():
                        order_update_data['collectionOption'] = option
                        break
            elif field == 'delivery_option':
                # Find the exact match from settings (case-insensitive)
                for option in settings.DELIVERY_OPTIONS:
                    if option.lower() == value.lower():
                        order_update_data['deliveryOption'] = option
                        break
            
            print(f"DEBUG: Order update data: {order_update_data}")
            
            # Ensure we have a valid order ID
            if not order_update_data['id']:
                return "❌ Unable to identify order ID. Please try selecting the order again."
            
            # Create update request
            order_update = OrderUpdateRequest(**order_update_data)
            
            print(f"DEBUG: OrderUpdateRequest object: {order_update.model_dump()}")
            
            # Update order
            update_result = self.order_service.update_order(order_update, self.session.token)
            
            print(f"DEBUG: Update result: {update_result}")
            
            if not update_result['success']:
                error_msg = update_result.get('error', 'Unknown error')
                return f"❌ Update failed: {error_msg}\n\nPlease try again or contact support if the issue persists."
            
            # Reset session state
            self.session.state = "authenticated"
            self.session.update_field = None
            
            return f"""✅ {update_result['message']}

    Your order has been updated successfully!

    What would you like to do next?

    1️⃣ **Place Order** - Create a new order
    2️⃣ **Update Order** - Modify another order
    3️⃣ **View Orders** - See your order history
    4️⃣ **Profile** - View your profile information"""
        
        except Exception as e:
            print(f"DEBUG: Exception in handle_update_input: {str(e)}")
            return f"❌ Error updating order: {str(e)}\n\nPlease try again or contact support."
    
    def show_orders(self) -> str:
        """Show customer orders"""
        print(f"DEBUG: Fetching orders for customer_id: {self.session.customer_id}")
        print(f"DEBUG: Using token: {self.session.token[:20]}..." if self.session.token else "No token")
    
        orders_result = self.order_service.get_order_detail(self.session.customer_id, self.session.token)
        print(f"DEBUG: Orders result: {orders_result}")
        if not orders_result['success']:
            return f"❌ Unable to load orders: {orders_result['message']}"
        
        if not orders_result['orders']:
            return """No orders found. 📭

Would you like to place your first order?

1️⃣ **Place Order** - Create a new laundry order
2️⃣ **Profile** - View your profile information

Type the number or name of the option."""
        
        orders_text = format_order_list(orders_result['orders'])
        
        return f"""{orders_text}

What would you like to do next?

1️⃣ **Place Order** - Create a new order
2️⃣ **Update Order** - Modify an existing order
3️⃣ **View Orders** - Refresh order list
4️⃣ **Profile** - View your profile information"""
    
    def show_profile(self) -> str:
        """Show customer profile"""
        profile_text = format_customer_info(self.session.customer_data)
        
        return f"""{profile_text}

What would you like to do next?

1️⃣ **Place Order** - Create a new laundry order
2️⃣ **Update Order** - Modify an existing order
3️⃣ **View Orders** - See your order history
4️⃣ **Profile** - View profile information

Type the number or name of the option."""
    
    def reset_conversation(self) -> str:
        """Reset the conversation"""
        self.session.reset_session()
        return self.handle_start_state("start")

import os
def create_chatbot_interface():
    """Create the Gradio chatbot interface"""
    chatbot = LaundryServiceChatbot()
    
    def chat_function(message, history):
       
        if message.lower().strip() in ['start', 'restart', 'reset']:
            return chatbot.reset_conversation()
        
        
        if chatbot.session.state == "awaiting_update_value" and hasattr(chatbot.session, 'update_field'):
            return chatbot.handle_update_input(message)
        
        return chatbot.process_message(message, history)
    
   
    css_file_path = "static/style.css"
    use_css_file = os.path.exists(css_file_path)
    
    
    interface_params = {
        "fn": chat_function,
        "title": "🧺 Laundry Service Chatbot",
        "description": "Welcome to our laundry service! I can help you register, place orders, and manage your laundry services. Type 'start' to begin!",
        "theme": gr.themes.Soft(),
      
        "examples": [
            "start",
            "Place Order",
            "View Orders", 
            "Update Order",
            "Profile"
        ]
    }
    
   
    if use_css_file:
        interface_params["css_paths"] = [css_file_path]
    else:
        
        interface_params["css"] = """
        .gradio-container {
            max-width: 800px !important;
            margin: 0 auto;
        }
        .message.user {
            background-color: #e3f2fd;
            border-radius: 15px;
            padding: 10px;
            margin: 5px 0;
        }
        .message.bot {
            background-color: #f5f5f5;
            border-radius: 15px;
            padding: 10px;
            margin: 5px 0;
        }
        """
    
  
    interface = gr.ChatInterface(**interface_params)
    
    return interface

def create_chatbot_interface_with_buttons():
    """Create the Gradio chatbot interface with button configuration"""
    chatbot = LaundryServiceChatbot()
    
    def chat_function(message, history):
      
        if message.lower().strip() in ['start', 'restart', 'reset']:
            return chatbot.reset_conversation()
        
    
        if chatbot.session.state == "awaiting_update_value" and hasattr(chatbot.session, 'update_field'):
            return chatbot.handle_update_input(message)
        
        return chatbot.process_message(message, history)
    
    
    
    interface = gr.ChatInterface(
        fn=chat_function,
        title="🧺 Laundry Service Chatbot",
        description="Welcome to our laundry service! I can help you register, place orders, and manage your laundry services. Type 'start' to begin!",
        theme=gr.themes.Soft(),
        retry_btn="🔄 Retry",
        undo_btn="↩️ Undo", 
        clear_btn="🗑️ Clear Chat",
        submit_btn="📤 Send",
        examples=[
            "start",
            "Place Order",
            "View Orders",
            "Update Order", 
            "Profile"
        ]
    )
    
    return interface
