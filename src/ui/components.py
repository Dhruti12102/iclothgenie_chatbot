import gradio as gr
from typing import List, Dict, Any, Optional
from config.settings import settings

def create_time_dropdown() -> gr.Dropdown:
    """Create time slot dropdown"""
    return gr.Dropdown(
        choices=settings.TIME_SLOTS,
        label="Select Time Slot",
        value=settings.TIME_SLOTS[0]
    )

def create_collection_dropdown() -> gr.Dropdown:
    """Create collection option dropdown"""
    return gr.Dropdown(
        choices=settings.COLLECTION_OPTIONS,
        label="Collection Option",
        value=settings.COLLECTION_OPTIONS[0]
    )

def create_delivery_dropdown() -> gr.Dropdown:
    """Create delivery option dropdown"""
    return gr.Dropdown(
        choices=settings.DELIVERY_OPTIONS,
        label="Delivery Option",
        value=settings.DELIVERY_OPTIONS[0]
    )

def create_services_checkboxes(services: List[Dict[str, Any]]) -> gr.CheckboxGroup:
    """Create services checkbox group"""
    if not services:
        return gr.CheckboxGroup(choices=[], label="Services")
    
    choices = []
    for service in services:
        name = service.get('name', 'Unknown Service')
        service_id = service.get('id', 0)
        choices.append(f"{name} (ID: {service_id})")
    
    return gr.CheckboxGroup(
        choices=choices,
        label="Select Services",
        value=[]
    )

def create_date_picker(label: str, minimum_date: Optional[str] = None) -> gr.Textbox:
    """Create date picker input"""
    return gr.Textbox(
        label=label,
        placeholder="YYYY-MM-DD",
        info="Please enter date in YYYY-MM-DD format"
    )

def create_customer_form() -> List[gr.Component]:
    """Create customer registration form components"""
    return [
        gr.Textbox(label="First Name", placeholder="Enter your first name"),
        gr.Textbox(label="Last Name", placeholder="Enter your last name"),
        gr.Textbox(label="Mobile Number", placeholder="Enter 10-digit mobile number"),
        gr.Textbox(label="Email Address", placeholder="Enter your email address"),
        gr.Textbox(label="Password", type="password", placeholder="Create a strong password"),
        gr.Textbox(label="Postcode", placeholder="Enter your postcode")
    ]

def create_address_form() -> List[gr.Component]:
    """Create address form components"""
    return [
        gr.Textbox(label="First Name", placeholder="Recipient's first name"),
        gr.Textbox(label="Last Name", placeholder="Recipient's last name"),
        gr.Textbox(label="Email", placeholder="Recipient's email"),
        gr.Textbox(label="Contact Number", placeholder="10-digit contact number"),
        gr.Textbox(label="Address Line 1", placeholder="Street address"),
        gr.Textbox(label="Address Line 2", placeholder="Apartment, suite, etc. (optional)"),
        gr.Textbox(label="Postcode", placeholder="Postcode")
    ]

def create_order_form() -> List[gr.Component]:
    """Create order form components"""
    return [
        create_date_picker("Pickup Date"),
        create_time_dropdown(),
        create_date_picker("Drop-off Date"),
        create_time_dropdown(),
        create_collection_dropdown(),
        create_delivery_dropdown()
    ]

def create_chat_interface() -> gr.ChatInterface:
    """Create the main chat interface"""
    return gr.ChatInterface(
        title="🧺 Laundry Service Chatbot",
        description="Welcome to our laundry service! I can help you register, place orders, and manage your laundry services.",
        theme=gr.themes.Soft(),
        css="""
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .chat-message {
            padding: 10px;
            margin: 5px 0;
            border-radius: 10px;
        }
        .user-message {
            background-color: #e3f2fd;
            text-align: right;
        }
        .bot-message {
            background-color: #f5f5f5;
            text-align: left;
        }
        """
    )

def format_service_options(services: List[Dict[str, Any]]) -> str:
    """Format services for user selection"""
    if not services:
        return "No services available"
    
    formatted = "Please select from the following services:\n\n"
    for i, service in enumerate(services, 1):
        formatted += f"{i}. {service.get('name', 'Unknown Service')}"
        if service.get('description'):
            formatted += f" - {service.get('description')}"
        formatted += f" (ID: {service.get('id', 0)})\n"
    
    return formatted

def create_update_options() -> List[str]:
    """Create options for order updates"""
    return [
        "Pickup Date",
        "Pickup Time",
        "Drop-off Date",
        "Drop-off Time",
        "Collection Option",
        "Delivery Option"
    ]