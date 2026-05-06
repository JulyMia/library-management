from __future__ import annotations
from datetime import datetime, timedelta
from models import DATE_FORMAT

def input_text(prompt: str, allow_empty: bool = False, default: str = "") -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        if allow_empty:
            return default
        print("输入不能为空，请重新输入。")

def input_int(prompt: str, default: int | None = None, minimum: int | None = None) -> int:
    while True:
        text = input(prompt).strip()
        try:
            value = default if not text and default is not None else int(text)
        except ValueError:
            print("请输入整数。")
            continue
        if minimum is not None and value < minimum:
            print(f"输入值不能小于 {minimum}。")
            continue
        return value

def now_date_text() -> str:
    return datetime.now().strftime(DATE_FORMAT)

def calc_due_date(start_date: str, days: int) -> str:
    try:
        value = datetime.strptime(start_date, DATE_FORMAT)
    except ValueError:
        value = datetime.now()
    return (value + timedelta(days=days)).strftime(DATE_FORMAT)

def pause() -> None:
    input("\n按回车键继续...")

def print_line(char: str = "-", width: int = 70) -> None:
    print(char * width)

def print_title(title: str) -> None:
    print_line("=")
    print(title.center(70))
    print_line("=")

def safe_lower(text: str) -> str:
    return (text or "").strip().lower()

def show_simple_table(rows: list[list[str]], headers: list[str]) -> None:
    if not rows:
        print("没有数据。")
        return
    widths = [len(h) for h in headers]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(str(value)))
    line = "+".join("-" * (w + 2) for w in widths)
    print(line)
    print(" | ".join(str(headers[i]).ljust(widths[i]) for i in range(len(headers))))
    print(line)
    for row in rows:
        print(" | ".join(str(row[i]).ljust(widths[i]) for i in range(len(row))))
    print(line)

def confirm(prompt: str = "确认执行该操作吗？(y/n): ") -> bool:
    return input(prompt).strip().lower() in {"y", "yes", "1"}

def print_book_rows(data: list[dict]) -> None:
    rows = [[item.get("book_id", ""), item.get("title", ""), item.get("author", ""), item.get("isbn", ""), f'{item.get("available_count", 0)}/{item.get("total_count", 0)}'] for item in data]
    show_simple_table(rows, ["编号", "书名", "作者", "ISBN", "库存"])

def print_user_rows(data: list[dict]) -> None:
    rows = [[item.get("user_id", ""), item.get("name", ""), item.get("user_type", ""), item.get("phone", ""), item.get("status", "")] for item in data]
    show_simple_table(rows, ["编号", "姓名", "类型", "电话", "状态"])

def print_record_rows(data: list[dict]) -> None:
    rows = [[item.get("record_id", ""), item.get("user_name", ""), item.get("book_title", ""), item.get("borrow_date", ""), item.get("due_date", ""), item.get("return_date", "") or "-", "已归还" if item.get("returned") else "未归还"] for item in data]
    show_simple_table(rows, ["记录号", "用户", "图书", "借出日期", "到期日期", "归还日期", "状态"])

def show_menu(title: str, options: list[str]) -> None:
    print_title(title)
    for i, item in enumerate(options, start=1):
        print(f"{i}. {item}")
    print_line()
