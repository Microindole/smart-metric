<template>
  <div class="home">
    <section class="workspace-header">
      <div class="header-copy">
        <div class="eyebrow">SmartMetric</div>
        <h1>安静、可解释的软件度量工作台。</h1>
        <p>面向真实项目的度量、扫描、估算和报告生成工作流。</p>
        <div class="header-actions">
          <button class="primary-action" @click="navigateTo('/usecase-metric')">开始度量</button>
          <button class="secondary-action" @click="navigateTo('/report-export')">查看报告导出</button>
        </div>
      </div>
      <div class="status-panel">
        <div class="status-label">Metric engines</div>
        <div class="status-value">5 core</div>
        <div class="status-text">UCP、LoC、OO、FP、CFG 均已接入可计算接口。</div>
      </div>
    </section>

    <section class="coverage-strip">
      <div v-for="item in requiredItems" :key="item.acronym" class="coverage-item">
        <span class="coverage-acronym">{{ item.acronym }}</span>
        <span class="coverage-name">{{ item.name }}</span>
      </div>
    </section>

    <section class="workbench">
      <div class="module-section">
        <div class="section-heading">
          <div>
            <h2>度量模块</h2>
            <p>选择一个模块开始计算、扫描或导出结果。</p>
          </div>
        </div>

        <div class="module-list">
          <button v-for="item in items" :key="item.path" class="module-item" @click="navigateTo(item.path)">
            <span class="module-acronym">{{ item.acronym }}</span>
            <span class="module-content">
              <span class="module-category">{{ item.category }}</span>
              <span class="module-title-row">
                <span class="module-title">{{ item.title }}</span>
                <span class="module-status">{{ item.status }}</span>
              </span>
              <span class="module-text">{{ item.text }}</span>
            </span>
          </button>
        </div>
      </div>

      <div class="side-notes">
        <div class="note-block">
          <div class="note-label">输入类型</div>
          <p>源码、用例图、类图、控制流图和手工规模参数。</p>
        </div>
        <div class="note-block">
          <div class="note-label">输出交付</div>
          <p>表格结果、CSV、Markdown、HTML 和 PDF 报告。</p>
        </div>
        <div class="note-block accent">
          <div class="note-label">工作流</div>
          <p>在各模块完成计算后，报告管线会汇总已保存的项目结果。</p>
        </div>
        <div class="plugin-panel">
          <div class="note-label">工作插件</div>
          <button v-for="plugin in plugins" :key="plugin.path" class="plugin-row" @click="navigateTo(plugin.path)">
            <span>
              <span class="plugin-name">{{ plugin.name }}</span>
              <span class="plugin-text">{{ plugin.text }}</span>
            </span>
            <span class="plugin-state">{{ plugin.state }}</span>
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
const requiredItems = [
  { acronym: 'UCP', name: '用例点' },
  { acronym: 'LoC', name: '代码行' },
  { acronym: 'OO', name: '面向对象' },
  { acronym: 'FP', name: '功能点' },
  { acronym: 'CFG', name: '控制流图' },
]

const items = [
  { path: '/usecase-metric', acronym: 'UCP', title: '用例点度量', text: '从用例与参与者复杂度计算 UUC、UAW、TCF、EF 与 UCP。', category: '需求规模', status: '可用' },
  { path: '/loc-metric', acronym: 'LoC', title: '代码行度量', text: '统计总行、空行、注释行、有效代码行与源码结构信息。', category: '代码规模', status: '可用' },
  { path: '/oo-metric', acronym: 'OO', title: '面向对象度量', text: '支持源码级和类图级 CK / LK 指标分析。', category: '设计质量', status: '可用' },
  { path: '/function-point', acronym: 'FP', title: '功能点度量', text: '按 EI、EO、EQ、ILF、EIF 与 GSC 因子计算功能点。', category: '功能规模', status: '可用' },
  { path: '/cfg-metric', acronym: 'CFG', title: '控制流图度量', text: '从源码或结构化图文件计算控制流图与圈复杂度。', category: '复杂度', status: '可用' },
  { path: '/project-metric', acronym: 'PRJ', title: '项目扫描', text: '扫描项目目录，汇总代码、依赖、设计图与风险文件。', category: '项目级', status: '工具' },
  { path: '/estimate-metric', acronym: 'EST', title: '项目估算', text: '基于 FP、UCP 或 LoC 估算工作量、成本、工期和人数。', category: '估算', status: '工具' },
  { path: '/report-export', acronym: 'RPT', title: '报告导出', text: '汇总已保存结果并导出 Markdown、HTML 或 PDF。', category: '交付', status: '工具' },
]

