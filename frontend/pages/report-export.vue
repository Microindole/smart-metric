<template>
  <AppLayout activeKey="report">
    <a-space direction="vertical" style="width: 100%" :size="14">
      <a-card title="报告基本信息">
        <a-row :gutter="12">
          <a-col :span="8">
            <div class="field-label">标题</div>
            <a-input v-model:value="form.title" placeholder="输入报告标题" />
          </a-col>
          <a-col :span="8">
            <div class="field-label">副标题</div>
            <a-input v-model:value="form.subtitle" placeholder="输入报告副标题" />
          </a-col>
          <a-col :span="8">
            <div class="field-label">导出格式</div>
            <a-select v-model:value="format" style="width: 100%">
              <a-select-option value="markdown">Markdown</a-select-option>
              <a-select-option value="html">HTML</a-select-option>
              <a-select-option value="pdf">PDF</a-select-option>
            </a-select>
          </a-col>
        </a-row>
      </a-card>

      <a-card title="Summary（JSON 对象）">
        <a-space direction="vertical" style="width: 100%">
          <a-textarea v-model:value="summaryText" :rows="8" />
          <div class="hint">示例：{"模块":"控制流图度量","文件数":1,"最大圈复杂度":2}</div>
        </a-space>
      </a-card>

      <a-card title="Sections（JSON 数组）">
        <a-space direction="vertical" style="width: 100%">
          <a-textarea v-model:value="sectionsText" :rows="16" />
          <div class="hint">每个 section 支持：heading、text、rows</div>
        </a-space>
      </a-card>

      <a-card title="操作">
        <a-space direction="vertical" style="width: 100%">
          <div class="field-label">参与自动汇总的模块</div>
          <a-checkbox-group v-model:value="selectedModules" :options="moduleOptions" />
        </a-space>
        <a-space wrap>
          <a-button type="primary" ghost @click="loadAggregated">自动汇总已保存结果</a-button>
          <a-button @click="loadSample">加载示例</a-button>
          <a-button danger ghost @click="clearSaved">清空本地结果缓存</a-button>
          <a-button @click="resetForm">清空</a-button>
          <a-button type="primary" :loading="loading" @click="exportReport">导出报告</a-button>
        </a-space>
        <div v-if="snapshotInfo.length" class="hint" style="margin-top: 10px">
          已检测到 {{ snapshotInfo.length }} 个模块结果：{{ snapshotInfo.map((item) => item.key).join('、') }}
        </div>
        <div v-else class="hint" style="margin-top: 10px">
          当前还没有可自动汇总的模块结果。请先在各度量页面完成计算。
        </div>
      </a-card>

      <a-card title="预览">
        <a-space direction="vertical" style="width: 100%">
          <div class="preview-title">{{ form.title || '未命名报告' }}</div>
          <div class="preview-subtitle">{{ form.subtitle || '无副标题' }}</div>
          <pre class="preview-box">{{ previewText }}</pre>
        </a-space>
      </a-card>
    </a-space>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import AppLayout from '~/components/AppLayout.vue'
import api from '~/utils/api'
import { buildReportPayloadFromSnapshots, clearMetricSnapshots, loadMetricSnapshots, moduleTitle } from '~/utils/reportDraft'

const SAMPLE = {
  title: 'SmartMetric 示例报告',
  subtitle: '用于验证 Markdown / HTML / PDF 导出',
  summary: {
    模块: '控制流图度量',
    文件数: 1,
    最大圈复杂度: 2,
  },
  sections: [
    {
      heading: '结果说明',
      text: '该报告演示如何从统一数据结构导出多种格式。',
    },
    {
      heading: '文件级结果',
      rows: [
        {
          filename: 'cfg_demo.oom',
          language: 'xml',
          cyclomatic_complexity: 2,
        },
      ],
    },
  ],
}

