from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from models import Book, BorrowRecord, User

class JsonStorage:
    def __init__(self, base_dir: str | Path | None = None) -> None:
        self.base_dir = Path(base_dir or Path(__file__).resolve().parent)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.books_file = self.base_dir / "books.json"
        self.users_file = self.base_dir / "users.json"
        self.records_file = self.base_dir / "records.json"
        self._ensure_files()

    def _ensure_files(self) -> None:
        for path in (self.books_file, self.users_file, self.records_file):
            if not path.exists():
                path.write_text("[]", encoding="utf-8")

    def _read_json(self, path: Path) -> list[dict[str, Any]]:
        try:
            data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        except (json.JSONDecodeError, OSError):
            data = []
        return data if isinstance(data, list) else []

    def _write_json(self, path: Path, data: list[dict[str, Any]]) -> None:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_books(self) -> list[Book]:
        return [Book.from_dict(item) for item in self._read_json(self.books_file)]

    def load_users(self) -> list[User]:
        return [User.from_dict(item) for item in self._read_json(self.users_file)]

    def load_records(self) -> list[BorrowRecord]:
        return [BorrowRecord.from_dict(item) for item in self._read_json(self.records_file)]

    def save_books(self, books: list[Book]) -> None:
        self._write_json(self.books_file, [item.to_dict() for item in books])

    def save_users(self, users: list[User]) -> None:
        self._write_json(self.users_file, [item.to_dict() for item in users])

    def save_records(self, records: list[BorrowRecord]) -> None:
        self._write_json(self.records_file, [item.to_dict() for item in records])

    def load_all(self) -> tuple[list[Book], list[User], list[BorrowRecord]]:
        return self.load_books(), self.load_users(), self.load_records()

    def save_all(self, books: list[Book], users: list[User], records: list[BorrowRecord]) -> None:
        self.save_books(books)
        self.save_users(users)
        self.save_records(records)

    def clear_all(self) -> None:
        self.save_all([], [], [])

    def get_info(self) -> dict[str, str]:
        return {
            "base_dir": str(self.base_dir),
            "books_file": str(self.books_file),
            "users_file": str(self.users_file),
            "records_file": str(self.records_file),
        }
