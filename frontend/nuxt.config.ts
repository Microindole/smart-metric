// @ts-nocheck
export default defineNuxtConfig({
  devtools: { enabled: false },
  css: ['ant-design-vue/dist/reset.css'],
  experimental: {
    appManifest: false,
  },
  vite: {
    optimizeDeps: {
      include: ['ant-design-vue', 'axios'],
    },
  },
  app: {
    head: {
      title: 'SmartMetric 自动化软件度量平台',
      meta: [{ name: 'viewport', content: 'width=device-width, initial-scale=1' }],
    },
  },
})
