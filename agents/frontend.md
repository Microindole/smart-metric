# 前端 Agent 规约

修改前端页面、菜单、启动方式或 API 调用后，必须回看并更新本文档；如果修改涉及验证步骤，还要同步更新 `agents/testing.md`。

## 重要原则

- 前端是 Nuxt 3 项目。
- 页面放在 `frontend/pages/`。
- 公共布局在 `frontend/components/AppLayout.vue`。
- API 调用统一通过 `frontend/utils/api.js` 的 Axios 实例。

## 不要做的事

- 不要把前端改回静态 HTML。
- 不要绕过 `utils/api.js` 到处硬编码后端地址。
- 不要在页面顶层写可能卡 SSR 的 `await navigateTo(...)`。
- 不要无原因改 `package-lock.json`。

## 页面入口

当前页面：

```text
frontend/pages/usecase-metric.vue
frontend/pages/loc-metric.vue
frontend/pages/function-point.vue
frontend/pages/cfg-metric.vue
frontend/pages/oo-metric.vue
frontend/pages/project-metric.vue
frontend/pages/ai-review.vue
frontend/pages/estimate-metric.vue
frontend/pages/report-export.vue
```

`report-export.vue` 当前支持从前端本地已保存的度量结果自动汇总，并可勾选参与汇总的模块，不再要求手工编写完整 JSON。

`project-metric.vue` 当前支持选择或输入项目目录路径，配置默认忽略、自定义忽略目录、自定义忽略通配规则，并调用后端项目扫描接口。
同时支持自动读取项目根目录 `.smartmetricignore`，并展示实际生效的忽略规则。
在本机开发环境下，可点击按钮通过系统目录选择框选择路径。

`loc-metric.vue` 当前支持 Java/Python/C++ 的结构化结果展示：

```text
代码行分析结果会按文件显示 language/class_count/method_count/condition_count/loop_count
抽象语法树分析结果（类级）支持显示 method_count/field_count/RFC/LCOM
抽象语法树分析结果（方法级）不再只在 Java 文件有数据，Python/C++ 也会生成方法行
```

`function-point.vue` 当前支持：

```text
手动输入 EI/EO/EQ/ILF/EIF 和 14 个 GSC 因子
点击“选择 FP JSON 并分析”读取本地 .json（如 samples/fp.json）
导入后自动回填计数与因子，并直接触发一次 FP 计算
```

`ai-review.vue` 当前支持：

```text
输入项目目录
点击按钮通过系统目录选择框选择项目目录
一键填入当前仓库路径
读取后端 AI 配置状态
选择模型和导出格式
指定 phase1/phase2 fixture 进行离线调试
读取本地 JSON 文件并以内联 payload 发送到后端
调用后端两阶段 AI 审查接口
导出 AI 审查报告
显示项目概览、重构顺序和重点文件结论
使用组件化 dashboard 展示 AI 审查结果，而不是把所有图和表堆在一个 vue 中
使用 ECharts 展示 AI 审查总分、质量维度雷达、严重级别、建议优先级、改动范围、问题类别、重点文件命中、目标符号命中、预期收益分布
切页后保持表单状态、loading 状态和审查结果
提供手动“中断审查”按钮，而不是在路由切换时自动取消
```

AI 审查页面请求约束：

```text
真实 AI 审查是两阶段调用，Web 端请求超时应显著高于普通接口
不要沿用全局 20 秒超时去调用 /api/metrics/ai-review/run
若超时，应明确提示用户稍后重试或先用离线 fixture 验证
切页时不要自动中断正在进行的 AI 审查
```

目录路径说明：

```text
浏览器不能直接安全暴露本机真实绝对目录路径
因此目录选择由后端弹出系统目录选择框完成
如果系统对话框不可用，仍可手动输入路径或使用“一键填入当前仓库路径”
本地 JSON 附件可通过文件选择器读取，因为这类文件可以直接读内容后以内联 payload 发送
```

菜单入口：

```text
frontend/components/AppLayout.vue
```

新增页面后，如果需要显示在侧边栏，只改 `AppLayout.vue` 中对应菜单项。

## 首页策略

当前首页 `frontend/pages/index.vue` 不再自动跳转，而是直接展示模块入口。

原因：

- 减少首屏阻塞
- 避免页面一进来就依赖后端接口
- 降低“3000 端口很久没反应”的体感问题

不要恢复成首页自动跳转。

## 当前视觉风格

前端采用 Claude-like 的专业工作台风格：

- `frontend/components/AppLayout.vue` 是统一工作台外壳，负责侧边导航、品牌区、工具页上下文标题、内容背景和页面宽度。
- `AppLayout.vue` 内置全局命令面板，提供模块搜索与快速跳转；不要新增重复的顶部导航或分散式快捷入口。
- 首页 `frontend/pages/index.vue` 是模块工作台入口，不做营销式落地页，也不恢复自动跳转；首屏以温暖留白、文字说明、覆盖状态和低边框模块清单为主，避免大卡片堆叠。
- 首页右侧可以承载工作插件式入口，例如项目扫描、估算器、报告管线，但应保持轻量列表形态，不要做成装饰型插件市场。
- 工具页应保持高信息密度、清晰表单、结果面板和导出动作，并依赖 `AppLayout` 的统一标题区建立页面层级。
- 视觉基调是暖白 / 深色正文 / clay 强调色，字体优先使用接近 Claude 的系统无衬线栈，避免大面积蓝紫渐变、装饰型卡片或夸张 hero。
- 新增页面应复用 `AppLayout`，并保持 8px 以内圆角、低饱和背景、克制阴影和清晰扫描路径。

## Nuxt 卡住排查

若用户说“前端无法加载”：

1. 检查残留 Node 进程：

```powershell
Get-CimInstance Win32_Process -Filter "name = 'node.exe'" | Select-Object ProcessId,CommandLine
```

2. 只停止本项目相关的 npm/nuxt 进程，不要停止 Codex 自己的 node 进程。

3. 清缓存：

```powershell
Remove-Item frontend\.nuxt -Recurse -Force
Remove-Item frontend\.output -Recurse -Force
```

4. 使用 dev 快速模式：

```powershell
cd frontend
npm run dev:fast -- --host 127.0.0.1 --port 3000
```

5. 先请求具体页面，不要只看 `/`：

```text
http://127.0.0.1:3000/usecase-metric
http://127.0.0.1:3000/function-point
http://127.0.0.1:3000/cfg-metric
```

## Nuxt 入口约定

- 开发入口：`npm run dev` / `npm run dev:fast`
- 构建入口：`npm run build` 或 `npm run build:clean`
- 生产启动入口：`npm run start`

不要直接运行：

```text
frontend/.nuxt/dist/server/server.mjs
```

原因：

- `.nuxt/` 是开发期生成物，不是稳定的对外启动入口
- 正确的生产入口是 `frontend/.output/server/index.mjs`
- 仓库已经在 `frontend/package.json` 中封装了 `npm run start`

## 关于 npm run build

不要把 `npm run build` 作为快速诊断命令。该项目在 Windows/Nuxt 环境下构建可能较慢，并且会产生大 chunk warning。

优先使用：

```powershell
npm run dev:fast
```

如果必须构建，先确保没有残留 dev/build 进程。
