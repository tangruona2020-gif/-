# Goods Popup Monitor

日本官方活动站点的个人用监控框架。它维护关注 IP，手动扫描活动卡片，只为命中的 IP 深入解析详情，并保留来源文本、链接和图片元数据。第一版完整适配器是 THEキャラ；其余 14 个来源仅有默认关闭的种子配置，不伪造抓取结果。

## 已实现与边界

已实现 SQLAlchemy/SQLite 数据模型、Alembic、REST API、最小 Dashboard、IP/别名管理 API、手动扫描 CLI、THEキャラ的离线可测解析、活动分类、入场信息、商品图候选、哈希、规则去重和异常空结果保护。当前管理页以 Dashboard 和自动生成的 `/docs` 管理 API 为主；完整表单式 CRUD 页面、浏览器渲染回退、两层关联页递归、截图和图片版本写库仍待完善。

系统不会登录、绕过验证码、抽选、购票或付款。外部请求可用 `ENABLE_EXTERNAL_REQUESTS=false` 总开关关闭。真实站点结构和使用规则可能变化；请低频、人工触发并遵守 robots.txt 与条款。

## 环境隔离与安装

所有依赖只进入本目录的 `.venv`，SQLite 位于 `data/app.db`，图片、日志、临时文件分别位于 `data/images`、`data/logs`、`data/tmp`。不修改 PATH，不安装 Node 依赖，不创建系统定时任务。

Windows（需先安装 Python 3.12 或 uv）：

```powershell
cd goods-popup-monitor
.\scripts\setup.ps1
.\scripts\run.ps1
```

macOS/Linux：

```sh
cd goods-popup-monitor
chmod +x scripts/*.sh
./scripts/setup.sh
./scripts/run.sh
```

打开 <http://127.0.0.1:8000/>；交互式 API 在 `/docs`。复制生成的 `.env` 只保留在本机。

## 使用

IP 可通过 `/docs` 的 `POST /api/ip-titles` 添加，再用 `POST /api/ip-titles/{id}/aliases` 添加日文、英文、中文、简称或系列名；也可修改、停用或删除演示数据。手动扫描：

```powershell
.\scripts\scan.ps1
# 或
.\.venv\Scripts\python.exe -m app.cli.scan --source the_chara
```

全部启用来源可运行 `python -m app.cli.scan --all`；未实现的适配器会明确报错。扫描记录在数据库 `/api/scans`，应用运行日志目录为 `data/logs/`。

## 开发与扩展

新增网站时继承 `app.adapters.base.BaseAdapter`，把站点选择器集中在新适配器模块，并在 `registry.py` 注册。通用匹配、分类、日期、图片与去重逻辑放在 `services/`。测试优先保存匿名化 HTML 到 `tests/fixtures/`，实时测试标记为 `integration`。

```sh
.venv/bin/python -m pytest
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy app
```

## 卸载

先停止 Uvicorn，然后删除整个 `goods-popup-monitor` 文件夹即可。项目没有全局依赖或系统任务，无需清理系统 Python、Node 或数据库环境。

## 已知限制

THEキャラ真实网页可能依赖 JavaScript 或改变 DOM；当前解析器有标题/相邻 DOM 后备策略并会在结构失效时明确失败，但仍需用实时页面定期人工验证。未提供 OCR、商品拆分或自动交易能力。演示 IP 仅用于说明，可由用户删除。
