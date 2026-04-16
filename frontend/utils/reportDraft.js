const STORAGE_KEY = 'smartmetric-report-draft'

export const saveMetricSnapshot = (moduleKey, payload) => {
  if (!process.client) return
  const current = loadMetricSnapshots()
  current[moduleKey] = {
    ...payload,
    updatedAt: new Date().toISOString(),
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(current))
}

export const loadMetricSnapshots = () => {
  if (!process.client) return {}
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
  } catch {
    return {}
  }
}

export const clearMetricSnapshots = () => {
  if (!process.client) return
  localStorage.removeItem(STORAGE_KEY)
}

export const buildReportPayloadFromSnapshots = (snapshots, selectedKeys = []) => {
  const entries = Object.entries(snapshots || {})
  const enabledEntries = entries.filter(
    ([key, value]) => value && value.summary && (!selectedKeys.length || selectedKeys.includes(key))
  )

  const summary = {
    模块数: enabledEntries.length,
    最后更新时间: latestUpdatedAt(enabledEntries),
  }

  const sections = enabledEntries.map(([key, value]) => ({
    heading: moduleTitle(key),
    text: buildSectionText(value),
    rows: normalizeRows(value.rows),
  }))

  return {
    title: 'SmartMetric 自动汇总报告',
    subtitle: '由前端已保存的度量结果自动生成',
    summary,
    sections,
  }
}

export const moduleTitle = (key) => {
  const titles = {
    usecase: '用例点度量',
    loc: '代码行度量',
    function_point: '功能点度量',
    cfg: '控制流图度量',
    oo: '面向对象度量',
    estimate: '项目估算',
  }
  return titles[key] || key
}

const latestUpdatedAt = (entries) => {
  const values = entries.map(([, value]) => value.updatedAt).filter(Boolean).sort()
  return values.at(-1) || ''
}

const buildSectionText = (snapshot) => {
  const parts = []
  if (snapshot.description) parts.push(snapshot.description)
  if (snapshot.summary) {
    parts.push(
      Object.entries(snapshot.summary)
        .map(([key, value]) => `${key}: ${value}`)
        .join('；')
    )
  }
  return parts.join('\n')
}

const normalizeRows = (rows) => {
  if (!Array.isArray(rows)) return []
  return rows.slice(0, 12)
}
