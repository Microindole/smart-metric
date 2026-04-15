# Git Agent 规约

修改 Git 身份、提交流程、分支/合并规则后，必须同步更新本文档。

## 仓库本地身份

本仓库应使用 local git config，不要修改全局配置。

当前期望：

```text
user.name  = Microindole
user.email = 1513979779@qq.com
```

检查：

```powershell
git config --local --get user.name
git config --local --get user.email
```

设置：

```powershell
git config --local user.name "Microindole"
git config --local user.email "1513979779@qq.com"
```

不要使用 `--global`。

## 提交前

必须检查：

```powershell
git status --short
git diff --stat
```

必须运行相关测试。

## 不要提交

```text
.venv/
frontend/node_modules/
frontend/.nuxt/
frontend/.output/
__pycache__/
*.pyc
*.log
```

## 修改提交作者

只改最近一次提交：

```powershell
git commit --amend --reset-author --no-edit
```

改更早历史会重写提交哈希。除非用户明确要求，否则不要做。

## 合并后注意

合并后若前端无法加载，先检查：

```text
frontend/pages/index.vue
残留 node 进程
frontend/.nuxt 缓存
```

不要直接反复运行 `npm run build`。
