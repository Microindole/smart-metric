<template>
  <a-layout class="app-layout">
    <a-layout-sider width="248" theme="light" class="sider">
      <div class="brand-block" @click="go('/')">
        <div class="brand-mark">SM</div>
        <div>
          <div class="brand-name">SmartMetric</div>
          <div class="brand-subtitle">Software Metrics</div>
        </div>
      </div>

      <button class="command-trigger" @click="openPalette">
        <span>命令面板</span>
        <span class="trigger-dot"></span>
      </button>

      <div class="nav-label">度量工具</div>
      <a-menu :selectedKeys="[activeKey]" mode="inline" class="nav-menu">
        <a-menu-item v-for="item in navItems" :key="item.key" @click="go(item.path)">
          <span class="nav-acronym">{{ item.acronym }}</span>
          <span>{{ item.label }}</span>
        </a-menu-item>
      </a-menu>

      <div class="sidebar-footer">
        <div class="footer-label">Metric suite</div>
        <div class="footer-value">5 个核心引擎</div>
        <div class="footer-meter">
          <span></span>
        </div>
      </div>
    </a-layout-sider>
    <a-layout class="main-layout">
      <main class="content">
        <div class="content-inner">
          <section class="page-context">
            <div>
              <div class="page-kicker">{{ activeItem.acronym }} · {{ activeItem.group }}</div>
              <h1>{{ activeItem.label }}</h1>
              <p>{{ activeItem.description }}</p>
            </div>
            <div class="context-actions">
              <button class="context-action subtle" @click="openPalette">命令</button>
              <button class="context-action" @click="go('/report-export')">报告导出</button>
            </div>
          </section>
          <slot />
        </div>
      </main>
    </a-layout>

    <transition name="palette-fade">
      <div v-if="paletteOpen" class="palette-overlay" @click.self="closePalette">
        <section class="command-palette" role="dialog" aria-modal="true" aria-label="SmartMetric command palette">
          <div class="palette-search">
            <span class="search-mark">SM</span>
            <input
              ref="commandInput"
              v-model="query"
              type="text"
              placeholder="搜索度量模块、报告或项目工具"
              @keydown.enter.prevent="runFirstCommand"
            >
          </div>

          <div class="palette-section">
            <div class="palette-label">模块</div>
            <button
              v-for="item in filteredItems"
              :key="item.key"
              class="command-row"
              @click="go(item.path)"
            >
              <span class="command-acronym">{{ item.acronym }}</span>
              <span class="command-copy">
                <span class="command-title">{{ item.label }}</span>
                <span class="command-meta">{{ item.group }} · {{ item.description }}</span>
              </span>
              <span class="command-state">打开</span>
            </button>
            <div v-if="filteredItems.length === 0" class="empty-command">没有匹配的模块</div>
          </div>

          <div class="palette-actions">
            <button @click="go('/project-metric')">项目扫描</button>
            <button @click="go('/estimate-metric')">项目估算</button>
            <button @click="go('/report-export')">生成报告</button>
          </div>
        </section>
      </div>
    </transition>
  </a-layout>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  activeKey: {
    type: String,
    default: 'usecase',
  },
})

const router = useRouter()
const paletteOpen = ref(false)
const query = ref('')
const commandInput = ref(null)

const navItems = [
  { key: 'usecase', path: '/usecase-metric', acronym: 'UCP', label: '用例点度量', group: '需求规模', description: '从用例复杂度、参与者复杂度和环境因子计算 UCP。' },
  { key: 'loc', path: '/loc-metric', acronym: 'LoC', label: '代码行度量', group: '代码规模', description: '统计源码行数、注释、空行和结构辅助指标。' },
  { key: 'fp', path: '/function-point', acronym: 'FP', label: '功能点度量', group: '功能规模', description: '基于 EI、EO、EQ、ILF、EIF 与 GSC 因子计算功能点。' },
  { key: 'oo', path: '/oo-metric', acronym: 'OO', label: '面向对象度量', group: '设计质量', description: '分析源码级与类图级 CK / LK 指标。' },
  { key: 'cfg', path: '/cfg-metric', acronym: 'CFG', label: '控制流图度量', group: '复杂度', description: '从源码或结构化控制流图计算圈复杂度。' },
  { key: 'project', path: '/project-metric', acronym: 'PRJ', label: '项目扫描', group: '项目级', description: '扫描项目目录，汇总代码、依赖、设计图和风险文件。' },
  { key: 'ai-review', path: '/ai-review', acronym: 'AI', label: 'AI 审查', group: '质量审查', description: '对项目风险文件进行本地审查与 AI 分析，生成审查建议。' },
  { key: 'estimate', path: '/estimate-metric', acronym: 'EST', label: '项目估算', group: '交付评估', description: '基于 FP、UCP 或 LoC 估算工作量、成本、工期与人数。' },
  { key: 'report', path: '/report-export', acronym: 'RPT', label: '报告导出', group: '交付物', description: '汇总度量结果并导出 Markdown、HTML 或 PDF 报告。' },
]

