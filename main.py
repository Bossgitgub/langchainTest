from fastapi import FastAPI
from pydantic import BaseModel

from Agent import agent

app = FastAPI()

class AskRequest(BaseModel):
    question: str

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/ask")
async def ask(req: AskRequest):

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": req.question
                }
            ]
        }
    )

    return {
        "result": str(result)
    }
