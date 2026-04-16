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
frontend/pages/estimate-metric.vue
frontend/pages/report-export.vue
```

`report-export.vue` 当前支持从前端本地已保存的度量结果自动汇总，并可勾选参与汇总的模块，不再要求手工编写完整 JSON。

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

## 关于 npm run build

不要把 `npm run build` 作为快速诊断命令。该项目在 Windows/Nuxt 环境下构建可能较慢，并且会产生大 chunk warning。

优先使用：

```powershell
npm run dev:fast
```

如果必须构建，先确保没有残留 dev/build 进程。
