# 三个重要pytest代码讲解

## 1. 说明

本文件选取实验二中最有代表性的 3 段 `pytest` 代码进行讲解，分别对应：

- 测试环境隔离
- 核心业务主流程验证
- 边界路径验证与缺陷发现

这 3 段代码能够较完整地体现本次实验二“面向可测试性改造”的主要思路，即：先构造稳定的测试环境，再围绕核心业务编写自动化测试，最后用边界测试发现并修复潜在缺陷。

## 2. 代码一：测试夹具与数据隔离

### 代码节选

```python
@pytest.fixture
def storage(tmp_path):
    """提供隔离的 JSON 存储目录。"""
    return JsonStorage(base_dir=tmp_path)


@pytest.fixture
def service(storage):
    """提供基于临时目录的业务服务对象。"""
    return LibraryService(storage=storage)
```

### 代码位置

- [conftest.py](file:///e:/路在何方？/软件体系结构/library_system/tests/conftest.py)

### 讲解

- 这段代码是整个测试体系能够稳定运行的基础。
- `tmp_path` 是 `pytest` 提供的临时目录夹具，每次执行测试时都会生成独立目录，因此不会污染项目根目录下真实的 `books.json`、`users.json`、`records.json`。
- `JsonStorage(base_dir=tmp_path)` 把存储层重定向到临时目录，体现了“通过依赖注入隔离外部环境”的测试思想。
- `service(storage)` 进一步把测试对象统一封装为 `LibraryService`，使每个测试函数都能直接获得一个干净、可重复使用的业务服务实例。

### 价值分析

- 它解决了原项目“测试会污染真实数据”的问题。
- 它让测试具备可重复执行能力，是实验二可测试性改造中最关键的基础设施。
- 这也是为什么本次实验选择以服务层为测试重点，而不是直接去测试命令行输入输出流程。

## 3. 代码二：借书主流程测试

### 代码节选

```python
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
```

### 代码位置

- [test_services.py](file:///e:/路在何方？/软件体系结构/library_system/tests/test_services.py)

### 讲解

- 这段代码验证的是系统最核心的业务路径之一，即“用户正常借书”的完整行为。
- 在执行借书前，测试先通过辅助函数构造图书和用户数据，保证测试前置条件清晰明确。
- 之后调用 `service.borrow_book()`，并从返回结果、库存变化、记录生成、备注写入等多个角度进行断言。
- 这里不是只验证“返回成功”这么简单，而是同时验证了业务副作用是否正确发生。

### 价值分析

- 它体现了自动化测试对核心业务流程的覆盖能力。
- 与手工点击菜单相比，这种测试更适合做回归验证，因为每次代码修改后都可以快速重复执行。
- 该测试也体现了实验一结构性重构的价值：如果 `borrow_book()` 仍然是原来那种更混乱的大函数，测试定位和断言设计都会更困难。

## 4. 代码三：库存不足测试与缺陷发现

### 代码节选

```python
def test_borrow_book_rejects_out_of_stock_book(service):
    """库存不足时不能借书。"""
    assert add_book(service, total_count=1, available_count=0)[0] is True
    assert add_user(service)[0] is True

    ok, message = service.borrow_book("U-1001", "B-1001")

    assert ok is False
    assert message == "图书库存不足。"
    assert len(service.records) == 0
```

### 代码位置

- [test_services.py](file:///e:/路在何方？/软件体系结构/library_system/tests/test_services.py)

### 讲解

- 这段代码看起来只是一个普通边界测试，但它在实际执行中帮助发现了一个真实缺陷。
- 最初系统在 `add_book()` 中对 `available_count` 的处理使用了 `or total_count` 的写法，导致当传入 `0` 时，会被错误当作“未提供值”，最终把库存重置为总库存。
- 因此，这个测试在第一次运行时失败了，说明系统其实不能正确表示“库存为 0 的图书”。
- 在修复 `services.py` 中对 `available_count` 的取值逻辑后，这个测试才成功通过。

### 价值分析

- 这段代码最能体现实验二的意义：测试不仅是“证明代码正确”，更是“帮助发现隐藏缺陷”。
- 它说明边界路径测试非常重要，因为 AI 生成代码常常在正常路径上表现正常，但在边界值处理上容易出错。
- 这也是实验报告里非常值得强调的一点，因为它能够说明本次测试改造带来了真正的工程收益，而不仅是形式上的测试补充。

## 5. 综合说明

- 上述 3 段代码分别代表了实验二中的 3 个关键层面：
  - 测试环境隔离
  - 核心业务路径验证
  - 边界路径验证与缺陷发现
- 它们共同构成了本次可测试性改造的主要成果。
- 从结果上看，当前系统已经能够使用 `pytest` 对核心逻辑进行自动回归验证，并且测试代码已经不再依赖手工 CLI 操作。
- 这说明系统的可测试性相较于初始状态有了明显提升。

## 版本记录

- v1：整理 3 个最重要的 pytest 代码片段，并给出面向实验报告的讲解说明。