const plugins = [
  { path: '/project-metric', name: '项目扫描', text: '目录、依赖与风险文件', state: 'Ready' },
  { path: '/estimate-metric', name: '估算器', text: '工作量、成本和工期', state: 'Ready' },
  { path: '/report-export', name: '报告管线', text: 'Markdown / HTML / PDF', state: 'Ready' },
]
</script>

<style scoped>
.home {
  min-height: 100vh;
  padding: 34px clamp(18px, 4vw, 54px) 48px;
  background:
    linear-gradient(90deg, rgba(255, 252, 247, 0.9) 0%, rgba(247, 243, 236, 0.56) 46%, transparent 100%),
    #f5f1ea;
}

.workspace-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: clamp(24px, 5vw, 72px);
  align-items: stretch;
  max-width: 1260px;
  margin: 0 auto 8px;
  padding: 42px 0 38px;
  border-bottom: 1px solid rgba(226, 217, 207, 0.9);
}

.header-copy {
  max-width: 760px;
}

.eyebrow {
  color: #a94f34;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

h1 {
  max-width: 900px;
  margin: 10px 0 12px;
  color: #191714;
  font-family: var(--sm-font-display);
  font-size: clamp(38px, 3.8vw, 52px);
  font-weight: 650;
  line-height: 1.1;
  letter-spacing: 0;
}

p {
  margin: 0;
  color: #766b60;
  line-height: 1.7;
}

.header-actions {
  display: flex;
  gap: 10px;
  margin-top: 24px;
}

.primary-action,
.secondary-action {
  min-height: 38px;
  padding: 0 15px;
  border-radius: 8px;
  font-weight: 750;
  cursor: pointer;
  transition: transform 0.16s ease, border-color 0.16s ease, color 0.16s ease, box-shadow 0.16s ease;
}

.primary-action {
  border: 1px solid #c65f3d;
  background: #c65f3d;
  color: #fffaf4;
  box-shadow: 0 12px 24px rgba(198, 95, 61, 0.2);
}

.secondary-action {
  border: 1px solid #d6cabe;
  background: #fffcf7;
  color: #3c342d;
}

.primary-action:hover,
.secondary-action:hover {
  transform: translateY(-1px);
}

.status-panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-left: 24px;
  border-left: 1px solid rgba(226, 217, 207, 0.92);
}

.status-label {
  color: #93887c;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.status-value {
  margin-top: 8px;
  color: #191714;
  font-size: 38px;
  font-weight: 800;
  line-height: 1;
}

.status-text {
  margin-top: 8px;
  color: #766b60;
  font-size: 13px;
  line-height: 1.5;
}

.coverage-strip {
  max-width: 1260px;
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 0;
  margin: 0 auto 28px;
  border-bottom: 1px solid rgba(226, 217, 207, 0.9);
}

.coverage-item {
  min-height: 58px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 10px 16px 0;
  border: 0;
  background: transparent;
}

.coverage-item + .coverage-item {
  padding-left: 18px;
  border-left: 1px solid rgba(226, 217, 207, 0.72);
}

.coverage-acronym {
  color: #a94f34;
  font-size: 13px;
  font-weight: 800;
}

.coverage-name {
  color: #312c26;
  font-size: 14px;
  font-weight: 700;
}

.workbench {
  max-width: 1260px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 32px;
  margin: 0 auto;
}

.module-section,
.side-notes {
  padding: 0;
  border: 0;
  background: transparent;
}

.section-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

h2 {
  margin: 0 0 6px;
  color: #191714;
  font-family: var(--sm-font-display);
  font-size: 22px;
  font-weight: 720;
  line-height: 1.3;
}

