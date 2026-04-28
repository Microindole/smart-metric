<template>
  <AppLayout activeKey="ai-review">
    <div class="page-wrap">
      <a-card title="AI 审查配置" class="panel-card">
        <a-row :gutter="12">
          <a-col :span="12">
            <div class="field-label">项目目录</div>
            <a-space-compact style="width: 100%">
              <a-input v-model:value="projectPath" placeholder="选择或输入项目根目录，例如 D:\\works\\smart-metric" />
              <a-button :loading="pickingDirectory" @click="pickProjectDirectory">选择目录</a-button>
            </a-space-compact>
          </a-col>
          <a-col :span="12">
            <div class="field-label">模型名</div>
            <a-input v-model:value="model" placeholder="例如 gpt-4.1-mini" />
          </a-col>
        </a-row>
        <a-row :gutter="12" style="margin-top: 12px">
          <a-col :span="12">
            <div class="field-label">输出格式</div>
            <a-select v-model:value="exportFormat" style="width: 100%">
              <a-select-option value="json">JSON</a-select-option>
              <a-select-option value="markdown">Markdown</a-select-option>
              <a-select-option value="html">HTML</a-select-option>
              <a-select-option value="pdf">PDF</a-select-option>
            </a-select>
          </a-col>
        </a-row>
        <a-row :gutter="12" style="margin-top: 12px">
          <a-col :span="8"><a-checkbox v-model:checked="useDefaultIgnores">使用默认忽略目录</a-checkbox></a-col>
          <a-col :span="8"><a-checkbox v-model:checked="useIgnoreFile">读取 .smartmetricignore</a-checkbox></a-col>
          <a-col :span="8">
            <div class="field-label">忽略文件名</div>
            <a-input v-model:value="ignoreFileName" placeholder=".smartmetricignore" />
          </a-col>
        </a-row>
        <a-row :gutter="12" style="margin-top: 12px">
          <a-col :span="12">
            <div class="field-label">第一轮 fixture（可选）</div>
            <a-space-compact style="width: 100%">
              <a-input v-model:value="phase1File" placeholder="例如 D:\\works\\smart-metric\\samples\\ai_review_phase1.json" />
              <a-button @click="pickJsonFile('phase1')">选择文件</a-button>
            </a-space-compact>
          </a-col>
          <a-col :span="12">
            <div class="field-label">第二轮 fixture（可选）</div>
            <a-space-compact style="width: 100%">
              <a-input v-model:value="phase2File" placeholder="例如 D:\\works\\smart-metric\\samples\\ai_review_phase2.json" />
              <a-button @click="pickJsonFile('phase2')">选择文件</a-button>
            </a-space-compact>
          </a-col>
        </a-row>
        <a-row :gutter="12" style="margin-top: 12px">
          <a-col :span="12">
            <div class="field-label">功能点 JSON（可选）</div>
            <a-space-compact style="width: 100%">
              <a-input v-model:value="fpFile" placeholder="例如 D:\\works\\smart-metric\\samples\\fp.json" />
              <a-button @click="pickJsonFile('fp')">选择文件</a-button>
            </a-space-compact>
          </a-col>
          <a-col :span="12">
            <div class="field-label">估算 JSON（可选）</div>
            <a-space-compact style="width: 100%">
              <a-input v-model:value="estimateFile" placeholder="例如 D:\\works\\smart-metric\\samples\\estimate.json" />
              <a-button @click="pickJsonFile('estimate')">选择文件</a-button>
            </a-space-compact>
          </a-col>
        </a-row>
        <div class="actions">
          <a-button type="primary" :loading="loading" @click="runReview">运行 AI 审查</a-button>
          <a-button @click="useCurrentWorkspace">填入当前仓库路径</a-button>
          <a-button @click="loadFixtureExample">填入离线示例</a-button>
          <a-button @click="loadConfig">刷新配置状态</a-button>
          <a-button :disabled="!reportPayload" @click="exportReport">导出审查报告</a-button>
        </div>
        <div class="hint">真实 AI 审查是两阶段调用，通常会比普通度量慢。Web 端已放宽超时，建议等待 1 到 3 分钟。</div>
      </a-card>

      <a-card title="配置状态" class="panel-card">
        <div class="effective-line">本地配置文件：{{ configSummary.local_config_exists ? '已找到' : '未找到' }}</div>
        <div class="effective-line">配置路径：{{ configSummary.local_config_path || '无' }}</div>
        <div class="effective-line">模板路径：{{ configSummary.example_config_path || '无' }}</div>
        <div class="effective-line">Provider：{{ configSummary.provider || 'openai_compat' }}</div>
        <div class="effective-line">模型：{{ configSummary.model || 'gpt-4.1-mini' }}</div>
        <div class="effective-line">API Base：{{ configSummary.api_base || '默认' }}</div>
        <div class="effective-line">API Key：{{ configSummary.api_key_configured ? '已配置' : '未配置' }}</div>
      </a-card>

      <a-card title="审查摘要" class="panel-card">
        <a-row :gutter="12">
          <a-col :span="6"><a-statistic title="AI 风险等级" :value="reviewSummary.riskLevel" /></a-col>
          <a-col :span="6"><a-statistic title="重点文件数" :value="focusFiles.length" /></a-col>
          <a-col :span="6"><a-statistic title="发现数" :value="findings.length" /></a-col>
          <a-col :span="6"><a-statistic title="建议数" :value="recommendations.length" /></a-col>
        </a-row>
      </a-card>

      <a-card title="审查结论" class="panel-card">
        <a-empty v-if="!hasResult" description="运行 AI 审查后，这里会显示项目概览、重构顺序和建议摘要。" />
        <div v-else class="overview-grid">
          <div class="overview-block">
            <div class="overview-title">项目概览</div>
            <div class="overview-text">{{ phase1Summary.project_overview || '无' }}</div>
          </div>
          <div class="overview-block">
            <div class="overview-title">总体优先级</div>
            <div class="overview-chip">{{ phase2Summary.overall_priority || 'unknown' }}</div>
          </div>
          <div class="overview-block">
            <div class="overview-title">建议重构顺序</div>
            <ol v-if="phase2Summary.refactor_order?.length" class="detail-list compact-list">
              <li v-for="(item, index) in phase2Summary.refactor_order" :key="`order-${index}`">{{ item }}</li>
            </ol>
            <div v-else class="overview-text">无</div>
          </div>
          <div class="overview-block">
            <div class="overview-title">重点文件</div>
            <ul v-if="focusFiles.length" class="detail-list compact-list">
              <li v-for="(file, index) in focusFiles" :key="`focus-${index}`">{{ file }}</li>
            </ul>
            <div v-else class="overview-text">无</div>
          </div>
        </div>
      </a-card>

      <a-card title="结果可视化" class="panel-card">
        <a-empty v-if="!hasResult" description="运行 AI 审查后，这里会显示严重级别和建议优先级图表。" />
        <div v-else class="chart-grid">
          <div class="chart-box">
            <div class="chart-title">发现严重级别</div>
            <div v-for="item in severityRows" :key="`severity-${item.label}`" class="bar-row">
              <span class="bar-label">{{ item.label }}</span>
              <span class="bar-track">
                <span class="bar-fill" :style="{ width: `${item.percent}%`, background: item.color }"></span>
              </span>
              <span class="bar-value">{{ item.count }}</span>
            </div>
          </div>
          <div class="chart-box">
            <div class="chart-title">建议优先级</div>
            <div v-for="item in priorityRows" :key="`priority-${item.label}`" class="bar-row">
              <span class="bar-label">{{ item.label }}</span>
              <span class="bar-track">
                <span class="bar-fill" :style="{ width: `${item.percent}%`, background: item.color }"></span>
              </span>
              <span class="bar-value">{{ item.count }}</span>
            </div>
          </div>
        </div>
      </a-card>

      <a-card title="重点文件" class="panel-card">
        <a-table :data-source="focusRows" :columns="focusColumns" row-key="filename" :pagination="false" />
      </a-card>

      <a-card title="AI 发现" class="panel-card">
        <a-table :data-source="findingRows" :columns="findingColumns" row-key="id" :pagination="{ pageSize: 6 }" />
      </a-card>

      <a-card title="改进建议" class="panel-card">
        <a-table :data-source="recommendationRows" :columns="recommendationColumns" row-key="rowKey" :pagination="{ pageSize: 6 }" />
      </a-card>

      <a-card title="建议详情" class="panel-card">
        <div v-if="!recommendationRows.length" class="hint">当前没有可展示的建议详情。</div>
        <div v-else class="recommendation-stack">
          <div v-for="item in recommendationRows" :key="item.rowKey" class="recommendation-card">
            <div class="recommendation-head">
              <div class="recommendation-title">{{ item.filename }}</div>
              <a-tag :color="priorityColor(item.priority)">{{ item.priority || 'unknown' }}</a-tag>
            </div>
            <div class="recommendation-line"><strong>问题：</strong>{{ item.problem }}</div>
            <div class="recommendation-line"><strong>建议：</strong>{{ item.suggestion }}</div>
            <div class="recommendation-line"><strong>预期收益：</strong>{{ item.expected_benefit }}</div>
            <div class="recommendation-line"><strong>改动范围：</strong>{{ item.refactor_scope }}</div>
            <div v-if="item.target_symbols?.length" class="recommendation-line">
              <strong>目标符号：</strong>{{ item.target_symbols.join('、') }}
            </div>
            <div v-if="item.evidence?.length" class="recommendation-line">
              <strong>证据：</strong>
              <ul class="detail-list">
                <li v-for="(evidence, index) in item.evidence" :key="`${item.rowKey}-e-${index}`">{{ evidence }}</li>
              </ul>
            </div>
            <div v-if="item.refactor_steps?.length" class="recommendation-line">
              <strong>建议步骤：</strong>
              <ol class="detail-list">
                <li v-for="(step, index) in item.refactor_steps" :key="`${item.rowKey}-s-${index}`">{{ step }}</li>
              </ol>
            </div>
          </div>
        </div>
      </a-card>

      <a-card title="JSON 预览" class="panel-card">
        <pre class="preview-box">{{ previewText }}</pre>
      </a-card>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import AppLayout from '~/components/AppLayout.vue'
