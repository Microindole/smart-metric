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

      <a-card v-if="selectedRow" :title="`${selectedRow.filename} 控制流图`">
        <div v-if="graphNodes.length" class="cfg-graph-canvas">
          <svg :viewBox="`0 0 700 ${graphHeight}`" role="img" :aria-label="`${selectedRow.filename} 控制流图`">
            <defs>
              <marker id="cfg-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
                <path d="M0,0 L0,6 L9,3 z" fill="#a94f34" />
              </marker>
            </defs>
            <path
              v-for="edge in graphEdges"
              :key="edge.key"
              class="cfg-edge"
              :d="edge.path"
              marker-end="url(#cfg-arrow)"
            />
            <text
              v-for="edge in graphEdges"
              :key="`${edge.key}-label`"
              class="cfg-edge-label"
              :x="edge.labelX"
              :y="edge.labelY"
            >
              {{ edge.label }}
            </text>
            <g v-for="node in graphNodes" :key="node.id" class="cfg-node">
              <rect
                v-if="node.type !== 'decision'"
                :x="node.x - node.width / 2"
                :y="node.y - 22"
                :width="node.width"
                height="44"
                rx="8"
                :class="`cfg-node-box ${node.type || 'normal'}`"
              />
              <polygon
                v-else
                :points="`${node.x},${node.y - 30} ${node.x + node.width / 2},${node.y} ${node.x},${node.y + 30} ${node.x - node.width / 2},${node.y}`"
                class="cfg-node-box decision"
              />
              <text class="cfg-node-label" :x="node.x" :y="node.y + 4">{{ node.label }}</text>
            </g>
          </svg>
        </div>
        <a-empty v-else description="暂无可绘制的控制流图节点" />
        <div class="mermaid-title">Mermaid 源码</div>
        <pre class="mermaid-box">{{ selectedRow.mermaid }}</pre>
      </a-card>
    </a-space>
  </AppLayout>
</template>

<script setup>
import { computed, h, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import AppLayout from '~/components/AppLayout.vue'
import api from '~/utils/api'
import { saveMetricSnapshot } from '~/utils/reportDraft'

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
        '查看图形'
      ),
  },
]

const graphNodes = computed(() => {
  const sourceNodes = selectedRow.value?.nodes || []
  const sourceEdges = selectedRow.value?.edges || []
  const incomingLabels = new Map()
  const outgoingCount = new Map()
  sourceEdges.forEach((edge) => {
    const labels = incomingLabels.get(edge.to) || []
    labels.push(edge.label)
    incomingLabels.set(edge.to, labels)
    outgoingCount.set(edge.from, (outgoingCount.get(edge.from) || 0) + 1)
  })

  return sourceNodes.map((node, index) => {
    const type = node.type || (outgoingCount.get(node.id) > 1 ? 'decision' : 'normal')
    const label = node.label || node.id || `node_${index + 1}`
    const incoming = incomingLabels.get(node.id) || []
    const hasBranchIncoming =
      incoming.some((item) => ['true', 'break', 'continue'].includes(item)) ||
      (!node.type && incoming.length > 1)
    const lane = type !== 'decision' && hasBranchIncoming ? 1 : 0
    return {
      id: node.id,
      type,
      label,
      width: Math.max(104, Math.min(190, String(label).length * 10 + 36)),
      x: type === 'branch' || lane === 1 ? 470 : 250,
      y: 48 + index * 86,
    }
  })
})

const graphHeight = computed(() => Math.max(140, graphNodes.value.length * 86 + 40))

const graphEdges = computed(() => {
  const nodeMap = new Map(graphNodes.value.map((node, index) => [node.id, { ...node, index }]))
  return (selectedRow.value?.edges || [])
    .map((edge, index) => {
      const from = nodeMap.get(edge.from)
      const to = nodeMap.get(edge.to)
      if (!from || !to) return null

      const label = edge.label || ''
      const sameOrBack = to.index <= from.index
      const path = sameOrBack
        ? `M ${from.x + from.width / 2} ${from.y} C 650 ${from.y}, 650 ${to.y}, ${to.x + to.width / 2} ${to.y}`
        : `M ${from.x} ${from.y + 24} C ${from.x} ${from.y + 54}, ${to.x} ${to.y - 54}, ${to.x} ${to.y - 24}`

      return {
        key: `${edge.from}-${edge.to}-${index}`,
        label,
        path,
        labelX: sameOrBack ? 612 : (from.x + to.x) / 2 + 14,
        labelY: sameOrBack ? (from.y + to.y) / 2 - 8 : (from.y + to.y) / 2 - 10,
      }
    })
    .filter(Boolean)
})

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
    saveMetricSnapshot('cfg', {
      description: '基于源码生成控制流图并计算圈复杂度。',
      summary: {
        文件数: data.data.summary.file_count,
        最大圈复杂度: data.data.summary.max_complexity,
        平均圈复杂度: data.data.summary.average_complexity,
        判定点总数: data.data.summary.total_decision_points,
      },
      rows: (data.data.files || []).map((item) => ({
        文件名: item.filename,
        语言: item.language,
        圈复杂度: item.cyclomatic_complexity,
      })),
    })
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
    saveMetricSnapshot('cfg', {
      description: '基于导入的控制流图文件计算圈复杂度。',
      summary: {
        文件数: 1,
        格式: item.format,
        节点数: item.node_count,
        边数: item.edge_count,
        圈复杂度: item.cyclomatic_complexity,
      },
      rows: [
        {
          文件名: item.filename,
          格式: item.format,
          节点数: item.node_count,
          边数: item.edge_count,
          圈复杂度: item.cyclomatic_complexity,
        },
      ],
    })
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
.cfg-graph-canvas {
  width: 100%;
  overflow-x: auto;
  margin-bottom: 14px;
  padding: 14px;
  border: 1px solid #eadfd4;
  border-radius: 8px;
  background: #fffaf4;
}

.cfg-graph-canvas svg {
  min-width: 680px;
  width: 100%;
}

.cfg-edge {
  fill: none;
  stroke: #a94f34;
  stroke-width: 1.8;
}

.cfg-edge-label {
  fill: #766b60;
  font-size: 12px;
  font-weight: 700;
}

.cfg-node-box {
  fill: #fffcf7;
  stroke: #d9c8ba;
  stroke-width: 1.4;
}

.cfg-node-box.start,
.cfg-node-box.end {
  fill: #f2e2d6;
  stroke: #c65f3d;
}

.cfg-node-box.decision {
  fill: #fff6ec;
  stroke: #c65f3d;
}

.cfg-node-box.branch {
  fill: #f7f1e9;
}

.cfg-node-label {
  fill: #191714;
  font-size: 13px;
  font-weight: 760;
  text-anchor: middle;
}

.mermaid-title {
  margin: 8px 0;
  color: #766b60;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

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
