<template>
  <a-card title="建议详情" class="panel-card">
    <div v-if="!recommendationRows.length" class="hint">当前没有可展示的建议详情。</div>
    <div v-else class="recommendation-stack">
      <div v-for="item in recommendationRows" :key="item.rowKey" class="recommendation-card">
        <div class="recommendation-head">
          <div class="recommendation-title">{{ item.filename }}</div>
          <a-tag :color="priorityColor(item.priority)">{{ item.priority || 'unknown' }}</a-tag>
        </div>
        <div class="recommendation-line"><strong>问题：</strong>{{ item.problem }}</div>
        <div class="recommendation-line"><strong>建议：</strong>{{ item.suggestion }}</div>
        <div class="recommendation-line"><strong>预期收益：</strong>{{ item.expected_benefit }}</div>
        <div class="recommendation-line"><strong>改动范围：</strong>{{ item.refactor_scope }}</div>
        <div v-if="item.target_symbols?.length" class="recommendation-line">
          <strong>目标符号：</strong>{{ item.target_symbols.join('、') }}
        </div>
        <div v-if="item.evidence?.length" class="recommendation-line">
          <strong>证据：</strong>
          <ul class="detail-list">
            <li v-for="(evidence, index) in item.evidence" :key="`${item.rowKey}-e-${index}`">{{ evidence }}</li>
          </ul>
        </div>
        <div v-if="item.refactor_steps?.length" class="recommendation-line">
          <strong>建议步骤：</strong>
          <ol class="detail-list">
            <li v-for="(step, index) in item.refactor_steps" :key="`${item.rowKey}-s-${index}`">{{ step }}</li>
          </ol>
        </div>
      </div>
    </div>
  </a-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  recommendations: { type: Array, default: () => [] },
})

const recommendationRows = computed(() =>
  props.recommendations.map((item, index) => ({ ...item, rowKey: `${item.filename}-${index}` }))
)

const priorityColor = (value) => {
  if (value === 'high') return 'red'
  if (value === 'medium') return 'orange'
  if (value === 'low') return 'blue'
  return 'default'
}
</script>

<style scoped>
.recommendation-stack {
  display: grid;
  gap: 12px;
}
.recommendation-card {
  border: 1px solid #e8edf5;
  border-radius: 8px;
  padding: 14px;
  background: #f8fafc;
}
.recommendation-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}
.recommendation-title {
  font-weight: 700;
  color: #102a43;
}
.recommendation-line {
  margin-bottom: 8px;
  color: #2f4058;
}
.detail-list {
  margin: 6px 0 0 18px;
}
</style>