const loading = ref(false)
const format = ref('markdown')
const snapshotInfo = ref([])
const selectedModules = ref([])
const form = reactive({
  title: 'SmartMetric 示例报告',
  subtitle: '用于验证 Markdown / HTML / PDF 导出',
})
const summaryText = ref(JSON.stringify(SAMPLE.summary, null, 2))
const sectionsText = ref(JSON.stringify(SAMPLE.sections, null, 2))

const previewText = computed(() => {
  try {
    return JSON.stringify(buildPayload(), null, 2)
  } catch (err) {
    return `JSON 解析失败：${err?.message || '未知错误'}`
  }
})

const moduleOptions = computed(() =>
  snapshotInfo.value.map((item) => ({
    label: moduleTitle(item.key),
    value: item.key,
  }))
)

const refreshSnapshots = () => {
  const snapshots = loadMetricSnapshots()
  snapshotInfo.value = Object.entries(snapshots).map(([key, value]) => ({
    key,
    updatedAt: value.updatedAt || '',
  }))
  selectedModules.value = snapshotInfo.value.map((item) => item.key)
}

const loadSample = () => {
  form.title = SAMPLE.title
  form.subtitle = SAMPLE.subtitle
  summaryText.value = JSON.stringify(SAMPLE.summary, null, 2)
  sectionsText.value = JSON.stringify(SAMPLE.sections, null, 2)
  message.success('已加载示例报告')
}

const loadAggregated = () => {
  const aggregated = buildReportPayloadFromSnapshots(loadMetricSnapshots(), selectedModules.value)
  form.title = aggregated.title
  form.subtitle = aggregated.subtitle
  summaryText.value = JSON.stringify(aggregated.summary, null, 2)
  sectionsText.value = JSON.stringify(aggregated.sections, null, 2)
  refreshSnapshots()
  message.success('已从各模块结果自动汇总报告')
}

const clearSaved = () => {
  clearMetricSnapshots()
  snapshotInfo.value = []
  selectedModules.value = []
  message.success('已清空前端本地保存的度量结果')
}

const resetForm = () => {
  form.title = ''
  form.subtitle = ''
  summaryText.value = '{}'
  sectionsText.value = '[]'
}

const buildPayload = () => {
  const summary = JSON.parse(summaryText.value || '{}')
  const sections = JSON.parse(sectionsText.value || '[]')
  return {
    title: form.title || 'SmartMetric 报告',
    subtitle: form.subtitle || '',
    summary,
    sections,
  }
}

const exportReport = async () => {
  loading.value = true
  try {
    const report = buildPayload()
    const filename = `${sanitizeFileName(report.title || 'smartmetric-report')}.${extension(format.value)}`
    const res = await api.post(
      '/api/export/report',
      {
        format: format.value,
        filename,
        report,
      },
      { responseType: 'blob' }
    )
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    window.URL.revokeObjectURL(url)
    message.success('报告导出完成')
  } catch (err) {
    message.error(err?.response?.data?.message || '报告导出失败，请检查 JSON 格式')
  } finally {
    loading.value = false
  }
}

const sanitizeFileName = (value) => value.replace(/[\\/:*?"<>|]+/g, '-').trim() || 'smartmetric-report'

const extension = (value) => {
  if (value === 'markdown') return 'md'
  return value
}

onMounted(() => {
  refreshSnapshots()
  if (snapshotInfo.value.length) {
    loadAggregated()
  }
})
</script>

<style scoped>
.field-label {
  margin-bottom: 6px;
  color: #516070;
  font-size: 12px;
}

.hint {
  color: #6b7280;
  font-size: 12px;
}

.preview-title {
  font-size: 24px;
  font-weight: 700;
  color: #102a43;
}

.preview-subtitle {
  color: #52667a;
}

.preview-box {
  white-space: pre-wrap;
  background: #111827;
  color: #d1fae5;
  padding: 12px;
  border-radius: 6px;
  min-height: 200px;
}
</style>
