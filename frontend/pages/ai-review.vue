<template>
  <AppLayout activeKey="ai-review">
    <div class="page-wrap">
      <a-card title="AI 审查配置" class="panel-card">
        <a-row :gutter="12">
          <a-col :span="12">
            <div class="field-label">项目目录</div>
            <a-space-compact style="width: 100%">
              <a-input v-model:value="state.projectPath" placeholder="选择或输入项目根目录，例如 D:\\works\\smart-metric" />
              <a-button :loading="state.pickingDirectory" @click="pickProjectDirectory">选择目录</a-button>
            </a-space-compact>
          </a-col>
          <a-col :span="12">
            <div class="field-label">模型名</div>
            <a-input v-model:value="state.model" placeholder="例如 gpt-4.1-mini" />
          </a-col>
        </a-row>

        <a-row :gutter="12" style="margin-top: 12px">
          <a-col :span="12">
            <div class="field-label">输出格式</div>
            <a-select v-model:value="state.exportFormat" style="width: 100%">
              <a-select-option value="json">JSON</a-select-option>
              <a-select-option value="markdown">Markdown</a-select-option>
              <a-select-option value="html">HTML</a-select-option>
              <a-select-option value="pdf">PDF</a-select-option>
            </a-select>
          </a-col>
        </a-row>

        <a-row :gutter="12" style="margin-top: 12px">
          <a-col :span="8"><a-checkbox v-model:checked="state.useDefaultIgnores">使用默认忽略目录</a-checkbox></a-col>
          <a-col :span="8"><a-checkbox v-model:checked="state.useIgnoreFile">读取 .smartmetricignore</a-checkbox></a-col>
          <a-col :span="8">
            <div class="field-label">忽略文件名</div>
            <a-input v-model:value="state.ignoreFileName" placeholder=".smartmetricignore" />
          </a-col>
        </a-row>

        <a-row :gutter="12" style="margin-top: 12px">
          <a-col :span="12">
            <div class="field-label">第一轮 fixture（可选）</div>
            <a-space-compact style="width: 100%">
              <a-input v-model:value="state.phase1File" placeholder="例如 D:\\works\\smart-metric\\samples\\ai_review_phase1.json" />
              <a-button @click="pickJsonFile('phase1')">选择文件</a-button>
            </a-space-compact>
          </a-col>
          <a-col :span="12">
            <div class="field-label">第二轮 fixture（可选）</div>
            <a-space-compact style="width: 100%">
              <a-input v-model:value="state.phase2File" placeholder="例如 D:\\works\\smart-metric\\samples\\ai_review_phase2.json" />
              <a-button @click="pickJsonFile('phase2')">选择文件</a-button>
            </a-space-compact>
          </a-col>
        </a-row>

        <a-row :gutter="12" style="margin-top: 12px">
          <a-col :span="12">
            <div class="field-label">功能点 JSON（可选）</div>
            <a-space-compact style="width: 100%">
              <a-input v-model:value="state.fpFile" placeholder="例如 D:\\works\\smart-metric\\samples\\fp.json" />
              <a-button @click="pickJsonFile('fp')">选择文件</a-button>
            </a-space-compact>
          </a-col>
          <a-col :span="12">
            <div class="field-label">估算 JSON（可选）</div>
            <a-space-compact style="width: 100%">
              <a-input v-model:value="state.estimateFile" placeholder="例如 D:\\works\\smart-metric\\samples\\estimate.json" />
              <a-button @click="pickJsonFile('estimate')">选择文件</a-button>
            </a-space-compact>
          </a-col>
        </a-row>

        <div class="actions">
          <a-button type="primary" :loading="state.loading" @click="runReview">运行 AI 审查</a-button>
          <a-button danger :disabled="!state.loading" @click="cancelReview">中断审查</a-button>
          <a-button @click="useCurrentWorkspace">填入当前仓库路径</a-button>
          <a-button @click="loadFixtureExample">填入离线示例</a-button>
          <a-button @click="loadConfig">刷新配置状态</a-button>
          <a-button :disabled="!state.reportPayload" @click="exportReport">导出审查报告</a-button>
        </div>
        <div class="hint">
          真实 AI 审查是两阶段调用，通常会比普通度量慢。切页不会自动中断，请求会继续执行；回到页面后会保持当前状态。
        </div>
      </a-card>

      <a-card title="配置状态" class="panel-card">
        <div class="effective-line">本地配置文件：{{ state.configSummary.local_config_exists ? '已找到' : '未找到' }}</div>
        <div class="effective-line">配置路径：{{ state.configSummary.local_config_path || '无' }}</div>
        <div class="effective-line">模板路径：{{ state.configSummary.example_config_path || '无' }}</div>
        <div class="effective-line">Provider：{{ state.configSummary.provider || 'openai_compat' }}</div>
        <div class="effective-line">模型：{{ state.configSummary.model || 'gpt-4.1-mini' }}</div>
        <div class="effective-line">API Base：{{ state.configSummary.api_base || '默认' }}</div>
        <div class="effective-line">API Key：{{ state.configSummary.api_key_configured ? '已配置' : '未配置' }}</div>
      </a-card>

      <ReviewSummaryCards
        :risk-level="reviewSummary.riskLevel"
        :focus-count="focusFiles.length"
        :finding-count="findings.length"
        :recommendation-count="recommendations.length"
      />

      <ReviewOverviewPanel
        :has-result="hasResult"
        :phase1-summary="phase1Summary"
        :phase2-summary="phase2Summary"
        :focus-files="focusFiles"
      />

      <ReviewChartsGrid
        :has-result="hasResult"
        :findings="findings"
        :recommendations="recommendations"
        :focus-files="focusFiles"
      />

      <ReviewTablesPanel
        :focus-files="focusFiles"
        :findings="findings"
        :recommendations="recommendations"
      />

      <ReviewRecommendationCards :recommendations="recommendations" />

      <ReviewJsonPreview :preview-text="previewText" />
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import AppLayout from '~/components/AppLayout.vue'
import ReviewChartsGrid from '~/components/ai-review/ReviewChartsGrid.vue'
import ReviewJsonPreview from '~/components/ai-review/ReviewJsonPreview.vue'
import ReviewOverviewPanel from '~/components/ai-review/ReviewOverviewPanel.vue'
import ReviewRecommendationCards from '~/components/ai-review/ReviewRecommendationCards.vue'
import ReviewSummaryCards from '~/components/ai-review/ReviewSummaryCards.vue'
import ReviewTablesPanel from '~/components/ai-review/ReviewTablesPanel.vue'
import { useAiReviewState } from '~/composables/useAiReviewState'
import api from '~/utils/api'

