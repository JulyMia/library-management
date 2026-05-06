from __future__ import annotations
from services import LibraryService

def generate_sample_data(service: LibraryService | None = None) -> tuple[bool, str]:
    return (service or LibraryService()).add_sample_data_if_empty()

def main() -> None:
    print(generate_sample_data()[1])

if __name__ == "__main__":
    main()
