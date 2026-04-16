<template>
  <a-layout class="app-layout">
    <a-layout-sider width="220" theme="light" class="sider">
      <div class="logo">
        <span class="logo-icon">📊</span>
        <span class="logo-text">SmartMetric</span>
      </div>
      <a-menu :selectedKeys="[activeKey]" mode="inline">
        <a-menu-item key="usecase" @click="$router.push('/usecase-metric')">用例点度量</a-menu-item>
        <a-menu-item key="loc" @click="$router.push('/loc-metric')">代码行度量</a-menu-item>
        <a-menu-item key="fp" @click="$router.push('/function-point')">功能点度量</a-menu-item>
        <a-menu-item key="oo" @click="$router.push('/oo-metric')">面向对象度量</a-menu-item>
        <a-menu-item key="cfg" @click="$router.push('/cfg-metric')">控制流图度量</a-menu-item>
        <a-menu-item key="estimate" @click="$router.push('/estimate-metric')">项目估算</a-menu-item>
        <a-menu-item key="report" @click="$router.push('/report-export')">报告导出</a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <div class="content">
        <div class="content-inner">
          <slot />
        </div>
      </div>
    </a-layout>
  </a-layout>
</template>

<script setup>
defineProps({
  activeKey: {
    type: String,
    default: 'usecase',
  },
})
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: linear-gradient(180deg, #f6f8fc 0%, #f2f4f8 100%);
}
.sider {
  border-right: 1px solid #e8edf5;
  box-shadow: 2px 0 12px rgba(15, 23, 42, 0.04);
}
.logo {
  height: 62px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-weight: 700;
  letter-spacing: 0.3px;
  border-bottom: 1px solid #eef2f7;
}
.logo-icon {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: linear-gradient(135deg, #2f80ed, #3aa0ff);
  color: #fff;
  font-size: 16px;
  box-shadow: 0 4px 10px rgba(47, 128, 237, 0.28);
}
.logo-text {
  font-size: 17px;
  color: #102a43;
}
.content {
  padding: 20px;
}
.content-inner {
  min-height: calc(100vh - 40px);
}
</style>
