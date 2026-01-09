"""File Storage Manager"""
import json
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone
import uuid


class FileManager:
    """Manage encrypted file storage"""

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = storage_dir / "index.json"
        self._load_index()

    def _load_index(self):
        """Load file index from disk"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {}
            self._save_index()

    def _save_index(self):
        """Save file index to disk"""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def save_encrypted_file(self, encrypted_content: bytes, metadata: dict, original_filename: str) -> str:
        """Save encrypted file and metadata"""
        # Generate unique file ID
        file_id = str(uuid.uuid4())[:8]

        # Create file paths
        content_path = self.storage_dir / f"{file_id}.enc"
        meta_path = self.storage_dir / f"{file_id}.meta"

        # Save encrypted content
        content_path.write_bytes(encrypted_content)

        # Save metadata
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Update index
        self.index[file_id] = {
            'original_filename': original_filename,
            'encrypted_filename': f"{file_id}.enc",
            'metadata_filename': f"{file_id}.meta",
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'size': len(encrypted_content)
        }
        self._save_index()

        return file_id

    def load_encrypted_file(self, file_id: str) -> tuple:
        """Load encrypted file and metadata"""
        if file_id not in self.index:
            raise ValueError(f"File ID '{file_id}' not found")

        content_path = self.storage_dir / f"{file_id}.enc"
        meta_path = self.storage_dir / f"{file_id}.meta"

        if not content_path.exists() or not meta_path.exists():
            raise FileNotFoundError(f"Encrypted file or metadata not found for ID '{file_id}'")

        # Load encrypted content
        encrypted_content = content_path.read_bytes()

        # Load metadata
        with open(meta_path, 'r') as f:
            metadata = json.load(f)

        return encrypted_content, metadata

    def list_files(self) -> List[dict]:
        """List all encrypted files"""
        files = []
        for file_id, info in self.index.items():
            files.append({
                'file_id': file_id,
                **info
            })
        return sorted(files, key=lambda x: x['timestamp'], reverse=True)

    def delete_file(self, file_id: str) -> bool:
        """Delete encrypted file and metadata"""
        if file_id not in self.index:
            return False

        content_path = self.storage_dir / f"{file_id}.enc"
        meta_path = self.storage_dir / f"{file_id}.meta"

        # Delete files
        if content_path.exists():
            content_path.unlink()
        if meta_path.exists():
            meta_path.unlink()

        # Remove from index
        del self.index[file_id]
        self._save_index()

        return True

    def get_file_info(self, file_id: str) -> Optional[dict]:
        """Get information about a specific file"""
        if file_id not in self.index:
            return None

        return {
            'file_id': file_id,
            **self.index[file_id]
        }

    def get_storage_stats(self) -> dict:
        """Get storage statistics"""
        total_files = len(self.index)
        total_size = sum(info['size'] for info in self.index.values())

        return {
            'total_files': total_files,
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
