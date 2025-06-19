import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from google.adk.runners import Runner
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

from manager_agent.agent import root_agent
from storage.session_service import PersistentSessionService

# --- Application Setup ---
app = FastAPI(title="Movie Chatbot API")
session_service = PersistentSessionService()

# The runner is now clean, with no reference to callbacks
runner = Runner(
    agent=root_agent,
    app_name="MovieChatbot",
    session_service=session_service
)

# --- API Data Models ---
class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

# --- API Endpoint ---
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    await session_service.create_session("MovieChatbot", request.user_id, request.session_id)
    message = types.Content(role="user", parts=[types.Part(text=request.message)])
    final_response = ""

    for event in runner.run(user_id=request.user_id, session_id=request.session_id, new_message=message):
        if event.is_final_response() and event.content:
            final_response = event.content.parts[0].text
            break

    return ChatResponse(response=final_response, session_id=request.session_id)

@app.get("/")
def read_root():
    return {"message": "Movie Chatbot API is running. Send POST requests to /chat."}