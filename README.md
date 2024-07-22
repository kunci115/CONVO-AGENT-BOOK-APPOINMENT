# Booking Agent

A conversational booking agent powered by GPT-4o, designed to handle appointment bookings seamlessly.

## Features

- **Azure OpenAI Integration**: Utilizes Azure OpenAI with Python for advanced conversational capabilities.
- **Contextual Understanding**: Maintains conversation history to provide context-aware responses.
- **Function Calls**: Demonstrates use cases for function calls with the GPT-4o model. Available function calls include:
  - `book_appointment`: Handles the booking of appointments.
  - `check_availability`: Checks the availability of time slots.
  - `query_appointment_by_email`: Retrieves appointments based on email.
  - `check_current_date`: Checks the current date.
- **Extensible**: Designed to allow for future feature additions and enhancements.

## Installation

1. Create a `.env` file with the following variables:
    ```env
    OPENAI_API_KEY=YOUR_API_KEY
    AZURE_OPENAI_ENDPOINT=YOUR_API_OPENAI_ENDPOINT
    CHAT_COMPLETIONS_DEPLOYMENT_NAME=Your_Model_Name (e.g., gpt-4o)
    OPENAI_API_KEY_2=ANOTHER_API_KEY (if needed)
    PROMPT_FILE_NAME=booking-agent.txt
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

### Server and Console UI
- **Simple Server**: Wrap your agent in a simple web server exposing a `/chat` POST endpoint. This endpoint will always receive the latest message. Refer to `api.yml` for the API definition.
  
- **Console UI**: Provide a console loop that allows a user to chat with your agent and book an appointment.

## Usage

There are two ways to run the booking agent:

1. **Web Server**:
    ```sh
    python server.py
    ```
    The server will listen on port 3000 at the `/chat` endpoint. You can send a POST request with the following format:
    ```json
    {
        "id": "user-1",
        "content": "hi"
    }
    ```

2. **Console Interface**:
    ```sh
    python console.py
    ```
    This will launch a CLI interface for interacting with the agent and booking appointments.

### Security
The agent is tested to ensure that no sensitive information is leaked when users query with parameters that are not defined, such as email.

---

Feel free to contribute to this project by submitting issues and pull requests. We look forward to seeing your enhancements and innovations!

---

If you have any questions or need further assistance, please reach out.
