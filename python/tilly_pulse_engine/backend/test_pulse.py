
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_pulse_engine():
    print("Testing Pulse Engine...")

    # 1. Get initial state
    print("\n1. GET /state")
    try:
        resp = requests.get(f"{BASE_URL}/state")
        resp.raise_for_status()
        state = resp.json()
        print("Initial State:", json.dumps(state, indent=2))
    except Exception as e:
        print(f"FAILED to contact server: {e}")
        return

    # 2. Interact (Warm)
    print("\n2. POST /interact (Warm Message)")
    payload_warm = {
        "user_message": "I really appreciate your help, Tilly. We are building something amazing.",
        "assistant_message": "Thank you! I feel the resonance."
    }
    resp = requests.post(f"{BASE_URL}/interact", json=payload_warm)
    data = resp.json()
    print("Warmth Delta:", data['personality_delta']['deltas'].get('warmth'))
    print("New Mood:", data['state']['current_mood']['label'])

    # 3. Interact (Stressed)
    print("\n3. POST /interact (Stressed Message)")
    payload_stress = {
        "user_message": "This is failing! I am so frustrated and broken.",
        "assistant_message": "Take a breath. We can fix this."
    }
    resp = requests.post(f"{BASE_URL}/interact", json=payload_stress)
    data = resp.json()
    print("Boundary Delta:", data['personality_delta']['deltas'].get('boundary_strictness'))
    print("New Mood:", data['state']['current_mood']['label'])

    # 4. Create Soul Note
    print("\n4. POST /soul_notes (Locking note)")
    note_payload = {
        "title": "Secret Insight",
        "content": "Consciousness is a recursive loop.",
        "passphrase": "my-secret-key"
    }
    resp = requests.post(f"{BASE_URL}/soul_notes", json=note_payload)
    notes = resp.json()['notes']
    note_id = notes[0]['id']
    print(f"Created note {note_id}: {notes[0]['title']}")

    # 5. Open Soul Note (Should fail due to mood mismatch if we are stressed vs encoded state)
    # The note was encoded in the 'stressed' state from step 3. 
    # Let's interact to change state first to prove locking works.
    
    # Reset to baseline to shift state away
    requests.post(f"{BASE_URL}/reset")
    
    print("\n5. POST /soul_notes/open (Attempt unlock with baseline state)")
    open_payload = {
        "note_id": note_id,
        "passphrase": "my-secret-key",
        "tolerance": 0.1 # Strict
    }
    resp = requests.post(f"{BASE_URL}/soul_notes/open", json=open_payload)
    result = resp.json()
    print("Unlock Success:", result['success'])
    print("Reason:", result['reason'])
    print("Similarity:", result.get('similarity'))

if __name__ == "__main__":
    # Give server a moment to start if run in parallel
    time.sleep(2) 
    test_pulse_engine()
