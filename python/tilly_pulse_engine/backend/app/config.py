from datetime import timedelta

# How quickly personality *drifts back* toward baseline
PERSONALITY_DECAY_RATE = 0.02  # per interaction

# How strongly each interaction can nudge traits
PERSONALITY_MAX_DELTA = 0.35

# Rolling window (in interactions) for Ψ_IE trend
PSI_IE_WINDOW = 20

# How much to weight new Ψ_IE vs historical (EMA factor)
PSI_IE_ALPHA = 0.15

# Default "balanced" mood
DEFAULT_VALENCE = 0.0
DEFAULT_AROUSAL = 0.5

# Mood EMA smoothing
MOOD_ALPHA = 0.25

# Maximum absolute mood change per interaction
MOOD_MAX_DELTA = 0.4
