<template>
  <AppLayout activeKey="estimate">
    <a-space direction="vertical" style="width: 100%" :size="14">
      <a-card title="项目工作量/成本/工期估算">
        <a-row :gutter="12">
          <a-col :span="6">
            <div class="field-label">度量来源</div>
            <a-select v-model:value="form.metric_type" style="width: 100%">
              <a-select-option value="fp">功能点 FP</a-select-option>
              <a-select-option value="ucp">用例点 UCP</a-select-option>
              <a-select-option value="loc">代码行 LoC</a-select-option>
            </a-select>
          </a-col>
          <a-col :span="6">
            <div class="field-label">度量值</div>
            <a-input-number v-model:value="form.metric_value" :min="0" style="width: 100%" />
          </a-col>
          <a-col :span="6">
            <div class="field-label">生产率（小时/单位）</div>
            <a-input-number v-model:value="form.productivity" :min="0" style="width: 100%" />
          </a-col>
          <a-col :span="6">
            <div class="field-label">团队人数</div>
            <a-input-number v-model:value="form.team_size" :min="1" style="width: 100%" />
          </a-col>
        </a-row>
        <a-row :gutter="12" style="margin-top: 12px">
          <a-col :span="8">
            <div class="field-label">人月工时</div>
            <a-input-number v-model:value="form.hours_per_person_month" :min="1" style="width: 100%" />
          </a-col>
          <a-col :span="8">
            <div class="field-label">人月成本</div>
            <a-input-number v-model:value="form.cost_per_person_month" :min="0" style="width: 100%" />
          </a-col>
          <a-col :span="8">
            <div class="field-label">目标工期（月，可选）</div>
            <a-input-number v-model:value="form.target_months" :min="0" style="width: 100%" />
          </a-col>
        </a-row>
        <a-button type="primary" :loading="loading" style="margin-top: 14px" @click="calculate">开始估算</a-button>
      </a-card>

      <a-card title="估算结果">
        <a-row :gutter="12">
          <a-col :span="6"><a-statistic title="工作量(小时)" :value="result.effort_hours" :precision="2" /></a-col>
          <a-col :span="6"><a-statistic title="工作量(人月)" :value="result.effort_person_months" :precision="2" /></a-col>
          <a-col :span="6"><a-statistic title="成本" :value="result.cost" :precision="2" /></a-col>
          <a-col :span="6"><a-statistic title="工期(月)" :value="result.duration_months" :precision="2" /></a-col>
        </a-row>
        <div class="recommend">建议人数：{{ result.recommended_people }}</div>
      </a-card>

      <a-card title="CLI 用法">
        <pre class="cli-box">python backend/cli.py estimate estimate-input.json</pre>
      </a-card>
    </a-space>
  </AppLayout>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { message } from 'ant-design-vue'
import AppLayout from '~/components/AppLayout.vue'
import api from '~/utils/api'

const loading = ref(false)
const form = reactive({
  metric_type: 'fp',
  metric_value: 0,
  productivity: 8,
  hours_per_person_month: 160,
  cost_per_person_month: 12000,
  team_size: 3,
  target_months: 0,
})
const result = reactive({
  effort_hours: 0,
  effort_person_months: 0,
  cost: 0,
  duration_months: 0,
  recommended_people: 0,
})

watch(
  () => form.metric_type,
  (value) => {
    form.productivity = value === 'ucp' ? 20 : value === 'loc' ? 0.05 : 8
  }
)

const calculate = async () => {
  loading.value = true
  try {
    const { data } = await api.post('/api/metrics/estimate/calculate', { ...form })
    Object.assign(result, data.data)
    message.success('估算完成')
  } catch (err) {
    message.error(err?.response?.data?.message || '估算失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.field-label {
  margin-bottom: 6px;
  color: #666;
  font-size: 12px;
}
.recommend {
  margin-top: 14px;
  font-weight: 700;
}
.cli-box {
  white-space: pre-wrap;
  background: #111827;
  color: #d1fae5;
  padding: 12px;
  border-radius: 6px;
}
</style>
