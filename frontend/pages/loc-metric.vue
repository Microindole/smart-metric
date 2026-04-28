<template>
  <AppLayout activeKey="loc">
    <div class="page-wrap">
      <a-card title="代码文件上传（Java/Python/C++）" class="panel-card">
        <div class="upload-row">
          <input type="file" multiple accept=".java,.py,.cpp,.cc,.cxx,.hpp,.h" @change="onFilesSelected" />
          <div class="upload-actions">
            <a-select v-model:value="language" style="width: 180px" placeholder="自动识别">
              <a-select-option value="">自动识别</a-select-option>
              <a-select-option value="java">Java</a-select-option>
              <a-select-option value="python">Python</a-select-option>
              <a-select-option value="cpp">C++</a-select-option>
            </a-select>
            <a-button type="primary" :loading="loading" @click="analyze">开始分析</a-button>
            <a-button @click="exportLoc">导出 CSV</a-button>
          </div>
        </div>
      </a-card>

      <a-card title="汇总结果" class="panel-card">
        <a-row :gutter="12">
          <a-col :span="6"><a-statistic title="总行数" :value="summary.total_lines" /></a-col>
          <a-col :span="6"><a-statistic title="有效代码行" :value="summary.code_lines" /></a-col>
          <a-col :span="6"><a-statistic title="注释行" :value="summary.comment_lines" /></a-col>
          <a-col :span="6"><a-statistic title="空行" :value="summary.blank_lines" /></a-col>
          <a-col :span="6"><a-statistic title="类总数" :value="summary.class_count" /></a-col>
          <a-col :span="6"><a-statistic title="方法总数" :value="summary.method_count" /></a-col>
        </a-row>
      </a-card>

      <a-card title="代码行分析结果" class="panel-card">
        <div v-if="structureSummaries.length">
          <div v-for="item in structureSummaries" :key="`${item.filename}-${item.language}`" class="analysis-line">
            该 {{ item.filename }}（{{ item.language }}）中：类 {{ item.class_count }} 个，方法 {{ item.method_count }} 个，判断语句 {{ item.condition_count }} 处，循环语句 {{ item.loop_count }} 处。
          </div>
        </div>
        <div v-else class="analysis-line">当前未检测到可展示的结构化结果（支持 Java/Python/C++）。</div>
      </a-card>

      <a-card title="抽象语法树分析结果（类级）" class="panel-card">
        <a-table :data-source="classRows" :columns="classColumns" row-key="rowKey" :pagination="{ pageSize: 6 }" />
      </a-card>

      <a-card title="抽象语法树分析结果（方法级）" class="panel-card">
        <a-table :data-source="methodRows" :columns="methodColumns" row-key="rowKey" :pagination="{ pageSize: 6 }" />
      </a-card>

      <a-card title="文件级结果" class="panel-card">
        <a-table :data-source="rows" :columns="columns" row-key="filename" :pagination="false" />
      </a-card>
    </div>
  </AppLayout>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import AppLayout from '~/components/AppLayout.vue'
import api from '~/utils/api'
import { saveMetricSnapshot } from '~/utils/reportDraft'

const loading = ref(false)
const selectedFiles = ref([])
const language = ref('')
const rows = ref([])
const classRows = ref([])
const methodRows = ref([])
const structureSummaries = ref([])
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

const classColumns = [
  { title: '文件名', dataIndex: 'filename', key: 'filename' },
  { title: '类名', dataIndex: 'class_name', key: 'class_name' },
  { title: '方法数(RFC基础)', dataIndex: 'method_count', key: 'method_count', width: 140 },
  { title: '字段数', dataIndex: 'field_count', key: 'field_count', width: 100 },
  { title: 'RFC', dataIndex: 'rfc', key: 'rfc', width: 90 },
  { title: 'LCOM', dataIndex: 'lcom', key: 'lcom', width: 90 },
]

const methodColumns = [
  { title: '文件名', dataIndex: 'filename', key: 'filename' },
  { title: '类名', dataIndex: 'class_name', key: 'class_name', width: 140 },
  { title: '方法名', dataIndex: 'method_name', key: 'method_name', width: 150 },
  { title: '调用的方法', dataIndex: 'called_methods', key: 'called_methods' },
  { title: '使用的变量', dataIndex: 'used_variables', key: 'used_variables' },
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
    classRows.value = (data.data.class_scales || []).map((x, i) => ({ ...x, rowKey: `${x.filename}-${x.class_name}-${i}` }))
    methodRows.value = (data.data.method_scales || []).map((x, i) => ({ ...x, rowKey: `${x.filename}-${x.class_name}-${x.method_name}-${i}` }))
    structureSummaries.value = data.data.structure_summaries || data.data.java_structure_summaries || []
    saveMetricSnapshot('loc', {
      description: '基于源码文件进行代码行与结构统计。',
      summary: {
        文件数: data.data.summary.file_count,
        总行数: data.data.summary.total_lines,
        有效代码行: data.data.summary.code_lines,
        注释行: data.data.summary.comment_lines,
        类总数: data.data.summary.class_count,
        方法总数: data.data.summary.method_count,
      },
      rows: (data.data.files || []).map((item) => ({
        文件名: item.filename,
        语言: item.language,
        总行数: item.total_lines,
        有效代码行: item.code_lines,
      })),
    })
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

<style scoped>
.page-wrap {
  display: grid;
  gap: 14px;
}
.panel-card {
  border-radius: 12px;
  border: 1px solid #e8edf5;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
}
.upload-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.upload-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.analysis-line {
  margin-bottom: 8px;
  color: #2f4058;
  line-height: 1.7;
}
</style>
