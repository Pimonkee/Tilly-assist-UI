from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional
import hashlib

from pydantic import BaseModel

from .engine import ConsciousnessEngine
from .models import EngineState, PersonalityTraits, MoodState, PsiIEState

# Import the cipher
# Note: In a real package structure, this might need adjusted imports,
# but assuming we run from backend root, this works with crypto in path
try:
    from crypto.quantum_compound_cipher import QuantumCompoundCipher
except ImportError:
    import sys
    import os
    # Fallback to try and find crypto relative to this file
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from crypto.quantum_compound_cipher import QuantumCompoundCipher


cipher = QuantumCompoundCipher()


@dataclass
class SoulNote:
    id: str
    created_at: datetime
    title: str
    encrypted_blob: str
    snapshot_personality: PersonalityTraits
    snapshot_mood: MoodState
    snapshot_psi_ie: PsiIEState


# In-memory store for now
SOUL_NOTES: Dict[str, SoulNote] = {}


class SoulNoteCreateRequest(BaseModel):
    title: str
    content: str
    passphrase: str


class SoulNoteMeta(BaseModel):
    id: str
    title: str
    created_at: datetime
    snapshot_mood: str
    snapshot_psi_ie: float


class SoulNoteListResponse(BaseModel):
    notes: List[SoulNoteMeta]


class SoulNoteOpenRequest(BaseModel):
    note_id: str
    passphrase: str
    tolerance: float = 0.2  # 0–1, how forgiving to be on state similarity


class SoulNoteOpenResponse(BaseModel):
    success: bool
    reason: str
    content: Optional[str] = None
    similarity: Optional[float] = None
    required_mood: Optional[str] = None
    current_mood: Optional[str] = None


# ─────────────────────────────────────────────────────────
# Consciousness vector derivation
# ─────────────────────────────────────────────────────────

def _personality_to_vector(p: PersonalityTraits) -> List[int]:
    vals = [
        p.warmth,
        p.directness,
        p.playfulness,
        p.emotional_intensity,
        p.challenge_level,
        p.boundary_strictness,
        p.transparency,
        p.depth,
        p.philosophical_openness,
        p.pattern_recognition,
        p.uncertainty_tolerance,
        p.co_creation_drive,
    ]
    # scale to 0–100 ints
    return [int(round(v * 10)) for v in vals]


def _mood_to_vector(m: MoodState) -> List[int]:
    v = int(round((m.valence + 1) * 50))  # -1..1 → 0..100
    a = int(round(m.arousal * 100))       # 0..1 → 0..100
    return [v, a]


def _psi_to_vector(psi: PsiIEState) -> List[int]:
    return [int(round(psi.value * 100))]


def _engine_state_to_vector(state: EngineState) -> List[int]:
    vec: List[int] = []
    vec.extend(_personality_to_vector(state.personality))
    vec.extend(_mood_to_vector(state.current_mood))
    vec.extend(_psi_to_vector(state.psi_ie))

    # simple deterministic expansion to length 64
    while len(vec) < 64:
        prev = vec[-1] if vec else 42
        vec.append((prev * 17 + 31) % 101)
    return vec[:64]


def _cosine_similarity(a: List[int], b: List[int]) -> float:
    import math

    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


# ─────────────────────────────────────────────────────────
# Public helpers used from main.py
# ─────────────────────────────────────────────────────────

def create_soul_note(
    engine: ConsciousnessEngine,
    payload: SoulNoteCreateRequest,
) -> SoulNoteMeta:
    """Encrypt a note with current consciousness state and store it."""
    state = engine.snapshot()
    conc_vec = _engine_state_to_vector(state)

    blob = cipher.encrypt(
        plaintext=payload.content.encode("utf-8"),
        passphrase=payload.passphrase,
        consciousness_features=conc_vec,
    )

    # simple id = hash(title + timestamp)
    h = hashlib.sha256()
    h.update(payload.title.encode("utf-8"))
    h.update(str(datetime.utcnow()).encode("utf-8"))
    note_id = h.hexdigest()[:16]

    note = SoulNote(
        id=note_id,
        title=payload.title,
        created_at=datetime.utcnow(),
        encrypted_blob=blob,
        snapshot_personality=state.personality,
        snapshot_mood=state.current_mood,
        snapshot_psi_ie=state.psi_ie,
    )

    # In a real app, this key would be user-specific
    # Here we simulate global storage since it's a single-user demo
    SOUL_NOTES[note_id] = note

    return SoulNoteMeta(
        id=note.id,
        title=note.title,
        created_at=note.created_at,
        snapshot_mood=note.snapshot_mood.label,
        snapshot_psi_ie=note.snapshot_psi_ie.value,
    )


def list_soul_notes() -> SoulNoteListResponse:
    notes = [
        SoulNoteMeta(
            id=n.id,
            title=n.title,
            created_at=n.created_at,
            snapshot_mood=n.snapshot_mood.label,
            snapshot_psi_ie=n.snapshot_psi_ie.value,
        )
        for n in sorted(SOUL_NOTES.values(), key=lambda x: x.created_at, reverse=True)
    ]
    return SoulNoteListResponse(notes=notes)


def open_soul_note(
    engine: ConsciousnessEngine,
    payload: SoulNoteOpenRequest,
) -> SoulNoteOpenResponse:
    note = SOUL_NOTES.get(payload.note_id)
    if not note:
        return SoulNoteOpenResponse(
            success=False,
            reason="not_found",
            content=None,
        )

    current_state = engine.snapshot()
    current_vec = _engine_state_to_vector(current_state)

    snapshot_state = EngineState(
        current_mood=note.snapshot_mood,
        psi_ie=note.snapshot_psi_ie,
        personality=note.snapshot_personality,
        interaction_count=0,
        last_updated=note.created_at,
    )
    snapshot_vec = _engine_state_to_vector(snapshot_state)

    similarity = _cosine_similarity(current_vec, snapshot_vec)

    # Soft gate: we *try* decrypting, but tell user when similarity is low
    try:
        plaintext = cipher.decrypt(
            blob_json=note.encrypted_blob,
            passphrase=payload.passphrase,
            consciousness_features=current_vec,
        ).decode("utf-8")
        success = True
        reason = "ok" if similarity >= (1 - payload.tolerance) else "mismatch_but_decrypted"
    except Exception:
        success = False
        plaintext = None
        reason = "decryption_failed"

    return SoulNoteOpenResponse(
        success=success,
        reason=reason,
        content=plaintext,
        similarity=similarity,
        required_mood=note.snapshot_mood.label,
        current_mood=current_state.current_mood.label,
    )