import api from '~/utils/api'

const loading = ref(false)
const pickingDirectory = ref(false)
const projectPath = ref('')
const model = ref('gpt-4.1-mini')
const exportFormat = ref('pdf')
const fpFile = ref('')
const estimateFile = ref('')
const phase1File = ref('')
const phase2File = ref('')
const phase1Payload = ref(null)
const phase2Payload = ref(null)
const fpPayload = ref(null)
const estimatePayload = ref(null)
const useDefaultIgnores = ref(true)
const useIgnoreFile = ref(true)
const ignoreFileName = ref('.smartmetricignore')
const reviewResult = ref(null)
const reportPayload = ref(null)
const configSummary = reactive({
  local_config_path: '',
  example_config_path: '',
  local_config_exists: false,
  provider: 'openai_compat',
  model: 'gpt-4.1-mini',
  api_base: '',
  api_key_configured: false,
})

const focusColumns = [
  { title: '文件', dataIndex: 'filename', key: 'filename' },
]

const findingColumns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 90 },
  { title: '严重级别', dataIndex: 'severity', key: 'severity', width: 100 },
  { title: '类别', dataIndex: 'category', key: 'category', width: 120 },
  { title: '文件', dataIndex: 'filename', key: 'filename' },
  { title: '原因', dataIndex: 'reason', key: 'reason' },
]

