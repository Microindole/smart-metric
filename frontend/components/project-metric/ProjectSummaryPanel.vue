<template>
  <a-card title="本次扫描结果" class="panel-card">
    <a-empty v-if="!hasResult" description="选择项目目录并点击开始扫描后，这里会显示项目级结果。" />
    <div v-else class="summary-wrap">
      <div class="meta-grid">
        <div class="meta-item">
          <div class="meta-label">项目目录</div>
          <div class="meta-value">{{ rootPath }}</div>
        </div>
        <div class="meta-item">
          <div class="meta-label">扫描模块</div>
          <div class="meta-value">{{ moduleText }}</div>
        </div>
      </div>
      <a-row :gutter="12">
        <a-col :span="6"><a-statistic title="总文件数" :value="summary.total_files" /></a-col>
        <a-col :span="6"><a-statistic title="代码文件数" :value="summary.code_file_count" /></a-col>
        <a-col :span="6"><a-statistic title="设计文件数" :value="summary.design_file_count" /></a-col>
        <a-col :span="6"><a-statistic title="总代码行" :value="summary.code_lines" /></a-col>
        <a-col :span="6"><a-statistic title="依赖边数" :value="summary.dependency_edge_count" /></a-col>
        <a-col :span="6"><a-statistic title="类总数" :value="summary.class_count" /></a-col>
        <a-col :span="6"><a-statistic title="上帝文件" :value="summary.god_files" /></a-col>
        <a-col :span="6"><a-statistic title="上帝类" :value="summary.god_classes" /></a-col>
      </a-row>
    </div>
  </a-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  hasResult: { type: Boolean, default: false },
  rootPath: { type: String, default: '' },
  modules: { type: Array, default: () => [] },
  summary: { type: Object, default: () => ({}) },
})

const moduleText = computed(() => (props.modules?.length ? props.modules.join('、') : '全部'))
</script>

<style scoped>
.summary-wrap {
  display: grid;
  gap: 14px;
}
.meta-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
.meta-item {
  padding: 12px;
  border: 1px solid #e8edf5;
  border-radius: 8px;
  background: #f8fafc;
}
.meta-label {
  margin-bottom: 6px;
  color: #516070;
  font-size: 12px;
}
.meta-value {
  color: #102a43;
  line-height: 1.7;
  word-break: break-all;
}
@media (max-width: 960px) {
  .meta-grid {
    grid-template-columns: 1fr;
  }
}
</style>
