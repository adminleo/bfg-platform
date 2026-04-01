import os
from contextlib import asynccontextmanager
from urllib.parse import parse_qs

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt

from src.agents.diagnosis_agent import DiagnosisAgent
from src.agents.coaching_agent import CoachingAgent
from src.agents.feedback_360_agent import Feedback360Agent

# ── Auth helper ──────────────────────────────────────────────
SECRET_KEY = os.environ.get("SECRET_KEY", "")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")


async def verify_ws_token(websocket: WebSocket) -> bool:
    """Validate JWT from ?token= query param on WebSocket connect.

    Returns True if valid, False otherwise (caller must close socket).
    """
    qs = parse_qs(websocket.scope.get("query_string", b"").decode())
    token_list = qs.get("token", [])
    if not token_list or not SECRET_KEY:
        return False
    try:
        payload = jwt.decode(token_list[0], SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub") is not None
    except JWTError:
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Gr8hub Agent Service", version="0.2.0", lifespan=lifespan)

# CORS — restrict to known origins; widen via ALLOWED_ORIGINS env var
_allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Agent instances
diagnosis_agent = DiagnosisAgent()
coaching_agent = CoachingAgent()
feedback_agent = Feedback360Agent()


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "gr8hub-agent-service"}


@app.websocket("/ws/diagnosis/{run_id}")
async def diagnosis_websocket(websocket: WebSocket, run_id: str):
    """WebSocket endpoint for conversational diagnostic assessment."""
    if not await verify_ws_token(websocket):
        await websocket.close(code=4001, reason="Authentication required")
        return
    await websocket.accept()
    try:
        # Send initial greeting
        greeting = await diagnosis_agent.start_session(run_id)
        await websocket.send_json({"type": "agent_message", "content": greeting})

        while True:
            data = await websocket.receive_json()
            user_message = data.get("content", "")

            # Process through diagnosis agent
            response = await diagnosis_agent.process_message(run_id, user_message)

            await websocket.send_json({
                "type": "agent_message",
                "content": response["message"],
                "progress": response.get("progress", 0),
                "polygon_update": response.get("polygon_update"),
                "is_complete": response.get("is_complete", False),
            })

            if response.get("is_complete"):
                # Send final results
                await websocket.send_json({
                    "type": "result",
                    "scores": response.get("scores"),
                    "polygon_data": response.get("polygon_data"),
                    "summary": response.get("summary"),
                })
                break

    except WebSocketDisconnect:
        await diagnosis_agent.save_session(run_id)


@app.websocket("/ws/coaching/{user_id}")
async def coaching_websocket(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for coaching agent interactions."""
    if not await verify_ws_token(websocket):
        await websocket.close(code=4001, reason="Authentication required")
        return
    await websocket.accept()
    try:
        greeting = await coaching_agent.start_session(user_id)
        await websocket.send_json({"type": "agent_message", "content": greeting})

        while True:
            data = await websocket.receive_json()
            user_message = data.get("content", "")

            response = await coaching_agent.process_message(user_id, user_message)
            await websocket.send_json({
                "type": "agent_message",
                "content": response["message"],
                "suggestions": response.get("suggestions", []),
            })

    except WebSocketDisconnect:
        await coaching_agent.save_session(user_id)


@app.websocket("/ws/feedback/{round_id}/{rater_id}")
async def feedback_websocket(
    websocket: WebSocket, round_id: str, rater_id: str
):
    """WebSocket endpoint for 360° feedback conversations."""
    if not await verify_ws_token(websocket):
        await websocket.close(code=4001, reason="Authentication required")
        return
    await websocket.accept()
    try:
        # Get params from query string or first message
        data = await websocket.receive_json()
        target_name = data.get("target_name", "Person")
        perspective = data.get("perspective", "peer")

        # Start the rater session
        greeting = await feedback_agent.start_rater_session(
            round_id=round_id,
            rater_id=rater_id,
            target_name=target_name,
            rater_perspective=perspective,
        )
        await websocket.send_json({"type": "agent_message", "content": greeting})

        while True:
            msg_data = await websocket.receive_json()
            user_message = msg_data.get("content", "")

            response = await feedback_agent.process_rater_message(
                round_id=round_id,
                rater_id=rater_id,
                message=user_message,
            )

            await websocket.send_json({
                "type": "agent_message",
                "content": response["message"],
                "progress": response.get("progress", 0),
                "is_complete": response.get("is_complete", False),
            })

            if response.get("is_complete"):
                # Send final scores
                await websocket.send_json({
                    "type": "result",
                    "scores": response.get("scores"),
                    "scil_scores": response.get("scil_scores"),
                })
                break

    except WebSocketDisconnect:
        await feedback_agent.save_session(round_id, rater_id)
