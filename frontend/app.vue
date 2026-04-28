<template>
  <NuxtPage />
</template>

<style>
html {
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  margin: 0;
  background: #f6f4ef;
  color: #191714;
  font-family: var(--sm-font-ui);
}

* {
  box-sizing: border-box;
}

::selection {
  background: rgba(198, 95, 61, 0.22);
  color: #191714;
}

::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: #f2ede5;
}

::-webkit-scrollbar-thumb {
  border: 2px solid #f2ede5;
  border-radius: 999px;
  background: #cfc3b7;
}

::-webkit-scrollbar-thumb:hover {
  background: #b8aa9c;
}

button,
a,
input,
textarea,
select {
  font: inherit;
}

button:focus-visible,
a:focus-visible {
  outline: 2px solid rgba(198, 95, 61, 0.42);
  outline-offset: 2px;
}

:root {
  --sm-font-ui: "Segoe UI Variable", Inter, "SF Pro Text", -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei UI", "PingFang SC", "Noto Sans CJK SC", sans-serif;
  --sm-font-display: "Segoe UI Variable Display", Inter, "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei UI", "PingFang SC", "Noto Sans CJK SC", sans-serif;
  --sm-ink: #191714;
  --sm-muted: #74695e;
  --sm-paper: #fffcf7;
  --sm-paper-soft: #f7f3ec;
  --sm-line: #e4dacf;
  --sm-accent: #c65f3d;
  --sm-accent-strong: #a94f34;
}

.ant-card {
  overflow: hidden;
  background: var(--sm-paper);
  border-color: var(--sm-line);
  border-radius: 8px;
  box-shadow: 0 1px 0 rgba(40, 32, 24, 0.04);
}

.ant-card-head {
  min-height: 52px;
  border-bottom-color: #ebe2d8;
  background: rgba(255, 252, 247, 0.86);
}

.ant-card-head-title {
  color: var(--sm-ink);
  font-weight: 760;
  letter-spacing: 0;
}

.ant-btn {
  border-radius: 7px;
  font-weight: 650;
}

.ant-btn-primary {
  background: var(--sm-accent);
  border-color: var(--sm-accent);
  box-shadow: 0 8px 18px rgba(198, 95, 61, 0.18);
}

.ant-btn-primary:hover,
.ant-btn-primary:focus {
  background: var(--sm-accent-strong) !important;
  border-color: var(--sm-accent-strong) !important;
}

.ant-input,
.ant-input-number,
.ant-select-selector,
.ant-upload,
.ant-table {
  border-radius: 7px !important;
}

.ant-input,
.ant-input-number,
.ant-select-selector {
  border-color: #ded4c8 !important;
  background: var(--sm-paper) !important;
}

.ant-input:focus,
.ant-input-focused,
.ant-input-number-focused,
.ant-select-focused .ant-select-selector {
  border-color: #c98a70 !important;
  box-shadow: 0 0 0 2px rgba(198, 95, 61, 0.1) !important;
}

.ant-tabs .ant-tabs-tab {
  color: #59524a;
}

.ant-tabs .ant-tabs-tab.ant-tabs-tab-active .ant-tabs-tab-btn {
  color: var(--sm-accent-strong);
  font-weight: 750;
}

.ant-tabs .ant-tabs-ink-bar {
  background: var(--sm-accent);
}

.ant-table-thead > tr > th {
  background: #fbf6ef !important;
  color: #312c26 !important;
  font-weight: 750 !important;
}

.ant-table-tbody > tr > td {
  border-bottom-color: #eee6dc !important;
}

.ant-table-tbody > tr:hover > td {
  background: #fff8ef !important;
}

.ant-statistic-title {
  color: #7b7167 !important;
}

.ant-statistic-content {
  color: #191714 !important;
}

.ant-table-wrapper .ant-table {
  border-radius: 8px;
}

.ant-empty-description {
  color: #9a8f84 !important;
}

@media (max-width: 760px) {
  body {
    overflow-x: hidden;
  }

  .ant-space {
    max-width: 100%;
  }

  .ant-space-horizontal {
    width: 100%;
    display: flex !important;
    flex-wrap: wrap;
    row-gap: 10px;
  }

  .ant-space-horizontal > .ant-space-item {
    flex: 0 0 auto;
    min-width: fit-content;
  }

  .ant-tabs {
    width: 100%;
  }

  .ant-tabs-nav {
    width: 100%;
  }

  .ant-btn {
    white-space: nowrap;
  }

  .ant-card {
    max-width: 100%;
  }

  .ant-card-body {
    overflow-x: auto;
  }

  .ant-row {
    row-gap: 12px;
  }

  .ant-select,
  .ant-input,
  .ant-input-number {
    max-width: 100%;
  }

  input[type="file"] {
    max-width: 100%;
    min-width: 180px;
  }

  .ant-table-wrapper {
    min-width: 640px;
  }
}

</style>
