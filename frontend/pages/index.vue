<template>
  <div class="home">
    <div class="hero">
      <div class="brand">SmartMetric</div>
      <h1>自动化软件度量平台</h1>
      <p>选择一个模块开始。首页不再自动跳转，也不在加载时依赖后端接口。</p>
    </div>

    <div class="grid">
      <button v-for="item in items" :key="item.path" class="entry" @click="navigateTo(item.path)">
        <div class="entry-title">{{ item.title }}</div>
        <div class="entry-text">{{ item.text }}</div>
      </button>
    </div>
  </div>
</template>

<script setup>
const items = [
  { path: '/usecase-metric', title: '用例点度量', text: 'UUC / UAW / TCF / EF / UCP' },
  { path: '/loc-metric', title: '代码行度量', text: 'LoC、类级与方法级统计' },
  { path: '/function-point', title: '功能点度量', text: 'EI / EO / EQ / ILF / EIF' },
  { path: '/oo-metric', title: '面向对象度量', text: '源码级与类图级 CK / LK' },
  { path: '/cfg-metric', title: '控制流图度量', text: '源码分析与图导入' },
  { path: '/estimate-metric', title: '项目估算', text: '工作量 / 成本 / 工期 / 人员' },
  { path: '/report-export', title: '报告导出', text: 'Markdown / HTML / PDF' },
]
</script>

<style scoped>
.home {
  min-height: 100vh;
  padding: 32px;
  background: linear-gradient(180deg, #f6f8fc 0%, #eef3fa 100%);
}

.hero {
  margin-bottom: 28px;
}

.brand {
  margin-bottom: 10px;
  color: #165dff;
  font-size: 14px;
  font-weight: 700;
}

h1 {
  margin: 0 0 10px;
  color: #102a43;
  font-size: 34px;
}

p {
  margin: 0;
  color: #52667a;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
}

.entry {
  border: 1px solid #dbe2ea;
  border-radius: 8px;
  background: #fff;
  padding: 18px;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease;
}

.entry:hover {
  border-color: #8ab4ff;
  box-shadow: 0 8px 18px rgba(16, 42, 67, 0.08);
  transform: translateY(-1px);
}

.entry-title {
  margin-bottom: 8px;
  color: #102a43;
  font-size: 18px;
  font-weight: 700;
}

.entry-text {
  color: #5a6c7f;
  line-height: 1.6;
}
</style>
