<template>
  <AppLayout activeKey="oo">
    <a-space direction="vertical" style="width: 100%" :size="14">
      <a-card>
        <a-tabs v-model:activeKey="mode">
          <a-tab-pane key="source" tab="源码级 CK/LK" />
          <a-tab-pane key="diagram" tab="类图级 OO 度量" />
        </a-tabs>
      </a-card>

      <a-card v-if="mode === 'source'" title="源码级 OO/结构度量">
        <a-space>
          <a-select v-model:value="sourceLanguage" style="width: 180px" :options="languageOptions" />
          <input type="file" multiple accept=".java,.py,.js,.jsx,.ts,.tsx,.cpp,.cc,.cxx,.hpp,.hh,.hxx,.c,.h" @change="onFilesSelected" />
          <a-button type="primary" :loading="loading" @click="analyze">开始源码度量</a-button>
          <a-button @click="exportRows">导出 CSV</a-button>
        </a-space>
      </a-card>

      <a-card v-else title="类图文件上传（.xml/.oom）">
        <a-space>
          <input type="file" accept=".xml,.oom" @change="onDiagramSelected" />
          <a-button type="primary" :loading="diagramLoading" @click="analyzeDiagram">开始类图度量</a-button>
          <a-button @click="exportRows">导出 CSV</a-button>
        </a-space>
      </a-card>

      <a-card title="汇总结果">
        <a-row :gutter="12">
          <a-col :span="4"><a-statistic title="类数" :value="summary.class_count" /></a-col>
          <a-col :span="4"><a-statistic title="方法数" :value="summary.total_methods" /></a-col>
          <a-col :span="4"><a-statistic title="属性数" :value="summary.total_attributes" /></a-col>
          <a-col :span="4"><a-statistic :title="mode === 'source' ? '平均 WMC' : '关系数'" :value="mode === 'source' ? summary.average_wmc : summary.relation_count" :precision="4" /></a-col>
          <a-col :span="4"><a-statistic title="最大 DIT" :value="summary.max_dit" /></a-col>
          <a-col :span="4"><a-statistic title="最大 CBO" :value="summary.max_cbo" /></a-col>
        </a-row>
      </a-card>

      <a-card :title="mode === 'source' ? '类级 CK/LK 结果' : '类图级 OO 结果'">
        <a-table :data-source="rows" :columns="columns" row-key="class_name" :pagination="false" />
      </a-card>
    </a-space>
  </AppLayout>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import AppLayout from '~/components/AppLayout.vue'
import api from '~/utils/api'

const mode = ref('source')
const selectedFiles = ref([])
const selectedDiagram = ref(null)
const sourceLanguage = ref('auto')
const loading = ref(false)
const diagramLoading = ref(false)
const rows = ref([])
const summary = reactive({
  class_count: 0,
  total_methods: 0,
  total_attributes: 0,
  average_wmc: 0,
  max_dit: 0,
  max_cbo: 0,
  average_lcom: 0,
  relation_count: 0,
})

