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
.\.venv\Scripts\python.exe -m unittest tests.test_project_report
.\.venv\Scripts\python.exe -m unittest tests.test_ai_review
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

若要验证生产构建链路，使用：

```powershell
cd frontend
npm run build
npm run start
```

不要直接运行：

```text
frontend/.nuxt/dist/server/server.mjs
```

检查页面：

```text
/
/usecase-metric
/loc-metric
/function-point
/cfg-metric
/project-metric
/ai-review
/oo-metric
/estimate-metric
/report-export
```

目录选择验证：

```text
1. 打开 /project-metric 或 /ai-review
2. 点击“选择目录”
3. 应弹出系统目录选择框
4. 选择目录后，输入框应回填绝对路径
5. 取消选择时，页面应提示已取消，不应报错
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
samples/ai_review_phase1.json
samples/ai_review_phase2.json
samples/fp.json
samples/estimate.json
```

完整端到端验收用例：

```text
docs/complete-test-case.md
```

该用例覆盖 UCP、LoC、FP、OO、CFG、项目扫描、项目估算和报告导出，并记录页面操作、测试数据和预期数值。

CLI 验证示例：

```powershell
python backend/cli.py --help
python backend/cli.py -L en --help
python backend/cli.py --lang en --help
python backend/cli.py help
python backend/cli.py help -a
python backend/cli.py ps D:\works\smart-metric -m inventory,loc
python backend/cli.py tb --suite unit
python backend/cli.py ai-review D:\works\smart-metric -F json --phase1-file samples/ai_review_phase1.json --phase2-file samples/ai_review_phase2.json
python backend/cli.py tp samples/cfg_demo.json
python backend/cli.py serve --host 127.0.0.1 --port 5000
python backend/cli.py oo-source samples/oo_demo.java
python backend/cli.py oo-source --language python samples/sample_script.py
python backend/cli.py oo-diagram samples/class_diagram_demo.xml
python backend/cli.py cfg-graph samples/cfg_demo.json
python backend/cli.py cfg-graph samples/cfg_demo.oom
python backend/cli.py project-scan D:\works\smart-metric
python backend/cli.py project-report D:\works\smart-metric -F pdf
python backend/cli.py project-scan D:\works\smart-metric --ignore-dir coverage --ignore-glob *.generated.py
python backend/cli.py project-scan D:\works\smart-metric --ignore-file .smartmetricignore
python backend/cli.py project-scan D:\works\smart-metric -m inventory,loc -d coverage -g *.generated.py
python backend/cli.py report samples/report_demo.json --format markdown
python backend/cli.py report samples/report_demo.json -F html -o report.html
python backend/cli.py report samples/report_demo.json --format pdf
```

AI 审查离线验证：

```text
1. 准备 phase1.json 和 phase2.json fixture
2. 运行 ai-review 命令并指定 --phase1-file / --phase2-file
3. 检查输出 JSON/PDF 是否生成
4. fixture 模式不依赖网络和 OPENAI_API_KEY
5. Web 页面可直接进入 /ai-review，检查配置状态和离线示例是否可用
6. 建议详情区域应能看到 evidence / target_symbols / refactor_steps
7. 审查结论区域应显示 project_overview / overall_priority / refactor_order
8. 结果可视化区域应显示 ECharts 图表，而不是空白占位
9. 真实 AI 模式下，Web 端不应因默认 20 秒超时报错
```

CLI 帮助显示约定：

```text
根帮助中主命令单独占一行
短别名单独下一行展示，不使用 serve / srv 这种拼接形式
子命令帮助中的别名使用 Aliases/别名 区块展示
help -a 在交互终端中分页显示，Enter 下一页，q 退出
常用选项同时支持长短参数，测试时优先覆盖一条短参数链路
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
