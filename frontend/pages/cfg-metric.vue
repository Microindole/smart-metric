<template>
  <AppLayout activeKey="cfg">
    <a-space direction="vertical" style="width: 100%" :size="14">
      <a-card>
        <a-tabs v-model:activeKey="mode">
          <a-tab-pane key="source" tab="从源码生成控制流图" />
          <a-tab-pane key="graph" tab="导入控制流图" />
        </a-tabs>
      </a-card>

      <a-card v-if="mode === 'source'" title="代码文件上传（Java/C/C++/Python）">
        <a-space direction="vertical" style="width: 100%">
          <input type="file" multiple accept=".java,.c,.h,.cpp,.cc,.cxx,.hpp,.py" @change="onFilesSelected" />
          <a-space>
            <a-select v-model:value="language" style="width: 180px" placeholder="自动识别">
              <a-select-option value="">自动识别</a-select-option>
              <a-select-option value="java">Java</a-select-option>
              <a-select-option value="c">C</a-select-option>
              <a-select-option value="cpp">C++</a-select-option>
              <a-select-option value="python">Python</a-select-option>
            </a-select>
            <a-button type="primary" :loading="loading" @click="analyze">开始分析</a-button>
            <a-button @click="exportRows">导出 CSV</a-button>
          </a-space>
        </a-space>
      </a-card>

      <a-card v-else title="控制流图文件导入（JSON/Mermaid/DOT/OOM/XML）">
        <a-space direction="vertical" style="width: 100%">
          <input type="file" accept=".json,.mmd,.mermaid,.dot,.oom,.xml" @change="onGraphSelected" />
          <a-space>
            <a-button type="primary" :loading="graphLoading" @click="importGraph">导入并计算</a-button>
          </a-space>
        </a-space>
        <div class="hint">
          JSON 格式示例：{"nodes":["start","if1","end"],"edges":[["start","if1"],["if1","end"]]}
        </div>
      </a-card>

      <a-card title="汇总结果">
        <a-row :gutter="12">
          <a-col :span="6"><a-statistic title="文件数" :value="summary.file_count" /></a-col>
          <a-col :span="6"><a-statistic title="最大圈复杂度" :value="summary.max_complexity" /></a-col>
          <a-col :span="6"><a-statistic title="平均圈复杂度" :value="summary.average_complexity" :precision="4" /></a-col>
          <a-col :span="6"><a-statistic :title="mode === 'graph' ? '边数' : '判定点总数'" :value="mode === 'graph' ? summary.edge_count : summary.total_decision_points" /></a-col>
        </a-row>
      </a-card>

      <a-card title="文件级结果">
        <a-table :data-source="rows" :columns="columns" row-key="filename" :pagination="false" />
      </a-card>

      <a-card v-if="selectedRow" :title="`${selectedRow.filename} 控制流图 Mermaid`">
        <pre class="mermaid-box">{{ selectedRow.mermaid }}</pre>
      </a-card>
    </a-space>
  </AppLayout>
</template>

<script setup>
import { h, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import AppLayout from '~/components/AppLayout.vue'
import api from '~/utils/api'

const loading = ref(false)
const graphLoading = ref(false)
const mode = ref('source')
const selectedFiles = ref([])
const selectedGraph = ref(null)
const language = ref('')
const rows = ref([])
const selectedRow = ref(null)
const summary = reactive({
  file_count: 0,
  max_complexity: 0,
  average_complexity: 0,
  total_decision_points: 0,
  edge_count: 0,
})

const columns = [
  { title: '文件名', dataIndex: 'filename', key: 'filename' },
  { title: '语言', dataIndex: 'language', key: 'language', width: 90 },
  { title: '判定点', dataIndex: 'decision_points', key: 'decision_points', width: 100 },
  { title: '圈复杂度', dataIndex: 'cyclomatic_complexity', key: 'cyclomatic_complexity', width: 110 },
  { title: 'E-N+2P', dataIndex: 'formula_complexity', key: 'formula_complexity', width: 110 },
  {
    title: '操作',
    key: 'action',
    width: 120,
    customRender: ({ record }) =>
      h(
        'a',
        {
          onClick: () => {
            selectedRow.value = record
          },
        },
        '查看图文本'
      ),
  },
]

const onFilesSelected = (e) => {
  selectedFiles.value = Array.from(e.target.files || [])
}

const onGraphSelected = (e) => {
  selectedGraph.value = e.target.files?.[0] || null
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

    const { data } = await api.post('/api/metrics/cfg/calculate', formData)
    rows.value = data.data.files
    Object.assign(summary, data.data.summary)
    selectedRow.value = rows.value[0] || null
    message.success('控制流图度量完成')
  } catch (err) {
    message.error(err?.response?.data?.message || '分析失败')
  } finally {
    loading.value = false
  }
}

const importGraph = async () => {
  if (!selectedGraph.value) {
    message.warning('请先选择控制流图文件')
    return
  }
  graphLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedGraph.value)
    const { data } = await api.post('/api/metrics/cfg/import-graph', formData)
    const item = {
      ...data.data,
      language: data.data.format,
      decision_points: '-',
      formula_complexity: data.data.cyclomatic_complexity,
    }
    rows.value = [item]
    Object.assign(summary, {
      file_count: 1,
      max_complexity: item.cyclomatic_complexity,
      average_complexity: item.cyclomatic_complexity,
      total_decision_points: 0,
      edge_count: item.edge_count,
    })
    selectedRow.value = item
    message.success('控制流图导入完成')
  } catch (err) {
    message.error(err?.response?.data?.message || '导入失败')
  } finally {
    graphLoading.value = false
  }
}

const exportRows = async () => {
  if (!rows.value.length) {
    message.warning('暂无可导出数据')
    return
  }
  try {
    const exportData = rows.value.map((row) => ({
      filename: row.filename,
      language: row.language,
      decision_points: row.decision_points,
      cyclomatic_complexity: row.cyclomatic_complexity,
      formula_complexity: row.formula_complexity,
    }))
    const res = await api.post('/api/export', { rows: exportData, filename: 'cfg-metric.csv' }, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = 'cfg-metric.csv'
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    message.error(err?.response?.data?.message || '导出失败')
  }
}
</script>

<style scoped>
.mermaid-box {
  white-space: pre-wrap;
  background: #111827;
  color: #d1fae5;
  padding: 12px;
  border-radius: 6px;
}
.hint {
  margin-top: 10px;
  color: #666;
  font-size: 12px;
}
</style>