const sourceColumns = [
  { title: '文件名', dataIndex: 'filename', key: 'filename' },
  { title: '类名', dataIndex: 'class_name', key: 'class_name', width: 140 },
  { title: '父类', dataIndex: 'parent', key: 'parent', width: 120 },
  { title: 'WMC', dataIndex: ['ck', 'wmc'], key: 'wmc', width: 90 },
  { title: 'DIT', dataIndex: ['ck', 'dit'], key: 'dit', width: 90 },
  { title: 'NOC', dataIndex: ['ck', 'noc'], key: 'noc', width: 90 },
  { title: 'CBO', dataIndex: ['ck', 'cbo'], key: 'cbo', width: 90 },
  { title: 'RFC', dataIndex: ['ck', 'rfc'], key: 'rfc', width: 90 },
  { title: 'LCOM', dataIndex: ['ck', 'lcom'], key: 'lcom', width: 90 },
  { title: 'NOM', dataIndex: ['lk', 'nom'], key: 'nom', width: 90 },
  { title: 'NOA', dataIndex: ['lk', 'noa'], key: 'noa', width: 90 },
]
const diagramColumns = [
  { title: '文件名', dataIndex: 'filename', key: 'filename' },
  { title: '类名', dataIndex: 'class_name', key: 'class_name', width: 140 },
  { title: '父类', dataIndex: 'parent', key: 'parent', width: 120 },
  { title: 'DIT', dataIndex: ['diagram_ck', 'dit'], key: 'dit', width: 90 },
  { title: 'NOC', dataIndex: ['diagram_ck', 'noc'], key: 'noc', width: 90 },
  { title: 'CBO', dataIndex: ['diagram_ck', 'cbo'], key: 'cbo', width: 90 },
  { title: 'NOM', dataIndex: ['diagram_lk', 'nom'], key: 'nom', width: 90 },
  { title: 'NOA', dataIndex: ['diagram_lk', 'noa'], key: 'noa', width: 90 },
]
const columns = computed(() => (mode.value === 'source' ? sourceColumns : diagramColumns))
const languageOptions = [
  { label: '自动识别', value: 'auto' },
  { label: 'Java', value: 'java' },
  { label: 'C', value: 'c' },
  { label: 'C++', value: 'cpp' },
  { label: 'Python', value: 'python' },
  { label: 'JavaScript', value: 'javascript' },
]

const onFilesSelected = (e) => {
  selectedFiles.value = Array.from(e.target.files || [])
}

const onDiagramSelected = (e) => {
  selectedDiagram.value = e.target.files?.[0] || null
}

const analyze = async () => {
  if (!selectedFiles.value.length) {
    message.warning('请先选择源码文件')
    return
  }
  loading.value = true
  try {
    const formData = new FormData()
    selectedFiles.value.forEach((f) => formData.append('files', f))
    if (sourceLanguage.value !== 'auto') {
      formData.append('language', sourceLanguage.value)
    }
    const { data } = await api.post('/api/metrics/oo/calculate', formData)
    rows.value = data.data.classes
    Object.assign(summary, data.data.summary)
    message.success('源码度量完成')
  } catch (err) {
    message.error(err?.response?.data?.message || '分析失败')
  } finally {
    loading.value = false
  }
}

const analyzeDiagram = async () => {
  if (!selectedDiagram.value) {
    message.warning('请先选择类图文件')
    return
  }
  diagramLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedDiagram.value)
    const { data } = await api.post('/api/metrics/oo/diagram-calculate', formData)
    rows.value = data.data.classes
    Object.assign(summary, data.data.summary)
    message.success('类图级面向对象度量完成')
  } catch (err) {
    message.error(err?.response?.data?.message || '类图分析失败')
  } finally {
    diagramLoading.value = false
  }
}

const exportRows = async () => {
  if (!rows.value.length) {
    message.warning('暂无可导出数据')
    return
  }
  const exportData = rows.value.map((row) => ({
    filename: row.filename,
    class_name: row.class_name,
    parent: row.parent,
    wmc: row.ck?.wmc,
    dit: row.ck?.dit ?? row.diagram_ck?.dit,
    noc: row.ck?.noc ?? row.diagram_ck?.noc,
    cbo: row.ck?.cbo ?? row.diagram_ck?.cbo,
    rfc: row.ck?.rfc,
    lcom: row.ck?.lcom,
    nom: row.lk?.nom ?? row.diagram_lk?.nom,
    noa: row.lk?.noa ?? row.diagram_lk?.noa,
    class_loc: row.lk?.class_loc,
  }))
  const res = await api.post('/api/export', { rows: exportData, filename: 'oo-metric.csv' }, { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const a = document.createElement('a')
  a.href = url
  a.download = 'oo-metric.csv'
  a.click()
  window.URL.revokeObjectURL(url)
}
</script>
