# 实验前基线建立操作说明

## 1. 文档目的

本说明用于建立“重构前基线”，为后续实验一、实验二中的重构优化提供可对比的原始证据。基线阶段需要完成以下工作：

- 保留当前版本作为初始版本
- 运行 `Pylint`、`Radon`、`CodeQL` 记录重构前数据
- 保存关键截图，作为实验报告中的原始依据

本说明默认项目路径为：

```text
e:\路在何方？\软件体系结构\library_system
```

默认终端环境为 Windows PowerShell。

## 2. 本阶段最终要得到什么

完成后，你至少应当保留以下材料：

- 一次“重构前初始版本”的 Git 提交记录
- 一份项目目录结构截图
- 一组静态分析结果截图
- 一组复杂度/可维护性指标截图
- 对应的文本结果文件
- 一次 CodeQL 扫描结果截图

建议最终保存成如下结构：

```text
library_system/
├── 作业文档/
│   ├── baseline/
│   │   ├── screenshots/
│   │   │   ├── 01-project-tree.png
│   │   │   ├── 02-git-status-before-commit.png
│   │   │   ├── 03-pylint-before.png
│   │   │   ├── 04-radon-cc-before.png
│   │   │   ├── 05-radon-mi-before.png
│   │   │   ├── 06-radon-raw-before.png
│   │   │   ├── 07-codeql-actions-success.png
│   │   │   └── 08-codeql-alerts.png
│   │   ├── pylint-before.txt
│   │   ├── radon-cc-before.txt
│   │   ├── radon-mi-before.txt
│   │   ├── radon-raw-before.txt
│   │   └── project-tree-before.txt
```

如果你不想新建目录，也可以继续使用项目根目录中已有的：

- `pylint-before.txt`
- `radon-cc-before.txt`
- `radon-mi-before.txt`
- `radon-raw-before.txt`

## 3. 第一步：保留当前版本作为初始版本

### 3.1 为什么必须先做这一步

实验报告里需要区分：

- 重构前版本
- 重构后版本

如果不先固定一个“起点版本”，后面就很难证明哪些数据属于改进前、哪些属于改进后。因此，建议先做一次正式的 Git 提交，把当前版本作为实验基线。

### 3.2 先检查当前状态

在项目根目录打开 PowerShell，执行：

```powershell
git status
```

你要截图保存当前状态，截图命名建议为：

```text
02-git-status-before-commit.png
```

### 3.3 当前项目的实际情况

当前仓库不是完全干净的，已经存在以下情况：

- `README.md` 有修改
- 项目中有未跟踪的实验文档、指导书、基线文本文件等

这不是错误，但意味着你在做“基线提交”前，要明确本次提交到底要保留哪些内容。

### 3.4 推荐做法

推荐使用以下两种方式之一：

#### 方案 A：将当前整个实验工作区作为基线提交

适合你希望把代码、文档、指导书、基线结果一起纳入实验过程记录。

```powershell
git add .
git commit -m "baseline: initial version before refactor"
```

#### 方案 B：只提交代码和必要配置作为基线

适合你希望提交更干净，只保留项目代码、工作流配置和必要说明。

```powershell
git add main.py models.py services.py storage.py utils.py sample_data.py README.md .github/workflows/codeql.yml
git commit -m "baseline: initial code before refactor"
```

如果你后续还要专门展示“实验过程中的增量演化”，建议使用方案 A，更容易在报告中解释。

### 3.5 可选增强：打标签

为了以后快速定位基线版本，建议打一个标签：

```powershell
git tag baseline-before-refactor
```

如果后续推送到远程仓库，也可以同步推送标签：

```powershell
git push origin baseline-before-refactor
```

### 3.6 这一步要截什么图

至少保存以下 2 张：

- `git status` 执行结果图
- 基线提交后的 `git log --oneline -n 5` 结果图

第二张截图建议命名：

```text
02b-git-log-baseline.png
```

命令如下：

```powershell
git log --oneline -n 5
```

## 4. 第二步：记录当前项目目录结构

### 4.1 为什么要保存目录结构

报告中的“系统结构与演化”部分通常需要说明当前项目在重构前的模块划分，例如：

- `main.py`：CLI 入口
- `services.py`：核心业务逻辑
- `models.py`：实体模型
- `storage.py`：JSON 持久化
- `utils.py`：工具函数

因此，你需要保存一份“重构前项目目录结构”的证据。

### 4.2 推荐方式一：直接截图 VS Code 左侧目录树

