# Contributing

本文件面向仓库协作者，说明开发、测试和提交流程。

## 基本原则

- 先看当前工作区状态，再开始修改
- 优先新增模块文件，少改公共入口
- 修改后必须运行相关测试
- 不要提交 `.venv/`、`node_modules/`、`.nuxt/`、`.output/`、`__pycache__/`
- 不要覆盖他人未提交改动

## 开发前检查

```powershell
git status --short
git log -5 --oneline
```

## 环境准备

### 后端

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

### 前端

```powershell
cd frontend
npm install
```

## 启动方式

### Web

后端：

```powershell
python backend\app.py
```

前端：

```powershell
cd frontend
npm run dev
```

### CLI

查看命令：

```powershell
python backend\cli.py --help
```

启动后端：

```powershell
python backend\cli.py serve --host 127.0.0.1 --port 5000
```

统一测试：

```powershell
python backend\cli.py test backend --suite all --start-server
```

按路径自动识别度量：

```powershell
python backend\cli.py test path <文件路径>
```

项目目录级扫描：

```powershell
python backend\cli.py project-scan <项目目录>
python backend\cli.py project-scan D:\works\smart-metric --modules inventory,loc,dependency,oo,design
python backend\cli.py project-scan D:\works\smart-metric --ignore-dir coverage --ignore-glob *.generated.py
python backend\cli.py project-scan D:\works\smart-metric --ignore-file .smartmetricignore
python backend\cli.py project-scan D:\works\smart-metric -m inventory,loc -d coverage -g *.generated.py
```

报告导出：

```powershell
python backend\cli.py report samples\report_demo.json --format markdown
python backend\cli.py report samples\report_demo.json --format html
python backend\cli.py report samples\report_demo.json --format pdf
```

## 自动化测试

推荐统一入口：

```powershell
python scripts\run_backend_tests.py --suite all --start-server
```

只跑单元测试：

```powershell
python scripts\run_backend_tests.py --suite unit
```

只跑接口冒烟测试：

```powershell
python scripts\run_backend_tests.py --suite smoke --start-server
```

## 目录约定

- 后端核心模块：`backend/core/<module_name>/`
- 后端路由：`backend/routes/`
- 前端页面：`frontend/pages/`
- 自动化测试脚本：`scripts/`
- 单元测试：`tests/`
- 样例文件：`samples/`

## 提交建议

- 一次提交只解决一类问题
- 功能代码、测试、文档尽量同批提交
- 提交前确认：
  - 相关测试通过
  - `README.md` / `CONTRIBUTING.md` / `agents/` 是否需要同步更新

## Agent 协作

agent 协作规约不写在本文件，固定入口在：

```text
AGENTS.md
```
