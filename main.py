import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from booking.process import book_appointment, query_appointment_by_email, check_availability
import json

# Load environment variables
load_dotenv()

# Azure OpenAI configuration
endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
api_key = os.environ["OPENAI_API_KEY"]
deployment = os.environ["CHAT_COMPLETIONS_DEPLOYMENT_NAME"]
token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

# Initialize client
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2024-02-01",
)

PROMPT_FILE_NAME = os.environ["PROMPT_FILE_NAME"]
# Read system prompt from file
with open('prompt/' + PROMPT_FILE_NAME, "r") as file:
    system_prompt = file.read()

# Initialize message history with system prompt
message_history = [
    {"role": "system", "content": system_prompt},
]

tools = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment slot",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "The date of the appointment (YYYY-MM-DD)",
                    },
                    "time": {
                        "type": "string",
                        "description": "The time of the appointment (HH:MM)",
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "Information about the user booking the appointment",
                    },
                    "email": {
                        "type": "string",
                        "description": "Email address to send the confirmation to",
                    },
                    "user_name": {
                        "type": "string",
                        "description": "detail info about user name"
                    }
                },
                "required": ["date", "time", "phone_number", "email", "user_name"],
            }
        }
    },
        {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "check appointment slot",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "The date of the appointment (YYYY-MM-DD)",
                    },
                    "time": {
                        "type": "string",
                        "description": "The time of the appointment (HH:MM)",
                    },
                },
                "required": ["date", "time"],
            }
        }
    },
    
            {
        "type": "function",
        "function": {
            "name": "query_appointment_by_email",
            "description": "check previous appointment by their email",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "the email in system while their book the appointment",
                    }
                },
                "required": ["email"],
            }
        }
    },
]

available_functions = {
    "book_appointment": book_appointment,
    "check_availability": check_availability,
    "query_appointment_by_email": query_appointment_by_email
}

def get_user_input():
    return input("User: ")

def get_response_from_openai(messages, available_functions):
    response = client.chat.completions.create(
        model=deployment,
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
        # verify function has correct number of arguments
        print()
        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model=deployment,
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response.choices[0].message.content
    return 
