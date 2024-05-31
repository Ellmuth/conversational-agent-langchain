from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional
from uuid import uuid4
import asyncio
import json

load_dotenv()

app = FastAPI()

class Message(BaseModel):
    user_message: str
    session_id: Optional[str] = None

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

sessions: Dict[str, List[Dict[str, str]]] = {}

@app.post("/chat/")
async def chat(message: Message):
    try:
        if message.session_id and message.session_id in sessions:
            session_id = message.session_id
        else:
            session_id = str(uuid4())
            sessions[session_id] = []

        # Get conversation history for the session
        conversation_history = sessions[session_id]
        conversation_history.append({"role": "user", "content": message.user_message})

        # Prepare the conversation context for Groq
        context = [{"role": msg["role"], "content": msg["content"]} for msg in conversation_history]

        # Call Groq API to generate AI response
        response = client.chat.completions.create(
            messages=context,
            model="llama3-8b-8192"  # Update with your model identifier
        )

        async def response_generator():
            ai_response = response.choices[0].message.content

            # Update session history
            conversation_history.append({"role": "assistant", "content": ai_response})
            sessions[session_id] = conversation_history

            yield json.dumps({"ai_response": ai_response, "session_id": session_id}) + "\n"

        return StreamingResponse(response_generator(), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/new_chat/")
async def new_chat():
    session_id = str(uuid4())
    sessions[session_id] = []
    return {"session_id": session_id}

@app.get("/sessions/")
async def get_sessions():
    return {"sessions": list(sessions.keys())}
