<template>
  <a-card title="项目扫描可视化" class="panel-card">
    <a-empty v-if="!hasResult" description="扫描完成后，这里会显示语言分布、上帝文件和结构风险图表。" />
    <div v-else class="chart-grid">
      <ClientOnly>
        <VChart class="chart-box" :option="languageChartOption" autoresize />
      </ClientOnly>
      <ClientOnly>
        <VChart class="chart-box" :option="riskChartOption" autoresize />
      </ClientOnly>
      <ClientOnly>
        <VChart class="chart-box wide-box" :option="godFileChartOption" autoresize />
      </ClientOnly>
    </div>
  </a-card>
</template>

<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent, TitleComponent } from 'echarts/components'

use([CanvasRenderer, PieChart, BarChart, GridComponent, LegendComponent, TooltipComponent, TitleComponent])

const props = defineProps({
  hasResult: { type: Boolean, default: false },
  languageRows: { type: Array, default: () => [] },
  godFileRows: { type: Array, default: () => [] },
  summary: { type: Object, default: () => ({}) },
})

const languageChartOption = computed(() => ({
  title: { text: '语言分布', left: 12, top: 10, textStyle: { fontSize: 14, fontWeight: 700, color: '#102a43' } },
  tooltip: { trigger: 'item' },
  legend: { bottom: 4, left: 'center' },
  series: [
    {
      type: 'pie',
      radius: ['44%', '70%'],
      center: ['50%', '48%'],
      label: { formatter: '{b}: {c}' },
      data: props.languageRows.map((item) => ({ name: item.language, value: item.count })),
    },
  ],
}))

const riskChartOption = computed(() => ({
  title: { text: '结构风险', left: 12, top: 10, textStyle: { fontSize: 14, fontWeight: 700, color: '#102a43' } },
  tooltip: { trigger: 'axis' },
  grid: { left: 48, right: 18, top: 52, bottom: 40 },
  xAxis: { type: 'category', data: ['上帝文件', '上帝类', '依赖边', '类总数'] },
  yAxis: { type: 'value', minInterval: 1 },
  series: [
    {
      type: 'bar',
      barMaxWidth: 42,
      data: [
        { value: props.summary.god_files || 0, itemStyle: { color: '#cf1322' } },
        { value: props.summary.god_classes || 0, itemStyle: { color: '#d48806' } },
        { value: props.summary.dependency_edge_count || 0, itemStyle: { color: '#1677ff' } },
        { value: props.summary.class_count || 0, itemStyle: { color: '#722ed1' } },
      ],
    },
  ],
}))

const godFileChartOption = computed(() => ({
  title: { text: '上帝文件代码量 Top', left: 12, top: 10, textStyle: { fontSize: 14, fontWeight: 700, color: '#102a43' } },
  tooltip: { trigger: 'axis' },
  grid: { left: 60, right: 18, top: 52, bottom: 70 },
  xAxis: {
    type: 'category',
    data: props.godFileRows.map((item) => item.filename),
    axisLabel: { interval: 0, rotate: props.godFileRows.length > 3 ? 18 : 0, overflow: 'truncate', width: 120 },
  },
  yAxis: { type: 'value', minInterval: 1 },
  series: [
    {
      type: 'bar',
      barMaxWidth: 42,
      data: props.godFileRows.map((item) => ({ value: item.code_lines || 0, itemStyle: { color: '#cf1322' } })),
    },
  ],
}))
</script>

<style scoped>
.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}
.chart-box {
  width: 100%;
  min-height: 320px;
  padding: 16px;
  border: 1px solid #e8edf5;
  border-radius: 8px;
  background: #f8fafc;
}
.wide-box {
  grid-column: 1 / -1;
}
@media (max-width: 960px) {
  .chart-grid {
    grid-template-columns: 1fr;
  }
  .wide-box {
    grid-column: auto;
  }
}
</style>
