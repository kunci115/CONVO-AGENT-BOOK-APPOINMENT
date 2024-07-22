import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from booking.process import book_appointment, query_appointment_by_email, check_availability, check_current_date
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

def get_user_input():
    return input("User: ")