const activeItem = computed(() => navItems.find((item) => item.key === props.activeKey) || navItems[0])

const filteredItems = computed(() => {
  const keyword = query.value.trim().toLowerCase()
  if (!keyword) {
    return navItems
  }

  return navItems.filter((item) => {
    const content = `${item.acronym} ${item.label} ${item.group} ${item.description}`.toLowerCase()
    return content.includes(keyword)
  })
})

const openPalette = () => {
  paletteOpen.value = true
  query.value = ''
  nextTick(() => {
    commandInput.value?.focus?.()
  })
}

const closePalette = () => {
  paletteOpen.value = false
}

const go = (path) => {
  closePalette()
  router.push(path)
}

const runFirstCommand = () => {
  if (filteredItems.value.length > 0) {
    go(filteredItems.value[0].path)
  }
}

const handleKeydown = (event) => {
  const key = event.key.toLowerCase()
  if ((event.ctrlKey || event.metaKey) && key === 'k') {
    event.preventDefault()
    openPalette()
  }

  if (event.key === 'Escape' && paletteOpen.value) {
    closePalette()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background:
    linear-gradient(90deg, rgba(255, 252, 247, 0.84) 0%, rgba(247, 243, 236, 0.44) 42%, transparent 100%),
    #f5f1ea;
}

.sider {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e2d9cf;
  background: #fffcf7;
}

.brand-block {
  height: 76px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 18px;
  border-bottom: 1px solid #e9e1d7;
  cursor: pointer;
  transition: background 0.16s ease;
}

.brand-block:hover {
  background: #f7f1e9;
}

.command-trigger {
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 14px 14px 4px;
  padding: 0 12px;
  border: 1px solid #e0d7cc;
  border-radius: 8px;
  background: #fffaf4;
  color: #3c342d;
  font-weight: 720;
  cursor: pointer;
  transition: background 0.16s ease, border-color 0.16s ease, transform 0.16s ease;
}

.command-trigger:hover {
  background: #f7f1e9;
  border-color: #cf8b72;
  transform: translateY(-1px);
}

.trigger-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #c65f3d;
  box-shadow: 0 0 0 4px rgba(198, 95, 61, 0.12);
}

.brand-mark {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  background: #191714;
  color: #fff;
  font-size: 13px;
  font-weight: 800;
}

.brand-name {
  color: #191714;
  font-size: 16px;
  font-weight: 760;
  line-height: 1.2;
}

.brand-subtitle {
  margin-top: 2px;
  color: #766b60;
  font-size: 12px;
}

.nav-label {
  padding: 18px 18px 8px;
  color: #93887c;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
}

.nav-menu {
  flex: 1;
  border-inline-end: 0 !important;
  padding: 0 10px;
}

.nav-menu :deep(.ant-menu-item) {
  height: 40px;
  margin: 3px 0;
  padding-inline: 12px !important;
  border-radius: 8px;
  color: #484038;
  transition: background 0.16s ease, color 0.16s ease;
}

.nav-menu :deep(.ant-menu-item-selected) {
  background: #f2e2d6;
  color: #a94f34;
  font-weight: 700;
}

.nav-menu :deep(.ant-menu-item:hover) {
  background: #f7f1e9;
  color: #a94f34;
}

.nav-menu :deep(.ant-menu-item::after) {
  display: none;
}

.nav-acronym {
  width: 34px;
  display: inline-flex;
  color: #5f554b;
  font-size: 12px;
  font-weight: 800;
}

.sidebar-footer {
  margin: auto 14px 16px;
  padding: 12px;
  border: 1px solid #e1d8ce;
  border-radius: 8px;
  background: #fbf7f1;
}

.footer-label {
  color: #93887c;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.footer-value {
  margin-top: 4px;
  color: #191714;
  font-size: 14px;
  font-weight: 800;
}

.footer-meter {
  height: 5px;
  overflow: hidden;
  margin-top: 10px;
  border-radius: 999px;
  background: #eadfd4;
}

.footer-meter span {
  display: block;
  width: 100%;
  height: 100%;
  border-radius: inherit;
  background: #c65f3d;
}

.main-layout {
  width: 100%;
  display: block;
  background: transparent;
}

.content {
  padding: 28px 30px;
  width: 100%;
}

.content-inner {
  width: 100%;
  min-height: calc(100vh - 48px);
  max-width: 1220px;
  margin: 0 auto;
}

