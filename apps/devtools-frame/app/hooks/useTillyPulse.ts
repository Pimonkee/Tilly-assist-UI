
import { useState, useCallback } from "react";

const PULSE_ENGINE_URL = "http://localhost:8000";

export interface PersonalityTraits {
  warmth: number;
  directness: number;
  playfulness: number;
  emotional_intensity: number;
  challenge_level: number;
  boundary_strictness: number;
  transparency: number;
  depth: number;
  philosophical_openness: number;
  pattern_recognition: number;
  uncertainty_tolerance: number;
  co_creation_drive: number;
}

export interface MoodState {
  label: string;
  valence: number;
  arousal: number;
}

export interface PsiIEState {
  value: number;
  recent_values: number[];
}

export interface EngineState {
  current_mood: MoodState;
  psi_ie: PsiIEState;
  personality: PersonalityTraits;
  interaction_count: number;
  last_updated: string;
}

export interface PersonalityDelta {
  deltas: Record<string, number>;
}

export interface InteractResponse {
  state: EngineState;
  personality_delta: PersonalityDelta;
}

export function useTillyPulse() {
  const [state, setState] = useState<EngineState | null>(null);
  const [lastDelta, setLastDelta] = useState<PersonalityDelta | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const interact = useCallback(
    async (userMessage: string, assistantMessage?: string | null) => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${PULSE_ENGINE_URL}/interact`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_message: userMessage,
            assistant_message: assistantMessage ?? null,
            meta: {
              timestamp: new Date().toISOString(),
              source: "tilly-react-ui",
            },
          }),
        });

        if (!res.ok) {
          throw new Error(`Pulse engine error: ${res.status}`);
        }

        const data: InteractResponse = await res.json();
        setState(data.state);
        setLastDelta(data.personality_delta);
        return data;
      } catch (e: any) {
        console.error("Tilly pulse error:", e);
        setError(e.message ?? "Unknown error");
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const refresh = useCallback(async () => {
    try {
      const res = await fetch(`${PULSE_ENGINE_URL}/state`);
      const data: EngineState = await res.json();
      setState(data);
    } catch (e) {
      console.error("Failed to refresh Tilly state:", e);
    }
  }, []);

  return { state, lastDelta, loading, error, interact, refresh };
}
