import json
from pathlib import Path

class SessionManager:
    def __init__(self, storage_dir: Path):
        self.session_file = storage_dir / "session.json"
        self.users_dir = storage_dir / "users"
        self.users_dir.mkdir(parents=True, exist_ok=True)
        
        # Load session atau buat default
        self.current_user = self._load_session()

    def _load_session(self):
        if self.session_file.exists():
            with open(self.session_file, 'r') as f:
                data = json.load(f)
                return data.get("current_user", "default")
        return "default"

    def login(self, username: str):
        """Ganti user aktif"""
        with open(self.session_file, 'w') as f:
            json.dump({"current_user": username}, f)
        self.current_user = username

    def get_user_key_dir(self) -> Path:
        """Dapatkan folder kunci untuk user yang sedang login"""
        user_path = self.users_dir / self.current_user / "keys"
        user_path.mkdir(parents=True, exist_ok=True)
        return user_path

    def get_current_user(self):
        return self.current_user

    def list_users(self):
        """List semua folder user yang ada"""
        return [p.name for p in self.users_dir.iterdir() if p.is_dir()]