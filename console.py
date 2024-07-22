
# Main loop
from main import get_user_input
from main import system_prompt
from tools import available_functions
from tools import get_response_from_openai


# Initialize message history with system prompt
message_history = [
    {"role": "system", "content": system_prompt},
]
while True:
    user_message = get_user_input()
    message_history.append({"role": "user", "content": user_message})
    
    response = get_response_from_openai(message_history, available_functions)
    
    print(f"Assistant: {response}")
    message_history.append({"role": "assistant", "content": response})
    
    # Optional: Save history to a file for persistence
    with open("chat-log/chat_history.txt", "a") as file:
        file.write(f"User: {user_message}\n")
        file.write(f"Assistant: {response}\n")