const { state, getActiveReviewController, setActiveReviewController } = useAiReviewState()

const focusFiles = computed(() => state.reviewResult?.review?.focus_files || [])
const findings = computed(() => state.reviewResult?.review?.phase1?.findings || [])
const recommendations = computed(() => state.reviewResult?.review?.phase2?.recommendations || [])
const hasResult = computed(() => Boolean(state.reviewResult?.review))
const phase1Summary = computed(() => state.reviewResult?.review?.phase1?.summary || {})
const phase2Summary = computed(() => state.reviewResult?.review?.phase2?.summary || {})
const reviewSummary = computed(() => ({
  riskLevel: state.reviewResult?.review?.phase1?.summary?.risk_level || 'unknown',
}))
const previewText = computed(() =>
  JSON.stringify(
    {
      review: state.reviewResult?.review || null,
      report: state.reportPayload || null,
    },
    null,
    2
  )
)

const loadConfig = async () => {
  try {
    const { data } = await api.get('/api/metrics/ai-review/config')
    Object.assign(state.configSummary, data.data)
    if (!state.projectPath && data.data.local_config_exists) {
      state.model = data.data.model || 'gpt-4.1-mini'
    }
  } catch (err) {
    message.error(err?.response?.data?.message || '读取 AI 配置失败')
  }
}

const loadFixtureExample = () => {
  state.projectPath = 'D:\\works\\smart-metric'
  state.phase1File = 'D:\\works\\smart-metric\\samples\\ai_review_phase1.json'
  state.phase2File = 'D:\\works\\smart-metric\\samples\\ai_review_phase2.json'
  state.fpFile = 'D:\\works\\smart-metric\\samples\\fp.json'
  state.estimateFile = 'D:\\works\\smart-metric\\samples\\estimate.json'
  state.phase1Payload = null
  state.phase2Payload = null
  state.fpPayload = null
  state.estimatePayload = null
  state.model = state.configSummary.model || 'gpt-4.1-mini'
  message.success('已填入离线示例')
}

