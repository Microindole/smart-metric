<template>
  <AppLayout activeKey="project">
    <div class="page-wrap">
      <a-card title="项目目录扫描" class="panel-card">
        <div class="form-grid">
          <a-space-compact style="width: 100%">
            <a-input v-model:value="projectPath" placeholder="选择或输入项目根目录，例如 D:\\works\\smart-metric" />
            <a-button :loading="pickingDirectory" @click="pickProjectDirectory">选择目录</a-button>
          </a-space-compact>
          <a-checkbox v-model:checked="useDefaultIgnores">使用默认忽略目录</a-checkbox>
          <a-checkbox v-model:checked="useIgnoreFile">读取 .smartmetricignore</a-checkbox>
          <a-input v-model:value="ignoreFileName" placeholder="忽略文件名，默认 .smartmetricignore" />
          <a-checkbox-group v-model:value="modules" :options="moduleOptions" />
          <a-textarea
            v-model:value="ignoreDirsText"
            :rows="3"
            placeholder="每行一个目录名，例如 node_modules&#10;dist&#10;coverage"
          />
          <a-textarea
            v-model:value="ignoreGlobsText"
            :rows="3"
            placeholder="每行一个通配规则，例如 *.min.js&#10;coverage/*&#10;**/*.generated.py"
          />
        </div>
        <div class="actions">
          <a-button type="primary" :loading="loading" @click="scanProject">开始扫描</a-button>
          <a-button @click="fillRecommendedIgnores">填入推荐忽略</a-button>
          <a-button @click="clearIgnoreInputs">清空自定义忽略</a-button>
        </div>
      </a-card>

      <ProjectSummaryPanel
        :has-result="hasResult"
        :root-path="rootPath"
        :modules="modules"
        :summary="summary"
      />

      <ProjectChartsPanel
        :has-result="hasResult"
        :language-rows="languageRows"
        :god-file-rows="godFileRows"
        :summary="summary"
      />

      <a-card title="忽略配置" class="panel-card">
        <div class="effective-line">默认忽略：{{ scanOptions.use_default_ignores ? '开启' : '关闭' }}</div>
        <div class="effective-line">忽略文件：{{ scanOptions.use_ignore_file ? '开启' : '关闭' }}</div>
        <div class="effective-line">忽略文件路径：{{ scanOptions.ignore_file_found ? scanOptions.ignore_file_path : '未找到' }}</div>
        <div class="effective-line">反向包含规则：{{ scanOptions.ignore_file_has_negation ? '有' : '无' }}</div>
        <div class="effective-line">忽略文件目录规则：{{ formatList(scanOptions.ignore_file_dirs) }}</div>
        <div class="effective-line">忽略文件通配规则：{{ formatList(scanOptions.ignore_file_globs) }}</div>
        <div class="effective-line">生效目录：{{ formatList(scanOptions.effective_ignore_dirs) }}</div>
        <div class="effective-line">生效通配：{{ formatList(scanOptions.effective_ignore_globs) }}</div>
      </a-card>

      <a-card title="语言分布" class="panel-card">
        <a-table :data-source="languageRows" :columns="languageColumns" row-key="language" :pagination="false" />
      </a-card>

      <a-card title="上帝文件排查" class="panel-card">
        <a-table :data-source="godFileRows" :columns="godFileColumns" row-key="filename" :pagination="{ pageSize: 6 }" />
      </a-card>

      <a-card title="上帝类排查" class="panel-card">
        <a-table :data-source="godClassRows" :columns="godClassColumns" row-key="rowKey" :pagination="{ pageSize: 6 }" />
      </a-card>

      <a-card title="文件级 LoC" class="panel-card">
        <a-table :data-source="locRows" :columns="locColumns" row-key="filename" :pagination="{ pageSize: 8 }" />
      </a-card>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed } from 'vue'
