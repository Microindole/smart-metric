import { reactive } from 'vue'

const state = reactive({
  loading: false,
  pickingDirectory: false,
  projectPath: '',
  model: 'gpt-4.1-mini',
  exportFormat: 'pdf',
  fpFile: '',
  estimateFile: '',
  phase1File: '',
  phase2File: '',
  phase1Payload: null,
  phase2Payload: null,
  fpPayload: null,
  estimatePayload: null,
  useDefaultIgnores: true,
  useIgnoreFile: true,
  ignoreFileName: '.smartmetricignore',
  reviewResult: null,
  reportPayload: null,
  configSummary: {
    local_config_path: '',
    example_config_path: '',
    local_config_exists: false,
    provider: 'openai_compat',
    model: 'gpt-4.1-mini',
    api_base: '',
    api_key_configured: false,
  },
})

let activeReviewController = null

export function useAiReviewState() {
  return {
    state,
    getActiveReviewController: () => activeReviewController,
    setActiveReviewController: (controller) => {
      activeReviewController = controller
    },
  }
}
