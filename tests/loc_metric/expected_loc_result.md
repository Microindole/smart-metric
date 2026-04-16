# 代码行度量预期结果（按当前实现）

> 说明：以下预期基于当前 `backend/core/loc_metric/scanner.py` 的规则（注释与代码同一行时，该行计入代码行，不计入注释行）。

## 单文件预期

- `JavaCase.java`
  - total_lines: 49
  - blank_lines: 7
  - comment_lines: 0
  - code_lines: 42
  - class_count: 1
  - method_count: 6

- `python_case.py`
  - total_lines: 23
  - blank_lines: 7
  - comment_lines: 2
  - code_lines: 14

- `cpp_case.cpp`
  - total_lines: 22
  - blank_lines: 2
  - comment_lines: 1
  - code_lines: 19

## 三文件一起上传汇总预期

- total_lines: 91
- blank_lines: 14
- comment_lines: 3
- code_lines: 74
- comment_ratio: 0.033（前端约 3%）
- class_count: 1
- method_count: 6

## Java 代码辅助度量预期（新增）

- java_structure_summaries（`JavaCase.java`）
  - class_count: 1
  - method_count: 6
  - condition_count: 4
  - loop_count: 1

- class_scales（`JavaCase`）
  - field_count: 3
  - method_count: 6
  - rfc: 9
  - lcom: 0

- method_scales（示例观察点）
  - `formatProfile` 调用 `computeLevel`
  - `exportSummary` 调用 `normalizeName`、`formatProfile`
