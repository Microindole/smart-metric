<template>
  <AppLayout activeKey="oo">
    <a-space direction="vertical" style="width: 100%" :size="14">
      <a-card title="Java 类代码上传">
        <a-space>
          <input type="file" multiple accept=".java" @change="onFilesSelected" />
          <a-button type="primary" :loading="loading" @click="analyze">开始 CK/LK 度量</a-button>
          <a-button @click="exportRows">导出 CSV</a-button>
        </a-space>
      </a-card>

      <a-card title="汇总结果">
        <a-row :gutter="12">
          <a-col :span="4"><a-statistic title="类数" :value="summary.class_count" /></a-col>
          <a-col :span="4"><a-statistic title="方法数" :value="summary.total_methods" /></a-col>
          <a-col :span="4"><a-statistic title="属性数" :value="summary.total_attributes" /></a-col>
          <a-col :span="4"><a-statistic title="平均 WMC" :value="summary.average_wmc" :precision="4" /></a-col>
          <a-col :span="4"><a-statistic title="最大 DIT" :value="summary.max_dit" /></a-col>
          <a-col :span="4"><a-statistic title="最大 CBO" :value="summary.max_cbo" /></a-col>
        </a-row>
      </a-card>

      <a-card title="类级 CK/LK 结果">
        <a-table :data-source="rows" :columns="columns" row-key="class_name" :pagination="false" />
      </a-card>
    </a-space>
  </AppLayout>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import AppLayout from '~/components/AppLayout.vue'
import api from '~/utils/api'

const selectedFiles = ref([])
const loading = ref(false)
const rows = ref([])
const summary = reactive({
  class_count: 0,
  total_methods: 0,
  total_attributes: 0,
  average_wmc: 0,
  max_dit: 0,
  max_cbo: 0,
  average_lcom: 0,
})

const columns = [
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

const onFilesSelected = (e) => {
  selectedFiles.value = Array.from(e.target.files || [])
}

const analyze = async () => {
  if (!selectedFiles.value.length) {
    message.warning('请先选择 Java 源码文件')
    return
  }
  loading.value = true
  try {
    const formData = new FormData()
    selectedFiles.value.forEach((f) => formData.append('files', f))
    const { data } = await api.post('/api/metrics/oo/calculate', formData)
    rows.value = data.data.classes
    Object.assign(summary, data.data.summary)
    message.success('面向对象度量完成')
  } catch (err) {
    message.error(err?.response?.data?.message || '分析失败')
  } finally {
    loading.value = false
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
    wmc: row.ck.wmc,
    dit: row.ck.dit,
    noc: row.ck.noc,
    cbo: row.ck.cbo,
    rfc: row.ck.rfc,
    lcom: row.ck.lcom,
    nom: row.lk.nom,
    noa: row.lk.noa,
    class_loc: row.lk.class_loc,
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
