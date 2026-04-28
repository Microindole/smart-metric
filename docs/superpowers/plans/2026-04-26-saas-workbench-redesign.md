# SmartMetric Claude-Like Workbench Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the existing Nuxt frontend into a Claude-like professional workbench without changing metric behavior or API contracts.

**Architecture:** Keep the existing route-per-page architecture and Ant Design Vue components. Improve the shared shell in `AppLayout.vue`, make `index.vue` a polished workbench launcher, and use `app.vue` only for global visual foundations.

**Tech Stack:** Nuxt 3, Vue SFCs, Ant Design Vue, CSS scoped styles, existing Axios API layer.

---

## File Structure

- Modify `frontend/app.vue`: add global app/body polish and Ant Design surface normalization.
- Modify `frontend/components/AppLayout.vue`: redesign the sidebar, product header, main workspace, and navigation affordances.
- Modify `frontend/pages/index.vue`: replace the basic home grid with a professional module workbench and five-function coverage section.
- Modify `agents/frontend.md`: document the Claude-like workbench shell and home-page convention for future agents.

No backend files or API files should change.

## Visual Constants

Use this visual system consistently:

- Background: `#f5f1ea`
- Primary text: `#191714`
- Secondary text: `#766b60`
- Border: `#e2d9cf`
- Accent: `#c65f3d`
- Radius: `8px` maximum for product UI controls and panels

## Tasks

### Task 1: Global Frontend Foundation

**Files:**
- Modify: `frontend/app.vue`

- [ ] **Step 1: Replace the minimal app wrapper with a classed root**

Use:

```vue
<template>
  <NuxtPage />
</template>

<style>
html {
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  margin: 0;
  background: #f5f1ea;
  color: #191714;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

* {
  box-sizing: border-box;
}

.ant-card {
  border-radius: 8px;
  border-color: #e2d9cf;
  box-shadow: 0 8px 24px rgba(16, 24, 40, 0.04);
}

.ant-card-head {
  border-bottom-color: #edf1f7;
}

.ant-btn {
  border-radius: 7px;
}

.ant-table-wrapper .ant-table {
  border-radius: 8px;
}
</style>
```

- [ ] **Step 2: Verify app still renders**

Run:

```powershell
curl.exe -I --max-time 10 http://127.0.0.1:3000/
```

Expected: `HTTP/1.1 200 OK`.

### Task 2: Shared Workbench Shell

**Files:**
- Modify: `frontend/components/AppLayout.vue`

- [ ] **Step 1: Replace the sidebar markup**

Use a structured shell:

```vue
<template>
  <a-layout class="app-layout">
    <a-layout-sider width="248" theme="light" class="sider">
      <div class="brand-block" @click="$router.push('/')">
        <div class="brand-mark">SM</div>
        <div>
          <div class="brand-name">SmartMetric</div>
          <div class="brand-subtitle">Software Metrics</div>
        </div>
      </div>

      <div class="nav-label">度量工具</div>
      <a-menu :selectedKeys="[activeKey]" mode="inline" class="nav-menu">
        <a-menu-item v-for="item in navItems" :key="item.key" @click="$router.push(item.path)">
          <span class="nav-acronym">{{ item.acronym }}</span>
          <span>{{ item.label }}</span>
        </a-menu-item>
      </a-menu>

      <div class="sidebar-footer">
        <div class="footer-label">Metric suite</div>
        <div class="footer-value">5 个核心引擎</div>
      </div>
    </a-layout-sider>

    <a-layout class="main-layout">
      <main class="content">
        <div class="content-inner">
          <slot />
        </div>
      </main>
    </a-layout>
  </a-layout>
</template>
```

- [ ] **Step 2: Add nav item data**

Use:

```vue
<script setup>
defineProps({
  activeKey: {
    type: String,
    default: 'usecase',
  },
})

const navItems = [
  { key: 'usecase', path: '/usecase-metric', acronym: 'UCP', label: '用例点度量' },
  { key: 'loc', path: '/loc-metric', acronym: 'LoC', label: '代码行度量' },
  { key: 'fp', path: '/function-point', acronym: 'FP', label: '功能点度量' },
  { key: 'oo', path: '/oo-metric', acronym: 'OO', label: '面向对象度量' },
  { key: 'cfg', path: '/cfg-metric', acronym: 'CFG', label: '控制流图度量' },
  { key: 'project', path: '/project-metric', acronym: 'PRJ', label: '项目扫描' },
  { key: 'estimate', path: '/estimate-metric', acronym: 'EST', label: '项目估算' },
  { key: 'report', path: '/report-export', acronym: 'RPT', label: '报告导出' },
]
</script>
```