这是最适合实验报告的方式，因为老师看起来最直观。

截图要求：

- 显示项目根目录 `library_system`
- 展开 `.github/workflows`
- 展开 `作业文档`（如果你已经新建）
- 保证 `main.py`、`services.py`、`models.py`、`storage.py`、`utils.py`、`README.md` 可见

建议截图命名：

```text
01-project-tree.png
```

### 4.3 推荐方式二：导出文本目录结构

可以额外生成一份文本，便于附录引用。

在 PowerShell 中执行：

```powershell
Get-ChildItem -Recurse | Select-Object FullName | Out-File -Encoding utf8 .\作业文档\baseline\project-tree-before.txt
```

如果 `baseline` 目录还没创建，先执行：

```powershell
New-Item -ItemType Directory -Force .\作业文档\baseline
New-Item -ItemType Directory -Force .\作业文档\baseline\screenshots
```

如果你只想看项目顶层结构，也可以使用：

```powershell
Get-ChildItem | Select-Object Name, Mode | Format-Table -AutoSize
```

然后截图这一页终端内容，作为备用结构证据。

## 5. 第三步：运行 Pylint，保存重构前静态分析结果

### 5.1 Pylint 的作用

`Pylint` 主要用于发现：

- 命名不规范
- 函数过长或参数设计不佳
- 重复逻辑倾向
- 风格问题
- 潜在代码味道

它适合作为实验一中“可读性、可修改性”的初始定量依据。

### 5.2 安装方式

如果还没有安装：

```powershell
python -m pip install pylint
```

### 5.3 推荐执行命令

在项目根目录执行：

```powershell
python -m pylint main.py models.py services.py storage.py utils.py sample_data.py | Tee-Object -FilePath .\作业文档\baseline\pylint-before.txt
```

如果你仍想沿用根目录已有文件名，也可以执行：

```powershell
python -m pylint main.py models.py services.py storage.py utils.py sample_data.py | Tee-Object -FilePath .\pylint-before.txt
```

### 5.4 这一步要截什么图

至少截 1 张图，建议包含：

- 终端顶部能看到执行命令
- 中间有若干实际问题提示
- 底部能看到总体评分或总结信息

建议截图命名：

```text
03-pylint-before.png
```

### 5.5 报告里怎么解释

你可以这样写：

> 在重构前，使用 Pylint 对项目核心 Python 文件进行静态检查，发现代码中存在命名泛化、职责集中、函数过长、结构可读性一般等问题。该结果可作为后续重构前后的定量对比依据。

## 6. 第四步：运行 Radon，记录复杂度与可维护性指标

### 6.1 Radon 的作用

`Radon` 适合测量：

- 圈复杂度（Cyclomatic Complexity）
- 可维护性指数（Maintainability Index）
- 原始代码统计（Raw metrics）

这三项很适合写进实验一报告中的“质量属性度量与结果分析”。

### 6.2 安装方式

如果还没有安装：

```powershell
python -m pip install radon
```

### 6.3 圈复杂度（CC）

执行：

```powershell
python -m radon cc . -s -a | Tee-Object -FilePath .\作业文档\baseline\radon-cc-before.txt
```

如果使用根目录文件：

```powershell
python -m radon cc . -s -a | Tee-Object -FilePath .\radon-cc-before.txt
```

这一步重点关注：

- `borrow_book()`
- `return_book()`
- `book_menu()`
- `user_menu()`
- `borrow_menu()`

如果这些函数复杂度偏高，后续重构就有明确抓手。

截图命名建议：

```text
04-radon-cc-before.png
```

### 6.4 可维护性指数（MI）

执行：

```powershell
python -m radon mi . -s | Tee-Object -FilePath .\作业文档\baseline\radon-mi-before.txt
```

如果使用根目录文件：

```powershell
python -m radon mi . -s | Tee-Object -FilePath .\radon-mi-before.txt
```

截图时尽量让以下信息可见：

- 文件名
- 评级结果（A/B/C）
- 可维护性分数或等级

截图命名建议：

```text
05-radon-mi-before.png
```

### 6.5 原始代码统计（RAW）

执行：

```powershell
python -m radon raw . -s | Tee-Object -FilePath .\作业文档\baseline\radon-raw-before.txt
```

如果使用根目录文件：

```powershell
python -m radon raw . -s | Tee-Object -FilePath .\radon-raw-before.txt
```

该指标主要用于补充说明代码规模，例如：

- 总行数
- 注释行数
- 空行数
- 注释比例

截图命名建议：

