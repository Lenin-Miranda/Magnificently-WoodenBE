from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler to provide consistent error responses
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the response data format
        custom_response_data = {}
        
        if isinstance(response.data, dict):
            for key, value in response.data.items():
                if isinstance(value, list):
                    # Convert list to string (first error message)
                    custom_response_data[key] = value[0] if value else 'Invalid value'
                else:
                    custom_response_data[key] = value
        else:
            # If response.data is a list or other type
            custom_response_data = {'detail': str(response.data)}
        
        response.data = custom_response_data

    return response