import { message } from 'ant-design-vue'
import AppLayout from '~/components/AppLayout.vue'
import ProjectChartsPanel from '~/components/project-metric/ProjectChartsPanel.vue'
import ProjectSummaryPanel from '~/components/project-metric/ProjectSummaryPanel.vue'
import { useProjectMetricState } from '~/composables/useProjectMetricState'
import api from '~/utils/api'
import { saveMetricSnapshot } from '~/utils/reportDraft'

const { state } = useProjectMetricState()
const loading = computed(() => state.loading)
const pickingDirectory = computed(() => state.pickingDirectory)
const projectPath = computed({
  get: () => state.projectPath,
  set: (value) => { state.projectPath = value },
})
const useDefaultIgnores = computed({
  get: () => state.useDefaultIgnores,
  set: (value) => { state.useDefaultIgnores = value },
})
const useIgnoreFile = computed({
  get: () => state.useIgnoreFile,
  set: (value) => { state.useIgnoreFile = value },
})
const ignoreFileName = computed({
  get: () => state.ignoreFileName,
  set: (value) => { state.ignoreFileName = value },
})
const modules = computed({
  get: () => state.modules,
  set: (value) => { state.modules = value },
})
const ignoreDirsText = computed({
  get: () => state.ignoreDirsText,
  set: (value) => { state.ignoreDirsText = value },
})
const ignoreGlobsText = computed({
  get: () => state.ignoreGlobsText,
  set: (value) => { state.ignoreGlobsText = value },
})
const result = computed(() => state.result)
const summary = computed(() => state.summary)
const scanOptions = computed(() => state.scanOptions)
const hasResult = computed(() => Boolean(state.result))
const rootPath = computed(() => state.result?.root || state.projectPath)

const moduleOptions = [
  { label: '资产清点', value: 'inventory' },
  { label: '代码行统计', value: 'loc' },
  { label: '依赖分析', value: 'dependency' },
  { label: '面向对象分析', value: 'oo' },
  { label: '设计图分析', value: 'design' },
]

const locColumns = [
  { title: '文件名', dataIndex: 'filename', key: 'filename' },
  { title: '语言', dataIndex: 'language', key: 'language', width: 110 },
  { title: '总行数', dataIndex: 'total_lines', key: 'total_lines', width: 100 },
  { title: '代码行', dataIndex: 'code_lines', key: 'code_lines', width: 100 },
  { title: '注释行', dataIndex: 'comment_lines', key: 'comment_lines', width: 100 },
  { title: '类数', dataIndex: 'class_count', key: 'class_count', width: 90 },
  { title: '方法数', dataIndex: 'method_count', key: 'method_count', width: 90 },
]

const godFileColumns = [
  { title: '文件名', dataIndex: 'filename', key: 'filename' },
  { title: '代码行', dataIndex: 'code_lines', key: 'code_lines', width: 100 },
  {
    title: '原因',
    dataIndex: 'reasons',
    key: 'reasons',
    customRender: ({ text }) => Array.isArray(text) ? text.join('，') : '',
  },
]

const godClassColumns = [
  { title: '文件名', dataIndex: 'filename', key: 'filename' },
  { title: '类名', dataIndex: 'class_name', key: 'class_name', width: 120 },
  { title: '语言', dataIndex: 'language', key: 'language', width: 100 },
  { title: 'WMC', dataIndex: 'wmc', key: 'wmc', width: 80 },
  { title: 'CBO', dataIndex: 'cbo', key: 'cbo', width: 80 },
  { title: 'NOM', dataIndex: 'nom', key: 'nom', width: 80 },
  {
    title: '原因',
    dataIndex: 'reasons',
    key: 'reasons',
    customRender: ({ text }) => Array.isArray(text) ? text.join('，') : '',
  },
]

const languageColumns = [
  { title: '语言', dataIndex: 'language', key: 'language' },
  { title: '文件数', dataIndex: 'count', key: 'count', width: 120 },
]

