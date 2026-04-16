<template>
  <AppLayout activeKey="usecase">
    <div class="page-wrap">
      <a-card title="文件上传（.oom）" class="panel-card">
        <div class="upload-row">
          <input type="file" accept=".oom,.xml" @change="onOomSelected" />
          <a-button type="primary" :loading="parseLoading" @click="parseOom">开始分析</a-button>
          <a-button @click="loadSampleFactors">加载默认因子</a-button>
        </div>
        <div v-if="selectedOomName" class="file-tip">当前文件：{{ selectedOomName }}</div>
      </a-card>

      <a-card title="UUC 计算" class="panel-card">
        <a-row :gutter="12">
          <a-col :span="8">
            <div class="field-label">简单用例个数</div>
            <a-input-number v-model:value="useCaseCounts.simple" :min="0" style="width: 100%" />
          </a-col>
          <a-col :span="8">
            <div class="field-label">普通用例个数</div>
            <a-input-number v-model:value="useCaseCounts.average" :min="0" style="width: 100%" />
          </a-col>
          <a-col :span="8">
            <div class="field-label">复杂用例个数</div>
            <a-input-number v-model:value="useCaseCounts.complex" :min="0" style="width: 100%" />
          </a-col>
        </a-row>
        <div class="result-line">UUC = {{ result.uuc }}</div>
      </a-card>

      <a-card title="UAW 计算" class="panel-card">
        <a-row :gutter="12">
          <a-col :span="8">
            <div class="field-label">简单角色个数</div>
            <a-input-number v-model:value="actorCounts.simple" :min="0" style="width: 100%" />
          </a-col>
          <a-col :span="8">
            <div class="field-label">普通角色个数</div>
            <a-input-number v-model:value="actorCounts.average" :min="0" style="width: 100%" />
          </a-col>
          <a-col :span="8">
            <div class="field-label">复杂角色个数</div>
            <a-input-number v-model:value="actorCounts.complex" :min="0" style="width: 100%" />
          </a-col>
        </a-row>
        <div class="result-line">UAW = {{ result.uaw }}</div>
      </a-card>

      <a-card title="TCF 计算" class="panel-card">
        <a-table :data-source="tcfFactors" :pagination="false" :columns="factorColumns" row-key="id" size="small">
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'level'">
              <a-input-number v-model:value="record.level" :min="0" :max="5" />
            </template>
          </template>
        </a-table>
        <div class="result-line">TCF = {{ result.tcf }}</div>
      </a-card>

      <a-card title="EF 计算" class="panel-card">
        <a-table :data-source="efFactors" :pagination="false" :columns="factorColumns" row-key="id" size="small">
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'level'">
              <a-input-number v-model:value="record.level" :min="0" :max="5" />
            </template>
          </template>
        </a-table>
        <div class="result-line">EF = {{ result.ef }}</div>
      </a-card>

      <a-card class="panel-card final-card">
        <a-space>
          <a-button type="primary" :loading="calcLoading" @click="calculate">计算 UCP</a-button>
          <a-button @click="exportResult">导出 CSV</a-button>
        </a-space>
        <div class="ucp">最终 UCP = {{ result.ucp }}</div>
      </a-card>
    </div>
  </AppLayout>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import AppLayout from '~/components/AppLayout.vue'
import api from '~/utils/api'

const selectedOom = ref(null)
const selectedOomName = ref('')
const parseLoading = ref(false)
const calcLoading = ref(false)

const useCaseCounts = reactive({ simple: 0, average: 0, complex: 0 })
const actorCounts = reactive({ simple: 0, average: 0, complex: 0 })
const tcfFactors = ref([])
const efFactors = ref([])

const result = reactive({ uuc: 0, uaw: 0, tcf: 0, ef: 0, ucp: 0 })

const factorColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '说明', dataIndex: 'name', key: 'name' },
  { title: '权重', dataIndex: 'weight', key: 'weight', width: 100 },
  { title: '等级', key: 'level', width: 120 },
]

const onOomSelected = (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  selectedOom.value = file
  selectedOomName.value = file.name
}

const loadSampleFactors = async () => {
  try {
    const { data } = await api.get('/api/metrics/usecase/default-factors')
    tcfFactors.value = data.data.tcf_factors
    efFactors.value = data.data.ef_factors
  } catch (err) {
    message.error(err?.response?.data?.message || '默认因子加载失败')
  }
}

const parseOom = async () => {
  if (!selectedOom.value) {
    message.warning('请先选择 .oom 文件')
    return
  }
  parseLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedOom.value)
    const { data } = await api.post('/api/metrics/usecase/parse-oom', formData)
    Object.assign(useCaseCounts, data.data.use_case_counts)
    Object.assign(actorCounts, data.data.actor_counts)
    message.success('解析成功，已回填 UUC/UAW 输入项')
  } catch (err) {
    message.error(err?.response?.data?.message || '解析失败')
  } finally {
    parseLoading.value = false
  }
}

const calculate = async () => {
  calcLoading.value = true
  try {
    const payload = {
      use_case_counts: { ...useCaseCounts },
      actor_counts: { ...actorCounts },
      tcf_factors: tcfFactors.value,
      ef_factors: efFactors.value,
    }
    const { data } = await api.post('/api/metrics/usecase/calculate', payload)
    Object.assign(result, {
      uuc: data.data.uuc,
      uaw: data.data.uaw,
      tcf: data.data.tcf,
      ef: data.data.ef,
      ucp: data.data.ucp,
    })
    message.success('UCP 计算完成')
  } catch (err) {
    message.error(err?.response?.data?.message || '计算失败')
  } finally {
    calcLoading.value = false
  }
}

const exportResult = async () => {
  try {
    const rows = [
      { metric: 'UUC', value: result.uuc },
      { metric: 'UAW', value: result.uaw },
      { metric: 'TCF', value: result.tcf },
      { metric: 'EF', value: result.ef },
      { metric: 'UCP', value: result.ucp },
    ]
    const res = await api.post('/api/export', { rows, filename: 'usecase-metric.csv' }, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = 'usecase-metric.csv'
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
  gap: 10px;
  flex-wrap: wrap;
}
.file-tip {
  margin-top: 10px;
  color: #3d4f68;
  font-size: 13px;
}
.field-label {
  margin-bottom: 7px;
  color: #4f5f75;
  font-size: 12px;
}
.result-line {
  margin-top: 12px;
  font-weight: 600;
  color: #1f3552;
}
.final-card {
  background: linear-gradient(180deg, #ffffff 0%, #f9fbff 100%);
}
.ucp {
  margin-top: 14px;
  font-size: 24px;
  font-weight: 700;
  color: #165dff;
}
</style>
