# SmartMetric

SmartMetric 是一个前后端分离的软件度量自动化工具，用于支撑软件度量课程实验。当前仓库已经覆盖需求/设计/代码阶段的一组核心度量能力，并同时提供 Web 端与 CLI 端入口。

功能清单、模块覆盖范围和能力说明已经提取到：

- [docs/06-功能清单.md](D:/works/smart-metric/docs/06-功能清单.md)
- [docs/README.md](D:/works/smart-metric/docs/README.md)

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

生产构建与启动：

```powershell
cd D:\works\smart-metric\frontend
npm run build
npm run start
```

注意：

- 不要直接运行 `frontend/.nuxt/dist/server/server.mjs`，这不是对外启动入口。
- `npm run build` 后应使用 `node .output/server/index.mjs`，仓库里已经封装成 `npm run start`。
- 如果出现 Nuxt 生成物异常，先执行 `npm run clean` 或 `npm run build:clean`。

前端页面包括：

- `/`
- `/usecase-metric`
- `/loc-metric`
- `/function-point`
- `/oo-metric`
- `/cfg-metric`
- `/project-metric`
- `/ai-review`
- `/report-export`

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
python backend\cli.py test path samples\class_diagram_demo.oom
python backend\cli.py test path samples\cfg_demo.json
python backend\cli.py test path tests\estimate_cli_input.json --metric estimate
python backend\cli.py tp samples\cfg_demo.json
python backend\cli.py tb --suite unit
python backend\cli.py ai-review D:\works\smart-metric -F json --phase1-file samples\ai_review_phase1.json --phase2-file samples\ai_review_phase2.json
python backend\cli.py ai-review D:\works\smart-metric -F pdf -P samples\fp.json
python backend\cli.py project-scan D:\works\smart-metric
python backend\cli.py project-report D:\works\smart-metric -F pdf
python backend\cli.py project-scan D:\works\smart-metric --ignore-dir coverage --ignore-glob *.generated.py
python backend\cli.py project-scan D:\works\smart-metric -m inventory,loc,oo -d coverage -g *.generated.py
python backend\cli.py ps D:\works\smart-metric -m inventory,loc
```

通过 CLI 启动后端：

```powershell
python backend\cli.py serve --host 127.0.0.1 --port 5000
```

CLI 计算示例：

```powershell
python backend\cli.py oo-source samples\oo_demo.java
python backend\cli.py oo-diagram samples\class_diagram_demo.xml
python backend\cli.py oo-diagram samples\class_diagram_demo.oom
python backend\cli.py cfg-graph samples\cfg_demo.json
python backend\cli.py oos samples\oo_demo.java
python backend\cli.py cfg samples\cfg_demo.json
python backend\cli.py ai-review D:\works\smart-metric -F pdf -o ai-review.pdf --phase1-file samples\ai_review_phase1.json --phase2-file samples\ai_review_phase2.json
python backend\cli.py project-scan D:\works\smart-metric --modules inventory,loc,dependency,oo,design
python backend\cli.py project-report D:\works\smart-metric -F pdf -o smartmetric-report.pdf -P fp.json
python backend\cli.py report samples\report_demo.json --format markdown
python backend\cli.py report samples\report_demo.json --format pdf
```

项目扫描忽略配置：

- CLI：`--ignore-dir <目录名>` 可重复传入，`--ignore-glob <通配规则>` 可重复传入，`--no-default-ignore` 可关闭默认忽略目录。
- CLI：`--ignore-file <文件名>` 可指定忽略文件名，`--no-ignore-file` 可关闭忽略文件读取。
- Web：打开 `/project-metric`，填写项目路径后，在“忽略目录”和“忽略通配规则”文本框中按行配置，也会自动读取项目根目录下的 `.smartmetricignore`。

`.smartmetricignore`：

- 默认文件名是项目根目录下的 `.smartmetricignore`
- 空行和 `#` 开头的行会忽略
- 常用语义尽量对齐 `.gitignore`
- 纯名称按目录名规则处理，例如 `coverage`
- 带通配符或路径的规则按 glob 处理，例如 `*.generated.py`、`frontend/dist/*`
- `!` 可用于反向包含，例如 `!/logs/keep.py`
- `/` 开头表示相对项目根目录，例如 `/logs/`

AI 审查：

- 默认通过 LangChain + OpenAI 两阶段审查：
  - 第一轮读取项目度量摘要并输出重点文件
  - 第二轮读取本地源码片段并输出改进建议
- 可通过环境变量配置：
  - `OPENAI_API_KEY`
  - `OPENAI_API_BASE`
  - `OPENAI_MODEL`
- 也可通过本地配置文件配置：
  - 模板文件：`backend/config/ai_review.example.json`
  - 本地文件：`backend/config/ai_review.local.json`
  - `ai_review.local.json` 已被 Git 忽略，不会提交
- 离线测试可通过 `--phase1-file` / `--phase2-file` 提供固定 JSON 结果

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

[scripts/README.md](./scripts/README.md)

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
- `POST /api/export/report`

## 样例文件

样例位于 `samples/`，当前主要包括：

- `sample_usecase.oom`
- `SampleStudent.java`
- `sample_script.py`
- `sample_algo.cpp`
- `oo_demo.java`
- `class_diagram_demo.xml`
- `class_diagram_demo.oom`
- `cfg_demo.json`
- `cfg_demo.mmd`
- `cfg_demo.dot`
- `cfg_demo.oom`
- `report_demo.json`

## 协作与提交

请先阅读：

[CONTRIBUTING.md](./CONTRIBUTING.md)

如果是 agent 接手仓库，还要先读：

[AGENTS.md](./AGENTS.md)



## License
[Apache-2.0](./LICENSE)