.secondary-action:hover {
  border-color: #c65f3d;
  color: #a94f34;
  box-shadow: 0 10px 24px rgba(82, 63, 45, 0.08);
}

.module-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0;
  border-top: 1px solid rgba(226, 217, 207, 0.9);
}

.module-item {
  min-height: 132px;
  display: flex;
  gap: 14px;
  padding: 20px 18px 22px 0;
  border: 0;
  border-bottom: 1px solid rgba(226, 217, 207, 0.9);
  border-radius: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
  transition: background 0.16s ease, color 0.16s ease;
}

.module-item:nth-child(even) {
  padding-left: 18px;
  border-left: 1px solid rgba(226, 217, 207, 0.72);
}

.module-item:hover {
  background: rgba(255, 252, 247, 0.72);
}

.module-acronym {
  width: 46px;
  height: 34px;
  flex: 0 0 auto;
  display: inline-grid;
  place-items: center;
  border-radius: 8px;
  background: #f4e5da;
  color: #a94f34;
  font-weight: 800;
}

.module-content {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.module-category {
  color: #93887c;
  font-size: 12px;
  font-weight: 800;
}

.module-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: 4px;
}

.module-title {
  color: #191714;
  font-size: 17px;
  font-weight: 760;
}

.module-status {
  flex: 0 0 auto;
  padding: 2px 7px;
  border: 1px solid #ead4c8;
  border-radius: 999px;
  color: #a94f34;
  font-size: 11px;
  font-weight: 760;
  line-height: 1.3;
}

.module-text {
  margin-top: 8px;
  color: #766b60;
  font-size: 14px;
  line-height: 1.6;
}

@media (max-width: 900px) {
  .home {
    padding: 16px;
  }

  .workspace-header {
    grid-template-columns: 1fr;
    padding: 22px;
  }

  .status-panel {
    padding-left: 0;
    padding-top: 18px;
    border-left: 0;
    border-top: 1px solid #e2d9cf;
  }
}

.side-notes {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding-left: 24px;
  border-left: 1px solid rgba(226, 217, 207, 0.9);
}

.note-block {
  padding: 0 0 18px;
  border-bottom: 1px solid #e2d9cf;
}

.note-block:last-child {
  padding-bottom: 0;
  border-bottom: 0;
}

.note-block.accent {
  margin-top: 18px;
  padding: 14px;
  border: 1px solid #ead4c8;
  border-radius: 8px;
  background: #fbf0e8;
}

.note-label {
  margin-bottom: 6px;
  color: #a94f34;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.plugin-panel {
  margin-top: 22px;
  padding-top: 18px;
  border-top: 1px solid #e2d9cf;
}

.plugin-row {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 8px;
  padding: 11px 0;
  border: 0;
  border-bottom: 1px solid rgba(226, 217, 207, 0.75);
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.plugin-row:last-child {
  border-bottom: 0;
}

.plugin-name,
.plugin-text {
  display: block;
}

.plugin-name {
  color: #191714;
  font-weight: 760;
}

.plugin-text {
  margin-top: 3px;
  color: #766b60;
  font-size: 13px;
}

.plugin-state {
  flex: 0 0 auto;
  color: #a94f34;
  font-size: 11px;
  font-weight: 820;
  text-transform: uppercase;
}

@media (max-width: 1020px) {
  .workbench {
    grid-template-columns: 1fr;
  }

  .module-list {
    grid-template-columns: 1fr;
  }

  .module-item:nth-child(even) {
    padding-left: 0;
    border-left: 0;
  }

  .side-notes {
    padding-left: 0;
    border-left: 0;
    border-top: 1px solid rgba(226, 217, 207, 0.9);
    padding-top: 20px;
  }
}

@media (max-width: 900px) {
  .coverage-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .coverage-item + .coverage-item {
    padding-left: 0;
    border-left: 0;
  }

  .section-heading {
    flex-direction: column;
  }

  .primary-action,
  .secondary-action {
    width: 100%;
  }

  .header-actions {
    flex-direction: column;
  }
}

@media (max-width: 560px) {
  h1 {
    font-size: 34px;
  }

  .coverage-strip,
  .module-list {
    grid-template-columns: 1fr;
  }
}
</style>
