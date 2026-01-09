"""Hybrid Cryptography Engine: Modified Caesar Cipher + RSA"""
import os
import hashlib
from typing import Tuple
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import json
import base64


class ModifiedCaesarCipher:
    """Modified Caesar Cipher dengan dynamic shift berdasarkan posisi byte dan salt"""

    def __init__(self, base_shift: int, salt: str):
        self.base_shift = base_shift
        self.salt = salt
        # Generate salt hash untuk dynamic shifting
        self.salt_hash = hashlib.sha256(salt.encode()).digest()

    def _calculate_dynamic_shift(self, position: int) -> int:
        """Calculate dynamic shift berdasarkan posisi byte dan salt"""
        # Kombinasi base shift dengan salt hash pada posisi tertentu
        salt_byte = self.salt_hash[position % len(self.salt_hash)]
        return (self.base_shift + salt_byte + position) % 256

    def encrypt_bytes(self, data: bytes) -> bytes:
        """Encrypt bytes menggunakan modified Caesar dengan dynamic shift"""
        encrypted = bytearray()
        for i, byte in enumerate(data):
            shift = self._calculate_dynamic_shift(i)
            encrypted_byte = (byte + shift) % 256
            encrypted.append(encrypted_byte)
        return bytes(encrypted)

    def decrypt_bytes(self, data: bytes) -> bytes:
        """Decrypt bytes menggunakan modified Caesar dengan dynamic shift"""
        decrypted = bytearray()
        for i, byte in enumerate(data):
            shift = self._calculate_dynamic_shift(i)
            decrypted_byte = (byte - shift) % 256
            decrypted.append(decrypted_byte)
        return bytes(decrypted)


class HybridCryptoEngine:
    """Hybrid Encryption: Modified Caesar (layer 1) + RSA (layer 2)"""

    def __init__(self, rsa_private_key=None, rsa_public_key=None):
        self.rsa_private_key = rsa_private_key
        self.rsa_public_key = rsa_public_key

    def generate_caesar_params(self, file_content: bytes) -> Tuple[int, str]:
        """Generate dynamic Caesar parameters berdasarkan file content"""
        # Base shift dari hash konten file
        content_hash = hashlib.sha256(file_content).hexdigest()
        base_shift = int(content_hash[:4], 16) % 256

        # Salt dari timestamp dan random
        salt = hashlib.sha256(os.urandom(32)).hexdigest()[:16]

        return base_shift, salt

    def encrypt_file(self, file_content: bytes, filename: str) -> Tuple[bytes, dict]:
        """Encrypt file dengan hybrid method"""
        if not self.rsa_public_key:
            raise ValueError("RSA public key not loaded")

        # Step 1: Generate Caesar parameters
        base_shift, salt = self.generate_caesar_params(file_content)

        # Step 2: Encrypt dengan Modified Caesar (Layer 1)
        caesar = ModifiedCaesarCipher(base_shift, salt)
        caesar_encrypted = caesar.encrypt_bytes(file_content)

        # Step 3: Create metadata
        metadata = {
            'filename': filename,
            'base_shift': base_shift,
            'salt': salt,
            'original_size': len(file_content),
            'file_hash': hashlib.sha256(file_content).hexdigest()
        }

        # Step 4: Encrypt metadata dengan RSA (Layer 2)
        metadata_json = json.dumps(metadata).encode()
        encrypted_metadata = self.rsa_public_key.encrypt(
            metadata_json,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Step 5: Encode metadata ke base64 untuk storage
        metadata_encoded = {
            'encrypted_metadata': base64.b64encode(encrypted_metadata).decode('utf-8'),
            'encrypted_size': len(caesar_encrypted)
        }

        return caesar_encrypted, metadata_encoded

    def decrypt_file(self, encrypted_content: bytes, metadata_encoded: dict) -> Tuple[bytes, str]:
        """Decrypt file dengan hybrid method"""
        if not self.rsa_private_key:
            raise ValueError("RSA private key not loaded")

        # Step 1: Decrypt metadata dengan RSA (Layer 2)
        encrypted_metadata = base64.b64decode(metadata_encoded['encrypted_metadata'])
        metadata_json = self.rsa_private_key.decrypt(
            encrypted_metadata,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        metadata = json.loads(metadata_json.decode())

        # Step 2: Decrypt dengan Modified Caesar (Layer 1)
        caesar = ModifiedCaesarCipher(metadata['base_shift'], metadata['salt'])
        decrypted_content = caesar.decrypt_bytes(encrypted_content)

        # Step 3: Verify integrity
        content_hash = hashlib.sha256(decrypted_content).hexdigest()
        if content_hash != metadata['file_hash']:
            raise ValueError("File integrity check failed! File may be corrupted.")

        return decrypted_content, metadata['filename']
