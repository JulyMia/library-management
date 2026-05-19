"""服务层核心业务测试。"""

from __future__ import annotations

from datetime import datetime, timedelta

from models import BorrowRecord


def add_book(service, **overrides):
    """添加一条默认图书数据，并允许覆盖字段。"""
    data = {
        "book_id": "B-1001",
        "title": "Python 程序设计",
        "author": "张三",
        "isbn": "9787301000001",
        "category": "计算机",
        "publisher": "高教出版社",
        "publish_year": 2024,
        "total_count": 5,
        "available_count": 5,
    }
    data.update(overrides)
    return service.add_book(data)


def add_user(service, **overrides):
    """添加一条默认用户数据，并允许覆盖字段。"""
    data = {
        "user_id": "U-1001",
        "name": "小明",
        "phone": "13800000001",
        "email": "xiaoming@example.com",
        "user_type": "普通用户",
        "department": "计算机学院",
        "status": "正常",
    }
    data.update(overrides)
    return service.add_user(data)


def test_add_book_succeeds_with_valid_data(service):
    """正常新增图书时应写入图书列表。"""
    ok, message = add_book(service)

    assert ok is True
    assert "图书添加成功" in message
    assert len(service.books) == 1
    assert service.books[0].book_id == "B-1001"


def test_add_user_succeeds_with_valid_data(service):
    """正常新增用户时应写入用户列表。"""
    ok, message = add_user(service)

    assert ok is True
    assert "用户添加成功" in message
    assert len(service.users) == 1
    assert service.users[0].user_id == "U-1001"


def test_borrow_book_creates_record_and_reduces_stock(service):
    """借书成功后应生成记录并减少库存。"""
    assert add_book(service)[0] is True
    assert add_user(service)[0] is True

    ok, message = service.borrow_book("U-1001", "B-1001", note="单元测试借阅")

    assert ok is True
    assert "借书成功" in message
    assert service.books[0].available_count == 4
    assert len(service.records) == 1
    assert service.records[0].note == "单元测试借阅"


def test_borrow_book_rejects_duplicate_active_record(service):
    """同一用户未归还前不能重复借同一本书。"""
    assert add_book(service)[0] is True
    assert add_user(service)[0] is True
    assert service.borrow_book("U-1001", "B-1001")[0] is True

    ok, message = service.borrow_book("U-1001", "B-1001")

    assert ok is False
    assert message == "该用户已经借阅过这本书且尚未归还。"
    assert len(service.records) == 1


def test_borrow_book_rejects_abnormal_user(service):
    """用户状态异常时不能借书。"""
    assert add_book(service)[0] is True
    assert add_user(service, status="冻结")[0] is True

    ok, message = service.borrow_book("U-1001", "B-1001")

    assert ok is False
    assert message == "用户状态异常，不能借书。"
    assert len(service.records) == 0


def test_borrow_book_rejects_out_of_stock_book(service):
    """库存不足时不能借书。"""
    assert add_book(service, total_count=1, available_count=0)[0] is True
    assert add_user(service)[0] is True

    ok, message = service.borrow_book("U-1001", "B-1001")

    assert ok is False
    assert message == "图书库存不足。"
    assert len(service.records) == 0


def test_return_book_marks_record_returned_and_restores_stock(service):
    """还书成功后应更新记录状态并恢复库存。"""
    assert add_book(service)[0] is True
    assert add_user(service)[0] is True
    assert service.borrow_book("U-1001", "B-1001")[0] is True
    record_id = service.records[0].record_id

    ok, message = service.return_book(record_id)

    assert ok is True
    assert message == "还书成功，未逾期。"
    assert service.records[0].returned is True
    assert service.records[0].return_date
    assert service.books[0].available_count == 5