.page-context {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 22px;
  padding: 8px 2px 12px;
  border-bottom: 1px solid rgba(226, 217, 207, 0.82);
}

.page-kicker {
  color: #a94f34;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.page-context h1 {
  margin: 6px 0 6px;
  color: #191714;
  font-family: var(--sm-font-display);
  font-size: 32px;
  font-weight: 680;
  line-height: 1.18;
}

.page-context p {
  margin: 0;
  color: #766b60;
  line-height: 1.65;
}

.context-actions {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 8px;
}

.context-action {
  flex: 0 0 auto;
  height: 36px;
  padding: 0 14px;
  border: 1px solid #d6cabe;
  border-radius: 8px;
  background: #fffcf7;
  color: #3c342d;
  font-weight: 700;
  cursor: pointer;
  transition: border-color 0.16s ease, color 0.16s ease, box-shadow 0.16s ease;
}

.context-action:hover {
  border-color: #c65f3d;
  color: #a94f34;
  box-shadow: 0 8px 18px rgba(82, 63, 45, 0.07);
}

.context-action.subtle {
  background: transparent;
  color: #74695e;
}

.palette-overlay {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: grid;
  place-items: start center;
  padding: 11vh 18px 18px;
  background: rgba(25, 23, 20, 0.22);
  backdrop-filter: blur(10px);
}

.command-palette {
  width: min(680px, 100%);
  overflow: hidden;
  border: 1px solid rgba(226, 217, 207, 0.94);
  border-radius: 10px;
  background: #fffcf7;
  box-shadow: 0 28px 70px rgba(45, 35, 27, 0.22);
}

.palette-search {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-bottom: 1px solid #ebe2d8;
}

.search-mark {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  background: #191714;
  color: #fffaf4;
  font-size: 12px;
  font-weight: 800;
}

.palette-search input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: #191714;
  font: inherit;
  font-size: 16px;
}

.palette-search input::placeholder {
  color: #998d82;
}

.palette-section {
  max-height: min(430px, 54vh);
  overflow: auto;
  padding: 8px;
}

.palette-label {
  padding: 8px 10px;
  color: #93887c;
  font-size: 11px;
  font-weight: 820;
  text-transform: uppercase;
}

.command-row {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  text-align: left;
  cursor: pointer;
  transition: background 0.14s ease;
}

.command-row:hover,
.command-row:focus-visible {
  outline: 0;
  background: #f7f1e9;
}

.command-acronym {
  width: 42px;
  height: 30px;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  border-radius: 8px;
  background: #f2e2d6;
  color: #a94f34;
  font-size: 12px;
  font-weight: 840;
}

.command-copy {
  min-width: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.command-title {
  color: #191714;
  font-weight: 760;
}

.command-meta {
  overflow: hidden;
  color: #74695e;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.command-state {
  color: #a94f34;
  font-size: 12px;
  font-weight: 760;
}

.empty-command {
  padding: 28px 12px 34px;
  color: #93887c;
  text-align: center;
}

.palette-actions {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  padding: 10px;
  border-top: 1px solid #ebe2d8;
  background: #fbf7f1;
}

.palette-actions button {
  min-height: 36px;
  border: 1px solid #e0d7cc;
  border-radius: 8px;
  background: #fffcf7;
  color: #3c342d;
  font-weight: 720;
  cursor: pointer;
}

.palette-actions button:hover {
  border-color: #cf8b72;
  color: #a94f34;
}

.palette-fade-enter-active,
.palette-fade-leave-active {
  transition: opacity 0.14s ease;
}

.palette-fade-enter-from,
.palette-fade-leave-to {
  opacity: 0;
}

@media (max-width: 760px) {
  .app-layout {
    display: block;
  }

  .sider {
    position: relative;
    width: 100% !important;
    min-width: 0 !important;
    max-width: none !important;
    height: auto;
    border-right: 0;
    border-bottom: 1px solid #e2d9cf;
  }

  .brand-block {
    height: 64px;
  }

  .nav-label {
    padding: 12px 16px 6px;
  }

  .nav-menu {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 4px;
    padding: 0 10px 10px;
  }

  .nav-menu :deep(.ant-menu-item) {
    width: auto;
    margin: 0;
  }

  .sidebar-footer {
    display: none;
  }

  .command-trigger {
    margin: 10px 14px;
  }

  .content {
    width: 100%;
    padding: 14px;
    overflow-x: auto;
  }

  .content-inner {
    width: 100%;
    min-width: 720px;
    max-width: none;
    min-height: auto;
  }

  .page-context {
    align-items: flex-start;
    flex-direction: column;
  }

  .context-actions {
    width: 100%;
  }

  .context-action {
    width: 100%;
  }

  .palette-actions {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 420px) {
  .nav-menu {
    grid-template-columns: 1fr;
  }
}
</style>
