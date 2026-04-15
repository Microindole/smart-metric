<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider width="220" theme="light" class="sider">
      <div class="logo">自动化软件度量平台</div>
      <a-menu :selectedKeys="[activeKey]" mode="inline">
        <a-menu-item key="usecase" @click="$router.push('/usecase-metric')">用例点度量</a-menu-item>
        <a-menu-item key="loc" @click="$router.push('/loc-metric')">代码行度量</a-menu-item>
        <a-menu-item key="fp" disabled>功能点度量(占位)</a-menu-item>
        <a-menu-item key="oo" disabled>面向对象度量(占位)</a-menu-item>
        <a-menu-item key="cfg" disabled>控制流图度量(占位)</a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <div class="header">SmartMetric · 阶段一</div>
      <div class="content">
        <slot />
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
.sider {
  border-right: 1px solid #eee;
}
.logo {
  height: 56px;
  line-height: 56px;
  text-align: center;
  font-weight: 700;
  border-bottom: 1px solid #f0f0f0;
}
.header {
  background: #fff;
  font-weight: 600;
  border-bottom: 1px solid #f0f0f0;
}
.content {
  padding: 18px;
}
</style>
