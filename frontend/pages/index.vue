<template>
  <div class="home-redirect">
    <a-spin />
    <div>正在进入用例点度量...</div>
    <a-button type="link" @click="$router.push('/usecase-metric')">手动进入</a-button>
  </div>
</template>

<script setup>
onMounted(() => {
  navigateTo('/usecase-metric')
})
</script>

<style scoped>
.home-redirect {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 12px;
}
</style>
