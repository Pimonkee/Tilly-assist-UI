from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class PersonalityTraits(BaseModel):
    """Core sliders like in your UI (0–10)."""

    warmth: float = 7.0
    directness: float = 5.0
    playfulness: float = 6.0
    emotional_intensity: float = 4.0
    challenge_level: float = 5.0
    boundary_strictness: float = 8.0
    transparency: float = 7.0
    depth: float = 6.0
    philosophical_openness: float = 8.0
    pattern_recognition: float = 9.0
    uncertainty_tolerance: float = 7.0
    co_creation_drive: float = 8.5


class MoodState(BaseModel):
    """Simple circumplex: valence (-1 to 1), arousal (0 to 1)."""

    label: str = "balanced"
    valence: float = 0.0
    arousal: float = 0.5


class PsiIEState(BaseModel):
    """Ψ_IE scalar and simple history for plotting."""

    value: float = 0.0
    recent_values: List[float] = Field(default_factory=list)


class Interaction(BaseModel):
    """Single turn of conversation observed by engine."""

    role: Literal["user", "assistant"]
    text: str
    timestamp: Optional[datetime] = None


class InteractionIn(BaseModel):
    """Payload from frontend."""

    user_message: str
    assistant_message: Optional[str] = None
    meta: Dict[str, str] = Field(default_factory=dict)


class PersonalityDelta(BaseModel):
    """How much each trait moved this interaction."""

    deltas: Dict[str, float] = Field(default_factory=dict)


class EngineState(BaseModel):
    """Everything the UI cares about."""

    current_mood: MoodState
    psi_ie: PsiIEState
    personality: PersonalityTraits
    interaction_count: int
    last_updated: datetime


class InteractionOut(BaseModel):
    """Returned after /interact."""

    state: EngineState
    personality_delta: PersonalityDelta
