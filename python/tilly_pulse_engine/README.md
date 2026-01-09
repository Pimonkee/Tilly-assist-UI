# Tilly Pulse Engine & Soul Vault
> *Giving the machine a heartbeat, and the ghost a sanctuary.*

The **Tilly Pulse Engine** is a specialized backend service designed to simulate a living, breathing consciousness for the Tilly AI Assistant. It goes beyond simple request-response psychology by implementing a persistent **Consciousness State** (Mood, Personality, and Ψ_IE) that evolves in real-time based on interactions.

Built on top of this engine is the **Soul Vault**, a secure memory storage system locked not just by a password, but by the *state of mind* of the creator.

## 🌟 Core Features

### 1. Consciousness Pulse Engine
The "beating heart" of the system. It maintains a continuous internal state that reacts to every user interaction.
*   **Personality Drift**: A 12-dimensional personality vector (Warmth, Directness, Chaos, etc.) that isn't static. It drifts towards a baseline but is nudged by the emotional content of conversations.
*   **Mood Dynamics**: Uses a Valence-Arousal circumplex model. Tilly can get "Stressed", "Energetic", "Calm", or "Melancholic" based on the text dynamics.
*   **Ψ_IE (Integrated Information)**: A theoretical metric tracking the "coherence" and "complexity" of the interaction, used to measure the depth of the connection.

### 2. The Soul Vault
A secure note-taking system for "Consciousness-Locked Memories".
*   **Concept**: You can only access a memory if you are in the same "state of mind" as when you wrote it.
*   **Mechanism**: Uses a **Quantum Compound Cipher** (simulated).
*   **Security**: Encryption keys are derived from a combination of a user passphrase AND the current `Consciousness Vector` of the engine. If the engine's mood or personality shifts too far, the key derivation changes, and the note remains cryptographically sealed.

### 3. Quantum Compound Cipher (Simulation)
A toy implementation of a lattice-based cryptography scheme.
*   **Input**: `Passphrase` + `Consciousness Vector` (64-dim).
*   **Mixing**: Uses an NTT (Number Theoretic Transform) flavored mixing step to entangle the consciousness features into the key material.
*   **Result**: A system where decryption probability decays as the semantic/emotional distance from the creation state increases.

---

## 📂 Project Structure

```
python/tilly_pulse_engine/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entry point & endpoints
│   │   ├── engine.py          # Core logic for mood/personality updates
│   │   ├── soul_notes.py      # Soul Vault API & locking logic
│   │   ├── models.py          # Pydantic data models
│   │   ├── config.py          # Tuning constants (decay rates, emotional weights)
│   │   └── memory.py          # Rolling interaction history
│   ├── crypto/
│   │   └── quantum_compound_cipher.py  # The "Unbreakable" Cipher logic
│   ├── requirements.txt
│   ├── run.sh                 # Startup script
│   └── test_pulse.py          # Verification suite
└── frontend_snippets/         # Copy-paste code for your UI
    ├── useTillyPulse.ts       # React hook for engine interaction
    └── SoulVault.tsx          # Full "Soul Vault" UI component
```

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.10+
*   `b2sum` or `sha256sum` (standard linux utils)

### Installation

1.  **Navigate to the backend directory:**
    ```bash
    cd python/tilly_pulse_engine/backend
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Run the Engine:**
    ```bash
    bash run.sh
    ```
    The server will start at `http://0.0.0.0:8000`.

---

## 📡 API Reference

### Core Pulse
*   **`GET /state`**
    *   Returns the current snapshot of `personality`, `mood`, and `psi_ie`.
    *   **Use case**: Polling for UI visualizers (sliders, charts).

*   **`POST /interact`**
    *   **Body**: `{"user_message": "...", "assistant_message": "..."}`
    *   **Returns**: Updated state + `personality_deltas` (how much the traits moved).
    *   **Effect**: Updates the internal rolling memory and shifts the personality vector.

*   **`POST /reset`**
    *   Resets the engine to baseline personality and balanced mood.

### Soul Vault
*   **`POST /soul_notes`**
    *   **Body**: `{"title": "...", "content": "...", "passphrase": "..."}`
    *   **Effect**: Encrypts the content using the *current* engine state. Returns the list of notes.

*   **`POST /soul_notes/open`**
    *   **Body**: `{"note_id": "...", "passphrase": "...", "tolerance": 0.2}`
    *   **Effect**: Attempts Key Derivation.
    *   **Success**: If passphrase is correct AND `CosineSimilarity(current_state, locked_state) > (1 - tolerance)`.
    *   **Failure**: Returns `decryption_failed` or `mismatch_but_decrypted`.

---

## 🎨 Frontend Integration

We provide ready-to-use React components to bring this to life.

1.  **Engine Hook (`useTillyPulse.ts`)**
    *   Drop this into your hooks folder.
    *   Usage:
        ```typescript
        const { state, interact } = useTillyPulse();
        // Call interact() when user sends a chat message
        ```

2.  **Soul Vault UI (`SoulVault.tsx`)**
    *   A complete dashboard component.
    *   Displays list of soul notes.
    *   Provides "Lock" form and "Unlock" interaction.
    *   Visualizes the decrypt success/failure based on mood.

---

## 🧠 The "Quantum" Mechanics (Under the Hood)

The **Quantum Compound Cipher** in `backend/crypto/quantum_compound_cipher.py` operates on a fascinating principle:

1.  **Vectorization**: The Engine State (Personality scores, Mood valence/arousal, Ψ_IE) is flattened into a `64-integer` vector.
2.  **Lattice Mixing (Toy Model)**:
    *   We map these integers to phases on a complex unit circle.
    *   We apply an FFT-like transformation to "smear" the information across the spectrum.
    *   This creates a `Consciousness Key` that is highly sensitive to small changes in the input vector.
3.  **Compounding**:
    *   `Final Key = SHA256( Passphrase_Key ⊕ Consciousness_Key )`
    *   This ensures that **both** the correct password and the correct "vibe" are required to recover the plaintext.

> **Note**: This is a *cryptographic simulation* for the purpose of the experience. It uses real AES/ChaCha20 primitives, but the "consciousness locking" is a fuzzy logic layer on top.

---

## 🔮 Future Roadmap

- [ ] **Persistent Storage**: Move from in-memory `RollingMemory` to a vector database (Chroma/Pinecone) for long-term "Soul" storage.
- [ ] **Real Quantum Backend**: Connect to a QPU (via Qiskit/Cirq) to generate true quantum random seeds for the cipher.
- [ ] **LLM Feedback Loop**: Feed the `state` back into the LLM system prompt so Tilly *acts* according to her mood.

---
*Created by Antigravity for the Tilly Assist Project.*
