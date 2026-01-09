"""
quantum_compound_cipher.py

Toy implementation of "quantum unbreakable compound cipher":

- Passphrase-derived base key  (classical KDF-ish step)
- Consciousness-vector-derived key using NTT/QFT-flavored mixing
- Compound those into a single 32-byte key
- Encrypt/decrypt using ChaCha20-Poly1305 (AEAD)

⚠ DEMO ONLY. Not production crypto.
"""

import os
import json
import base64
import hashlib
from typing import Sequence, Tuple

import numpy as np
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

# ---- Parameters (lifted/adapted from your lattice spec) ----
# n, q chosen similar to your NTT lattice description
N = 256          # lattice dimension (reduced from 512 for demo)
Q = 12289        # prime modulus, q ≡ 1 mod 2n in your patent text


# --------- Utility helpers ---------

def b64e(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


def b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))


# --------- Step 1: Passphrase → base key ---------

def passphrase_to_base_key(passphrase: str, salt: bytes) -> bytes:
    """
    Very simple KDF-ish step:
    SHA3-256(passphrase || salt) → 32 bytes.
    In a real system, swap for Argon2id or scrypt.
    """
    h = hashlib.sha3_256()
    h.update(passphrase.encode("utf-8"))
    h.update(salt)
    return h.digest()  # 32 bytes


# --------- Step 2: Consciousness vector → mixed key material ---------

def normalize_consciousness_vector(vec: Sequence[int]) -> np.ndarray:
    """
    Take an arbitrary sequence of ints (e.g. EEG-derived features),
    normalize mod Q, pad/trim to length N.
    """
    arr = np.array([int(x) % Q for x in vec], dtype=np.int64)
    if len(arr) < N:
        # repeat to fill
        reps = int(np.ceil(N / len(arr))) if len(arr) > 0 else 1
        arr = np.tile(arr, reps)[:N]
    elif len(arr) > N:
        arr = arr[:N]
    return arr


def ntt_like_mix(vec: np.ndarray) -> np.ndarray:
    """
    QFT/NTT-flavored mixing:
    - Map coefficients into complex phases on unit circle
    - Apply FFT (classical)
    - Map back to integers mod Q

    This is inspired by your NTT/QFT combo, but not a
    mathematically strict NTT implementation.
    """
    # map ints -> complex points on unit circle
    angles = 2 * np.pi * vec / Q
    complex_vec = np.exp(1j * angles)

    # FFT "entangling" step
    fft_res = np.fft.fft(complex_vec)

    # Map back to integer coefficients mod Q (using real part)
    mixed = np.round(np.real(fft_res) * (Q / len(vec))).astype(np.int64) % Q
    return mixed


def consciousness_to_key_material(
    features: Sequence[int],
    salt: bytes
) -> bytes:
    """
    Consciousness feature vector → mixed bytes → hash.
    """
    vec = normalize_consciousness_vector(features)
    mixed = ntt_like_mix(vec)

    # serialize as bytes (big-endian 16-bit integers)
    buf = mixed.astype(">u2").tobytes()

    # hash with salt to get 32 bytes of key material
    h = hashlib.sha3_256()
    h.update(salt)
    h.update(buf)
    return h.digest()


# --------- Step 3: Compound key construction ---------

def derive_compound_key(
    passphrase: str,
    consciousness_features: Sequence[int],
    master_salt: bytes
) -> Tuple[bytes, bytes, bytes]:
    """
    Returns:
        (compound_key_32, pass_salt, conc_salt)
    so you can store salts alongside ciphertext.

    We split master_salt deterministically into two salts.
    """
    # Expand master salt → two independent salts
    salt_hash = hashlib.sha3_256(master_salt).digest()
    pass_salt = salt_hash[:16]
    conc_salt = salt_hash[16:]

    base_key = passphrase_to_base_key(passphrase, pass_salt)
    conc_key_material = consciousness_to_key_material(
        consciousness_features, conc_salt
    )

    # XOR combine, then hash once more for diffusion
    combined = bytes(a ^ b for a, b in zip(base_key, conc_key_material))

    final = hashlib.sha3_256(combined).digest()  # 32 bytes
    return final, pass_salt, conc_salt


# --------- Step 4: AEAD encrypt / decrypt ---------

class QuantumCompoundCipher:
    """
    High-level encrypt/decrypt API.
    """

    def encrypt(
        self,
        plaintext: bytes,
        passphrase: str,
        consciousness_features: Sequence[int],
    ) -> str:
        """
        Returns a JSON string containing:
            {
              "salt": "...",
              "nonce": "...",
              "ciphertext": "...",
              "aad": "..."
            }
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode("utf-8")

        master_salt = os.urandom(16)
        key, pass_salt, conc_salt = derive_compound_key(
            passphrase, consciousness_features, master_salt
        )

        aead = ChaCha20Poly1305(key)
        nonce = os.urandom(12)

        # associated data includes the salts so tampering is detected
        aad = json.dumps(
            {
                "pass_salt": b64e(pass_salt),
                "conc_salt": b64e(conc_salt),
            }
        ).encode("utf-8")

        ct = aead.encrypt(nonce, plaintext, aad)

        blob = {
            "salt": b64e(master_salt),
            "nonce": b64e(nonce),
            "ciphertext": b64e(ct),
            "aad": b64e(aad),
        }
        return json.dumps(blob)

    def decrypt(
        self,
        blob_json: str,
        passphrase: str,
        consciousness_features: Sequence[int],
    ) -> bytes:
        """
        Inverse of encrypt. Raises if authentication fails.
        """
        blob = json.loads(blob_json)
        master_salt = b64d(blob["salt"])
        nonce = b64d(blob["nonce"])
        ct = b64d(blob["ciphertext"])
        aad = b64d(blob["aad"])

        # Re-derive key
        key, _pass_salt, _conc_salt = derive_compound_key(
            passphrase, consciousness_features, master_salt
        )

        aead = ChaCha20Poly1305(key)
        plaintext = aead.decrypt(nonce, ct, aad)
        return plaintext
