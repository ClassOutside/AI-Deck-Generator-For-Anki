import base64
import os
from typing import Optional, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionService:
    def __init__(self, iterations: int = 100_000):
        self.iterations = iterations
        self.backend = default_backend()

    def derive_key(self, pin: str, salt: bytes) -> bytes:
        """
        Derives a symmetric key from the PIN and salt using PBKDF2.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.iterations,
            backend=self.backend,
        )
        return kdf.derive(pin.encode())

    def encrypt(self, data: str, key: bytes) -> Tuple[bytes, bytes]:
        """
        Encrypts the data string using AES-CBC with PKCS7 padding.
        Returns (iv, encrypted_bytes)
        """
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data.encode()) + padder.finalize()

        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return iv, encrypted

    def decrypt(self, pin: str, encrypted_api_key_b64: str, salt_b64: str, iv_b64: str) -> Optional[str]:
        """
        Decrypts the encrypted API key given the PIN, encrypted data, salt, and IV (all base64 encoded).
        Returns decrypted string or None on failure.
        """
        try:
            salt = base64.b64decode(salt_b64)
            iv = base64.b64decode(iv_b64)
            ciphertext = base64.b64decode(encrypted_api_key_b64)
        except Exception as e:
            print(f"[Decrypt] Base64 decoding error: {e}")
            return None

        try:
            key = self.derive_key(pin, salt)
        except Exception as e:
            print(f"[Decrypt] Key derivation error: {e}")
            return None

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
        decryptor = cipher.decryptor()

        try:
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        except Exception as e:
            print(f"[Decrypt] Decryption error: {e}")
            return None

        try:
            unpadder = padding.PKCS7(128).unpadder()
            plaintext_bytes = unpadder.update(padded_plaintext) + unpadder.finalize()
            return plaintext_bytes.decode("utf-8")
        except Exception as e:
            print(f"[Decrypt] Unpadding or decoding error: {e}")
            return None
