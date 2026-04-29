<template>
  <a-card title="审查结论" class="panel-card">
    <a-empty v-if="!hasResult" description="运行 AI 审查后，这里会显示项目概览、重构顺序和建议摘要。" />
    <div v-else class="overview-grid">
      <div class="overview-block">
        <div class="overview-title">项目概览</div>
        <div class="overview-text">{{ phase1Summary.project_overview || '无' }}</div>
      </div>
      <div class="overview-block">
        <div class="overview-title">总体优先级</div>
        <div class="overview-chip">{{ phase2Summary.overall_priority || 'unknown' }}</div>
      </div>
      <div class="overview-block">
        <div class="overview-title">建议重构顺序</div>
        <ol v-if="phase2Summary.refactor_order?.length" class="detail-list compact-list">
          <li v-for="(item, index) in phase2Summary.refactor_order" :key="`order-${index}`">{{ item }}</li>
        </ol>
        <div v-else class="overview-text">无</div>
      </div>
      <div class="overview-block">
        <div class="overview-title">重点文件</div>
        <ul v-if="focusFiles.length" class="detail-list compact-list">
          <li v-for="(file, index) in focusFiles" :key="`focus-${index}`">{{ file }}</li>
        </ul>
        <div v-else class="overview-text">无</div>
      </div>
    </div>
  </a-card>
</template>

<script setup>
defineProps({
  hasResult: { type: Boolean, default: false },
  phase1Summary: { type: Object, default: () => ({}) },
  phase2Summary: { type: Object, default: () => ({}) },
  focusFiles: { type: Array, default: () => [] },
})
</script>

<style scoped>
.overview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
.overview-block {
  border: 1px solid #e8edf5;
  border-radius: 8px;
  padding: 12px;
  background: #f8fafc;
}
.overview-title {
  margin-bottom: 8px;
  color: #516070;
  font-size: 12px;
}
.overview-text {
  color: #102a43;
  line-height: 1.7;
}
.overview-chip {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: #e6f4ff;
  color: #0958d9;
  font-weight: 600;
}
.detail-list {
  margin: 6px 0 0 18px;
}
.compact-list {
  margin-top: 0;
}
@media (max-width: 960px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }
}
</style>
