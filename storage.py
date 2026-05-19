"""JSON 持久化层，负责加载和保存本地数据文件。"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from models import Book, BorrowRecord, User

class JsonStorage:
    """基于 JSON 文件的简单存储实现。"""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        """初始化数据目录和文件路径。"""
        self.base_dir = Path(base_dir or Path(__file__).resolve().parent)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.books_file = self.base_dir / "books.json"
        self.users_file = self.base_dir / "users.json"
        self.records_file = self.base_dir / "records.json"
        self._ensure_files()

    def _ensure_files(self) -> None:
        """确保核心数据文件存在。"""
        for path in (self.books_file, self.users_file, self.records_file):
            if not path.exists():
                path.write_text("[]", encoding="utf-8")

    def _read_json(self, path: Path) -> list[dict[str, Any]]:
        """读取 JSON 文件并返回列表数据。"""
        try:
            data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        except (json.JSONDecodeError, OSError):
            data = []
        return data if isinstance(data, list) else []

    def _write_json(self, path: Path, data: list[dict[str, Any]]) -> None:
        """将列表数据写入指定 JSON 文件。"""
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_books(self) -> list[Book]:
        """加载全部图书数据。"""
        return [Book.from_dict(item) for item in self._read_json(self.books_file)]

    def load_users(self) -> list[User]:
        """加载全部用户数据。"""
        return [User.from_dict(item) for item in self._read_json(self.users_file)]

    def load_records(self) -> list[BorrowRecord]:
        """加载全部借阅记录数据。"""
        return [BorrowRecord.from_dict(item) for item in self._read_json(self.records_file)]

    def save_books(self, books: list[Book]) -> None:
        """保存全部图书数据。"""
        self._write_json(self.books_file, [item.to_dict() for item in books])

    def save_users(self, users: list[User]) -> None:
        """保存全部用户数据。"""
        self._write_json(self.users_file, [item.to_dict() for item in users])

    def save_records(self, records: list[BorrowRecord]) -> None:
        """保存全部借阅记录数据。"""
        self._write_json(self.records_file, [item.to_dict() for item in records])

    def load_all(self) -> tuple[list[Book], list[User], list[BorrowRecord]]:
        """一次性加载全部业务数据。"""
        return self.load_books(), self.load_users(), self.load_records()

    def save_all(self, books: list[Book], users: list[User], records: list[BorrowRecord]) -> None:
        """一次性保存全部业务数据。"""
        self.save_books(books)
        self.save_users(users)
        self.save_records(records)

    def clear_all(self) -> None:
        """清空全部业务数据。"""
        self.save_all([], [], [])

    def get_info(self) -> dict[str, str]:
        """返回当前存储配置说明。"""
        return {
            "base_dir": str(self.base_dir),
            "books_file": str(self.books_file),
            "users_file": str(self.users_file),
            "records_file": str(self.records_file),
        }
