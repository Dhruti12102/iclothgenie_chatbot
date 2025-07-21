from typing import List, Dict, Any, Union
from datetime import datetime

def format_services_list(services: List[Dict[str, Any]]) -> str:
    """Format services list for display"""
    if not services:
        return "No services available"
    
    formatted = "📋 **Available Services:**\n\n"
    
    for i, service in enumerate(services, 1):
        if isinstance(service, dict):
            # Handle different possible field names
            service_id = service.get('id') or service.get('ID') or service.get('serviceId')
            service_name = service.get('name') or service.get('serviceName') or service.get('title')
            service_desc = service.get('description') or service.get('desc') or service.get('details')
            service_price = service.get('price') or service.get('cost') or service.get('amount')
            
            formatted += f"**ID: {service_id}** - {service_name or 'Unknown Service'}\n"
            
            if service_desc:
                formatted += f"   📝 {service_desc}\n"
            if service_price:
                formatted += f"   💰 Price: ${service_price}\n"
            formatted += "\n"
        else:
            formatted += f"{i}. **Unknown Service Format**\n\n"
    
    return formatted

def format_order_summary(order_data: Dict[str, Any], customer_data: Dict[str, Any]) -> str:
    """Format order summary for display"""
    summary = "📋 **Order Summary**\n\n"
    
    # Customer Information
    summary += f"👤 **Customer:** {customer_data.get('firstname', '')} {customer_data.get('lastname', '')}\n"
    summary += f"📧 **Email:** {customer_data.get('email', '')}\n"
    summary += f"📱 **Mobile:** {customer_data.get('mobileNo', '')}\n\n"
    
    # Order Details
    summary += f"📅 **Pickup Date:** {order_data.get('pickupDate', '')}\n"
    summary += f"🕒 **Pickup Time:** {order_data.get('pickupTime', '')}\n"
    summary += f"📅 **Drop-off Date:** {order_data.get('dropOffDate', '')}\n"
    summary += f"🕒 **Drop-off Time:** {order_data.get('dropOffTime', '')}\n\n"
    
    # Collection & Delivery
    summary += f"🚚 **Collection:** {order_data.get('collectionOption', '')}\n"
    summary += f"🏠 **Delivery:** {order_data.get('deliveryOption', '')}\n\n"
    
    # Address
    if order_data.get('orderAddress'):
        addr = order_data['orderAddress']
        summary += f"📍 **Address:**\n"
        summary += f"   {addr.get('firstname', '')} {addr.get('lastname', '')}\n"
        summary += f"   {addr.get('addressLine1', '')}\n"
        if addr.get('addressLine2'):
            summary += f"   {addr.get('addressLine2')}\n"
        summary += f"   {addr.get('postCode', '')}\n"
        summary += f"   📞 {addr.get('contactNo', '')}\n\n"
    
    # Services
    if order_data.get('Services'):
        summary += f"🧺 **Services:** {order_data.get('Services', '')}\n"
    if order_data.get('SubServices'):
        summary += f"🔧 **Sub-services:** {order_data.get('SubServices', '')}\n"
    
    return summary

def format_order_list(orders: List[Dict[str, Any]]) -> str:
    """Format order list for display"""
    if not orders:
        return "No orders found"
    
    formatted = "📋 **Your Orders:**\n\n"
    
    for i, order in enumerate(orders, 1):
        formatted += f"**Order #{i}**\n"
        formatted += f"📅 Pickup: {order.get('pickupDate', '')} at {order.get('pickupTime', '')}\n"
        formatted += f"📅 Drop-off: {order.get('dropOffDate', '')} at {order.get('dropOffTime', '')}\n"
        formatted += f"📊 Status: {order.get('status', 'Pending')}\n"
        if order.get('totalAmount'):
            formatted += f"💰 Amount: ${order.get('totalAmount')}\n"
        formatted += "\n"
    
    return formatted

def format_selected_services(services: List[Dict[str, Any]]) -> str:
    """Format selected services for display"""
    if not services:
        return "No services selected"
    
    formatted = "🧺 **Selected Services:**\n\n"
    total_price = 0
    
    for i, service in enumerate(services, 1):
        if isinstance(service, dict):
            # Handle different possible field names
            service_id = service.get('id') or service.get('ID') or service.get('serviceId')
            service_name = service.get('name') or service.get('serviceName') or service.get('title')
            service_desc = service.get('description') or service.get('desc') or service.get('details')
            service_price = service.get('price') or service.get('cost') or service.get('amount')
            
            formatted += f"{i}. **{service_name or 'Unknown Service'}** (ID: {service_id})\n"
            
            if service_desc:
                formatted += f"   📝 {service_desc}\n"
            if service_price:
                try:
                    price = float(service_price)
                    total_price += price
                    formatted += f"   💰 Price: ${price:.2f}\n"
                except (ValueError, TypeError):
                    formatted += f"   💰 Price: {service_price}\n"
            formatted += "\n"
        else:
            formatted += f"{i}. **Unknown Service Format**\n\n"
    
    if total_price > 0:
        formatted += f"**Total Estimated Price: ${total_price:.2f}**\n\n"
    
    return formatted

def format_customer_info(customer_data: Union[Dict[str, Any], Any]) -> str:
    """Format customer information for display"""
    # Handle both dictionary and Pydantic model objects
    if hasattr(customer_data, 'model_dump'):
        # It's a Pydantic model, convert to dict
        data = customer_data.model_dump()
    elif hasattr(customer_data, '__dict__'):
        # It's an object with attributes
        data = customer_data.__dict__
    else:
        # It's already a dictionary
        data = customer_data
    
    info = "👤 **Customer Information:**\n\n"
    info += f"**Name:** {data.get('firstname', '')} {data.get('lastname', '')}\n"
    info += f"**Email:** {data.get('email', '')}\n"
    info += f"**Mobile:** {data.get('mobileNo', '')}\n"
    info += f"**Total Orders:** {data.get('totalOrder', 0)}\n"
    
    return info

def format_datetime_for_display(datetime_str: str) -> str:
    """Format datetime string for better display"""
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y at %I:%M %p')
    except:
        return datetime_str

def format_error_message(error: str) -> str:
    """Format error message for display"""
    return f"❌ **Error:** {error}"

def format_success_message(message: str) -> str:
    """Format success message for display"""
    return f"✅ **Success:** {message}"