const recommendationColumns = [
  { title: '优先级', dataIndex: 'priority', key: 'priority', width: 100 },
  { title: '文件', dataIndex: 'filename', key: 'filename' },
  { title: '问题', dataIndex: 'problem', key: 'problem' },
  { title: '建议', dataIndex: 'suggestion', key: 'suggestion' },
  { title: '收益', dataIndex: 'expected_benefit', key: 'expected_benefit' },
]

const focusFiles = computed(() => reviewResult.value?.review?.focus_files || [])
const findings = computed(() => reviewResult.value?.review?.phase1?.findings || [])
const recommendations = computed(() => reviewResult.value?.review?.phase2?.recommendations || [])
const hasResult = computed(() => Boolean(reviewResult.value?.review))
const focusRows = computed(() => focusFiles.value.map((filename) => ({ filename })))
const findingRows = computed(() => findings.value)
const recommendationRows = computed(() =>
  recommendations.value.map((item, index) => ({ ...item, rowKey: `${item.filename}-${index}` }))
)
const phase1Summary = computed(() => reviewResult.value?.review?.phase1?.summary || {})
const phase2Summary = computed(() => reviewResult.value?.review?.phase2?.summary || {})
const reviewSummary = computed(() => ({
  riskLevel: reviewResult.value?.review?.phase1?.summary?.risk_level || 'unknown',
}))
const severityRows = computed(() => buildDistribution(findings.value, 'severity'))
const priorityRows = computed(() => buildDistribution(recommendations.value, 'priority'))
const previewText = computed(() =>
  JSON.stringify(
    {
      review: reviewResult.value?.review || null,
      report: reportPayload.value || null,
    },
    null,
    2
  )
)
const loadConfig = async () => {
  try {
    const { data } = await api.get('/api/metrics/ai-review/config')
    Object.assign(configSummary, data.data)
    if (!projectPath.value && data.data.local_config_exists) {
      model.value = data.data.model || 'gpt-4.1-mini'
    }
  } catch (err) {
    message.error(err?.response?.data?.message || '读取 AI 配置失败')
  }
}

