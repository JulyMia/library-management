"""pytest 公共夹具。"""

from __future__ import annotations

import pytest

from services import LibraryService
from storage import JsonStorage


@pytest.fixture
def storage(tmp_path):
    """提供隔离的 JSON 存储目录。"""
    return JsonStorage(base_dir=tmp_path)


@pytest.fixture
def service(storage):
    """提供基于临时目录的业务服务对象。"""
    return LibraryService(storage=storage)
