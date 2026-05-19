"""工具函数测试。"""

from __future__ import annotations

from utils import (
    calc_due_date,
    confirm,
    input_int,
    input_text,
    pause,
    print_book_rows,
    print_record_rows,
    print_title,
    print_user_rows,
    safe_lower,
    show_menu,
    show_simple_table,
)


def test_input_text_retries_until_non_empty(monkeypatch, capsys):
    """input_text 应在空输入时重复提示。"""
    answers = iter(["", "有效输入"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    result = input_text("请输入：")

    captured = capsys.readouterr()
    assert result == "有效输入"
    assert "输入不能为空" in captured.out


def test_input_text_returns_default_when_allow_empty(monkeypatch):
    """允许空输入时应返回默认值。"""
    monkeypatch.setattr("builtins.input", lambda _: "")

    assert input_text("请输入：", allow_empty=True, default="默认值") == "默认值"


def test_input_int_handles_invalid_and_minimum(monkeypatch, capsys):
    """input_int 应处理非法输入和最小值限制。"""
    answers = iter(["abc", "0", "3"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    result = input_int("请输入整数：", minimum=1)

    captured = capsys.readouterr()
    assert result == 3
    assert "请输入整数" in captured.out
    assert "不能小于 1" in captured.out


def test_input_int_returns_default(monkeypatch):
    """空输入且提供默认值时应返回默认值。"""
    monkeypatch.setattr("builtins.input", lambda _: "")

    assert input_int("请输入整数：", default=7) == 7


def test_calc_due_date_and_safe_lower():
    """日期计算和小写转换应返回预期结果。"""
    assert calc_due_date("2026-05-01", 5) == "2026-05-06"
    assert safe_lower("  PyThOn  ") == "python"


def test_calc_due_date_with_invalid_date_returns_valid_text():
    """非法日期输入时仍应返回可解析的日期文本。"""
    result = calc_due_date("invalid-date", 3)

    assert len(result) == 10
    assert result.count("-") == 2


def test_confirm_and_pause(monkeypatch):
    """确认输入和暂停函数应可被安全调用。"""
    answers = iter(["yes", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    assert confirm() is True
    pause()


def test_show_simple_table_outputs_rows(capsys):
    """表格输出应包含表头和数据内容。"""
    show_simple_table([["B-1001", "Python"]], ["编号", "书名"])

    captured = capsys.readouterr()
    assert "编号" in captured.out
    assert "Python" in captured.out


def test_show_simple_table_outputs_empty_message(capsys):
    """空表格时应输出没有数据提示。"""
    show_simple_table([], ["编号", "书名"])

    captured = capsys.readouterr()
    assert "没有数据" in captured.out


def test_print_helpers_and_menu_output(capsys):
    """展示类工具函数应输出关键字段。"""
    print_title("测试标题")
    print_book_rows(
        [{"book_id": "B-1001", "title": "Python", "author": "张三", "isbn": "1", "available_count": 2, "total_count": 5}]
    )
    print_user_rows(
        [{"user_id": "U-1001", "name": "小明", "user_type": "普通用户", "phone": "138", "status": "正常"}]
    )
    print_record_rows(
        [{"record_id": "R-1001", "user_name": "小明", "book_title": "Python", "borrow_date": "2026-05-01", "due_date": "2026-05-10", "return_date": "", "returned": False}]
    )
    show_menu("菜单", ["功能一", "功能二"])

    captured = capsys.readouterr()
    assert "测试标题" in captured.out
    assert "Python" in captured.out
    assert "小明" in captured.out
    assert "R-1001" in captured.out
    assert "功能一" in captured.out