- [ ] **Step 3: Add shell styles**

Use CSS that keeps the app professional, readable, and not one-hue dominated. Key rules:

```css
.app-layout { min-height: 100vh; background: #f5f1ea; }
.sider { position: sticky; top: 0; height: 100vh; border-right: 1px solid #e2d9cf; background: #fffcf7; }
.brand-block { height: 76px; display: flex; align-items: center; gap: 12px; padding: 0 18px; cursor: pointer; border-bottom: 1px solid #edf1f7; }
.brand-mark { width: 36px; height: 36px; border-radius: 8px; display: grid; place-items: center; background: #191714; color: #fffcf7; font-size: 13px; font-weight: 800; }
.brand-name { color: #191714; font-size: 16px; font-weight: 800; line-height: 1.2; }
.brand-subtitle { color: #766b60; font-size: 12px; margin-top: 2px; }
.nav-label { padding: 18px 18px 8px; color: #98a2b3; font-size: 12px; font-weight: 700; text-transform: uppercase; }
.nav-menu { border-inline-end: 0 !important; padding: 0 10px; }
.nav-acronym { display: inline-flex; width: 34px; color: #475467; font-size: 12px; font-weight: 800; }
.main-layout { background: transparent; }
.content { padding: 24px; }
.content-inner { min-height: calc(100vh - 48px); max-width: 1320px; margin: 0 auto; }
.sidebar-footer { margin: auto 14px 16px; padding: 12px; border: 1px solid #e2d9cf; border-radius: 8px; background: #fbf7f1; }
```

- [ ] **Step 4: Verify core pages still return 200**

Run:

```powershell
curl.exe -I --max-time 10 http://127.0.0.1:3000/usecase-metric
curl.exe -I --max-time 10 http://127.0.0.1:3000/oo-metric
```

Expected: both return `HTTP/1.1 200 OK`.

### Task 3: Workbench Home Page

**Files:**
- Modify: `frontend/pages/index.vue`

- [ ] **Step 1: Replace current hero with workbench header**

Use utility copy:

```vue
<section class="workspace-header">
  <div>
    <div class="eyebrow">SmartMetric Workbench</div>
    <h1>软件度量工作台</h1>
    <p>面向真实项目的度量、扫描、估算和报告生成工作流。</p>
  </div>
  <div class="status-panel">
    <div class="status-label">Metric engines</div>
    <div class="status-value">5 core</div>
    <div class="status-text">核心度量已接入 Web 与后端接口</div>
  </div>
</section>
```

- [ ] **Step 2: Replace module data**

Use explicit acronym and category fields:

```js
const items = [
  { path: '/usecase-metric', acronym: 'UCP', title: '用例点度量', text: '从用例与参与者复杂度计算 UUC、UAW、TCF、EF 与 UCP。', category: '需求规模' },
  { path: '/loc-metric', acronym: 'LoC', title: '代码行度量', text: '统计总行、空行、注释行、有效代码行与源码结构信息。', category: '代码规模' },
  { path: '/oo-metric', acronym: 'OO', title: '面向对象度量', text: '支持源码级和类图级 CK / LK 指标分析。', category: '设计质量' },
  { path: '/function-point', acronym: 'FP', title: '功能点度量', text: '按 EI、EO、EQ、ILF、EIF 与 GSC 因子计算功能点。', category: '功能规模' },
  { path: '/cfg-metric', acronym: 'CFG', title: '控制流图度量', text: '从源码或结构化图文件计算控制流图与圈复杂度。', category: '复杂度' },
  { path: '/project-metric', acronym: 'PRJ', title: '项目扫描', text: '扫描项目目录，汇总代码、依赖、设计图与风险文件。', category: '项目级' },
  { path: '/estimate-metric', acronym: 'EST', title: '项目估算', text: '基于 FP、UCP 或 LoC 估算工作量、成本、工期和人数。', category: '估算' },
  { path: '/report-export', acronym: 'RPT', title: '报告导出', text: '汇总已保存结果并导出 Markdown、HTML 或 PDF。', category: '交付' },
]
```

- [ ] **Step 3: Render module launcher**

Use repeated module buttons with no nested cards:

```vue
<section class="module-section">
  <div class="section-heading">
    <h2>度量模块</h2>
    <p>选择一个模块开始计算或导出结果。</p>
  </div>
  <div class="module-grid">
    <button v-for="item in items" :key="item.path" class="module-item" @click="navigateTo(item.path)">
      <span class="module-acronym">{{ item.acronym }}</span>
      <span class="module-content">
        <span class="module-category">{{ item.category }}</span>
        <span class="module-title">{{ item.title }}</span>
        <span class="module-text">{{ item.text }}</span>
      </span>
    </button>
  </div>
</section>
```