const loadFixtureExample = () => {
  projectPath.value = 'D:\\works\\smart-metric'
  phase1File.value = 'D:\\works\\smart-metric\\samples\\ai_review_phase1.json'
  phase2File.value = 'D:\\works\\smart-metric\\samples\\ai_review_phase2.json'
  fpFile.value = 'D:\\works\\smart-metric\\samples\\fp.json'
  estimateFile.value = 'D:\\works\\smart-metric\\samples\\estimate.json'
  phase1Payload.value = null
  phase2Payload.value = null
  fpPayload.value = null
  estimatePayload.value = null
  model.value = configSummary.model || 'gpt-4.1-mini'
  message.success('已填入离线示例')
}

const useCurrentWorkspace = () => {
  projectPath.value = 'D:\\works\\smart-metric'
  message.success('已填入当前仓库路径')
}

const pickProjectDirectory = async () => {
  pickingDirectory.value = true
  try {
    const { data } = await api.post('/api/system/pick-directory', {
      initial_directory: projectPath.value.trim() || 'D:\\works\\smart-metric',
      title: '选择 AI 审查项目目录',
    })
    projectPath.value = data.data.path
    message.success('已选择项目目录')
  } catch (err) {
    const status = err?.response?.status
    if (status === 409) {
      message.info('已取消目录选择')
    } else {
      message.error(err?.response?.data?.message || '选择项目目录失败')
    }
  } finally {
    pickingDirectory.value = false
  }
}

const runReview = async () => {
  if (!projectPath.value.trim()) {
    message.warning('请先输入项目目录路径')
    return
  }
  loading.value = true
  try {
    const payload = {
      path: projectPath.value.trim(),
      modules: ['inventory', 'loc', 'dependency', 'oo', 'design'],
      use_default_ignores: useDefaultIgnores.value,
      use_ignore_file: useIgnoreFile.value,
      ignore_file_name: ignoreFileName.value.trim() || '.smartmetricignore',
      model: model.value.trim() || 'gpt-4.1-mini',
      fp_file: fpPayload.value ? undefined : (fpFile.value.trim() || undefined),
      estimate_file: estimatePayload.value ? undefined : (estimateFile.value.trim() || undefined),
      function_point_payload: fpPayload.value || undefined,
      estimate_payload: estimatePayload.value || undefined,
      phase1_file: phase1File.value.trim() || undefined,
      phase2_file: phase2File.value.trim() || undefined,
      phase1_payload: phase1Payload.value || undefined,
      phase2_payload: phase2Payload.value || undefined,
    }
    const { data } = await api.post('/api/metrics/ai-review/run', payload, { timeout: 300000 })
    reviewResult.value = data.data
    reportPayload.value = data.data.report
    message.success('AI 审查完成')
  } catch (err) {
    const timeout = err?.code === 'ECONNABORTED'
    message.error(
      timeout
        ? 'AI 审查超时，请稍后重试，或先使用离线 fixture 验证页面链路'
        : (err?.response?.data?.message || 'AI 审查失败')
    )
  } finally {
    loading.value = false
  }
}

const exportReport = async () => {
  if (!reportPayload.value) {
    message.warning('请先运行 AI 审查')
    return
  }
  try {
    const filename = `ai-review.${exportFormat.value === 'markdown' ? 'md' : exportFormat.value}`
    const res = await api.post(
      '/api/export/report',
      {
        format: exportFormat.value,
        filename,
        report: reportPayload.value,
      },
      { responseType: 'blob', timeout: 300000 }
    )
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    window.URL.revokeObjectURL(url)
    message.success('AI 审查报告导出完成')
  } catch (err) {
    message.error(err?.response?.data?.message || '导出 AI 审查报告失败')
  }
}

