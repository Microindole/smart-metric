# 控制流图度量设计说明

本模块用于完成实验指导书中的“控制流图度量”和“圈复杂度度量”。

## 设计模式

模块采用策略模式：

```text
ControlFlowAnalyzer
  ├─ JavaAstAnalyzer     Java，基于 javalang
  ├─ PythonAstAnalyzer   Python，基于标准库 ast
  └─ CStyleAnalyzer      C / C++，规则分析
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

当前是“AST 策略 + 规则策略”的混合实现。

已启用 AST 的语言：

```text
Python -> 标准库 ast
Java   -> javalang
```

继续使用规则策略的语言：

```text
C/C++ -> CStyleAnalyzer
```

Java/Python AST 解析失败时，会 fallback 到原规则策略，避免接口直接失败。

## 后续 AST 升级建议

```text
Java       -> 当前使用 javalang；后续可升级 JavaParser / Eclipse ASTParser
C/C++      -> 当前规则分析；后续可升级 libclang / clang AST
Python     -> 当前使用 ast；后续可细化 ast.NodeVisitor
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
