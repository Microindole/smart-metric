export const distributionPalette = {
  high: '#cf1322',
  medium: '#d48806',
  low: '#1677ff',
  unknown: '#8c8c8c',
  small: '#52c41a',
  large: '#722ed1',
}

export function buildDistribution(items, field, order = ['high', 'medium', 'low', 'unknown']) {
  const counts = (items || []).reduce((acc, item) => {
    const key = item?.[field] || 'unknown'
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})
  const max = Math.max(...Object.values(counts), 1)
  return order
    .filter((key) => counts[key])
    .map((key) => ({
      label: key,
      count: counts[key],
      percent: Math.round((counts[key] / max) * 100),
      color: distributionPalette[key] || '#1677ff',
    }))
}

export function buildCategoryRows(findings) {
  return buildGroupedRows(findings, 'category', '#1677ff').slice(0, 8)
}

export function buildBenefitRows(recommendations) {
  return buildGroupedRows(
    (recommendations || []).map((item) => ({ expected_benefit: normalizeBenefit(item?.expected_benefit) })),
    'expected_benefit',
    '#13c2c2'
  ).slice(0, 8)
}

export function buildFileImpactRows(findings, recommendations, focusFiles) {
  const counts = {}
  for (const filename of focusFiles || []) {
    if (!filename) continue
    counts[filename] = counts[filename] || 0
  }
  for (const item of findings || []) {
    const filename = item?.filename
    if (!filename) continue
    counts[filename] = (counts[filename] || 0) + 1
  }
  for (const item of recommendations || []) {
    const filename = item?.filename
    if (!filename) continue
    counts[filename] = (counts[filename] || 0) + 1
  }
  return Object.entries(counts)
    .map(([label, count]) => ({ label, count, color: '#1677ff' }))
    .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label))
    .slice(0, 8)
}

export function buildSymbolHitRows(recommendations) {
  const counts = {}
  for (const item of recommendations || []) {
    for (const symbol of item?.target_symbols || []) {
      if (!symbol) continue
      counts[symbol] = (counts[symbol] || 0) + 1
    }
  }
  return Object.entries(counts)
    .map(([label, count]) => ({ label, count, color: '#722ed1' }))
    .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label))
    .slice(0, 10)
}

export function buildScoreSummary(findings, recommendations) {
  const severityCounts = countBy(findings, 'severity')
  const priorityCounts = countBy(recommendations, 'priority')
  const scopeCounts = countBy(recommendations, 'refactor_scope')
  const symbolCount = (recommendations || []).reduce((acc, item) => acc + (item?.target_symbols?.length || 0), 0)

  const riskPenalty =
    (severityCounts.high || 0) * 16 +
    (severityCounts.medium || 0) * 8 +
    (severityCounts.low || 0) * 4 +
    (priorityCounts.high || 0) * 14 +
    (priorityCounts.medium || 0) * 7 +
    (priorityCounts.low || 0) * 3

  const overall = clamp(100 - riskPenalty, 18, 96)
  const maintainability = clamp(100 - (severityCounts.high || 0) * 18 - (priorityCounts.high || 0) * 10, 16, 98)
  const complexity = clamp(100 - (severityCounts.high || 0) * 14 - (severityCounts.medium || 0) * 8, 20, 96)
  const testability = clamp(100 - (priorityCounts.high || 0) * 10 - (scopeCounts.large || 0) * 6, 24, 96)
  const actionability = clamp(40 + symbolCount * 5 + (recommendations?.length || 0) * 6, 30, 98)
  const scopePressure = clamp(100 - (scopeCounts.large || 0) * 14 - (scopeCounts.medium || 0) * 8, 18, 96)

  return {
    overall,
    maintainability,
    complexity,
    testability,
    actionability,
    scopePressure,
  }
}

