"""领域模型定义，包括图书、用户和借阅记录。"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

@dataclass
class Book:  # pylint: disable=too-many-instance-attributes
    """图书实体。"""

    book_id: str
    title: str
    author: str
    isbn: str
    category: str = ""
    publisher: str = ""
    publish_year: int = 0
    total_count: int = 0
    available_count: int = 0
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """将图书对象转换为字典。"""
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "category": self.category,
            "publisher": self.publisher,
            "publish_year": self.publish_year,
            "total_count": self.total_count,
            "available_count": self.available_count,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Book":
        """从字典创建图书对象。"""
        return cls(
            book_id=str(data.get("book_id", "")),
            title=str(data.get("title", "")),
            author=str(data.get("author", "")),
            isbn=str(data.get("isbn", "")),
            category=str(data.get("category", "")),
            publisher=str(data.get("publisher", "")),
            publish_year=int(data.get("publish_year", 0) or 0),
            total_count=int(data.get("total_count", 0) or 0),
            available_count=int(data.get("available_count", 0) or 0),
            description=str(data.get("description", "")),
        )

    def short_text(self) -> str:
        """返回用于简要展示的图书文本。"""
        return (
            f"[{self.book_id}] {self.title} / {self.author} / ISBN:{self.isbn} / "
            f"库存:{self.available_count}/{self.total_count}"
        )

@dataclass
class User:  # pylint: disable=too-many-instance-attributes
    """用户实体。"""

    user_id: str
    name: str
    phone: str
    email: str
    user_type: str = "普通用户"
    department: str = ""
    register_date: str = field(default_factory=lambda: datetime.now().strftime(DATE_FORMAT))
    status: str = "正常"

    def to_dict(self) -> dict[str, Any]:
        """将用户对象转换为字典。"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "user_type": self.user_type,
            "department": self.department,
            "register_date": self.register_date,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User":
        """从字典创建用户对象。"""
        return cls(
            user_id=str(data.get("user_id", "")),
            name=str(data.get("name", "")),
            phone=str(data.get("phone", "")),
            email=str(data.get("email", "")),
            user_type=str(data.get("user_type", "普通用户")),
            department=str(data.get("department", "")),
            register_date=str(data.get("register_date", datetime.now().strftime(DATE_FORMAT))),
            status=str(data.get("status", "正常")),
        )

    def short_text(self) -> str:
        """返回用于简要展示的用户文本。"""
        return (
            f"[{self.user_id}] {self.name} / {self.user_type} / "
            f"电话:{self.phone} / 状态:{self.status}"
        )

@dataclass
class BorrowRecord:  # pylint: disable=too-many-instance-attributes
    """借阅记录实体。"""

    record_id: str
    user_id: str
    user_name: str
    book_id: str
    book_title: str
    isbn: str
    borrow_date: str
    due_date: str
    return_date: str = ""
    returned: bool = False
    overdue_days: int = 0
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        """将借阅记录对象转换为字典。"""
        return {
            "record_id": self.record_id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "book_id": self.book_id,
            "book_title": self.book_title,
            "isbn": self.isbn,
            "borrow_date": self.borrow_date,
            "due_date": self.due_date,
            "return_date": self.return_date,
            "returned": self.returned,
            "overdue_days": self.overdue_days,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BorrowRecord":
        """从字典创建借阅记录对象。"""
        return cls(
            record_id=str(data.get("record_id", "")),
            user_id=str(data.get("user_id", "")),
            user_name=str(data.get("user_name", "")),
            book_id=str(data.get("book_id", "")),
            book_title=str(data.get("book_title", "")),
            isbn=str(data.get("isbn", "")),
            borrow_date=str(data.get("borrow_date", "")),
            due_date=str(data.get("due_date", "")),
            return_date=str(data.get("return_date", "")),
            returned=bool(data.get("returned", False)),
            overdue_days=int(data.get("overdue_days", 0) or 0),
            note=str(data.get("note", "")),
        )

    def is_overdue(self, now_text: str | None = None) -> bool:
        """判断记录在给定日期下是否逾期。"""
        if self.returned:
            return self.overdue_days > 0
        if not self.due_date:
            return False
        now_value = datetime.now()
        if now_text:
            try:
                now_value = datetime.strptime(now_text, DATE_FORMAT)
            except ValueError:
                now_value = datetime.now()
        due_value = datetime.strptime(self.due_date, DATE_FORMAT)
        return now_value.date() > due_value.date()

    def calculate_overdue_days(self, now_text: str | None = None) -> int:
        """计算记录的逾期天数。"""
        if not self.due_date:
            return 0
        if self.returned and self.return_date:
            end_text = self.return_date
        else:
            end_text = now_text or datetime.now().strftime(DATE_FORMAT)
        try:
            due_value = datetime.strptime(self.due_date, DATE_FORMAT)
            end_value = datetime.strptime(end_text, DATE_FORMAT)
        except ValueError:
            return 0
        days = (end_value.date() - due_value.date()).days
        return days if days > 0 else 0

    def short_text(self) -> str:
        """返回用于简要展示的借阅记录文本。"""
        state = "已归还" if self.returned else "未归还"
        return (
            f"[{self.record_id}] 用户:{self.user_name} 图书:{self.book_title} "
            f"借出:{self.borrow_date} 到期:{self.due_date} 状态:{state}"
        )
