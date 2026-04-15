# 控制流图度量设计说明

本模块用于完成实验指导书中的“控制流图度量”和“圈复杂度度量”。

## 设计模式

模块采用策略模式：

```text
ControlFlowAnalyzer
  ├─ CStyleAnalyzer      Java / C / C++
  └─ PythonAnalyzer      Python
```

工厂方法：

```text
strategies/factory.py -> create_analyzer(language)
```

服务入口：

```text
service.py -> analyze_cfg_files(...)
```

路由入口：

```text
backend/routes/metrics_45.py
```

## 为什么这样设计

控制流图度量和圈复杂度依赖语言语法结构。不同语言的条件、循环、异常处理、短路表达式写法不同，因此不适合把所有规则写在一个函数里。

策略模式的好处：

- 每种语言的识别逻辑独立。
- 新增语言只需要新增一个 Analyzer。
- 现有 API 和前端不用跟着改。
- 后续可以把规则分析替换成 AST 分析。

## 当前实现方式

当前是轻量级规则分析，不是完整 AST。

原因：

- Java 的 AST 通常需要 Eclipse ASTParser、JavaParser 或 javalang。
- C/C++ 的 AST 通常需要 clang。
- Python 可以用标准库 ast，但为了和多语言接口保持一致，当前先统一采用规则策略。

当前实现已经预留替换点：只要实现 `ControlFlowAnalyzer` 接口，就能替换为 AST 版本。

## 后续 AST 升级建议

```text
Java       -> JavaParser / Eclipse ASTParser / javalang
C/C++      -> libclang / clang AST
Python     -> ast.NodeVisitor
```

升级时保持输出字段不变：

```text
language
analysis_method
decision_points
cyclomatic_complexity
formula_complexity
summary
nodes
edges
mermaid
```