```text
06-radon-raw-before.png
```

### 6.6 报告里怎么解释

可以这样写：

> 使用 Radon 对系统进行重构前度量，重点记录圈复杂度、可维护性指数和原始代码统计，为后续函数拆分、职责分离和结构优化提供量化基线。

## 7. 第五步：运行 CodeQL，保存重构前安全/静态分析结果

### 7.1 当前项目已经具备的条件

当前项目已经存在 GitHub Actions 工作流文件：

```text
.github/workflows/codeql.yml
```

配置内容表明：

- 支持 `workflow_dispatch`
- 使用 `python` 语言分析
- 会在 GitHub Actions 中自动执行 CodeQL 扫描

因此，你不需要本地复杂安装，最推荐的方式是直接推送到 GitHub 后执行工作流。

### 7.2 使用前提

你需要满足以下条件：

- 项目已经关联到 GitHub 仓库
- 你有推送权限
- `.github/workflows/codeql.yml` 已经提交到仓库

### 7.3 推荐操作步骤

#### 第一步：推送基线版本

```powershell
git push origin main
```

如果你使用的是 `master` 分支，就换成：

```powershell
git push origin master
```

如果你创建了标签，也可以推送：

```powershell
git push --tags
```

#### 第二步：进入 GitHub 仓库

打开：

- 仓库主页
- `Actions`
- 选择 `CodeQL` 工作流

#### 第三步：手动触发工作流

因为配置里有 `workflow_dispatch`，你可以点击：

- `Run workflow`
- 选择分支 `main` 或 `master`
- 点击运行

#### 第四步：等待运行完成

运行成功后，进入本次工作流详情页，确认：

- `Initialize CodeQL`
- `Autobuild`
- `Perform CodeQL Analysis`

都显示成功。

### 7.4 这一步要截什么图

至少保存 2 张：

#### 图 1：Actions 成功运行页面

页面中应清楚看到：

- 工作流名称 `CodeQL`
- 最近一次运行成功
- 运行时间
- 分支名称

建议命名：

```text
07-codeql-actions-success.png
```

#### 图 2：Code scanning / Security 结果页面

进入：

- `Security`
- `Code scanning`

如果有问题，就截图问题列表；如果没有问题，也截图“0 alerts”页面。

建议命名：

```text
08-codeql-alerts.png
```

### 7.5 报告里怎么解释

你可以这样写：

> 在重构前通过 GitHub Actions 运行 CodeQL 工作流，对项目进行自动化静态安全分析，并保存扫描结果作为基线。CodeQL 结果与 Pylint、Radon 一起构成后续重构前后的对比依据。

## 8. 截图清单与“必须拍到什么”

下面是最推荐的截图清单。

### 8.1 当前项目目录结构

- 文件名：`01-project-tree.png`
- 建议来源：VS Code 左侧目录树
- 必须拍到：
  - `main.py`
  - `services.py`
  - `models.py`
  - `storage.py`
  - `utils.py`
  - `README.md`
  - `.github/workflows/codeql.yml`

### 8.2 Git 当前状态

- 文件名：`02-git-status-before-commit.png`
- 来源：PowerShell 终端
- 必须拍到：
  - 执行命令 `git status`
  - 终端输出

### 8.3 Git 基线提交记录

- 文件名：`02b-git-log-baseline.png`
- 来源：PowerShell 终端
- 必须拍到：
  - 执行命令 `git log --oneline -n 5`
  - 含有 `baseline` 字样的提交

### 8.4 Pylint 结果

- 文件名：`03-pylint-before.png`
- 来源：PowerShell 终端
- 必须拍到：
  - 执行命令
  - 若干问题提示
  - 总体评分或总结信息

### 8.5 Radon 圈复杂度

- 文件名：`04-radon-cc-before.png`
- 来源：PowerShell 终端
- 必须拍到：
  - 执行命令
  - 函数复杂度结果
  - 平均复杂度

### 8.6 Radon 可维护性指数

- 文件名：`05-radon-mi-before.png`
- 来源：PowerShell 终端
- 必须拍到：
  - 执行命令
  - 文件等级
  - 分数或等级结果

### 8.7 Radon 原始统计

- 文件名：`06-radon-raw-before.png`
- 来源：PowerShell 终端
- 必须拍到：
  - 执行命令
  - 代码行数、注释行数、空行等数据

### 8.8 CodeQL 工作流成功页

- 文件名：`07-codeql-actions-success.png`
- 来源：GitHub Actions 页面
- 必须拍到：
  - 工作流名
  - 成功标识
  - 分支
  - 时间

