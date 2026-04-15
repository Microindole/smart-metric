<template>
  <AppLayout activeKey="loc">
    <a-space direction="vertical" style="width: 100%" :size="14">
      <a-card title="代码文件上传（Java/Python/C++）">
        <a-space direction="vertical" style="width: 100%">
          <input type="file" multiple accept=".java,.py,.cpp,.cc,.cxx,.hpp,.h" @change="onFilesSelected" />
          <a-space>
            <a-select v-model:value="language" style="width: 180px" placeholder="自动识别">
              <a-select-option value="">自动识别</a-select-option>
              <a-select-option value="java">Java</a-select-option>
              <a-select-option value="python">Python</a-select-option>
              <a-select-option value="cpp">C++</a-select-option>
            </a-select>
            <a-button type="primary" :loading="loading" @click="analyze">开始分析</a-button>
            <a-button @click="exportLoc">导出 CSV</a-button>
          </a-space>
        </a-space>
      </a-card>

      <a-card title="汇总结果">
        <a-row :gutter="12">
          <a-col :span="6"><a-statistic title="总行数" :value="summary.total_lines" /></a-col>
          <a-col :span="6"><a-statistic title="有效代码行" :value="summary.code_lines" /></a-col>
          <a-col :span="6"><a-statistic title="注释行" :value="summary.comment_lines" /></a-col>
          <a-col :span="6"><a-statistic title="空行" :value="summary.blank_lines" /></a-col>
        </a-row>
      </a-card>

      <a-card title="文件级结果">
        <a-table :data-source="rows" :columns="columns" row-key="filename" :pagination="false" />
      </a-card>
    </a-space>
  </AppLayout>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import AppLayout from '~/components/AppLayout.vue'
import api from '~/utils/api'

const loading = ref(false)
const selectedFiles = ref([])
const language = ref('')
const rows = ref([])
const summary = reactive({ total_lines: 0, code_lines: 0, comment_lines: 0, blank_lines: 0 })

const columns = [
  { title: '文件名', dataIndex: 'filename', key: 'filename' },
  { title: '语言', dataIndex: 'language', key: 'language', width: 110 },
  { title: '总行数', dataIndex: 'total_lines', key: 'total_lines', width: 100 },
  { title: '有效代码行', dataIndex: 'code_lines', key: 'code_lines', width: 120 },
  { title: '注释行', dataIndex: 'comment_lines', key: 'comment_lines', width: 100 },
  { title: '空行', dataIndex: 'blank_lines', key: 'blank_lines', width: 90 },
  {
    title: '注释率',
    dataIndex: 'comment_ratio',
    key: 'comment_ratio',
    width: 100,
    customRender: ({ text }) => `${Math.round((Number(text) || 0) * 100)}%`,
  },
]

const onFilesSelected = (e) => {
  selectedFiles.value = Array.from(e.target.files || [])
}

const analyze = async () => {
  if (!selectedFiles.value.length) {
    message.warning('请先选择代码文件')
    return
  }

  loading.value = true
  try {
    const formData = new FormData()
    selectedFiles.value.forEach((f) => formData.append('files', f))
    if (language.value) formData.append('language', language.value)

    const { data } = await api.post('/api/metrics/loc/calculate', formData)
    rows.value = data.data.files
    Object.assign(summary, data.data.summary)
    message.success('代码行统计完成')
  } catch (err) {
    message.error(err?.response?.data?.message || '统计失败')
  } finally {
    loading.value = false
  }
}

const exportLoc = async () => {
  if (!rows.value.length) {
    message.warning('暂无可导出数据')
    return
  }
  try {
    const res = await api.post('/api/export', { rows: rows.value, filename: 'loc-metric.csv' }, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = 'loc-metric.csv'
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    message.error(err?.response?.data?.message || '导出失败')
  }
}
</script>
