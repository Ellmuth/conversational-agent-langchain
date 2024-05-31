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
from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
import re
import spacy

load_dotenv()

app = FastAPI()

class Message(BaseModel):
    user_message: str
    session_id: Optional[str] = None

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

sessions: Dict[str, List[Dict[str, str]]] = {}
knowledge_base: Dict[str, List[str]] = {}

nlp = spacy.load("en_core_web_sm")

@app.post("/chat/")
async def chat(message: Message):
    try:
        if message.session_id and message.session_id in sessions:
            session_id = message.session_id
        else:
            session_id = str(uuid4())
            sessions[session_id] = []
            knowledge_base[session_id] = []

        # Get conversation history for the session
        conversation_history = sessions[session_id]
        conversation_history.append({"role": "user", "content": message.user_message})

        # Prepare the conversation context for Groq
        context = [{"role": msg["role"], "content": msg["content"]} for msg in conversation_history]

        # Call Groq API to generate AI response
        response = client.chat.completions.create(
            messages=context,
            model="llama3-8b-8192"
        )

        async def response_generator():
            ai_response = response.choices[0].message.content

            # Update session history
            conversation_history.append({"role": "assistant", "content": ai_response})
            sessions[session_id] = conversation_history

            # Extract and save relevant information
            extracted_info = extract_information(message.user_message)
            if extracted_info:
                knowledge_base[session_id].extend(extracted_info)

            yield json.dumps({"ai_response": ai_response, "session_id": session_id}) + "\n"

        return StreamingResponse(response_generator(), media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/new_chat/")
async def new_chat():
    session_id = str(uuid4())
    sessions[session_id] = []
    knowledge_base[session_id] = []
    return {"session_id": session_id}

@app.get("/sessions/")
async def get_sessions():
    return {"sessions": list(sessions.keys())}

@app.get("/knowledge/{session_id}")
async def get_knowledge(session_id: str):
    if session_id in knowledge_base:
        return {"knowledge": knowledge_base[session_id]}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

def extract_information(message: str) -> List[str]:
    # Improved implementation for extracting personal information
    extracted_info = []
    doc = nlp(message)

    # Extract names
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            extracted_info.append(f"User mentioned the name: {ent.text}")

    # Extract ages
    age_match = re.search(r'\b(\d{1,2}) years? old\b', message)
    if age_match:
        extracted_info.append(f"User mentioned their age: {age_match.group(1)} years old")

    # Extract locations
    for ent in doc.ents:
        if ent.label_ == "GPE":
            extracted_info.append(f"User mentioned their location: {ent.text}")

    return extracted_info

# LangChain setup for memory extraction
system_prompt_initial = """
Your job is to assess a brief chat history in order to determine if the conversation contains any personal information.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(system_prompt_initial),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system",
            "Remember, only respond with TRUE or FALSE. Do not provide any other information.",
        ),
    ]
)

llm = ChatOpenAI(
    model="gpt-3.5-turbo-0125",
    streaming=True,
    temperature=0.0,
)

sentinel_runnable = {"messages": RunnablePassthrough()} | prompt | llm
