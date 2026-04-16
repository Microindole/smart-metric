# SmartMetric Agent 执行规约

本目录只面向后续 agent，不是用户手册，也不是实验报告正文。

agent 接手任务时，先读根目录 `AGENTS.md`，再读本文件，然后按任务类型读取对应文件：

```text
agents/backend.md
agents/frontend.md
agents/metrics.md
agents/testing.md
agents/git.md
```

## 文档同步强制规则

任何代码变更后，agent 必须同步检查 `agents/` 文档是否需要更新。

必须更新的情况：

- 后端接口、路由、核心模块、返回结构发生变化。
- 前端页面、菜单、启动方式、API 调用方式发生变化。
- 度量模型、公式、指标含义、输入输出发生变化。
- 测试命令、样例文件、验证步骤发生变化。
- Git 配置、提交流程、协作规则发生变化。

若代码变更不需要更新文档，最终回复必须写明：

```text
本次代码变更不影响 agents 文档，原因：...
```

## 任务前必须做

1. 查看工作区状态：

```powershell
git status --short
```

2. 查看最近提交：

```powershell
git log -5 --oneline
```

3. 不要假设当前代码等于历史上下文。必须以本地文件为准。

4. 若存在用户未提交改动，不要覆盖。先判断是否与当前任务相关：

- 无关：避开该文件。
- 相关：读清楚后在现有改动上继续。
- 冲突严重：停下说明风险。

## 项目定位

SmartMetric 是前后端分离的软件度量自动化工具。

当前主要功能：

```text
用例点 UCP
代码行 LoC
功能点 FP
控制流图/圈复杂度
面向对象 CK/LK
项目目录级扫描（代码量、依赖、设计图、上帝文件）
项目工作量/成本/工期/人员估算
CSV 导出
CLI 调用入口
根目录 scripts 自动化测试
Markdown/HTML/PDF 报告导出
```

技术栈：

```text
后端：Python Flask
前端：Nuxt 3 + Ant Design Vue + Axios
测试：Python unittest
```

## 总体架构

```text
frontend/pages/*.vue
  -> frontend/utils/api.js
    -> backend/app.py
      -> backend/routes/*.py
        -> backend/core/<metric_module>/
```

后端业务逻辑不得直接堆进 `backend/app.py`。`app.py` 只做：

```text
Flask app 创建
CORS
已有基础路由
蓝图注册
```

新增功能优先采用：

```text
backend/core/<module_name>/
backend/routes/<route_name>.py
frontend/pages/<page-name>.vue
tests/test_<module_name>.py
```

## 当前重要入口

后端入口：

```text
backend/app.py
```

前端入口：

```text
frontend/app.vue
frontend/pages/index.vue
frontend/components/AppLayout.vue
```

Axios 配置：

```text
frontend/utils/api.js
```

## 启动命令

后端：

```powershell
cd D:\works\smart-metric
.\.venv\Scripts\Activate.ps1
python backend\app.py
```

前端：

```powershell
cd D:\works\smart-metric\frontend
npm run dev
```

若 Nuxt 卡住，优先读 `agents/frontend.md` 的故障处理，不要反复跑 `npm run build`。

CLI：

```powershell
cd D:\works\smart-metric
.\.venv\Scripts\Activate.ps1
python backend\cli.py --help
```

CLI 启动后端：

```powershell
python backend\cli.py serve --host 127.0.0.1 --port 5000
```

统一 CLI 测试：

```powershell
python backend\cli.py test backend --suite all --start-server
python backend\cli.py test path samples\class_diagram_demo.xml
python backend\cli.py project-scan D:\works\smart-metric
```

## 开发原则

- 小步修改。
- 尽量新增模块文件，少改公共文件。
- 必须改公共入口时，只做最小注册或最小导航修改。
- 不要删除已有样例、测试、空占位文件，除非用户明确要求。
- 不要提交 `.venv/`、`node_modules/`、`.nuxt/`、`.output/`、`__pycache__/`。
- 修改后必须运行相关测试。

## 指导书覆盖重点

指导书要求不是只做页面，必须能说明度量模型和实现方法。

当前功能映射：

```text
LoC                 backend/core/loc_metric/
UCP                 backend/core/usecase_metric/
FP                  backend/core/function_point_metric/
CFG/圈复杂度         backend/core/cfg_metric/
CK/LK               backend/core/oo_metric/
项目目录级扫描       backend/core/project_metric/
估算                backend/core/estimate_metric/
UML/OOM 解析         backend/core/diagram_parser/
类图级 OO            backend/core/class_diagram_metric/
```

## 关于 AST

不要把“所有度量都要 AST”理解错。

- 功能点 FP：不依赖 AST，属于需求/设计规模度量。
- 控制流图/圈复杂度：适合 AST 或语言语法策略。
- CK/LK：适合 Java AST 或类结构分析。

当前实现：

```text
CFG：策略模式 + 规则分析，预留 AST 替换点。
OO：Java 轻量类结构分析，预留 JavaParser/Eclipse ASTParser 替换空间。
```

如果用户要求“更符合 ASTParser”，优先在现有策略接口内替换某个语言 analyzer，不要推翻 API。