- [ ] **Step 4: Add home styles**

Use a restrained workbench visual:

```css
.home { min-height: 100vh; padding: 28px; background: #f5f1ea; }
.workspace-header { display: grid; grid-template-columns: 1fr 260px; gap: 20px; align-items: stretch; margin-bottom: 24px; padding: 28px; border: 1px solid #e2d9cf; border-radius: 8px; background: #fffcf7; }
.eyebrow { color: #c65f3d; font-size: 12px; font-weight: 800; text-transform: uppercase; }
h1 { margin: 8px 0 10px; color: #191714; font-size: 32px; line-height: 1.2; }
p { margin: 0; color: #766b60; line-height: 1.7; }
.status-panel { border-left: 1px solid #e2d9cf; padding-left: 20px; display: flex; flex-direction: column; justify-content: center; }
.status-value { color: #191714; font-size: 38px; font-weight: 800; line-height: 1; }
.module-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }
.module-item { min-height: 138px; display: flex; gap: 14px; padding: 18px; text-align: left; border: 1px solid #e2d9cf; border-radius: 8px; background: #fffcf7; cursor: pointer; transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease; }
.module-item:hover { transform: translateY(-2px); border-color: #b8c7e6; box-shadow: 0 12px 28px rgba(16, 24, 40, .08); }
.module-acronym { width: 46px; height: 34px; border-radius: 8px; display: inline-grid; place-items: center; background: #f4e5da; color: #a94f34; font-weight: 800; }
```

- [ ] **Step 5: Verify home page**

Run:

```powershell
curl.exe -I --max-time 10 http://127.0.0.1:3000/
```

Expected: `HTTP/1.1 200 OK`.

### Task 4: Frontend Agent Documentation

**Files:**
- Modify: `agents/frontend.md`

- [ ] **Step 1: Add visual convention note**

Add a section:

```markdown
## 当前视觉风格

前端采用专业 Claude-like 工作台风格：

- `frontend/components/AppLayout.vue` 是统一工作台外壳，负责侧边导航、品牌区、内容背景和页面宽度。
- 首页 `frontend/pages/index.vue` 是模块工作台入口，不做营销式落地页，也不恢复自动跳转。
- 工具页应保持高信息密度、清晰表单、结果面板和导出动作，不要做夸张 hero 或装饰型卡片。
- 新增页面应复用 `AppLayout`，并保持 8px 以内圆角、低饱和背景、单一主强调色。
```

- [ ] **Step 2: Verify documentation mentions the new convention**

Run:

```powershell
Select-String -Path agents\frontend.md -Pattern "专业 Claude-like 工作台"
```

Expected: at least one matching line.

### Task 5: Final Verification

**Files:**
- No file edits.

- [ ] **Step 1: Check frontend routes**

Run:

```powershell
curl.exe -I --max-time 10 http://127.0.0.1:3000/
curl.exe -I --max-time 10 http://127.0.0.1:3000/usecase-metric
curl.exe -I --max-time 10 http://127.0.0.1:3000/loc-metric
curl.exe -I --max-time 10 http://127.0.0.1:3000/function-point
curl.exe -I --max-time 10 http://127.0.0.1:3000/oo-metric
curl.exe -I --max-time 10 http://127.0.0.1:3000/cfg-metric
curl.exe -I --max-time 10 http://127.0.0.1:3000/project-metric
curl.exe -I --max-time 10 http://127.0.0.1:3000/estimate-metric
curl.exe -I --max-time 10 http://127.0.0.1:3000/report-export
```

Expected: every route returns `HTTP/1.1 200 OK`.

- [ ] **Step 2: Check backend still responds**

Run:

```powershell
curl.exe --max-time 10 http://127.0.0.1:5000/api/health
```

Expected: response includes `"success":true`.

- [ ] **Step 3: Inspect git diff**

Run:

```powershell
git diff --stat
git status --short
```

Expected: only planned frontend, docs, and ignore-rule files changed.

## Self-Review

Spec coverage:

- Claude-like workbench shell: covered by Task 2.
- Home workbench launcher: covered by Task 3.
- Global visual foundation: covered by Task 1.
- Frontend documentation update: covered by Task 4.
- Verification: covered by Task 5.

Placeholder scan: no TODO/TBD placeholders remain.

Type consistency: routes, `activeKey`, and nav keys match existing page usage.