### 8.9 CodeQL 告警页

- 文件名：`08-codeql-alerts.png`
- 来源：GitHub Security 页面
- 必须拍到：
  - Code scanning 页面
  - 告警数量或 0 alerts

## 9. 推荐的完整执行顺序

建议严格按下面顺序操作：

1. 检查当前仓库状态  
   执行 `git status`，截图保存。

2. 创建保存目录  
   执行：

   ```powershell
   New-Item -ItemType Directory -Force .\作业文档\baseline
   New-Item -ItemType Directory -Force .\作业文档\baseline\screenshots
   ```

3. 保存项目目录结构  
   截 VS Code 左侧目录树图，必要时导出文本目录。

4. 提交当前版本为基线  
   执行 `git add`、`git commit`，再执行 `git log --oneline -n 5` 并截图。

5. 运行 `Pylint`  
   保存文本文件与截图。

6. 运行 `Radon cc`  
   保存文本文件与截图。

7. 运行 `Radon mi`  
   保存文本文件与截图。

8. 运行 `Radon raw`  
   保存文本文件与截图。

9. 推送 GitHub 并运行 `CodeQL`  
   保存 Actions 页与 Code scanning 页截图。

10. 将所有截图和文本结果归档  
    按统一命名放到 `作业文档/baseline/` 下。

## 10. 可直接复制执行的命令清单

下面是一套适合直接复制的命令顺序。

### 10.1 创建目录

```powershell
New-Item -ItemType Directory -Force .\作业文档\baseline
New-Item -ItemType Directory -Force .\作业文档\baseline\screenshots
```

### 10.2 查看当前状态

```powershell
git status
```

### 10.3 提交基线版本

```powershell
git add .
git commit -m "baseline: initial version before refactor"
git tag baseline-before-refactor
git log --oneline -n 5
```

### 10.4 导出项目结构

```powershell
Get-ChildItem -Recurse | Select-Object FullName | Out-File -Encoding utf8 .\作业文档\baseline\project-tree-before.txt
```

### 10.5 安装工具

```powershell
python -m pip install pylint radon
```

### 10.6 运行 Pylint

```powershell
python -m pylint main.py models.py services.py storage.py utils.py sample_data.py | Tee-Object -FilePath .\作业文档\baseline\pylint-before.txt
```

### 10.7 运行 Radon

```powershell
python -m radon cc . -s -a | Tee-Object -FilePath .\作业文档\baseline\radon-cc-before.txt
python -m radon mi . -s | Tee-Object -FilePath .\作业文档\baseline\radon-mi-before.txt
python -m radon raw . -s | Tee-Object -FilePath .\作业文档\baseline\radon-raw-before.txt
```

### 10.8 推送并触发 CodeQL

```powershell
git push origin main
git push origin baseline-before-refactor
```

如果标签没有单独推送成功，可以执行：

```powershell
git push --tags
```

## 11. 报告中如何描述这一阶段

你可以在实验报告中这样概述本阶段：

> 在实施重构前，首先对当前图书馆管理系统建立实验基线。具体做法包括：使用 Git 固定重构前初始版本；保存当前项目目录结构；使用 Pylint、Radon 对代码进行静态分析与复杂度度量；使用 GitHub Actions 运行 CodeQL 进行自动化安全分析。上述结果作为后续重构前后质量属性对比的原始依据。

## 12. 常见问题

### 12.1 `git commit` 提示没有配置用户名和邮箱

执行：

```powershell
git config user.name "你的名字"
git config user.email "你的邮箱"
```

如果想全局配置：

```powershell
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

### 12.2 `python -m pylint` 或 `python -m radon` 找不到模块

重新安装：

```powershell
python -m pip install pylint radon
```

### 12.3 GitHub 上看不到 `Actions`

可能原因：

- 仓库未推送
- Actions 未启用
- 当前不是 GitHub 仓库

需要先确认远程仓库：

```powershell
git remote -v
```

### 12.4 CodeQL 没有告警怎么办

没有告警也完全可以作为实验材料使用。你只需要截图“0 alerts”页面，并在报告中说明：

> 重构前 CodeQL 未发现高危安全问题，但该结果仍可作为自动化静态分析基线，并与其他质量度量工具共同支撑实验分析。

## 版本记录

- v1：生成实验前基线建立操作说明，包含 Git 保留初始版本、Pylint/Radon/CodeQL 执行步骤、截图清单与文件命名建议。
