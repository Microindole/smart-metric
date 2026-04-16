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
```

职责：

```text
递归扫描项目目录
统计总代码量与各文件 LoC
分析源码依赖关系
排查上帝文件与上帝类
清点并分析用例图/类图/控制流图设计文件
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
