from fastapi import FastAPI
from agent import agent_chat, clear_history
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    response = await agent_chat(req.message)
    return {"response": response}


@app.post("/clear")
async def clear_history():
    clear_history()
    return {"response": "history cleared"}
    