export function buildGaugeOption(title, value) {
  return {
    backgroundColor: 'transparent',
    title: {
      text: title,
      left: 12,
      top: 10,
      textStyle: { fontSize: 14, fontWeight: 700, color: '#102a43' },
    },
    series: [
      {
        type: 'gauge',
        min: 0,
        max: 100,
        progress: { show: true, width: 12 },
        axisLine: { lineStyle: { width: 12 } },
        splitLine: { distance: -14, length: 10 },
        axisTick: { distance: -14, length: 4 },
        axisLabel: { distance: 18, color: '#516070' },
        detail: {
          valueAnimation: true,
          formatter: '{value}',
          color: '#102a43',
          fontSize: 24,
          offsetCenter: [0, '60%'],
        },
        data: [{ value }],
      },
    ],
  }
}

export function buildRadarOption(title, scores) {
  return {
    backgroundColor: 'transparent',
    title: {
      text: title,
      left: 12,
      top: 10,
      textStyle: { fontSize: 14, fontWeight: 700, color: '#102a43' },
    },
    tooltip: {},
    radar: {
      radius: '62%',
      indicator: [
        { name: '可维护性', max: 100 },
        { name: '复杂度', max: 100 },
        { name: '可测试性', max: 100 },
        { name: '建议可执行性', max: 100 },
        { name: '改动压力', max: 100 },
      ],
      splitArea: { areaStyle: { color: ['#f8fafc', '#f3f6fb'] } },
      axisName: { color: '#516070' },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: [
              scores.maintainability,
              scores.complexity,
              scores.testability,
              scores.actionability,
              scores.scopePressure,
            ],
            areaStyle: { color: 'rgba(22, 119, 255, 0.18)' },
            lineStyle: { color: '#1677ff' },
            itemStyle: { color: '#1677ff' },
          },
        ],
      },
    ],
  }
}

export function buildPieOption(title, rows) {
  return {
    backgroundColor: 'transparent',
    title: {
      text: title,
      left: 12,
      top: 10,
      textStyle: { fontSize: 14, fontWeight: 700, color: '#102a43' },
    },
    tooltip: { trigger: 'item' },
    legend: { bottom: 4, left: 'center', itemWidth: 10, itemHeight: 10 },
    series: [
      {
        type: 'pie',
        radius: ['44%', '70%'],
        center: ['50%', '48%'],
        label: { formatter: '{b}: {c}' },
        data: rows.map((item) => ({
          name: item.label,
          value: item.count,
          itemStyle: { color: item.color },
        })),
      },
    ],
  }
}

export function buildBarOption(title, rows, options = {}) {
  const categoryField = options.categoryField || 'label'
  const valueField = options.valueField || 'count'
  return {
    backgroundColor: 'transparent',
    title: {
      text: title,
      left: 12,
      top: 10,
      textStyle: { fontSize: 14, fontWeight: 700, color: '#102a43' },
    },
    tooltip: { trigger: 'axis' },
    grid: { left: 54, right: 18, top: 52, bottom: 62 },
    xAxis: {
      type: 'category',
      data: rows.map((item) => item[categoryField]),
      axisLabel: {
        interval: 0,
        rotate: rows.length > 4 ? 18 : 0,
        overflow: 'truncate',
        width: 110,
      },
    },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        type: 'bar',
        barMaxWidth: 42,
        data: rows.map((item) => ({
          value: item[valueField],
          itemStyle: { color: item.color || '#1677ff' },
        })),
      },
    ],
  }
}

function buildGroupedRows(items, field, color) {
  const counts = (items || []).reduce((acc, item) => {
    const key = String(item?.[field] || 'unknown').trim() || 'unknown'
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})
  return Object.entries(counts)
    .map(([label, count]) => ({ label, count, color }))
    .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label))
}

function normalizeBenefit(value) {
  const text = String(value || '').trim()
  if (!text) return 'unknown'
  if (text.length <= 18) return text
  return `${text.slice(0, 18)}...`
}

function countBy(items, field) {
  return (items || []).reduce((acc, item) => {
    const key = item?.[field] || 'unknown'
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, Math.round(value)))
}
