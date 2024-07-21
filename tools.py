import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from booking.process import book_appointment, query_appointment_by_email, check_availability
import json

# Load environment variables
load_dotenv()

# Azure OpenAI configuration
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version="2024-02-01",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment slot",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                    "time": {"type": "string", "description": "HH:MM"},
                    "phone_number": {"type": "string", "description": "User's phone number"},
                    "email": {"type": "string", "description": "User's email address"},
                    "user_name": {"type": "string", "description": "User's name"}
                },
                "required": ["date", "time", "phone_number", "email", "user_name"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check appointment slot",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "YYYY-MM-DD"},
                    "time": {"type": "string", "description": "HH:MM"},
                },
                "required": ["date", "time"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_appointment_by_email",
            "description": "Check previous appointment by email",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "User's email address"},
                },
                "required": ["email"],
            }
        }
    },
]

available_functions = {
    "book_appointment": book_appointment,
    "check_availability": check_availability
}

def get_response_from_openai(messages, available_functions):
    model = os.getenv['CHAT_COMPLETIONS_DEPLOYMENT_NAME']
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    response_message = response.choices[0].message
    response_tool_calls = response_message.tool_calls
    if response_tool_calls is None:
        return response_message.content
    messages.append(response_message)
    for tool_call in response_tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        function_name = tool_call.function.name
        # verify function exists
        if function_name not in available_functions:
            return "Function " + function_name + " does not exist"
        function_to_call = available_functions[function_name]
        
        function_args = json.loads(tool_call.function.arguments)
        function_response = function_to_call(**function_args)
    
        print()
        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            }
        ) 
        second_response = client.chat.completions.create(
            model=model,
            messages=messages,
        ) 
        return second_response.choices[0].message.content
    return 