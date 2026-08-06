import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile


class Storage:

    def __init__(
        self,
        root: str = "uploads",
    ):
        self.root = Path(root)
        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save(
        self,
        file: UploadFile,
        folder: str,
    ) -> dict:

        directory = self.root / folder
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        extension = Path(file.filename).suffix

        filename = f"{uuid.uuid4()}{extension}"

        path = directory / filename

        with path.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        return {
            "filename": filename,
            "original_name": file.filename,
            "path": str(path),
            "size": path.stat().st_size,
            "content_type": (
                file.content_type
                or "application/octet-stream"
            ),
        }

    def delete(
        self,
        path: str,
    ) -> bool:

        file = Path(path)

        if file.exists():
            file.unlink()
            return True

        return False

    def exists(
        self,
        path: str,
    ) -> bool:

        return Path(path).exists()

    def get_path(
        self,
        path: str,
    ) -> Path:

        return Path(path)


storage = Storage()
