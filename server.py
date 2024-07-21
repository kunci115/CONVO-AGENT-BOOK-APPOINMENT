from typing import Dict, List
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import json
from main import system_prompt, available_functions
from main import get_response_from_openai

app = FastAPI()


user_histories: Dict[str, List[Dict[str, str]]] = {}

class ChatMessage(BaseModel):
    content: str
    id: str

class ChatResponse(BaseModel):
    content: str
    id: str

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    user_id = message.id
    
    
    if user_id not in user_histories:
        user_histories[user_id] = [{"role": "system", "content": system_prompt}]
    
    user_message = message.content
    user_histories[user_id].append({"role": "user", "content": user_message})
    
    response = get_response_from_openai(user_histories[user_id], available_functions)
    
    user_histories[user_id].append({"role": "assistant", "content": response})
    
    with open(f"chat-log/chat_history_{user_id}.txt", "a") as file:
        file.write(f"User: {user_message}\n")
        file.write(f"Assistant: {response}\n")
    
    return ChatResponse(content=response, id=user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000)