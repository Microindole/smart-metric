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

`tests.test_45_metrics` 包含 Java/Python 控制流 AST 策略断言，并固定校验 `samples/cfg_complex_demo.py` 的演示复杂度：

```text
Java   -> ast-java-javalang
Python -> ast-python
cfg_complex_demo.py -> cyclomatic_complexity = 12
```

其中 CFG 图形断言要求普通 `if` 分支不能画回自身，只有 `for/while/do` 循环允许出现回边。

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

项目扫描结果验证：

```text
1. /project-metric 页面在未扫描前应显示“选择项目目录并点击开始扫描后，这里会显示项目级结果”
2. 扫描完成后应显示：项目目录、扫描模块、摘要统计
3. 应显示项目扫描可视化图表，而不是只有空表格
4. 切换到其它页面再返回 /project-metric 时，最近一次扫描结果应保留
5. 扫描整个仓库时，Web 端不应因默认 20 秒超时报错
```

报告导出页手动验证：

```text
1. 先在任一度量页面完成一次计算
2. 进入 /report-export
3. 勾选要参与汇总的模块
4. 点击“自动汇总已保存结果”
5. 导出 markdown/html/pdf
```

功能点页 JSON 导入验证：

```text
1. 打开 /function-point
2. 点击“选择 FP JSON 并分析”
3. 选择 samples/fp.json
4. 页面应自动回填功能点计数与 GSC 因子并完成计算
5. 结果区应显示 UFP/GSC 总分/VAF/FP，且无报错提示
```

控制流图页面手动验证：

```text
1. 打开 /cfg-metric
2. 上传 samples/sample_script.py 并点击开始分析
3. 应看到 sample_script.py 的控制流图 SVG 预览，最小图为 Start -> End
4. 下方仍应显示 Mermaid 源码
5. 如需分支演示，上传 samples/cfg_complex_demo.py，预期圈复杂度为 12
6. 如需导入图文件演示，优先导入 samples/cfg_login_flow.json，预期圈复杂度为 5
7. 如需最小导入样例，导入 samples/cfg_demo.json
```

## 样例文件

```text
samples/sample_usecase.oom
samples/SampleStudent.java
samples/sample_script.py
samples/cfg_complex_demo.py
samples/sample_algo.cpp
samples/oo_demo.java
samples/class_diagram_demo.xml
samples/cfg_demo.json
samples/cfg_login_flow.json
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
SHOW.md
```

其中：

- `docs/complete-test-case.md` 偏验收和预期数值
- `SHOW.md` 偏课堂演示顺序、现场讲解和兜底方案

样例使用约定（OO 源码分析）：

```text
samples/SampleStudent.java 现在为更高复杂度教学样例（约百行，含较多字段/方法）
samples/sample_script.py 与 samples/sample_algo.cpp 都包含类与多个方法
在 /oo-metric 或 CLI oo-source 中应能看到“类级 + 方法级”结果，不再只是极简演示
```

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
8. 结果可视化区域应显示组件化 dashboard，而不是单页堆叠图表
9. 图表至少应包含：AI 审查总分、质量维度雷达、严重级别、优先级、改动范围、问题类别、重点文件命中、目标符号命中、预期收益分布
10. 真实 AI 模式下，Web 端不应因默认 20 秒超时报错
11. 切换到其它页面再返回 /ai-review 时，loading 和结果状态应保持
12. 手动点击“中断审查”后，页面应提示已取消
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
