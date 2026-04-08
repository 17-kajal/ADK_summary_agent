import uuid
import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import root_agent

load_dotenv()

app = FastAPI(title="ADK Summary Agent")

# ADK setup
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="summary_app",
    session_service=session_service,
)

# Request model
class SummaryRequest(BaseModel):
    text: str

# Health check
@app.get("/")
def root():
    return {"message": "ADK Summary Agent is running 🚀"}

# Summarization endpoint
@app.post("/summarize")
async def summarize(request: SummaryRequest):
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        user_id = "local-user"
        session_id = str(uuid.uuid4())

        await session_service.create_session(
            app_name="summary_app",
            user_id=user_id,
            session_id=session_id
        )

        content = types.Content(
            role="user",
            parts=[types.Part(text=request.text)]
        )

        final_response = ""

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if (
                hasattr(event, "content")
                and event.content
                and hasattr(event.content, "parts")
                and event.content.parts
                and hasattr(event, "is_final_response")
                and event.is_final_response()
            ):
                final_response = event.content.parts[0].text

        if not final_response:
            raise HTTPException(status_code=500, detail="No summary returned")

        return {"summary": final_response}

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))