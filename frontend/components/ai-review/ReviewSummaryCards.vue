<template>
  <a-card title="审查摘要" class="panel-card">
    <a-row :gutter="12">
      <a-col :span="6"><a-statistic title="AI 风险等级" :value="riskLevel" /></a-col>
      <a-col :span="6"><a-statistic title="重点文件数" :value="focusCount" /></a-col>
      <a-col :span="6"><a-statistic title="发现数" :value="findingCount" /></a-col>
      <a-col :span="6"><a-statistic title="建议数" :value="recommendationCount" /></a-col>
    </a-row>
  </a-card>
</template>

<script setup>
defineProps({
  riskLevel: { type: String, default: 'unknown' },
  focusCount: { type: Number, default: 0 },
  findingCount: { type: Number, default: 0 },
  recommendationCount: { type: Number, default: 0 },
})
</script>
