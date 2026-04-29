# 后端 Agent 规约

修改后端代码后，必须回看并更新本文档；如果修改涉及度量模型，还要同步更新 `agents/metrics.md`；如果修改涉及测试，还要同步更新 `agents/testing.md`。

## 不要做的事

- 不要把新业务逻辑直接写进 `backend/app.py`。
- 不要随意改已有接口返回格式。
- 不要把上传文件落盘到仓库，除非任务明确要求。
- 不要引入重依赖，除非有测试和说明。

## 推荐新增后端功能方式

新增核心模块：

```text
backend/core/<module_name>/
  __init__.py
  service.py
```

新增路由模块：

```text
backend/routes/<module_routes>.py
```

在 `backend/app.py` 只做最小注册：

```python
from routes.<module_routes> import <blueprint>
app.register_blueprint(<blueprint>)
```

## API 返回格式

现有后端多数接口使用：

```json
{
  "success": true,
  "data": {}
}
```

错误格式：

```json
{
  "success": false,
  "message": "错误说明"
}
```

新增接口应保持一致。

本机系统对话框接口：

```text
POST /api/system/pick-directory
```

约束：

```text
该接口用于本机开发/演示环境
由后端弹出系统目录选择框，再把选中路径返回前端
不要把它设计成远程部署环境下的通用能力
```

## 当前路由模块

```text
backend/routes/metrics_45.py
  功能点度量
  控制流图源码分析
  控制流图导入（JSON / Mermaid / DOT / OOM / XML）

backend/routes/metrics_oo_estimate.py
  面向对象 CK/LK 度量
  类图级 OO 度量
  项目估算

backend/routes/system_dialog.py
  本机系统目录选择对话框
  为 project-metric / ai-review 页面提供目录选择能力
```

后端依赖中包含：

```text
javalang
reportlab
```

用途：Java 控制流图 AST 策略。
`reportlab` 用于 PDF 报告导出。

## 当前核心模块

```text
backend/core/loc_metric/
backend/core/usecase_metric/
backend/core/function_point_metric/
backend/core/cfg_metric/
backend/core/oo_metric/
backend/core/estimate_metric/
backend/core/diagram_parser/
backend/core/class_diagram_metric/
backend/core/project_metric/
```

`backend/core/loc_metric/` 当前输出约定：

```text
/api/metrics/loc/calculate 不再只返回 Java 结构化结果
Java/Python/C++ 文件都会尝试生成 structure_summaries、class_scales、method_scales
class_scales 统一包含 class_name/method_count/field_count/rfc/lcom
method_scales 至少包含 class_name/method_name，并与前端方法级表格对齐
```

CLI 入口：

```text
backend/cli.py
backend/cli_app/
```

CLI 不替代 Web，但属于正式入口之一。新增度量模块时，如果输入适合文件/JSON 调用，应评估是否补 CLI 子命令。

当前 CLI 同时支持后端启动：

```powershell
python backend\cli.py serve --host 127.0.0.1 --port 5000
```

项目目录级扫描：

```powershell
python backend\cli.py project-scan D:\works\smart-metric
python backend\cli.py project-scan D:\works\smart-metric --modules inventory,loc,dependency,oo,design
python backend\cli.py project-scan D:\works\smart-metric --ignore-dir coverage --ignore-glob *.generated.py
```

并支持统一测试入口：

```powershell
python backend\cli.py test backend --suite all --start-server
python backend\cli.py test path <文件路径> [--metric ...]
```

CLI 设计要求：

```text
命令模式：backend/cli_app/commands/*.py
帮助资源外置：backend/cli_app/i18n/*.json
命令逻辑复用：backend/core/*
命令需同时保留长命令和短别名
常用选项需同时保留长参数和短参数（如 -L/-l/-m/-o/-H/-p/-s）
根帮助仅展示主命令，短别名单独下一行展示
help/help -a 作为正式命令存在，交互终端下帮助输出支持分页
```

报告导出：

```text
backend/core/report_export.py
/api/export/report
backend/cli.py report
```

项目目录级扫描模块：

```text
backend/core/project_metric/
backend/cli.py project-scan
backend/cli.py project-report
backend/core/ai_review/
backend/cli.py ai-review
```

职责：

```text
递归扫描项目目录
统计总代码量与各文件 LoC
分析源码依赖关系
排查上帝文件与上帝类
清点并分析用例图/类图/控制流图设计文件
构建项目级总报告并导出 markdown/html/pdf
基于本地度量结果和源码片段执行两阶段 AI 审查
```

AI 审查模块：

```text
backend/core/ai_review/
  prompting.py           prompt 变量构建
  context_builder.py     本地报告转 AI 上下文
  source_selector.py     重点文件选择与源码裁剪
  langchain_adapter.py   LangChain/OpenAI 适配层
  config.py              本地配置文件与环境变量合并
  service.py             两阶段审查主流程
backend/config/ai_review.example.json
backend/config/ai_review.local.json
```

约束：

```text
AI 审查必须先复用本地 project-scan / loc / cfg / oo 结果
不要让模型直接读取整个仓库
优先使用结构化 JSON 返回，不依赖自由文本
fixture 模式用于离线测试，真实模式依赖 OPENAI_API_KEY
本地配置文件使用 example 入库、local 忽略的模式
```

忽略配置：

```text
默认忽略 .git/.venv/node_modules/.nuxt/.output/dist/build 等目录
自动读取项目根目录 .smartmetricignore
CLI 可追加 --ignore-dir 和 --ignore-glob
CLI 可通过 --ignore-file 指定文件名，或 --no-ignore-file 关闭
CLI 同时提供短参数 -m/-d/-g/-f/-G/-D
后端 API: POST /api/metrics/project/scan
```

## 多语言控制流设计

控制流图模块采用策略模式：

```text
backend/core/cfg_metric/strategies/base.py
backend/core/cfg_metric/strategies/c_style.py
backend/core/cfg_metric/strategies/python_strategy.py
backend/core/cfg_metric/strategies/factory.py
```

新增语言时：

1. 新增 `<language>_strategy.py`。
2. 实现 `ControlFlowAnalyzer` 接口。
3. 在 `factory.py` 注册。
4. 补测试。

不要把所有语言规则继续塞进一个函数。

## 面向对象度量

当前位置：

```text
backend/core/oo_metric/
```

当前源码级度量采用策略模式，支持：

```text
Java
C
C++
Python
JavaScript
```

输出 CK 指标：

```text
WMC
DIT
NOC
CBO
RFC
LCOM
```

LK/规模类指标：

```text
NOM
NOA
class_loc
avg_method_complexity
```

后续若升级 ASTParser，保持 `analyze_oo_files(files)` 的输出结构不变。

类图级 OO 度量位置：

```text
backend/core/class_diagram_metric/
```

类图解析约定：

```text
支持 .xml / .oom 文件
支持嵌套在 class 节点下的 Attribute / Operation
解析属性名时应兼容 name / Name 等大小写差异
演示样例包含 samples/class_diagram_demo.xml 和 samples/class_diagram_demo.oom
```

源码级策略位置：

```text
backend/core/oo_metric/strategies/
```

## 后端测试

运行当前新增模块测试：

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_45_metrics tests.test_oo_estimate_metrics
```

若新增后端模块，新增对应 `tests/test_*.py`。
