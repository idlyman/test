import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

user_queues: Dict[str, asyncio.Queue] = {}

class Msg(BaseModel):
    sender: str
    receiver: str
    text: str

@app.post("/send")
async def send_message(msg: Msg):
    # Ensure receiver queue exists
    if msg.receiver not in user_queues:
        user_queues[msg.receiver] = asyncio.Queue()

    # Put message in receiver's queue
    await user_queues[msg.receiver].put(f"{msg.sender}: {msg.text}")

    # Ensure sender also has a queue
    if msg.sender not in user_queues:
        user_queues[msg.sender] = asyncio.Queue()

    try:
        # Wait for a reply with timeout
        response = await asyncio.wait_for(user_queues[msg.sender].get(), timeout=30)
        return {"messages": response}
    except asyncio.TimeoutError:
        return {"messages": "No new messages"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("relay_http:app", host="0.0.0.0", port=8000)
