from __future__ import annotations

from collections.abc import Callable

from services import LibraryService
from utils import (
    confirm,
    input_int,
    input_text,
    pause,
    print_book_rows,
    print_line,
    print_record_rows,
    print_title,
    print_user_rows,
    show_menu,
)


class LibraryCLI:
    def __init__(self) -> None:
        self.service = LibraryService()

    def _run_menu_loop(
        self,
        title: str,
        options: list[str],
        handlers: dict[str, Callable[[], None]],
        exit_choice: str,
    ) -> None:
        while True:
            show_menu(title, options)
            choice = input("请选择功能编号: ").strip()
            if choice == exit_choice:
                return
            handler = handlers.get(choice)
            if handler is None:
                print("输入有误，请重新选择。")
                pause()
                continue
            handler()

    def _pause_with_message(self, message: str) -> None:
        print(message)
        pause()

    def _show_books(self) -> None:
        print_book_rows(self.service.export_books_as_dicts())

    def _show_users(self) -> None:
        print_user_rows(self.service.export_users_as_dicts())

    def _show_unreturned_records(self) -> None:
        data = self.service.get_unreturned_records()
        print_record_rows(self.service.export_records_as_dicts(data))

    def _collect_book_info(self) -> dict[str, object]:
        book_info = {
            "title": input_text("书名: "),
            "author": input_text("作者: "),
            "isbn": input_text("ISBN: "),
            "category": input_text("分类(可空): ", allow_empty=True),
            "publisher": input_text("出版社(可空): ", allow_empty=True),
            "publish_year": input_int("出版年份(默认0): ", default=0, minimum=0),
            "total_count": input_int("总库存数量: ", default=1, minimum=0),
            "description": input_text("简介(可空): ", allow_empty=True),
        }
        book_info["available_count"] = book_info["total_count"]
        return book_info

    def _collect_book_update_info(self) -> dict[str, str]:
        updated_info: dict[str, str] = {}
        print("直接回车表示该字段不修改。")
        field_prompts = {
            "title": "新书名: ",
            "author": "新作者: ",
            "isbn": "新ISBN: ",
            "category": "新分类: ",
            "publisher": "新出版社: ",
            "publish_year": "新出版年份: ",
            "total_count": "新总库存: ",
            "available_count": "新可借库存: ",
            "description": "新简介: ",
        }
        allow_empty_fields = {"category", "publisher", "description"}
        for field_name, prompt in field_prompts.items():
            value = input(prompt).strip()
            if value or field_name in allow_empty_fields:
                updated_info[field_name] = value
        return updated_info

    def _collect_user_info(self) -> dict[str, str]:
        print("用户类型可输入: 普通用户 / 教师用户 / 管理员")
        return {
            "name": input_text("姓名: "),
            "phone": input_text("电话: ", allow_empty=True),
            "email": input_text("邮箱: ", allow_empty=True),
            "user_type": input_text("用户类型: "),
            "department": input_text("所属部门(可空): ", allow_empty=True),
            "status": input_text("状态(默认正常): ", allow_empty=True, default="正常") or "正常",
        }

    def _collect_user_update_info(self) -> dict[str, str]:
        updated_info: dict[str, str] = {}
        print("直接回车表示不修改该项。")
        field_prompts = {
            "name": "新姓名: ",
            "phone": "新电话: ",
            "email": "新邮箱: ",
            "user_type": "新用户类型: ",
            "department": "新部门: ",
            "status": "新状态: ",
        }
        allow_empty_fields = {"email", "department"}
        for field_name, prompt in field_prompts.items():
            value = input(prompt).strip()
            if value or field_name in allow_empty_fields:
                updated_info[field_name] = value
        return updated_info

    def _handle_add_book(self) -> None:
        _, message = self.service.add_book(self._collect_book_info())
        self._pause_with_message(message)

    def _handle_delete_book(self) -> None:
        self._show_books()
        book_id = input_text("请输入要删除的图书编号: ")
        if confirm():
            _, message = self.service.delete_book(book_id)
            print(message)
        else:
            print("已取消删除。")
        pause()

    def _handle_update_book(self) -> None:
        self._show_books()
        book_id = input_text("请输入要修改的图书编号: ")
        _, message = self.service.update_book(book_id, self._collect_book_update_info())
        self._pause_with_message(message)

    def _handle_show_books(self) -> None:
        self._show_books()
        pause()

    def _handle_add_user(self) -> None:
        _, message = self.service.add_user(self._collect_user_info())
        self._pause_with_message(message)

    def _handle_delete_user(self) -> None:
        self._show_users()
        user_id = input_text("请输入要删除的用户编号: ")
        if confirm():
            _, message = self.service.delete_user(user_id)
            print(message)
        else:
            print("已取消删除。")
        pause()

    def _handle_update_user(self) -> None:
        self._show_users()
        user_id = input_text("请输入要修改的用户编号: ")
        _, message = self.service.update_user(user_id, self._collect_user_update_info())
        self._pause_with_message(message)

    def _handle_search_user(self) -> None:
        keyword = input_text("请输入姓名、编号、电话、邮箱或类型关键词: ")
        data = self.service.search_users(keyword)
        print_user_rows(self.service.export_users_as_dicts(data))
        pause()

    def _handle_show_users(self) -> None:
        self._show_users()
        pause()

    def _handle_borrow_book(self) -> None:
        print_title("当前用户列表")
        self._show_users()
        print_title("当前图书列表")
        self._show_books()
        user_id = input_text("请输入用户编号: ")
        book_id = input_text("请输入图书编号: ")
        note = input_text("备注(可空): ", allow_empty=True)
        _, message = self.service.borrow_book(user_id, book_id, note)
        print(message)
        pause()

    def _handle_return_book(self) -> None:
        self._show_unreturned_records()
        record_id = input_text("请输入要归还的记录号: ")
        _, message = self.service.return_book(record_id)
        self._pause_with_message(message)

    def _handle_user_records(self) -> None:
        self._show_users()
        user_id = input_text("请输入用户编号: ")
        data = self.service.get_user_records(user_id)
        if not data:
            print("没有找到该用户的借阅记录。")
        else:
            print_record_rows(self.service.export_records_as_dicts(data))
        pause()

    def _handle_show_unreturned_records(self) -> None:
        self._show_unreturned_records()
        pause()

    def _handle_set_borrow_days(self) -> None:
        days = input_int("请输入默认借阅天数: ", default=30, minimum=1)
        _, message = self.service.set_default_borrow_days(days)
        self._pause_with_message(message)

    def _handle_show_overdue_records(self) -> None:
        data = self.service.get_overdue_records()
        if not data:
            print("当前没有逾期记录。")
        else:
            print_record_rows(self.service.export_records_as_dicts(data))
            print_line()
            for item in data:
                state = "已归还后逾期" if item.returned else "仍未归还且逾期"
                print(
                    f"记录号:{item.record_id} 用户:{item.user_name} 图书:{item.book_title} "
                    f"逾期天数:{item.overdue_days} 状态:{state}"
                )
        pause()

    def _handle_show_overdue_help(self) -> None:
        print("系统默认借阅天数可在借阅管理菜单中设置。")
        print("逾期判断方式较简单: 当前日期或归还日期晚于到期日期即视为逾期。")
        print("该版本未实现罚款规则、节假日顺延等复杂业务。")
        pause()

    def run(self) -> None:
        main_handlers = {
            "1": self.book_menu,
            "2": self.user_menu,
            "3": self.borrow_menu,
            "4": self.overdue_menu,
            "5": self.show_stats,
            "6": self.load_sample_data,
        }
        while True:
            show_menu(
                "图书馆管理系统",
                [
                    "图书管理",
                    "用户管理",
                    "借阅管理",
                    "逾期管理",
                    "统计信息",
                    "导入样例数据",
                    "退出系统",
                ],
            )
            choice = input("请选择功能编号: ").strip()
            if choice == "7":
                print("系统已退出。")
                break
            handler = main_handlers.get(choice)
            if handler is None:
                print("输入有误，请重新选择。")
                pause()
                continue
            handler()

    def book_menu(self) -> None:
        self._run_menu_loop(
            "图书管理",
            [
                "添加图书",
                "删除图书",
                "修改图书信息",
                "查询图书",
                "显示全部图书",
                "返回主菜单",
            ],
            {
                "1": self._handle_add_book,
                "2": self._handle_delete_book,
                "3": self._handle_update_book,
                "4": self.search_books_menu,
                "5": self._handle_show_books,
            },
            "6",
        )

    def search_books_menu(self) -> None:
        show_menu(
            "查询图书",
            [
                "按书名查询",
                "按作者查询",
                "按ISBN查询",
                "综合查询",
            ],
        )
        choice = input("请选择查询方式: ").strip()
        keyword = input_text("请输入关键词: ")
        if choice == "1":
            data = self.service.search_books(keyword, "title")
        elif choice == "2":
            data = self.service.search_books(keyword, "author")
        elif choice == "3":
            data = self.service.search_books(keyword, "isbn")
        else:
            data = self.service.search_books(keyword, "all")
        print_book_rows(self.service.export_books_as_dicts(data))
        pause()

    def user_menu(self) -> None:
        self._run_menu_loop(
            "用户管理",
            [
                "添加用户",
                "删除用户",
                "修改用户信息",
                "查询用户",
                "显示全部用户",
                "返回主菜单",
            ],
            {
                "1": self._handle_add_user,
                "2": self._handle_delete_user,
                "3": self._handle_update_user,
                "4": self._handle_search_user,
                "5": self._handle_show_users,
            },
            "6",
        )

    def borrow_menu(self) -> None:
        self._run_menu_loop(
            "借阅管理",
            [
                "用户借书",
                "用户还书",
                "查询某个用户的借阅记录",
                "查询所有未归还记录",
                "设置默认借阅天数",
                "返回主菜单",
            ],
            {
                "1": self._handle_borrow_book,
                "2": self._handle_return_book,
                "3": self._handle_user_records,
                "4": self._handle_show_unreturned_records,
                "5": self._handle_set_borrow_days,
            },
            "6",
        )

    def overdue_menu(self) -> None:
        self._run_menu_loop(
            "逾期管理",
            [
                "查看当前逾期记录",
                "查看逾期详情说明",
                "返回主菜单",
            ],
            {
                "1": self._handle_show_overdue_records,
                "2": self._handle_show_overdue_help,
            },
            "3",
        )

    def show_stats(self) -> None:
        print_title("统计信息")
        data = self.service.get_statistics()
        for key, value in data.items():
            print(f"{key}: {value}")
        pause()

    def load_sample_data(self) -> None:
        if confirm("确认导入样例数据吗？仅在空数据时有效。(y/n): "):
            ok, msg = self.service.add_sample_data_if_empty()
            print(msg)
        else:
            print("已取消。")
        pause()


def main() -> None:
    cli = LibraryCLI()
    cli.run()


if __name__ == "__main__":
    main()
