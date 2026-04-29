<template>
  <a-card title="结果可视化" class="panel-card">
    <a-empty
      v-if="!hasResult"
      description="运行 AI 审查后，这里会显示评分、严重级别、优先级、改动范围、类别、重点文件、目标符号和收益图表。"
    />
    <div v-else class="chart-grid">
      <ClientOnly>
        <VChart class="chart-box compact-box" :option="overallGaugeOption" autoresize />
      </ClientOnly>
      <ClientOnly>
        <VChart class="chart-box compact-box" :option="qualityRadarOption" autoresize />
      </ClientOnly>
      <ClientOnly>
        <VChart class="chart-box" :option="severityChartOption" autoresize />
      </ClientOnly>
      <ClientOnly>
        <VChart class="chart-box" :option="priorityChartOption" autoresize />
      </ClientOnly>
      <ClientOnly>
        <VChart class="chart-box" :option="scopeChartOption" autoresize />
      </ClientOnly>
      <ClientOnly>
        <VChart class="chart-box" :option="categoryChartOption" autoresize />
      </ClientOnly>
      <ClientOnly>
        <VChart class="chart-box" :option="focusChartOption" autoresize />
      </ClientOnly>
      <ClientOnly>
        <VChart class="chart-box" :option="symbolChartOption" autoresize />
      </ClientOnly>
      <ClientOnly>
        <VChart class="chart-box wide-box" :option="benefitChartOption" autoresize />
      </ClientOnly>
    </div>
  </a-card>
</template>

<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, GaugeChart, RadarChart } from 'echarts/charts'
import { GridComponent, LegendComponent, PolarComponent, RadarComponent, TooltipComponent, TitleComponent } from 'echarts/components'
import {
  buildBarOption,
  buildBenefitRows,
  buildCategoryRows,
  buildDistribution,
  buildFileImpactRows,
  buildGaugeOption,
  buildPieOption,
  buildRadarOption,
  buildScoreSummary,
  buildSymbolHitRows,
} from '~/utils/aiReviewDashboard'

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  GaugeChart,
  RadarChart,
  GridComponent,
  LegendComponent,
  PolarComponent,
  RadarComponent,
  TooltipComponent,
  TitleComponent,
])

const props = defineProps({
  hasResult: { type: Boolean, default: false },
  findings: { type: Array, default: () => [] },
  recommendations: { type: Array, default: () => [] },
  focusFiles: { type: Array, default: () => [] },
})

const severityRows = computed(() => buildDistribution(props.findings, 'severity'))
const priorityRows = computed(() => buildDistribution(props.recommendations, 'priority'))
const scopeRows = computed(() => buildDistribution(props.recommendations, 'refactor_scope', ['small', 'medium', 'large', 'unknown']))
const categoryRows = computed(() => buildCategoryRows(props.findings))
const focusImpactRows = computed(() => buildFileImpactRows(props.findings, props.recommendations, props.focusFiles))
const symbolHitRows = computed(() => buildSymbolHitRows(props.recommendations))
const benefitRows = computed(() => buildBenefitRows(props.recommendations))
const scoreSummary = computed(() => buildScoreSummary(props.findings, props.recommendations))

const overallGaugeOption = computed(() => buildGaugeOption('AI 审查总分', scoreSummary.value.overall))
const qualityRadarOption = computed(() => buildRadarOption('质量维度雷达', scoreSummary.value))
const severityChartOption = computed(() => buildPieOption('发现严重级别', severityRows.value))
const scopeChartOption = computed(() => buildPieOption('改动范围分布', scopeRows.value))
const priorityChartOption = computed(() => buildBarOption('建议优先级', priorityRows.value))
const categoryChartOption = computed(() => buildBarOption('问题类别分布', categoryRows.value))
const focusChartOption = computed(() => buildBarOption('重点文件命中次数', focusImpactRows.value))
const symbolChartOption = computed(() => buildBarOption('目标符号命中次数', symbolHitRows.value))
const benefitChartOption = computed(() => buildBarOption('预期收益分布', benefitRows.value))
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
.compact-box {
  min-height: 280px;
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