const pickJsonFile = async (kind) => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json,application/json'
  input.onchange = async () => {
    const file = input.files?.[0]
    if (!file) return
    try {
      const text = await file.text()
      const parsed = JSON.parse(text)
      if (kind === 'phase1') {
        phase1Payload.value = parsed
        phase1File.value = file.name
      } else if (kind === 'phase2') {
        phase2Payload.value = parsed
        phase2File.value = file.name
      } else if (kind === 'fp') {
        fpPayload.value = parsed
        fpFile.value = file.name
      } else if (kind === 'estimate') {
        estimatePayload.value = parsed
        estimateFile.value = file.name
      }
      message.success('JSON 文件已读取')
    } catch (err) {
      message.error('JSON 文件解析失败')
    }
  }
  input.click()
}

const priorityColor = (value) => {
  if (value === 'high') return 'red'
  if (value === 'medium') return 'orange'
  if (value === 'low') return 'blue'
  return 'default'
}

const buildDistribution = (items, field) => {
  const palette = {
    high: '#cf1322',
    medium: '#d48806',
    low: '#1677ff',
    unknown: '#8c8c8c',
  }
  const counts = items.reduce((acc, item) => {
    const key = item?.[field] || 'unknown'
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})
  const max = Math.max(...Object.values(counts), 1)
  return ['high', 'medium', 'low', 'unknown']
    .filter((key) => counts[key])
    .map((key) => ({
      label: key,
      count: counts[key],
      percent: Math.round((counts[key] / max) * 100),
      color: palette[key],
    }))
}

onMounted(() => {
  loadConfig()
})
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
.field-label {
  margin-bottom: 6px;
  color: #516070;
  font-size: 12px;
}
.actions {
  margin-top: 14px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.effective-line {
  line-height: 1.8;
  color: #2f4058;
}
.overview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
.overview-block {
  border: 1px solid #e8edf5;
  border-radius: 8px;
  padding: 12px;
  background: #f8fafc;
}
.overview-title {
  margin-bottom: 8px;
  color: #516070;
  font-size: 12px;
}
.overview-text {
  color: #102a43;
  line-height: 1.7;
}
.overview-chip {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: #e6f4ff;
  color: #0958d9;
  font-weight: 600;
}
.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}
.chart-box {
  width: 100%;
  min-height: 240px;
  display: grid;
  align-content: start;
  gap: 12px;
  padding: 16px;
  border: 1px solid #e8edf5;
  border-radius: 8px;
  background: #f8fafc;
}
.chart-title {
  color: #102a43;
  font-weight: 700;
}
.bar-row {
  display: grid;
  grid-template-columns: 76px minmax(0, 1fr) 32px;
  align-items: center;
  gap: 10px;
}
.bar-label {
  color: #516070;
  font-size: 12px;
  text-transform: uppercase;
}
.bar-track {
  height: 10px;
  overflow: hidden;
  border-radius: 999px;
  background: #e8edf5;
}
.bar-fill {
  display: block;
  height: 100%;
  min-width: 8px;
  border-radius: inherit;
}
.bar-value {
  color: #102a43;
  font-weight: 700;
  text-align: right;
}
.recommendation-stack {
  display: grid;
  gap: 12px;
}
.recommendation-card {
  border: 1px solid #e8edf5;
  border-radius: 8px;
  padding: 14px;
  background: #f8fafc;
}
.recommendation-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}
.recommendation-title {
  font-weight: 700;
  color: #102a43;
}
.recommendation-line {
  margin-bottom: 8px;
  color: #2f4058;
}
.detail-list {
  margin: 6px 0 0 18px;
}
.compact-list {
  margin-top: 0;
}
.preview-box {
  white-space: pre-wrap;
  background: #111827;
  color: #d1fae5;
  padding: 12px;
  border-radius: 6px;
  min-height: 220px;
}
@media (max-width: 960px) {
  .overview-grid,
  .chart-grid {
    grid-template-columns: 1fr;
  }
}
</style>
