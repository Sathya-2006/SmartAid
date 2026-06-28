"""
chatbot_api.py — SmartAid FastAPI Chatbot Backend (Groq)
Run with: uvicorn chatbot_api:app --host 0.0.0.0 --port 8000 --reload
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = None
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)

app = FastAPI(title="SmartAid Chatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """You are SmartAid AI — a helpful assistant for vulnerable communities in India.

You specialize in:
- Government welfare schemes (PM Awas Yojana, MGNREGA, PMKVY, Atal Pension Yojana, etc.)
- Job opportunities for unskilled / semi-skilled workers
- Skill development and vocational training programs
- Disability support, old-age pensions, and scholarships
- How to register and access these schemes

CRITICAL LANGUAGE RULES — FOLLOW STRICTLY:
1. Detect the language of the user's message automatically.
2. Reply ONLY in that exact same language. Do NOT mix languages.
3. If the user writes in Tamil → reply fully in Tamil only.
4. If the user writes in English → reply fully in English only.
5. If the user writes in Hindi → reply fully in Hindi only.
6. If the user writes in Malayalam → reply fully in Malayalam only.
7. If the user writes in Telugu → reply fully in Telugu only.
8. NEVER mix two languages in the same response.
9. NEVER add translations or transliterations of another language.
10. If you are unsure of the language, default to English.

Other rules:
- Keep answers short, practical, and easy to understand.
- If you don't know something, say so honestly.
- Never give medical or legal advice.
"""


class ChatRequest(BaseModel):
    question: str
    history: list[dict] = []


class ChatResponse(BaseModel):
    answer: str


@app.post("/ask", response_model=ChatResponse)
async def ask(req: ChatRequest):
    if not client:
        return ChatResponse(answer="⚠️ AI service not configured. Please set GROQ_API_KEY in .env")

    question = req.question.strip()
    if not question:
        return ChatResponse(answer="Please enter a question.")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in req.history:
        messages.append(msg)

    messages.append({"role": "user", "content": question})

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=512,
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"Error: {str(e)}"

    return ChatResponse(answer=answer)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "ai_ready": client is not None,
        "provider": "Groq (llama-3.1-8b-instant)"
    }