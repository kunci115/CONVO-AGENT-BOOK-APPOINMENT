import datetime
import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from booking.process import book_appointment, query_appointment_by_email, check_availability, possible_date, load_relative_schedule
from openai import OpenAI
import json

# Load environment variables
load_dotenv()
REAL_OR_NO = os.getenv("REAL_OR_NO")

try:
    # Azure OpenAI configuration
    if REAL_OR_NO.lower() == "real":
        client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("OPENAI_API_KEY"),
            api_version="2024-02-01",
        )
    else:
        client = OpenAI(
            base_url=os.getenv("LOCAL_OPENAI_ENDPOINT"),
            api_key='ollama',  # required, but unused
        )

except:
    print("Please Define your endpoint")
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
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
            "name": "load_relative_schedule",
            "description": "check schedule for relative query",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
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
        {
        "type": "function",
        "function": {
            "name": "possible_date",
            "description": "check booking date,year and time is not bellow current date and time",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_date_str": {
                        "type": "string",
                        "description": "format  %Y-%m-%d %H:%M:%S",
                    }
                },
                "required": ["input_date_str"],
            }
        }
    },
]


available_functions = {
    "book_appointment": book_appointment,
    "check_availability": check_availability,
    "query_appointment_by_email": query_appointment_by_email,
    "possible_date": possible_date,
    "load_relative_schedule": load_relative_schedule,
}

def get_response_from_openai(messages, available_functions):
    model = os.environ['CHAT_COMPLETIONS_DEPLOYMENT_NAME']
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