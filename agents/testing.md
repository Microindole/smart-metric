# 测试 Agent 规约

新增或修改测试、样例文件、启动验证流程后，必须同步更新本文档。

## 必跑后端测试

第四/第五点、OO、估算模块：

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_45_metrics tests.test_oo_estimate_metrics
```

报告导出测试：

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_report_export
```

项目目录级扫描测试：

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_project_metric
```

统一自动化入口：

```powershell
.\.venv\Scripts\python.exe scripts\run_backend_tests.py --suite all --start-server
.\.venv\Scripts\python.exe backend\cli.py test backend --suite all --start-server
```

脚本位置：

```text
scripts/run_backend_tests.py
scripts/backend_smoke.py
```

`tests.test_45_metrics` 包含 Java/Python 控制流 AST 策略断言：

```text
Java   -> ast-java-javalang
Python -> ast-python
```

如果 `.venv` 不存在：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

## 前端检查

不要优先跑 `npm run build`。优先启动 dev server：

```powershell
cd frontend
npm run dev:fast -- --host 127.0.0.1 --port 3000
```

检查页面：

```text
/
/usecase-metric
/loc-metric
/function-point
/cfg-metric
/oo-metric
/estimate-metric
/report-export
```

报告导出页手动验证：

```text
1. 先在任一度量页面完成一次计算
2. 进入 /report-export
3. 勾选要参与汇总的模块
4. 点击“自动汇总已保存结果”
5. 导出 markdown/html/pdf
```

## 样例文件

```text
samples/sample_usecase.oom
samples/SampleStudent.java
samples/sample_script.py
samples/sample_algo.cpp
samples/oo_demo.java
samples/class_diagram_demo.xml
samples/cfg_demo.json
samples/cfg_demo.mmd
samples/cfg_demo.dot
samples/cfg_demo.oom
samples/report_demo.json
```

CLI 验证示例：

```powershell
python backend/cli.py --help
python backend/cli.py --lang en --help
python backend/cli.py serve --host 127.0.0.1 --port 5000
python backend/cli.py oo-source samples/oo_demo.java
python backend/cli.py oo-source --language python samples/sample_script.py
python backend/cli.py oo-diagram samples/class_diagram_demo.xml
python backend/cli.py cfg-graph samples/cfg_demo.json
python backend/cli.py cfg-graph samples/cfg_demo.oom
python backend/cli.py project-scan D:\works\smart-metric
python backend/cli.py report samples/report_demo.json --format markdown
python backend/cli.py report samples/report_demo.json --format pdf
```

自动化测试脚本示例：

```powershell
python scripts/run_backend_tests.py --suite unit
python scripts/run_backend_tests.py --suite smoke --start-server
python scripts/run_backend_tests.py --suite all --start-server
python backend/cli.py test backend --suite unit
python backend/cli.py test path samples/class_diagram_demo.xml
```

## 接口手动验证

后端健康检查：

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/health"
```

功能点默认配置：

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/api/metrics/function-point/defaults"
```

## 测试失败处理

- 先看是否是依赖环境问题。
- 再看是否是接口返回格式变化。
- 不要为了让测试通过删除断言。
- 修改输出结构时，同步修改前端和文档。
