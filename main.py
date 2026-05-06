from __future__ import annotations

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

    def run(self) -> None:
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
            if choice == "1":
                self.book_menu()
            elif choice == "2":
                self.user_menu()
            elif choice == "3":
                self.borrow_menu()
            elif choice == "4":
                self.overdue_menu()
            elif choice == "5":
                self.show_stats()
            elif choice == "6":
                self.load_sample_data()
            elif choice == "7":
                print("系统已退出。")
                break
            else:
                print("输入有误，请重新选择。")
                pause()

    def book_menu(self) -> None:
        while True:
            show_menu(
                "图书管理",
                [
                    "添加图书",
                    "删除图书",
                    "修改图书信息",
                    "查询图书",
                    "显示全部图书",
                    "返回主菜单",
                ],
            )
            choice = input("请选择功能编号: ").strip()
            if choice == "1":
                info = {
                    "title": input_text("书名: "),
                    "author": input_text("作者: "),
                    "isbn": input_text("ISBN: "),
                    "category": input_text("分类(可空): ", allow_empty=True),
                    "publisher": input_text("出版社(可空): ", allow_empty=True),
                    "publish_year": input_int("出版年份(默认0): ", default=0, minimum=0),
                    "total_count": input_int("总库存数量: ", default=1, minimum=0),
                    "description": input_text("简介(可空): ", allow_empty=True),
                }
                info["available_count"] = info["total_count"]
                ok, msg = self.service.add_book(info)
                print(msg)
                pause()
            elif choice == "2":
                data = self.service.export_books_as_dicts()
                print_book_rows(data)
                book_id = input_text("请输入要删除的图书编号: ")
                if confirm():
                    ok, msg = self.service.delete_book(book_id)
                    print(msg)
                else:
                    print("已取消删除。")
                pause()
            elif choice == "3":
                data = self.service.export_books_as_dicts()
                print_book_rows(data)
                book_id = input_text("请输入要修改的图书编号: ")
                info = {}
                print("直接回车表示该字段不修改。")
                title = input("新书名: ").strip()
                author = input("新作者: ").strip()
                isbn = input("新ISBN: ").strip()
                category = input("新分类: ").strip()
                publisher = input("新出版社: ").strip()
                publish_year = input("新出版年份: ").strip()
                total_count = input("新总库存: ").strip()
                available_count = input("新可借库存: ").strip()
                description = input("新简介: ").strip()
                if title:
                    info["title"] = title
                if author:
                    info["author"] = author
                if isbn:
                    info["isbn"] = isbn
                if category or category == "":
                    info["category"] = category
                if publisher or publisher == "":
                    info["publisher"] = publisher
                if publish_year:
                    info["publish_year"] = publish_year
                if total_count:
                    info["total_count"] = total_count
                if available_count:
                    info["available_count"] = available_count
                if description or description == "":
                    info["description"] = description
                ok, msg = self.service.update_book(book_id, info)
                print(msg)
                pause()
            elif choice == "4":
                self.search_books_menu()
            elif choice == "5":
                data = self.service.export_books_as_dicts()
                print_book_rows(data)
                pause()
            elif choice == "6":
                break
            else:
                print("输入有误，请重新选择。")
                pause()

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
        while True:
            show_menu(
                "用户管理",
                [
                    "添加用户",
                    "删除用户",
                    "修改用户信息",
                    "查询用户",
                    "显示全部用户",
                    "返回主菜单",
                ],
            )
            choice = input("请选择功能编号: ").strip()
            if choice == "1":
                print("用户类型可输入: 普通用户 / 教师用户 / 管理员")
                info = {
                    "name": input_text("姓名: "),
                    "phone": input_text("电话: ", allow_empty=True),
                    "email": input_text("邮箱: ", allow_empty=True),
                    "user_type": input_text("用户类型: "),
                    "department": input_text("所属部门(可空): ", allow_empty=True),
                    "status": input_text("状态(默认正常): ", allow_empty=True, default="正常") or "正常",
                }
                ok, msg = self.service.add_user(info)
                print(msg)
                pause()
            elif choice == "2":
                data = self.service.export_users_as_dicts()
                print_user_rows(data)
                user_id = input_text("请输入要删除的用户编号: ")
                if confirm():
                    ok, msg = self.service.delete_user(user_id)
                    print(msg)
                else:
                    print("已取消删除。")
                pause()
            elif choice == "3":
                data = self.service.export_users_as_dicts()
                print_user_rows(data)
                user_id = input_text("请输入要修改的用户编号: ")
                info = {}
                print("直接回车表示不修改该项。")
                name = input("新姓名: ").strip()
                phone = input("新电话: ").strip()
                email = input("新邮箱: ").strip()
                user_type = input("新用户类型: ").strip()
                department = input("新部门: ").strip()
                status = input("新状态: ").strip()
                if name:
                    info["name"] = name
                if phone:
                    info["phone"] = phone
                if email or email == "":
                    info["email"] = email
                if user_type:
                    info["user_type"] = user_type
                if department or department == "":
                    info["department"] = department
                if status:
                    info["status"] = status
                ok, msg = self.service.update_user(user_id, info)
                print(msg)
                pause()
            elif choice == "4":
                keyword = input_text("请输入姓名、编号、电话、邮箱或类型关键词: ")
                data = self.service.search_users(keyword)
                print_user_rows(self.service.export_users_as_dicts(data))
                pause()
            elif choice == "5":
                data = self.service.export_users_as_dicts()
                print_user_rows(data)
                pause()
            elif choice == "6":
                break
            else:
                print("输入有误，请重新选择。")
                pause()

    def borrow_menu(self) -> None:
        while True:
            show_menu(
                "借阅管理",
                [
                    "用户借书",
                    "用户还书",
                    "查询某个用户的借阅记录",
                    "查询所有未归还记录",
                    "设置默认借阅天数",
                    "返回主菜单",
                ],
            )
            choice = input("请选择功能编号: ").strip()
            if choice == "1":
                print_title("当前用户列表")
                print_user_rows(self.service.export_users_as_dicts())
                print_title("当前图书列表")
                print_book_rows(self.service.export_books_as_dicts())
                user_id = input_text("请输入用户编号: ")
                book_id = input_text("请输入图书编号: ")
                note = input_text("备注(可空): ", allow_empty=True)
                ok, msg = self.service.borrow_book(user_id, book_id, note)
                print(msg)
                if not ok:
                    print("提示: 该版本中用户校验、库存校验、重复借阅校验都放在一个函数里，便于后续重构。")
                pause()
            elif choice == "2":
                data = self.service.get_unreturned_records()
                print_record_rows(self.service.export_records_as_dicts(data))
                record_id = input_text("请输入要归还的记录号: ")
                ok, msg = self.service.return_book(record_id)
                print(msg)
                pause()
            elif choice == "3":
                print_user_rows(self.service.export_users_as_dicts())
                user_id = input_text("请输入用户编号: ")
                data = self.service.get_user_records(user_id)
                if not data:
                    print("没有找到该用户的借阅记录。")
                else:
                    print_record_rows(self.service.export_records_as_dicts(data))
                pause()
            elif choice == "4":
                data = self.service.get_unreturned_records()
                print_record_rows(self.service.export_records_as_dicts(data))
                pause()
            elif choice == "5":
                days = input_int("请输入默认借阅天数: ", default=30, minimum=1)
                ok, msg = self.service.set_default_borrow_days(days)
                print(msg)
                pause()
            elif choice == "6":
                break
            else:
                print("输入有误，请重新选择。")
                pause()

    def overdue_menu(self) -> None:
        while True:
            show_menu(
                "逾期管理",
                [
                    "查看当前逾期记录",
                    "查看逾期详情说明",
                    "返回主菜单",
                ],
            )
            choice = input("请选择功能编号: ").strip()
            if choice == "1":
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
            elif choice == "2":
                print("系统默认借阅天数可在借阅管理菜单中设置。")
                print("逾期判断方式较简单: 当前日期或归还日期晚于到期日期即视为逾期。")
                print("该版本未实现罚款规则、节假日顺延等复杂业务。")
                pause()
            elif choice == "3":
                break
            else:
                print("输入有误，请重新选择。")
                pause()

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
