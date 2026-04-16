# 后端自动化测试脚本

本目录放根目录级别的自动化测试工具，当前主要面向后端。

## 入口

统一入口：

```powershell
python scripts/run_backend_tests.py
```

## 常用命令

只跑单元测试：

```powershell
python scripts/run_backend_tests.py --suite unit
```

只跑接口冒烟测试（要求后端已启动）：

```powershell
python scripts/run_backend_tests.py --suite smoke
```

自动启动后端，再跑全部测试：

```powershell
python scripts/run_backend_tests.py --suite all --start-server
```

也可以通过统一 CLI 入口运行：

```powershell
python backend\cli.py test backend --suite all --start-server
```

指定端口：

```powershell
python scripts/run_backend_tests.py --suite all --start-server --port 5001 --base-url http://127.0.0.1:5001
```

## 当前覆盖

- `unittest` 单元测试聚合
- 后端健康检查
- 功能点默认配置与计算
- 项目估算接口
- 控制流图导入接口
- 类图级 OO 度量接口

## 说明

- 接口冒烟测试使用 Python 标准库 `urllib`，不额外引入 `requests`
- 如果后续新增后端模块，应评估是否要加入 `scripts/backend_smoke.py`
