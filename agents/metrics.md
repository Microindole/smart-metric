# 度量模块 Agent 规约

修改任意度量模型、公式、指标含义、输入输出、策略模式实现后，必须同步更新本文档。

本文件描述各度量模块的边界。不要把不同度量模型混在一起。

## LoC 代码行度量

位置：

```text
backend/core/loc_metric/
frontend/pages/loc-metric.vue
```

职责：

```text
总行数
空行
注释行
有效代码行
Java 结构辅助分析
```

## 用例点 UCP

位置：

```text
backend/core/usecase_metric/
frontend/pages/usecase-metric.vue
```

职责：

```text
UUC
UAW
TCF
EF
UCP
.oom 用例图解析
```

## 功能点 FP

位置：

```text
backend/core/function_point_metric/
frontend/pages/function-point.vue
```

职责：

```text
EI / EO / EQ / ILF / EIF
UFP
14 个 GSC 因子
VAF
FP
```

注意：

```text
功能点不需要 AST。
它是需求/设计阶段的功能规模度量。
```

## 控制流图 CFG / 圈复杂度

位置：

```text
backend/core/cfg_metric/
frontend/pages/cfg-metric.vue
```

职责：

```text
从源码生成控制流图
导入 JSON/Mermaid/DOT/OOM/XML 控制流图
计算 V(G)=E-N+2P
计算 decision_points + 1
```

设计：

```text
策略模式
JavaAstAnalyzer   -> Java，基于 javalang
PythonAstAnalyzer -> Python，基于标准库 ast
CStyleAnalyzer    -> C/C++，规则分析
```

Java/Python AST 解析失败时会 fallback 到规则策略，接口不直接崩溃。

如果用户要求 AI 识别图片流程图，不要默认接入 AI。当前支持的是结构化图：

```text
JSON
Mermaid
DOT
OOM
XML
```

图片识别应作为扩展功能，需要单独说明准确性和依赖。

## 面向对象 CK/LK

位置：

```text
backend/core/oo_metric/
frontend/pages/oo-metric.vue
```

职责：

```text
WMC
DIT
NOC
CBO
RFC
LCOM
NOM
NOA
class_loc
avg_method_complexity
```

当前支持：

```text
Java / C / C++ / Python / JavaScript 源码
策略模式
```

另外已支持类图级 OO 度量：

```text
backend/core/class_diagram_metric/
```

输入：

```text
.xml
.oom
```

输出：

```text
类图级 DIT
NOC
CBO
NOM
NOA
关系数
```

升级方向：

```text
JavaParser
Eclipse ASTParser
javalang
```

## 项目估算

位置：

```text
backend/core/estimate_metric/
frontend/pages/estimate-metric.vue
```

职责：

```text
工作量（小时）
工作量（人月）
成本
工期（月）
建议人数
```

输入可来自：

```text
FP
UCP
LoC
```

## CLI

CLI 入口：

```text
backend/cli.py
backend/cli_app/
```

当前子命令：

```text
serve
test backend
test path
oo-source
oo-diagram
fp
cfg-source
cfg-graph
estimate
```