const useCurrentWorkspace = () => {
  state.projectPath = 'D:\\works\\smart-metric'
  message.success('已填入当前仓库路径')
}

const pickProjectDirectory = async () => {
  state.pickingDirectory = true
  try {
    const { data } = await api.post('/api/system/pick-directory', {
      initial_directory: (state.projectPath || '').trim() || 'D:\\works\\smart-metric',
      title: '选择 AI 审查项目目录',
    })
    state.projectPath = data.data.path
    message.success('已选择项目目录')
  } catch (err) {
    const status = err?.response?.status
    if (status === 409) {
      message.info('已取消目录选择')
    } else {
      message.error(err?.response?.data?.message || '选择项目目录失败')
    }
  } finally {
    state.pickingDirectory = false
  }
}

const runReview = async () => {
  if (!(state.projectPath || '').trim()) {
    message.warning('请先输入项目目录路径')
    return
  }
  const currentController = getActiveReviewController()
  if (currentController) {
    currentController.abort()
  }
  const controller = new AbortController()
  setActiveReviewController(controller)
  state.loading = true
  try {
    const payload = {
      path: state.projectPath.trim(),
      modules: ['inventory', 'loc', 'dependency', 'oo', 'design'],
      use_default_ignores: state.useDefaultIgnores,
      use_ignore_file: state.useIgnoreFile,
      ignore_file_name: state.ignoreFileName.trim() || '.smartmetricignore',
      model: state.model.trim() || 'gpt-4.1-mini',
      fp_file: state.fpPayload ? undefined : (state.fpFile.trim() || undefined),
      estimate_file: state.estimatePayload ? undefined : (state.estimateFile.trim() || undefined),
      function_point_payload: state.fpPayload || undefined,
      estimate_payload: state.estimatePayload || undefined,
      phase1_file: state.phase1File.trim() || undefined,
      phase2_file: state.phase2File.trim() || undefined,
      phase1_payload: state.phase1Payload || undefined,
      phase2_payload: state.phase2Payload || undefined,
    }
    const { data } = await api.post('/api/metrics/ai-review/run', payload, {
      timeout: 300000,
      signal: controller.signal,
    })
    state.reviewResult = data.data
    state.reportPayload = data.data.report
    message.success('AI 审查完成')
  } catch (err) {
    const timeout = err?.code === 'ECONNABORTED'
    const canceled = err?.code === 'ERR_CANCELED' || err?.name === 'CanceledError'
    if (canceled) {
      message.info('AI 审查已取消')
      return
    }
    message.error(
      timeout
        ? 'AI 审查超时，请稍后重试，或先使用离线 fixture 验证页面链路'
        : (err?.response?.data?.message || 'AI 审查失败')
    )
  } finally {
    if (getActiveReviewController() === controller) {
      setActiveReviewController(null)
    }
    state.loading = false
  }
}

const cancelReview = () => {
  const controller = getActiveReviewController()
  if (!controller) return
  controller.abort()
}

const exportReport = async () => {
  if (!state.reportPayload) {
    message.warning('请先运行 AI 审查')
    return
  }
  try {
    const filename = `ai-review.${state.exportFormat === 'markdown' ? 'md' : state.exportFormat}`
    const res = await api.post(
      '/api/export/report',
      {
        format: state.exportFormat,
        filename,
        report: state.reportPayload,
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
        state.phase1Payload = parsed
        state.phase1File = file.name
      } else if (kind === 'phase2') {
        state.phase2Payload = parsed
        state.phase2File = file.name
      } else if (kind === 'fp') {
        state.fpPayload = parsed
        state.fpFile = file.name
      } else if (kind === 'estimate') {
        state.estimatePayload = parsed
        state.estimateFile = file.name
      }
      message.success('JSON 文件已读取')
    } catch {
      message.error('JSON 文件解析失败')
    }
  }
  input.click()
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
.hint {
  margin-top: 10px;
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
</style>
