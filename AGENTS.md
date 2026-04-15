# SmartMetric Agent 入口

本文件是后续 agent 接手仓库时的固定入口。

必须先阅读：

```text
agents/README.md
```

再按任务类型阅读：

```text
agents/backend.md
agents/frontend.md
agents/metrics.md
agents/testing.md
agents/git.md
```

## 强制规则

任何 agent 修改代码后，都必须同步检查并更新 `agents/` 下相关文档。

更新要求：

- 新增或修改后端模块：更新 `agents/backend.md` 和必要的 `agents/metrics.md`。
- 新增或修改前端页面/菜单/启动方式：更新 `agents/frontend.md`。
- 新增或修改度量模型、公式、输入输出：更新 `agents/metrics.md`。
- 新增或修改测试命令、样例、验证流程：更新 `agents/testing.md`。
- 修改 Git 流程、提交策略、身份配置：更新 `agents/git.md`。
- 调整项目总体架构或开发原则：更新 `agents/README.md`。

如果确认某次代码变更不需要更新文档，必须在最终回复中明确说明原因。
