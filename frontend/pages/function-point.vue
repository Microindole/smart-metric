<template>
  <AppLayout activeKey="fp">
    <a-space direction="vertical" style="width: 100%" :size="14">
      <a-card title="功能点计数">
        <a-table :data-source="countRows" :columns="countColumns" row-key="type" :pagination="false" size="small">
          <template #bodyCell="{ column, record }">
            <template v-if="['simple', 'average', 'complex'].includes(column.key)">
              <a-input-number v-model:value="record[column.key]" :min="0" style="width: 100%" />
            </template>
          </template>
        </a-table>
      </a-card>

      <a-card title="14 个通用系统特征因子">
        <a-table :data-source="gscFactors" :columns="gscColumns" row-key="id" :pagination="false" size="small">
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'level'">
              <a-input-number v-model:value="record.level" :min="0" :max="5" />
            </template>
          </template>
        </a-table>
      </a-card>

      <a-card>
        <a-space>
          <a-button type="primary" :loading="loading" @click="calculate">计算 FP</a-button>
          <a-button @click="openFpFilePicker">选择 FP JSON 并分析</a-button>
          <a-button @click="loadDefaults">重置因子</a-button>
          <a-button @click="exportResult">导出 CSV</a-button>
        </a-space>
        <input
          ref="fpFileInput"
          type="file"
          accept=".json,application/json"
          style="display: none"
          @change="onFpFileSelected"
        />
      </a-card>

      <a-card title="计算结果">
        <a-row :gutter="12">
          <a-col :span="6"><a-statistic title="UFP" :value="result.ufp" /></a-col>
          <a-col :span="6"><a-statistic title="GSC 总分" :value="result.gsc_total" /></a-col>
          <a-col :span="6"><a-statistic title="VAF" :value="result.vaf" :precision="4" /></a-col>
          <a-col :span="6"><a-statistic title="FP" :value="result.fp" :precision="4" /></a-col>
        </a-row>
      </a-card>

      <a-card title="功能类型明细">
        <a-table :data-source="result.details" :columns="detailColumns" row-key="type" :pagination="false" size="small" />
      </a-card>
    </a-space>
  </AppLayout>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import AppLayout from '~/components/AppLayout.vue'
import api from '~/utils/api'
import { saveMetricSnapshot } from '~/utils/reportDraft'

const loading = ref(false)
const fpFileInput = ref(null)
const countRows = reactive([
  { type: 'EI', name: '外部输入', simple: 0, average: 0, complex: 0 },
  { type: 'EO', name: '外部输出', simple: 0, average: 0, complex: 0 },
  { type: 'EQ', name: '外部查询', simple: 0, average: 0, complex: 0 },
  { type: 'ILF', name: '内部逻辑文件', simple: 0, average: 0, complex: 0 },
  { type: 'EIF', name: '外部接口文件', simple: 0, average: 0, complex: 0 },
])
const gscFactors = ref([])
const result = reactive({ ufp: 0, gsc_total: 0, vaf: 0, fp: 0, details: [] })

const countColumns = [
  { title: '类型', dataIndex: 'type', key: 'type', width: 90 },
  { title: '说明', dataIndex: 'name', key: 'name' },
  { title: '简单', key: 'simple', width: 150 },
  { title: '平均', key: 'average', width: 150 },
  { title: '复杂', key: 'complex', width: 150 },
]
const gscColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '因子', dataIndex: 'name', key: 'name' },
  { title: '等级(0-5)', key: 'level', width: 150 },
]
const detailColumns = [
  { title: '类型', dataIndex: 'type', key: 'type', width: 90 },
  { title: '说明', dataIndex: 'name', key: 'name' },
  { title: '小计', dataIndex: 'subtotal', key: 'subtotal', width: 120 },
]

const normalizeLevel = (value) => {
  const numeric = Number(value)
  if (Number.isNaN(numeric)) {
    return 0
  }
  return Math.min(5, Math.max(0, Math.round(numeric)))
}

const normalizeCount = (value) => {
  const numeric = Number(value)
  if (Number.isNaN(numeric)) {
    return 0
  }
  return Math.max(0, Math.round(numeric))
}

const openFpFilePicker = () => {
  fpFileInput.value?.click()
}

const applyFpPayload = (payload) => {
  const counts = payload?.counts || {}
  countRows.forEach((row) => {
    const source = counts[row.type] || {}
    row.simple = normalizeCount(source.simple)
    row.average = normalizeCount(source.average)
    row.complex = normalizeCount(source.complex)
  })

  if (Array.isArray(payload?.gsc_factors) && payload.gsc_factors.length) {
    gscFactors.value = payload.gsc_factors.map((factor, index) => ({
      ...(gscFactors.value[index] || {}),
      ...factor,
      level: normalizeLevel(factor?.level),
    }))
  }
}

const onFpFileSelected = async (event) => {
  const file = event?.target?.files?.[0]
  event.target.value = ''
  if (!file) {
    return
  }

  try {
    const text = await file.text()
    const payload = JSON.parse(text)
    if (!payload || typeof payload !== 'object') {
      throw new Error('INVALID_PAYLOAD')
    }
    applyFpPayload(payload)
    await calculate()
  } catch (err) {
    message.error('JSON 文件解析失败，请检查 fp.json 格式')
  }
}

const loadDefaults = async () => {
  try {
    const { data } = await api.get('/api/metrics/function-point/defaults')
    gscFactors.value = data.data.gsc_factors
  } catch (err) {
    message.error(err?.response?.data?.message || '默认因子加载失败')
  }
}

const calculate = async () => {
  loading.value = true
  try {
    const counts = {}
    countRows.forEach((row) => {
      counts[row.type] = {
        simple: row.simple,
        average: row.average,
        complex: row.complex,
      }
    })
    const { data } = await api.post('/api/metrics/function-point/calculate', {
      counts,
      gsc_factors: gscFactors.value,
    })
    Object.assign(result, data.data)
    saveMetricSnapshot('function_point', {
      description: '基于功能点计数和 GSC 因子自动生成。',
      summary: {
        UFP: data.data.ufp,
        GSC总分: data.data.gsc_total,
        VAF: data.data.vaf,
        FP: data.data.fp,
      },
      rows: (data.data.details || []).map((item) => ({
        类型: item.type,
        说明: item.name,
        小计: item.subtotal,
      })),
    })
    message.success('功能点计算完成')
  } catch (err) {
    message.error(err?.response?.data?.message || '计算失败')
  } finally {
    loading.value = false
  }
}

const exportResult = async () => {
  try {
    const rows = [
      { metric: 'UFP', value: result.ufp },
      { metric: 'GSC_TOTAL', value: result.gsc_total },
      { metric: 'VAF', value: result.vaf },
      { metric: 'FP', value: result.fp },
    ]
    const res = await api.post('/api/export', { rows, filename: 'function-point.csv' }, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = 'function-point.csv'
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    message.error(err?.response?.data?.message || '导出失败')
  }
}

onMounted(loadDefaults)
</script>
