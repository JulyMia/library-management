"""领域模型纯逻辑测试。"""

from __future__ import annotations

from models import BorrowRecord


def test_book_user_and_record_to_dict_round_trip():
    """核心模型应支持字典转换和关键字段展示。"""
    from models import Book, User

    book = Book(
        book_id="B-1001",
        title="Python 程序设计",
        author="张三",
        isbn="9787301000001",
        total_count=5,
        available_count=4,
    )
    user = User(
        user_id="U-1001",
        name="小明",
        phone="13800000001",
        email="xiaoming@example.com",
    )
    record = BorrowRecord(
        record_id="R-1001",
        user_id="U-1001",
        user_name="小明",
        book_id="B-1001",
        book_title="Python 程序设计",
        isbn="9787301000001",
        borrow_date="2026-05-01",
        due_date="2026-05-10",
    )

    assert Book.from_dict(book.to_dict()).title == "Python 程序设计"
    assert User.from_dict(user.to_dict()).name == "小明"
    assert BorrowRecord.from_dict(record.to_dict()).book_title == "Python 程序设计"
    assert "库存:4/5" in book.short_text()
    assert "状态:正常" in user.short_text()
    assert "未归还" in record.short_text()


def test_calculate_overdue_days_uses_given_now_text():
    """未归还记录应按传入日期计算逾期天数。"""
    record = BorrowRecord(
        record_id="R-1001",
        user_id="U-1001",
        user_name="小明",
        book_id="B-1001",
        book_title="Python 程序设计",
        isbn="9787301000001",
        borrow_date="2026-05-01",
        due_date="2026-05-10",
        returned=False,
    )

    assert record.calculate_overdue_days("2026-05-15") == 5


def test_calculate_overdue_days_returns_zero_for_invalid_dates():
    """非法日期时应安全返回 0。"""
    record = BorrowRecord(
        record_id="R-1003",
        user_id="U-1003",
        user_name="管理员",
        book_id="B-1003",
        book_title="数据库系统概论",
        isbn="9787301000003",
        borrow_date="2026-05-01",
        due_date="invalid-date",
        returned=False,
    )

    assert record.calculate_overdue_days("2026-05-15") == 0


def test_is_overdue_handles_now_text_and_empty_due_date():
    """逾期判断应覆盖正常与空日期路径。"""
    record = BorrowRecord(
        record_id="R-1004",
        user_id="U-1004",
        user_name="教师",
        book_id="B-1004",
        book_title="设计模式",
        isbn="9787301000004",
        borrow_date="2026-05-01",
        due_date="2026-05-10",
        returned=False,
    )
    empty_due_record = BorrowRecord(
        record_id="R-1005",
        user_id="U-1005",
        user_name="教师",
        book_id="B-1005",
        book_title="软件工程",
        isbn="9787301000005",
        borrow_date="2026-05-01",
        due_date="",
        returned=False,
    )

    assert record.is_overdue("2026-05-12") is True
    assert empty_due_record.is_overdue() is False


def test_is_overdue_returns_true_for_returned_record_with_overdue_days():
    """已归还且记录了逾期天数的记录应被识别为逾期。"""
    record = BorrowRecord(
        record_id="R-1002",
        user_id="U-1002",
        user_name="王老师",
        book_id="B-1002",
        book_title="软件工程导论",
        isbn="9787301000002",
        borrow_date="2026-05-01",
        due_date="2026-05-10",
        return_date="2026-05-14",
        returned=True,
        overdue_days=4,
    )

    assert record.is_overdue() is True
