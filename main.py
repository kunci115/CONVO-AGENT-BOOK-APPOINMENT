import datetime
import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from booking.process import book_appointment, query_appointment_by_email, check_availability, possible_date
import json

# Load environment variables
load_dotenv()
current_date = datetime.datetime.now().strftime("%Y-%m-%d")

PROMPT_FILE_NAME = os.environ["PROMPT_FILE_NAME"]
# Read system prompt from file
with open('prompt/' + PROMPT_FILE_NAME, "r") as file:
    system_prompt = file.read()
system_prompt=system_prompt.replace("{ current_date }", current_date)
print(system_prompt)

# Initialize message history with system prompt
message_history = [
    {"role": "system", "content": system_prompt},
]

def get_user_input():
    return input("User: ")

