<template>
  <a-card title="重点文件" class="panel-card">
    <a-table :data-source="focusRows" :columns="focusColumns" row-key="filename" :pagination="false" />
  </a-card>

  <a-card title="AI 发现" class="panel-card">
    <a-table :data-source="findings" :columns="findingColumns" row-key="id" :pagination="{ pageSize: 6 }" />
  </a-card>

  <a-card title="改进建议" class="panel-card">
    <a-table :data-source="recommendationRows" :columns="recommendationColumns" row-key="rowKey" :pagination="{ pageSize: 6 }" />
  </a-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  focusFiles: { type: Array, default: () => [] },
  findings: { type: Array, default: () => [] },
  recommendations: { type: Array, default: () => [] },
})

const focusColumns = [{ title: '文件', dataIndex: 'filename', key: 'filename' }]
const findingColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 90 },
  { title: '严重级别', dataIndex: 'severity', key: 'severity', width: 100 },
  { title: '类别', dataIndex: 'category', key: 'category', width: 120 },
  { title: '文件', dataIndex: 'filename', key: 'filename' },
  { title: '原因', dataIndex: 'reason', key: 'reason' },
]
const recommendationColumns = [
  { title: '优先级', dataIndex: 'priority', key: 'priority', width: 100 },
  { title: '文件', dataIndex: 'filename', key: 'filename' },
  { title: '问题', dataIndex: 'problem', key: 'problem' },
  { title: '建议', dataIndex: 'suggestion', key: 'suggestion' },
  { title: '收益', dataIndex: 'expected_benefit', key: 'expected_benefit' },
]

const focusRows = computed(() => props.focusFiles.map((filename) => ({ filename })))
const recommendationRows = computed(() =>
  props.recommendations.map((item, index) => ({ ...item, rowKey: `${item.filename}-${index}` }))
)
</script>
