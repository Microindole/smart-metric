# SmartMetric 完整验收用例

本文档是一条端到端验收用例，用来确认 SmartMetric 作为软件度量产品可用，而不是只展示页面入口。覆盖核心度量、项目级工具、报告管线和自动化验证。

## 用例编号

SM-E2E-001

## 验收目标

验证以下能力形成闭环：

- 用例点度量 UCP
- 代码行度量 LoC
- 功能点度量 FP
- 面向对象度量 OO / CK / LK
- 控制流图与圈复杂度 CFG
- 项目扫描
- 报告导出

## 前置条件

后端已启动：

```powershell
cd E:\smart-metric
.\.venv\Scripts\python.exe backend\app.py
```

前端已启动：

```powershell
cd E:\smart-metric\frontend
npm run dev:fast -- --host 127.0.0.1 --port 3000
```

打开：

```text
http://127.0.0.1:3000/
```

## 测试数据

使用仓库内置样例：

```text
samples/SampleStudent.java
samples/oo_demo.java
samples/class_diagram_demo.xml
samples/sample_script.py
samples/cfg_complex_demo.py
samples/cfg_demo.json
samples/cfg_login_flow.json
samples/report_demo.json
samples/
```

## 页面验收流程

### 1. 首页和命令面板

操作：

1. 打开首页。
2. 点击侧栏“命令面板”。
3. 搜索 `OO`、`报告`、`项目扫描`。
4. 选择任一结果进入对应页面。

预期：

- 首页表现为产品工作台，不出现“实验步骤”或报告书式检查清单。
- 命令面板可以搜索并跳转到模块。
- 路由跳转后页面仍保持统一侧栏和页面标题。

### 2. 用例点度量 UCP

页面：

```text
/usecase-metric
```

输入：

```text
用例数量：
simple = 2
average = 1
complex = 1

参与者数量：
simple = 1
average = 1
complex = 0

TCF / EF 因子保持默认 0
```

操作：

1. 填写上述数量。
2. 点击计算。
3. 点击导出 CSV。

预期结果：

```text
UUC = 35
UAW = 3
TCF = 0.6
EF = 1.4
UCP = 31.92
```

### 3. 代码行度量 LoC

页面：

```text
/loc-metric
```

输入：

```text
samples/SampleStudent.java
```

操作：

1. 语言选择自动识别。
2. 上传文件并点击计算。
3. 点击导出 CSV。

预期结果：

```text
total_lines = 16
code_lines = 11
comment_lines = 2
blank_lines = 3
class_count = 1
method_count = 2
comment_ratio = 0.125
```

### 4. 功能点度量 FP

页面：

```text
/function-point
```

输入：

```text
EI: simple = 2, average = 1, complex = 0
EO: simple = 1, average = 0, complex = 0
EQ: simple = 0, average = 1, complex = 0
ILF: simple = 1, average = 0, complex = 0
EIF: simple = 1, average = 0, complex = 0

14 个 GSC 因子全部设为 3
```

操作：

1. 填写功能计数。
2. 将所有 GSC 因子设为 3。
3. 点击计算。
4. 点击导出 CSV。

预期结果：

```text
UFP = 30
GSC_TOTAL = 42
VAF = 1.07
FP = 32.1
```

### 5. 面向对象度量 OO

页面：

```text
/oo-metric
```

源码级输入：

```text
samples/oo_demo.java
```

操作：

1. 选择源码级 CK/LK。
2. 语言选择自动识别。
3. 上传 `oo_demo.java` 并点击计算。
4. 点击导出 CSV。

预期结果：

```text
class_count = 3
total_methods = 4
total_attributes = 3
average_wmc = 2.0
max_dit = 1
max_cbo = 2
```

类图级输入：

```text
samples/class_diagram_demo.xml
```

预期：

```text
class_count = 3
```

### 6. 控制流图度量 CFG

页面：

```text
/cfg-metric
```

源码级输入：

```text
基础样例：samples/sample_script.py
复杂度演示样例：samples/cfg_complex_demo.py
```

基础样例预期结果：

```text
file_count = 1
max_complexity = 1
total_decision_points = 0
```

复杂度演示样例预期结果：

```text
file_count = 1
max_complexity = 12
total_decision_points = 11
```

图文件输入：

```text
常见业务流程样例：samples/cfg_login_flow.json
最小分支样例：samples/cfg_demo.json
```

常见业务流程样例预期结果：

```text
node_count = 14
edge_count = 17
cyclomatic_complexity = 5
```

最小分支样例预期结果：

```text
node_count = 6
edge_count = 6
cyclomatic_complexity = 2
```

