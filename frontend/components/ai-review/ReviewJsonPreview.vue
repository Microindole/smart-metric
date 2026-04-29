<template>
  <a-card title="JSON 预览" class="panel-card">
    <pre class="preview-box">{{ previewText }}</pre>
  </a-card>
</template>

<script setup>
defineProps({
  previewText: { type: String, default: '' },
})
</script>

<style scoped>
.preview-box {
  white-space: pre-wrap;
  background: #111827;
  color: #d1fae5;
  padding: 12px;
  border-radius: 6px;
  min-height: 220px;
}
</style>