const locRows = computed(() => state.result?.loc?.files || [])
const godFileRows = computed(() => state.result?.oo?.god_files || [])
const godClassRows = computed(() => (state.result?.oo?.god_classes || []).map((item, index) => ({ ...item, rowKey: `${item.filename}-${item.class_name}-${index}` })))
const languageRows = computed(() => {
  const breakdown = state.result?.summary?.language_breakdown || {}
  return Object.entries(breakdown).map(([language, count]) => ({ language, count }))
})

const parseLines = (text) => text.split(/\r?\n/).map((item) => item.trim()).filter(Boolean)

const scanProject = async () => {
  if (!projectPath.value.trim()) {
    message.warning('请先输入项目目录路径')
    return
  }

  state.loading = true
  try {
    const payload = {
      path: projectPath.value.trim(),
      modules: modules.value,
      use_default_ignores: useDefaultIgnores.value,
      use_ignore_file: useIgnoreFile.value,
      ignore_file_name: ignoreFileName.value.trim() || '.smartmetricignore',
      ignore_dirs: parseLines(ignoreDirsText.value),
      ignore_globs: parseLines(ignoreGlobsText.value),
    }

    const { data } = await api.post('/api/metrics/project/scan', payload, { timeout: 300000 })
    state.result = data.data
    Object.assign(state.summary, {
      total_files: data.data.summary.total_files || 0,
      code_file_count: data.data.summary.code_file_count || 0,
      design_file_count: data.data.summary.design_file_count || 0,
      code_lines: data.data.summary.code_lines || 0,
      dependency_edge_count: data.data.summary.dependency_edge_count || 0,
      class_count: data.data.summary.class_count || 0,
      god_files: data.data.summary.god_files || 0,
      god_classes: data.data.summary.god_classes || 0,
    })
    Object.assign(state.scanOptions, data.data.scan_options || {
      use_default_ignores: true,
      use_ignore_file: true,
      ignore_file_path: '',
      ignore_file_found: false,
      ignore_file_has_negation: false,
      ignore_file_dirs: [],
      ignore_file_globs: [],
      ignore_dirs: [],
      ignore_globs: [],
      effective_ignore_dirs: [],
      effective_ignore_globs: [],
    })
    saveMetricSnapshot('project', {
      description: '基于项目目录进行总代码量、依赖关系、设计图和上帝文件排查。',
      summary: {
        项目目录: data.data.root,
        代码文件数: data.data.summary.code_file_count,
        设计文件数: data.data.summary.design_file_count,
        代码行: data.data.summary.code_lines || 0,
        依赖边数: data.data.summary.dependency_edge_count || 0,
        上帝文件: data.data.summary.god_files || 0,
        上帝类: data.data.summary.god_classes || 0,
      },
      rows: (data.data.oo?.god_files || []).map((item) => ({
        文件名: item.filename,
        代码行: item.code_lines,
        原因: Array.isArray(item.reasons) ? item.reasons.join('，') : '',
      })),
    })
    message.success('项目扫描完成')
  } catch (err) {
    const timeout = err?.code === 'ECONNABORTED'
    message.error(
      timeout
        ? '项目扫描超时，请稍后重试。项目级扫描会比单文件度量慢很多。'
        : (err?.response?.data?.message || '项目扫描失败')
    )
  } finally {
    state.loading = false
  }
}

const fillRecommendedIgnores = () => {
  ignoreDirsText.value = ['coverage', 'tmp', 'temp'].join('\n')
  ignoreGlobsText.value = ['*.min.js', '*.map', '*.generated.*'].join('\n')
}

const clearIgnoreInputs = () => {
  ignoreDirsText.value = ''
  ignoreGlobsText.value = ''
}

const pickProjectDirectory = async () => {
  state.pickingDirectory = true
  try {
    const { data } = await api.post('/api/system/pick-directory', {
      initial_directory: projectPath.value.trim() || 'D:\\works\\smart-metric',
      title: '选择项目扫描目录',
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
    state.pickingDirectory = false
  }
}

const formatList = (items) => Array.isArray(items) && items.length ? items.join('，') : '无'
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
.form-grid {
  display: grid;
  gap: 12px;
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
