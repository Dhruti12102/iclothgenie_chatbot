import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Server Configuration
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', '7860'))
    SHARE = os.getenv('SHARE', 'False').lower() == 'true'
    
    # API Configuration
    API_BASE_URL = os.getenv('API_BASE_URL', 'https://admin.iclothgenie.com/api')
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
    
    # Application Settings
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '3600'))
    
    # API Endpoints
    ENDPOINTS = {
        'INSERT_CUSTOMER': '/Authentication/InsertCustomer',
        'LOGIN': '/Authentication/Login',
        'INSERT_ORDER': '/Order/InsertOrder',
        'UPDATE_ORDER': '/Order/UpdateOrder',
        'GET_ORDER_DETAIL': '/Order/GetOrderDetail',
        'GET_ALL_SERVICES': '/Services/GetAllServices',
        'VALIDATE_POSTCODE': '/Postcode/IsValidPostcode'
    }
    
    # Time slots
    TIME_SLOTS = [
        "09:00 AM - 11:00 AM",
        "11:00 AM - 01:00 PM",
        "01:00 PM - 03:00 PM",
        "03:00 PM - 05:00 PM",
        "05:00 PM - 07:00 PM",
        "07:00 PM - 09:00 PM"
    ]
    
    # Collection and Delivery Options
    COLLECTION_OPTIONS = [
        "Driver collects from you",
        "Drop off at store"
    ]
    
    DELIVERY_OPTIONS = [
        "Driver delivers to you",
        "Collect from store"
    ]

settings = Settings()