def test_return_book_reports_overdue_days(service):
    """逾期归还时应返回逾期提示并写入逾期天数。"""
    assert add_book(service)[0] is True
    assert add_user(service)[0] is True
    overdue_record = BorrowRecord(
        record_id="R-1001",
        user_id="U-1001",
        user_name="小明",
        book_id="B-1001",
        book_title="Python 程序设计",
        isbn="9787301000001",
        borrow_date=(datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
        due_date=(datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
        returned=False,
    )
    service.records.append(overdue_record)
    service.books[0].available_count = 4
    service.save_all()

    ok, message = service.return_book("R-1001")

    assert ok is True
    assert "已逾期" in message
    assert service.records[0].overdue_days >= 3
    assert service.records[0].returned is True


def test_return_book_rejects_already_returned_record(service):
    """重复归还同一借阅记录时应返回失败。"""
    assert add_book(service)[0] is True
    assert add_user(service)[0] is True
    assert service.borrow_book("U-1001", "B-1001")[0] is True
    record_id = service.records[0].record_id
    assert service.return_book(record_id)[0] is True

    ok, message = service.return_book(record_id)

    assert ok is False
    assert message == "该记录已归还。"


def test_get_overdue_records_returns_only_overdue_items(service):
    """逾期查询应仅返回逾期记录并刷新逾期天数。"""
    assert add_book(service)[0] is True
    assert add_user(service)[0] is True
    service.records.extend(
        [
            BorrowRecord(
                record_id="R-1001",
                user_id="U-1001",
                user_name="小明",
                book_id="B-1001",
                book_title="Python 程序设计",
                isbn="9787301000001",
                borrow_date=(datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d"),
                due_date=(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
                returned=False,
            ),
            BorrowRecord(
                record_id="R-1002",
                user_id="U-1001",
                user_name="小明",
                book_id="B-1001",
                book_title="Python 程序设计",
                isbn="9787301000001",
                borrow_date=datetime.now().strftime("%Y-%m-%d"),
                due_date=(datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
                returned=False,
            ),
        ]
    )

    records = service.get_overdue_records()

    assert [item.record_id for item in records] == ["R-1001"]
    assert records[0].overdue_days >= 5


def test_update_book_rejects_duplicate_isbn(service):
    """修改图书时应阻止 ISBN 与其他图书重复。"""
    assert add_book(service, book_id="B-1001", isbn="9787301000001")[0] is True
    assert add_book(service, book_id="B-1002", isbn="9787301000002")[0] is True

    ok, message = service.update_book("B-1002", {"isbn": "9787301000001"})

    assert ok is False
    assert message == "ISBN 与其他图书重复。"


def test_update_book_updates_counts_and_description(service):
    """修改图书时应同步更新库存与描述。"""
    assert add_book(service, total_count=5, available_count=3)[0] is True

    ok, message = service.update_book(
        "B-1001",
        {"total_count": 8, "available_count": 6, "description": "重构后测试数据"},
    )

    assert ok is True
    assert message == "图书信息修改成功。"
    assert service.books[0].total_count == 8
    assert service.books[0].available_count == 6
    assert service.books[0].description == "重构后测试数据"


def test_search_books_supports_all_and_single_field(service):
    """图书查询应支持全字段与单字段查询。"""
    assert add_book(service, book_id="B-1001", title="Python 程序设计", author="张三")[0] is True
    assert add_book(service, book_id="B-1002", title="软件工程导论", author="李四", isbn="9787301000002")[0] is True

    all_result = service.search_books("python")
    author_result = service.search_books("李四", field_name="author")
    all_books = service.search_books("")

    assert [item.book_id for item in all_result] == ["B-1001"]
    assert [item.book_id for item in author_result] == ["B-1002"]
    assert len(all_books) == 2


def test_update_user_and_search_users(service):
    """用户更新与查询应返回正确结果。"""
    assert add_user(service, user_id="U-1001", phone="13800000001", name="小明")[0] is True
    assert add_user(service, user_id="U-1002", phone="13800000002", name="王老师", user_type="教师用户")[0] is True

    ok, message = service.update_user(
        "U-1001",
        {"phone": "13800000003", "department": "软件学院", "status": "冻结"},
    )
    duplicate_ok, duplicate_message = service.update_user("U-1001", {"phone": "13800000002"})
    search_result = service.search_users("王老师")
    all_users = service.search_users("")

    assert ok is True
    assert message == "用户信息修改成功。"
    assert service.users[0].phone == "13800000003"
    assert service.users[0].status == "冻结"
    assert duplicate_ok is False
    assert duplicate_message == "手机号与其他用户重复。"
    assert [item.user_id for item in search_result] == ["U-1002"]
    assert len(all_users) == 2


def test_delete_book_and_delete_user_validate_active_records(service):
    """删除图书和用户时应校验未归还记录。"""
    assert add_book(service, book_id="B-1001")[0] is True
    assert add_book(service, book_id="B-1002", isbn="9787301000002")[0] is True
    assert add_user(service, user_id="U-1001")[0] is True
    assert add_user(service, user_id="U-1002", phone="13800000002")[0] is True
    assert service.borrow_book("U-1001", "B-1001")[0] is True

    delete_book_ok, delete_book_message = service.delete_book("B-1001")
    delete_user_ok, delete_user_message = service.delete_user("U-1001")
    free_book_ok, free_book_message = service.delete_book("B-1002")
    free_user_ok, free_user_message = service.delete_user("U-1002")

    assert delete_book_ok is False
    assert delete_book_message == "该图书存在未归还记录，不能删除。"
    assert delete_user_ok is False
    assert delete_user_message == "该用户存在未归还图书，不能删除。"
    assert free_book_ok is True
    assert free_book_message == "图书删除成功。"
    assert free_user_ok is True
    assert free_user_message == "用户删除成功。"


def test_record_queries_and_exports(service):
    """记录查询、导出与字典转换应返回一致数据。"""
    assert add_book(service)[0] is True
    assert add_user(service)[0] is True
    assert service.borrow_book("U-1001", "B-1001", note="导出测试")[0] is True

    user_records = service.get_user_records("U-1001")
    unreturned_records = service.get_unreturned_records()
    exported_books = service.export_books_as_dicts()
    exported_users = service.export_users_as_dicts()
    exported_records = service.export_records_as_dicts()

    assert len(user_records) == 1
    assert len(unreturned_records) == 1
    assert exported_books[0]["book_id"] == "B-1001"
    assert exported_users[0]["user_id"] == "U-1001"
    assert exported_records[0]["note"] == "导出测试"
    assert exported_records[0]["returned"] is False


def test_statistics_and_default_borrow_days(service):
    """统计信息与默认借阅天数设置应反映当前状态。"""
    assert add_book(service, book_id="B-1001", total_count=5, available_count=4)[0] is True
    assert add_book(service, book_id="B-1002", isbn="9787301000002", total_count=3, available_count=3)[0] is True
    assert add_user(service, user_id="U-1001", user_type="普通用户")[0] is True
    assert add_user(service, user_id="U-1002", phone="13800000002", user_type="教师用户")[0] is True
    assert add_user(service, user_id="U-1003", phone="13800000003", user_type="管理员")[0] is True
    assert service.borrow_book("U-1001", "B-1001")[0] is True

    invalid_ok, invalid_message = service.set_default_borrow_days(0)
    valid_ok, valid_message = service.set_default_borrow_days(45)
    statistics = service.get_statistics()

    assert invalid_ok is False
    assert invalid_message == "借阅天数必须大于 0。"
    assert valid_ok is True
    assert valid_message == "默认借阅天数已设置为 45 天。"
    assert statistics["图书种类数"] == 2
    assert statistics["图书总库存"] == 8
    assert statistics["当前可借库存"] == 6
    assert statistics["用户总数"] == 3
    assert statistics["普通用户数"] == 1
    assert statistics["教师用户数"] == 1
    assert statistics["管理员数"] == 1
    assert statistics["当前未归还数量"] == 1
    assert statistics["默认借阅天数"] == 45
    assert statistics["数据目录"]


def test_add_sample_data_if_empty_only_runs_once(service):
    """样例数据导入应仅在空数据状态下执行一次。"""
    ok, message = service.add_sample_data_if_empty()
    second_ok, second_message = service.add_sample_data_if_empty()

    assert ok is True
    assert message == "样例数据导入成功。"
    assert len(service.books) == 4
    assert len(service.users) == 3
    assert len(service.records) == 1
    assert service.records[0].returned is False
    assert second_ok is False
    assert second_message == "当前已有数据，未重复导入样例数据。"
