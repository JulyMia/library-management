from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from models import Book, BorrowRecord, User
from storage import JsonStorage
from utils import calc_due_date, now_date_text, safe_lower


class LibraryService:
    def __init__(self, storage: JsonStorage | None = None) -> None:
        self.storage = storage or JsonStorage()
        self.books, self.users, self.records = self.storage.load_all()
        self.default_borrow_days = 30

    def reload(self) -> None:
        self.books, self.users, self.records = self.storage.load_all()

    def save_all(self) -> None:
        self.storage.save_all(self.books, self.users, self.records)

    def _make_id(self, prefix: str) -> str:
        return f"{prefix}-{uuid4().hex[:8]}"

    def _find_book_obj(self, book_id: str) -> Book | None:
        for item in self.books:
            if item.book_id == book_id:
                return item
        return None

    def _find_user_obj(self, user_id: str) -> User | None:
        for item in self.users:
            if item.user_id == user_id:
                return item
        return None

    def _find_record_obj(self, record_id: str) -> BorrowRecord | None:
        for item in self.records:
            if item.record_id == record_id:
                return item
        return None

    def _book_exists(self, isbn: str, exclude_book_id: str | None = None) -> bool:
        return any(
            item.isbn == isbn and item.book_id != exclude_book_id
            for item in self.books
        )

    def _phone_exists(self, phone: str, exclude_user_id: str | None = None) -> bool:
        return any(
            item.phone == phone and item.user_id != exclude_user_id
            for item in self.users
        )

    def _normalize_available_count(self, available_count: int, total_count: int) -> int:
        return min(max(0, available_count), total_count)

    def _save_books(self) -> None:
        self.storage.save_books(self.books)

    def _save_users(self) -> None:
        self.storage.save_users(self.users)

    def _save_books_and_records(self) -> None:
        self.storage.save_books(self.books)
        self.storage.save_records(self.records)

    def _get_active_borrow_count(self, user_id: str) -> int:
        return sum(
            1 for item in self.records if item.user_id == user_id and not item.returned
        )

    def _has_active_borrow(self, user_id: str, book_id: str) -> bool:
        return any(
            item.user_id == user_id and item.book_id == book_id and not item.returned
            for item in self.records
        )

    def _create_borrow_record(
        self,
        user: User,
        book: Book,
        note: str,
    ) -> tuple[BorrowRecord, str]:
        start_date = now_date_text()
        due_date = calc_due_date(start_date, self.default_borrow_days)
        record = BorrowRecord(
            record_id=self._make_id("R"),
            user_id=user.user_id,
            user_name=user.name,
            book_id=book.book_id,
            book_title=book.title,
            isbn=book.isbn,
            borrow_date=start_date,
            due_date=due_date,
            note=note,
        )
        return record, due_date

    def _get_book_or_error(self, book_id: str) -> tuple[Book | None, str | None]:
        book = self._find_book_obj(book_id)
        if book is None:
            return None, "未找到图书。"
        return book, None

    def _get_user_or_error(self, user_id: str) -> tuple[User | None, str | None]:
        user = self._find_user_obj(user_id)
        if user is None:
            return None, "未找到用户。"
        return user, None

    def _get_record_or_error(
        self,
        record_id: str,
    ) -> tuple[BorrowRecord | None, str | None]:
        record = self._find_record_obj(record_id)
        if record is None:
            return None, "借阅记录不存在。"
        return record, None

    def _can_delete_book(self, book_id: str) -> bool:
        return not any(
            record.book_id == book_id and not record.returned for record in self.records
        )

    def _can_delete_user(self, user_id: str) -> bool:
        return not any(
            record.user_id == user_id and not record.returned for record in self.records
        )

    def _validate_user_for_borrow(self, user: User) -> tuple[bool, str]:
        if user.status != "正常":
            return False, "用户状态异常，不能借书。"
        if self._get_active_borrow_count(user.user_id) >= 10:
            return False, "该用户当前借阅数量已达上限。"
        return True, ""

    def _validate_book_for_borrow(self, book: Book) -> tuple[bool, str]:
        if book.available_count <= 0:
            return False, "图书库存不足。"
        return True, ""

    def _validate_borrow_request(self, user: User, book: Book) -> tuple[bool, str]:
        is_valid, message = self._validate_user_for_borrow(user)
        if not is_valid:
            return False, message
        is_valid, message = self._validate_book_for_borrow(book)
        if not is_valid:
            return False, message
        if self._has_active_borrow(user.user_id, book.book_id):
            return False, "该用户已经借阅过这本书且尚未归还。"
        return True, ""

    def _apply_book_updates(self, book: Book, info: dict[str, Any]) -> tuple[bool, str]:
        if "title" in info and str(info["title"]).strip():
            book.title = str(info["title"]).strip()
        if "author" in info and str(info["author"]).strip():
            book.author = str(info["author"]).strip()
        if "isbn" in info and str(info["isbn"]).strip():
            new_isbn = str(info["isbn"]).strip()
            if self._book_exists(new_isbn, exclude_book_id=book.book_id):
                return False, "ISBN 与其他图书重复。"
            book.isbn = new_isbn
        if "category" in info:
            book.category = str(info["category"]).strip()
        if "publisher" in info:
            book.publisher = str(info["publisher"]).strip()
        if "publish_year" in info and str(info["publish_year"]).strip():
            book.publish_year = int(info["publish_year"])
        if "description" in info:
            book.description = str(info["description"]).strip()
        if "total_count" in info and str(info["total_count"]).strip():
            total = int(info["total_count"])
            diff = total - book.total_count
            book.total_count = total
            book.available_count = self._normalize_available_count(
                book.available_count + diff,
                book.total_count,
            )
        if "available_count" in info and str(info["available_count"]).strip():
            requested_count = int(info["available_count"])
            book.available_count = self._normalize_available_count(
                requested_count,
                book.total_count,
            )
        return True, ""

    def _apply_user_updates(self, user: User, info: dict[str, Any]) -> tuple[bool, str]:
        if "name" in info and str(info["name"]).strip():
            user.name = str(info["name"]).strip()
        if "phone" in info and str(info["phone"]).strip():
            phone = str(info["phone"]).strip()
            if self._phone_exists(phone, exclude_user_id=user.user_id):
                return False, "手机号与其他用户重复。"
            user.phone = phone
        if "email" in info:
            user.email = str(info["email"]).strip()
        if "user_type" in info and str(info["user_type"]).strip():
            user.user_type = str(info["user_type"]).strip()
        if "department" in info:
            user.department = str(info["department"]).strip()
        if "status" in info and str(info["status"]).strip():
            user.status = str(info["status"]).strip()
        return True, ""

    def add_book(self, info: dict[str, Any]) -> tuple[bool, str]:
        book_id = info.get("book_id") or self._make_id("B")
        title = str(info.get("title", "")).strip()
        author = str(info.get("author", "")).strip()
        isbn = str(info.get("isbn", "")).strip()
        total_count = int(info.get("total_count", 0) or 0)
        available_count = int(info.get("available_count", total_count) or total_count)

        if not title or not author or not isbn:
            return False, "书名、作者、ISBN 不能为空。"
        for item in self.books:
            if item.book_id == book_id:
                return False, "图书编号已存在。"
        if self._book_exists(isbn):
            return False, "ISBN 已存在，本版本只做简单限制。"

        new_book = Book(
            book_id=book_id,
            title=title,
            author=author,
            isbn=isbn,
            category=str(info.get("category", "")),
            publisher=str(info.get("publisher", "")),
            publish_year=int(info.get("publish_year", 0) or 0),
            total_count=total_count,
            available_count=available_count,
            description=str(info.get("description", "")),
        )
        self.books.append(new_book)
        self._save_books()
        return True, f"图书添加成功，编号为 {new_book.book_id}。"

    def delete_book(self, book_id: str) -> tuple[bool, str]:
        book_to_delete, error_message = self._get_book_or_error(book_id)
        if error_message:
            return False, error_message
        if not self._can_delete_book(book_id):
            return False, "该图书存在未归还记录，不能删除。"
        assert book_to_delete is not None
        self.books.remove(book_to_delete)
        self._save_books()
        return True, "图书删除成功。"

    def update_book(self, book_id: str, info: dict[str, Any]) -> tuple[bool, str]:
        book_to_update, error_message = self._get_book_or_error(book_id)
        if error_message:
            return False, error_message
        assert book_to_update is not None
        is_updated, message = self._apply_book_updates(book_to_update, info)
        if not is_updated:
            return False, message
        self._save_books()
        return True, "图书信息修改成功。"

    def search_books(self, keyword: str = "", field_name: str = "all") -> list[Book]:
        if not keyword:
            return list(self.books)
        temp = safe_lower(keyword)
        result = []
        for item in self.books:
            if field_name == "title" and temp in safe_lower(item.title):
                result.append(item)
            elif field_name == "author" and temp in safe_lower(item.author):
                result.append(item)
            elif field_name == "isbn" and temp in safe_lower(item.isbn):
                result.append(item)
            elif field_name == "all":
                if (
                    temp in safe_lower(item.title)
                    or temp in safe_lower(item.author)
                    or temp in safe_lower(item.isbn)
                ):
                    result.append(item)
        return result

    def list_books(self) -> list[Book]:
        return list(self.books)

    def add_user(self, info: dict[str, Any]) -> tuple[bool, str]:
        user_id = info.get("user_id") or self._make_id("U")
        name = str(info.get("name", "")).strip()
        phone = str(info.get("phone", "")).strip()
        email = str(info.get("email", "")).strip()
        user_type = str(info.get("user_type", "普通用户")).strip() or "普通用户"

        if not name:
            return False, "用户名不能为空。"
        for item in self.users:
            if item.user_id == user_id:
                return False, "用户编号已存在。"
        if phone and self._phone_exists(phone):
            return False, "手机号已存在，本版本只做简单处理。"

        new_user = User(
            user_id=user_id,
            name=name,
            phone=phone,
            email=email,
            user_type=user_type,
            department=str(info.get("department", "")),
            status=str(info.get("status", "正常")),
        )
        self.users.append(new_user)
        self._save_users()
        return True, f"用户添加成功，编号为 {new_user.user_id}。"

    def delete_user(self, user_id: str) -> tuple[bool, str]:
        user_to_delete, error_message = self._get_user_or_error(user_id)
        if error_message:
            return False, error_message
        if not self._can_delete_user(user_id):
            return False, "该用户存在未归还图书，不能删除。"
        assert user_to_delete is not None
        self.users.remove(user_to_delete)
        self._save_users()
        return True, "用户删除成功。"

    def update_user(self, user_id: str, info: dict[str, Any]) -> tuple[bool, str]:
        user_to_update, error_message = self._get_user_or_error(user_id)
        if error_message:
            return False, error_message
        assert user_to_update is not None
        is_updated, message = self._apply_user_updates(user_to_update, info)
        if not is_updated:
            return False, message
        self._save_users()
        return True, "用户信息修改成功。"

    def search_users(self, keyword: str = "") -> list[User]:
        if not keyword:
            return list(self.users)
        temp = safe_lower(keyword)
        result = []
        for item in self.users:
            if (
                temp in safe_lower(item.user_id)
                or temp in safe_lower(item.name)
                or temp in safe_lower(item.phone)
                or temp in safe_lower(item.email)
                or temp in safe_lower(item.user_type)
            ):
                result.append(item)
        return result

    def list_users(self) -> list[User]:
        return list(self.users)

    def borrow_book(self, user_id: str, book_id: str, note: str = "") -> tuple[bool, str]:
        user = self._find_user_obj(user_id)
        if user is None:
            return False, "用户不存在。"
        book = self._find_book_obj(book_id)
        if book is None:
            return False, "图书不存在。"
        is_valid, message = self._validate_borrow_request(user, book)
        if not is_valid:
            return False, message
        record, due_date = self._create_borrow_record(user, book, note)
        book.available_count -= 1
        self.records.append(record)
        self._save_books_and_records()
        return True, f"借书成功，应还日期为 {due_date}。"

    def return_book(self, record_id: str) -> tuple[bool, str]:
        record_to_return, error_message = self._get_record_or_error(record_id)
        if error_message:
            return False, error_message
        if record_to_return.returned:
            return False, "该记录已归还。"

        book, error_message = self._get_book_or_error(record_to_return.book_id)
        if error_message:
            return False, "图书记录异常，图书已不存在。"
        assert record_to_return is not None
        assert book is not None
        record_to_return.returned = True
        record_to_return.return_date = now_date_text()
        record_to_return.overdue_days = record_to_return.calculate_overdue_days()
        book.available_count = self._normalize_available_count(
            book.available_count + 1,
            book.total_count,
        )
        self._save_books_and_records()
        if record_to_return.overdue_days > 0:
            return True, f"还书成功，已逾期 {record_to_return.overdue_days} 天。"
        return True, "还书成功，未逾期。"

    def get_user_records(self, user_id: str) -> list[BorrowRecord]:
        result = []
        for item in self.records:
            if item.user_id == user_id:
                if not item.returned:
                    item.overdue_days = item.calculate_overdue_days()
                result.append(item)
        return result

    def get_unreturned_records(self) -> list[BorrowRecord]:
        result = []
        for item in self.records:
            if not item.returned:
                item.overdue_days = item.calculate_overdue_days()
                result.append(item)
        return result

    def get_overdue_records(self) -> list[BorrowRecord]:
        result = []
        for item in self.records:
            if item.returned:
                if item.overdue_days > 0:
                    result.append(item)
            else:
                days = item.calculate_overdue_days()
                item.overdue_days = days
                if days > 0:
                    result.append(item)
        self.storage.save_records(self.records)
        return result

    def set_default_borrow_days(self, days: int) -> tuple[bool, str]:
        if days <= 0:
            return False, "借阅天数必须大于 0。"
        self.default_borrow_days = days
        return True, f"默认借阅天数已设置为 {days} 天。"

    def get_statistics(self) -> dict[str, Any]:
        total_books = len(self.books)
        total_stock = 0
        available_stock = 0
        borrowed_count = 0
        overdue_count = 0
        user_count = len(self.users)
        admin_count = 0
        teacher_count = 0
        normal_count = 0

        for book in self.books:
            total_stock += book.total_count
            available_stock += book.available_count
        for record in self.records:
            if not record.returned:
                borrowed_count += 1
                if record.calculate_overdue_days() > 0:
                    overdue_count += 1
        for user in self.users:
            if user.user_type == "管理员":
                admin_count += 1
            elif user.user_type == "教师用户":
                teacher_count += 1
            else:
                normal_count += 1

        return {
            "图书种类数": total_books,
            "图书总库存": total_stock,
            "当前可借库存": available_stock,
            "用户总数": user_count,
            "普通用户数": normal_count,
            "教师用户数": teacher_count,
            "管理员数": admin_count,
            "当前未归还数量": borrowed_count,
            "当前逾期数量": overdue_count,
            "默认借阅天数": self.default_borrow_days,
            "数据目录": self.storage.get_info().get("base_dir", ""),
        }

    def export_books_as_dicts(self, items: list[Book] | None = None) -> list[dict[str, Any]]:
        data = items if items is not None else self.books
        return [item.to_dict() for item in data]

    def export_users_as_dicts(self, items: list[User] | None = None) -> list[dict[str, Any]]:
        data = items if items is not None else self.users
        return [item.to_dict() for item in data]

    def export_records_as_dicts(
        self,
        items: list[BorrowRecord] | None = None,
    ) -> list[dict[str, Any]]:
        data = items if items is not None else self.records
        record_dicts = []
        for item in data:
            record_data = item.to_dict()
            if not item.returned:
                record_data["overdue_days"] = item.calculate_overdue_days()
            record_dicts.append(record_data)
        return record_dicts

    def add_sample_data_if_empty(self) -> tuple[bool, str]:
        if self.books or self.users or self.records:
            return False, "当前已有数据，未重复导入样例数据。"

        books = [
            Book("B-1001", "Python 程序设计", "张三", "9787301000001", "计算机", "高教出版社", 2021, 6, 6, "基础教材"),
            Book("B-1002", "软件工程导论", "李四", "9787301000002", "软件工程", "清华大学出版社", 2020, 5, 5, "课程常用书"),
            Book("B-1003", "数据库系统概论", "王五", "9787301000003", "数据库", "人民邮电出版社", 2022, 4, 4, "数据库基础"),
            Book("B-1004", "设计模式", "GoF", "9787301000004", "软件设计", "机械工业出版社", 2019, 3, 3, "经典书籍"),
        ]
        users = [
            User("U-1001", "小明", "13800000001", "xiaoming@example.com", "普通用户", "计算机学院"),
            User("U-1002", "王老师", "13800000002", "teacher@example.com", "教师用户", "软件学院"),
            User("U-1003", "管理员", "13800000003", "admin@example.com", "管理员", "图书馆"),
        ]
        self.books.extend(books)
        self.users.extend(users)

        old_date = datetime.now().replace(day=max(1, datetime.now().day - 40)).strftime("%Y-%m-%d")
        due_date = calc_due_date(old_date, 30)
        self.records.append(
            BorrowRecord(
                record_id="R-1001",
                user_id="U-1001",
                user_name="小明",
                book_id="B-1002",
                book_title="软件工程导论",
                isbn="9787301000002",
                borrow_date=old_date,
                due_date=due_date,
                returned=False,
                note="系统初始化生成的示例借阅",
            )
        )
        for item in self.books:
            if item.book_id == "B-1002":
                item.available_count -= 1
        self.save_all()
        return True, "样例数据导入成功。"