### 7. 项目扫描

页面：

```text
/project-metric
```

输入：

```text
E:\smart-metric\samples
```

操作：

1. 输入样例目录路径。
2. 保持默认扫描选项。
3. 点击项目扫描。

预期结果：

```text
total_files = 11
code_file_count = 4
design_file_count = 6
total_lines = 65
code_lines = 44
class_count = 5
usecase_diagram_count = 1
class_diagram_count = 1
cfg_graph_count = 4
god_files = 0
god_classes = 0
```

输入：

```text
metric_type = fp
metric_value = 32.1
productivity = 8
hours_per_person_month = 160
cost_per_person_month = 12000
team_size = 2
```

预期结果：

```text
effort_hours = 256.8
effort_person_months = 1.605
cost = 19260
duration_months = 0.8025
recommended_people = 2
```

### 9. 报告导出

页面：

```text
/report-export
```

操作：

1. 先完成 UCP、LoC、FP、OO、CFG 中至少两项计算，保证本地有已保存结果。
2. 进入报告导出页面。
3. 选择需要汇总的模块。
4. 点击自动汇总已保存结果。
5. 分别导出 Markdown、HTML、PDF。

预期：

- 报告标题、摘要和模块明细可见。
- Markdown 文件包含 `# SmartMetric` 标题。
- HTML 文件可在浏览器打开。
- PDF 文件以 `%PDF` 文件头生成。

## 自动化验证

后端完整测试：

```powershell
cd E:\smart-metric
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test*.py"
```

预期：

```text
Ran 48 tests
OK
```

五个核心接口 smoke：

```powershell
@'
import io
import json
import sys
from pathlib import Path

root = Path(r"E:\smart-metric")
sys.path.insert(0, str(root / "backend"))
from app import app

client = app.test_client()
checks = []

resp = client.post("/api/metrics/usecase/calculate", json={
    "use_case_counts": {"simple": 1, "average": 1},
    "actor_counts": {"simple": 1},
})
checks.append({"module": "UCP", "status": resp.status_code, "value": resp.get_json()["data"]["ucp"]})

resp = client.post("/api/metrics/loc/calculate", data={
    "files": (io.BytesIO(b"def f():\n    return 1\n"), "demo.py")
}, content_type="multipart/form-data")
checks.append({"module": "LoC", "status": resp.status_code, "value": resp.get_json()["data"]["summary"]["code_lines"]})

resp = client.post("/api/metrics/function-point/calculate", json={
    "counts": {"EI": {"simple": 1}},
    "gsc_factors": [{"level": 0} for _ in range(14)],
})
checks.append({"module": "FP", "status": resp.status_code, "value": resp.get_json()["data"]["fp"]})

resp = client.post("/api/metrics/oo/calculate", data={
    "files": (io.BytesIO(b"class User { public int getId() { return 1; } }"), "User.java")
}, content_type="multipart/form-data")
checks.append({"module": "OO", "status": resp.status_code, "value": resp.get_json()["data"]["summary"]["class_count"]})

resp = client.post("/api/metrics/cfg/calculate", data={
    "files": (io.BytesIO(b"def f(x):\n    if x:\n        return 1\n    return 0\n"), "demo.py")
}, content_type="multipart/form-data")
checks.append({"module": "CFG", "status": resp.status_code, "value": resp.get_json()["data"]["summary"]["max_complexity"]})

print(json.dumps(checks, ensure_ascii=False, indent=2))
'@ | .\.venv\Scripts\python.exe -
```

预期：

```json
[
  {"module": "UCP", "status": 200, "value": 13.44},
  {"module": "LoC", "status": 200, "value": 2},
  {"module": "FP", "status": 200, "value": 1.95},
  {"module": "OO", "status": 200, "value": 1},
  {"module": "CFG", "status": 200, "value": 2}
]
```

前端路由检查：

```powershell
$routes = @(
  '/',
  '/usecase-metric',
  '/loc-metric',
  '/function-point',
  '/oo-metric',
  '/cfg-metric',
  '/project-metric',
  '/report-export'
)

foreach ($route in $routes) {
  $response = Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:3000$route"
  "{0} {1}" -f $route, $response.StatusCode
}
```

预期：

```text
每个路由均返回 200
```

## 通过标准

本用例通过需要同时满足：

- 五个核心度量页面均能计算并显示结果。
- 样例文件上传后结果与本文档预期一致。
- 项目扫描能识别样例目录中的代码文件、设计文件和图文件。
- 报告导出能汇总已保存结果并生成 Markdown、HTML、PDF。
- 自动化测试 `48 tests OK`。
- 前端全部路由返回 200。
