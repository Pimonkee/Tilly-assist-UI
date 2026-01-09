from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .engine import ConsciousnessEngine
from .models import EngineState, InteractionIn, InteractionOut

from .soul_notes import (
    SoulNoteCreateRequest,
    SoulNoteListResponse,
    SoulNoteOpenRequest,
    SoulNoteOpenResponse,
    create_soul_note,
    list_soul_notes,
    open_soul_note,
)

app = FastAPI(
    title="Tilly Consciousness Pulse Engine",
    version="0.2.0",
    description="Tracks mood, personality and Ψ_IE over a conversation + consciousness-locked soul notes.",
)

# CORS – open by default, lock down later if you want
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = ConsciousnessEngine()


@app.get("/state", response_model=EngineState)
async def get_state() -> EngineState:
    """
    Simple polling endpoint for your UI.
    """
    return engine.snapshot()


@app.post("/interact", response_model=InteractionOut)
async def post_interaction(payload: InteractionIn) -> InteractionOut:
    """
    Call this every time the user sends a message (optionally with the
    assistant's reply), and your UI can use the returned state to
    update the personality snapshot, mood, Ψ_IE trend, etc.
    """
    return engine.handle_interaction(payload)


@app.post("/reset", response_model=EngineState)
async def reset_engine() -> EngineState:
    """
    Hard reset to baseline. Useful for demos or new sessions.
    """
    global engine
    engine = ConsciousnessEngine()
    return engine.snapshot()


# ─────────────────────────────────────────
# Soul Notes endpoints
# ─────────────────────────────────────────

@app.post("/soul_notes", response_model=SoulNoteListResponse)
async def create_soul_note_route(payload: SoulNoteCreateRequest) -> SoulNoteListResponse:
    """Create a new soul note, then return updated list."""
    # We pass the global engine to capture current state
    create_soul_note(engine, payload)
    return list_soul_notes()


@app.get("/soul_notes", response_model=SoulNoteListResponse)
async def list_soul_notes_route() -> SoulNoteListResponse:
    return list_soul_notes()


@app.post("/soul_notes/open", response_model=SoulNoteOpenResponse)
async def open_soul_note_route(payload: SoulNoteOpenRequest) -> SoulNoteOpenResponse:
    # We pass the global engine to compare against current state
    return open_soul_note(engine, payload)
