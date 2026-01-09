from __future__ import annotations

import math
from datetime import datetime
from typing import Dict, Tuple

from .config import (
    MOOD_ALPHA,
    MOOD_MAX_DELTA,
    PERSONALITY_DECAY_RATE,
    PERSONALITY_MAX_DELTA,
    PSI_IE_ALPHA,
    PSI_IE_WINDOW,
)
from .memory import RollingMemory
from .models import (
    EngineState,
    Interaction,
    InteractionIn,
    InteractionOut,
    MoodState,
    PersonalityDelta,
    PersonalityTraits,
    PsiIEState,
)


def _clip(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


class ConsciousnessEngine:
    """
    The beating heart: takes text, emits personality/mood/Ψ_IE shifts.
    Very lightweight now but *designed* so you can drop in better
    NLP/affect models later.
    """

    def __init__(self) -> None:
        self.personality = PersonalityTraits()
        self.baseline = self.personality.model_copy(deep=True)

        self.mood = MoodState()
        self.psi_ie = PsiIEState()
        self.memory = RollingMemory(maxlen=400)

        self.interaction_count: int = 0
        self.last_updated: datetime = datetime.utcnow()

    # ──────────────────────────────────────────────
    # PUBLIC INTERFACE
    # ──────────────────────────────────────────────

    def handle_interaction(self, payload: InteractionIn) -> InteractionOut:
        """Main entry from /interact."""

        now = datetime.utcnow()
        self.interaction_count += 1

        # 1) Log interaction(s) into memory
        self._record_turns(payload, now)

        # 2) Derive crude "emotion vector" from the user message
        valence, arousal, stimulation = self._analyze_text(payload.user_message)

        # 3) Update mood based on this interaction
        self._update_mood(valence, arousal)

        # 4) Update Ψ_IE using mood + message complexity
        self._update_psi_ie(valence, stimulation)

        # 5) Update personality sliders from mood + content
        delta = self._update_personality(valence, arousal, stimulation)

        self.last_updated = now

        state = EngineState(
            current_mood=self.mood,
            psi_ie=self.psi_ie,
            personality=self.personality,
            interaction_count=self.interaction_count,
            last_updated=self.last_updated,
        )

        return InteractionOut(
            state=state,
            personality_delta=PersonalityDelta(deltas=delta),
        )

    def snapshot(self) -> EngineState:
        """Return current state for GET /state."""
        return EngineState(
            current_mood=self.mood,
            psi_ie=self.psi_ie,
            personality=self.personality,
            interaction_count=self.interaction_count,
            last_updated=self.last_updated,
        )

    # ──────────────────────────────────────────────
    # INTERNALS
    # ──────────────────────────────────────────────

    def _record_turns(self, payload: InteractionIn, now: datetime) -> None:
        self.memory.add(
            Interaction(role="user", text=payload.user_message, timestamp=now)
        )
        if payload.assistant_message:
            self.memory.add(
                Interaction(
                    role="assistant",
                    text=payload.assistant_message,
                    timestamp=now,
                )
            )

    def _analyze_text(self, text: str) -> Tuple[float, float, float]:
        """
        Super simple heuristic "emotion decoder".
        Later you can plug in a real sentiment/affect model here.

        Returns:
            valence in [-1, 1]
            arousal in [0, 1]
            stimulation ~ [0, 1] (how demanding/complex/high-energy)
        """
        stripped = text.strip()
        length = len(stripped)

        # crude sentiment-ish guess
        lower = stripped.lower()
        positive_tokens = ["love", "thank", "good", "awesome", "great", "beautiful"]
        negative_tokens = ["hate", "fuck", "stupid", "angry", "sad", "broken", "afraid"]

        score = 0.0
        for t in positive_tokens:
            if t in lower:
                score += 1.0
        for t in negative_tokens:
            if t in lower:
                score -= 1.0

        # normalize sentiment into -1..1
        valence = _clip(score / 3.0, -1.0, 1.0)

        # arousal: length + punctuation
        exclam = stripped.count("!")
        question = stripped.count("?")
        caps_ratio = (
            sum(1 for ch in stripped if ch.isupper()) / (len(stripped) + 1e-6)
        )

        energy = (
            (length / 280.0)
            + (0.4 * exclam)
            + (0.2 * question)
            + (1.2 * caps_ratio)
        )
        arousal = _clip(energy, 0.0, 1.0)

        # "stimulation" as a companion feature (requests, commands, etc.)
        demand_tokens = ["help", "need", "build", "fix", "now", "please"]
        stim = 0.0
        for t in demand_tokens:
            if t in lower:
                stim += 0.3
        stimulation = _clip(stim + arousal * 0.3, 0.0, 1.0)

        return valence, arousal, stimulation

    def _update_mood(self, valence: float, arousal: float) -> None:
        """EMA on mood, gently constrained."""
        old_v = self.mood.valence
        old_a = self.mood.arousal

        new_v = old_v + MOOD_ALPHA * (valence - old_v)
        new_a = old_a + MOOD_ALPHA * (arousal - old_a)

        # clamp change per step
        dv = _clip(new_v - old_v, -MOOD_MAX_DELTA, MOOD_MAX_DELTA)
        da = _clip(new_a - old_a, -MOOD_MAX_DELTA, MOOD_MAX_DELTA)

        self.mood.valence = _clip(old_v + dv, -1.0, 1.0)
        self.mood.arousal = _clip(old_a + da, 0.0, 1.0)

        # label for UI
        if abs(self.mood.valence) < 0.15 and abs(self.mood.arousal - 0.5) < 0.15:
            label = "balanced"
        elif self.mood.valence > 0.2 and self.mood.arousal >= 0.6:
            label = "engaged"
        elif self.mood.valence < -0.2 and self.mood.arousal >= 0.6:
            label = "stressed"
        elif self.mood.arousal < 0.3:
            label = "calm"
        else:
            label = "reflective"

        self.mood.label = label

    def _update_psi_ie(self, valence: float, stimulation: float) -> None:
        """
        Ψ_IE is treated as "coherence + co-creation energy".

        Here we approximate with:
        - high when valence is near 0 (non-judgmental presence)
        - plus a bump from stimulation (active collaboration)
        """
        coherence = 1.0 - abs(valence)  # centered engagement
        raw = _clip(0.6 * coherence + 0.4 * stimulation, 0.0, 1.0)

        # EMA
        prev = self.psi_ie.value
        updated = (1 - PSI_IE_ALPHA) * prev + PSI_IE_ALPHA * raw
        self.psi_ie.value = updated

        # rolling history for plotting
        self.psi_ie.recent_values.append(updated)
        if len(self.psi_ie.recent_values) > PSI_IE_WINDOW:
            self.psi_ie.recent_values = self.psi_ie.recent_values[-PSI_IE_WINDOW:]

    def _update_personality(
        self, valence: float, arousal: float, stimulation: float
    ) -> Dict[str, float]:
        """
        Softly nudge traits based on interaction "vibe".

        This is intentionally simple & interpretable; you can
        later replace it with a neural policy.
        """

        delta: Dict[str, float] = {}

        # First gently decay traits toward baseline
        for field in self.personality.model_fields:
            current = getattr(self.personality, field)
            base = getattr(self.baseline, field)
            decay_step = PERSONALITY_DECAY_RATE * (base - current)
            new_val = current + decay_step
            setattr(self.personality, field, new_val)
            delta[field] = decay_step

        # Now add interaction-driven nudges
        # Positive, warm, engaged message
        if valence > 0.2:
            delta["warmth"] = delta.get("warmth", 0) + 0.18 * valence
            delta["playfulness"] = delta.get("playfulness", 0) + 0.12 * arousal
            delta["co_creation_drive"] = delta.get("co_creation_drive", 0) + 0.10 * stimulation
        # Critical / distressed message
        if valence < -0.2:
            delta["depth"] = delta.get("depth", 0) + 0.15 * abs(valence)
            delta["transparency"] = delta.get("transparency", 0) + 0.10 * abs(valence)
            delta["boundary_strictness"] = delta.get("boundary_strictness", 0) + 0.12 * abs(valence)

        # High uncertainty, big questions
        if self.memory.history() and "?" in self.memory.history()[-1].text:
            delta["philosophical_openness"] = delta.get("philosophical_openness", 0) + 0.08 * arousal
            delta["uncertainty_tolerance"] = delta.get("uncertainty_tolerance", 0) + 0.08 * arousal

        # High stimulation / build requests → challenge mode
        if stimulation > 0.4:
            delta["challenge_level"] = delta.get("challenge_level", 0) + 0.12 * stimulation
            delta["pattern_recognition"] = delta.get("pattern_recognition", 0) + 0.05 * stimulation

        # Apply and clamp to [0, 10]
        for field, dv in delta.items():
            current = getattr(self.personality, field)
            dv_clipped = _clip(dv, -PERSONALITY_MAX_DELTA, PERSONALITY_MAX_DELTA)
            new_val = _clip(current + dv_clipped, 0.0, 10.0)
            setattr(self.personality, field, new_val)
            delta[field] = dv_clipped

        return delta
