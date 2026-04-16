# SmartMetric

SmartMetric 是一个前后端分离的软件度量自动化工具，用于支撑软件度量课程实验。当前仓库已经覆盖需求/设计/代码阶段的一组核心度量能力，并同时提供 Web 端与 CLI 端入口。

## 当前已实现

- 用例点度量 `UUC / UAW / TCF / EF / UCP`
- 代码行度量 `LoC`
- 功能点度量 `FP`
- 控制流图导入与圈复杂度度量
- 源码控制流分析（Java / Python / C / C++）
- 面向对象度量 `CK / LK`（源码级支持 Java / C / C++ / Python / JavaScript）
- 类图级 OO 度量（`.xml` / `.oom`）
- 项目工作量 / 成本 / 工期 / 人员估算
- CSV 导出
- 根目录自动化测试脚本

## 目录结构

```text
smart-metric/
├── backend/       Flask 后端、CLI、核心度量模块
├── frontend/      Nuxt 3 前端页面
├── samples/       样例输入文件
├── tests/         Python unittest
├── scripts/       根目录自动化测试脚本
├── agents/        面向 agent 的仓库协作规约
├── docs/          课程文档与报告材料
└── CONTRIBUTING.md
```

## 快速启动

### 1. 后端 Web 服务

```powershell
cd D:\works\smart-metric
.\.venv\Scripts\Activate.ps1
python backend\app.py
```

默认地址：

```text
http://127.0.0.1:5000
```

### 2. 前端

```powershell
cd D:\works\smart-metric\frontend
npm install
npm run dev
```

默认地址：

```text
http://127.0.0.1:3000
```

### 3. CLI 入口

查看帮助：

```powershell
cd D:\works\smart-metric
.\.venv\Scripts\Activate.ps1
python backend\cli.py --help
```

统一测试入口：

```powershell
python backend\cli.py test backend --suite all --start-server
```

按路径自动识别并度量：

```powershell
python backend\cli.py test path samples\class_diagram_demo.xml
python backend\cli.py test path samples\cfg_demo.json
python backend\cli.py test path tests\estimate_cli_input.json --metric estimate
```

通过 CLI 启动后端：

```powershell
python backend\cli.py serve --host 127.0.0.1 --port 5000
```

CLI 计算示例：

```powershell
python backend\cli.py oo-source samples\oo_demo.java
python backend\cli.py oo-diagram samples\class_diagram_demo.xml
python backend\cli.py cfg-graph samples\cfg_demo.json
```

## 自动化测试

统一入口：

```powershell
.\.venv\Scripts\python.exe scripts\run_backend_tests.py --suite all --start-server
```

常用命令：

```powershell
.\.venv\Scripts\python.exe scripts\run_backend_tests.py --suite unit
.\.venv\Scripts\python.exe scripts\run_backend_tests.py --suite smoke --start-server
```

说明见：

```text
scripts/README.md
```

## 核心接口

- `GET /api/health`
- `GET /api/metrics/usecase/default-factors`
- `POST /api/metrics/usecase/parse-oom`
- `POST /api/metrics/usecase/calculate`
- `POST /api/metrics/loc/calculate`
- `GET /api/metrics/function-point/defaults`
- `POST /api/metrics/function-point/calculate`
- `POST /api/metrics/cfg/calculate`
- `POST /api/metrics/cfg/import-graph`
- `POST /api/metrics/oo/calculate`
- `POST /api/metrics/oo/diagram-calculate`
- `POST /api/metrics/estimate/calculate`
- `POST /api/export`

## 样例文件

样例位于 `samples/`，当前主要包括：

- `sample_usecase.oom`
- `SampleStudent.java`
- `sample_script.py`
- `sample_algo.cpp`
- `oo_demo.java`
- `class_diagram_demo.xml`
- `cfg_demo.json`
- `cfg_demo.mmd`
- `cfg_demo.dot`

## 协作与提交

请先阅读：

```text
CONTRIBUTING.md
```

如果是 agent 接手仓库，还要先读：

```text
AGENTS.md
```


## License
[Apache-2.0](./LICENSE)
