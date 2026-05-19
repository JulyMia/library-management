"""样例数据导入脚本。"""

from __future__ import annotations
from services import LibraryService

def generate_sample_data(service: LibraryService | None = None) -> tuple[bool, str]:
    """导入样例数据并返回执行结果。"""
    return (service or LibraryService()).add_sample_data_if_empty()

def main() -> None:
    """脚本入口。"""
    print(generate_sample_data()[1])

if __name__ == "__main__":
    main()
