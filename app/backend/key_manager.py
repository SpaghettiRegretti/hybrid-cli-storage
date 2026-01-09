"""RSA Key Management"""
import os
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from typing import Tuple, Optional


class KeyManager:
    """Manage RSA key generation, saving, and loading"""

    def __init__(self, keys_dir: Path):
        self.keys_dir = keys_dir
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        self.private_key_path = self.keys_dir / "private_key.pem"
        self.public_key_path = self.keys_dir / "public_key.pem"

    def generate_key_pair(self, key_size: int = 2048) -> Tuple:
        """Generate RSA key pair"""
        print(f"🔑 Generating RSA {key_size}-bit key pair...")

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        # Save keys
        self._save_private_key(private_key)
        self._save_public_key(public_key)

        print(f"✅ Keys generated and saved to {self.keys_dir}")
        return private_key, public_key

    def _save_private_key(self, private_key):
        """Save private key to file"""
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        self.private_key_path.write_bytes(pem)
        os.chmod(self.private_key_path, 0o600)  # Protect private key

    def _save_public_key(self, public_key):
        """Save public key to file"""
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.public_key_path.write_bytes(pem)

    def load_keys(self) -> Tuple:
        """Load existing RSA key pair"""
        if not self.private_key_path.exists() or not self.public_key_path.exists():
            return None, None

        private_key = serialization.load_pem_private_key(
            self.private_key_path.read_bytes(),
            password=None,
            backend=default_backend()
        )

        public_key = serialization.load_pem_public_key(
            self.public_key_path.read_bytes(),
            backend=default_backend()
        )

        return private_key, public_key

    def keys_exist(self) -> bool:
        """Check if keys already exist"""
        return self.private_key_path.exists() and self.public_key_path.exists()

    def get_key_info(self) -> Optional[dict]:
        """Get information about current keys"""
        if not self.keys_exist():
            return None

        private_key, public_key = self.load_keys()
        key_size = private_key.key_size

        return {
            'key_size': key_size,
            'private_key_path': str(self.private_key_path),
            'public_key_path': str(self.public_key_path)
        }
