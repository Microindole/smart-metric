import { reactive } from 'vue'

const state = reactive({
  loading: false,
  pickingDirectory: false,
  projectPath: '',
  useDefaultIgnores: true,
  useIgnoreFile: true,
  ignoreFileName: '.smartmetricignore',
  modules: ['inventory', 'loc', 'dependency', 'oo', 'design'],
  ignoreDirsText: '',
  ignoreGlobsText: '',
  result: null,
  summary: {
    total_files: 0,
    code_file_count: 0,
    design_file_count: 0,
    code_lines: 0,
    dependency_edge_count: 0,
    class_count: 0,
    god_files: 0,
    god_classes: 0,
  },
  scanOptions: {
    use_default_ignores: true,
    use_ignore_file: true,
    ignore_file_path: '',
    ignore_file_found: false,
    ignore_file_has_negation: false,
    ignore_file_dirs: [],
    ignore_file_globs: [],
    ignore_dirs: [],
    ignore_globs: [],
    effective_ignore_dirs: [],
    effective_ignore_globs: [],
  },
})

export function useProjectMetricState() {
  return { state }
}
