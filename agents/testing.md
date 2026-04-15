# 测试 Agent 规约

新增或修改测试、样例文件、启动验证流程后，必须同步更新本文档。

## 必跑后端测试

第四/第五点、OO、估算模块：

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_45_metrics tests.test_oo_estimate_metrics
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
```

## 样例文件

```text
samples/sample_usecase.oom
samples/SampleStudent.java
samples/sample_script.py
samples/sample_algo.cpp
samples/oo_demo.java
samples/cfg_demo.json
samples/cfg_demo.mmd
samples/cfg_demo.dot
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
