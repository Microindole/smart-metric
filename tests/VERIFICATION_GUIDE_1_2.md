# SmartMetric 阶段一验证指南（用例点度量 + 代码行度量）

本文给出两个模块的验证方法、测试输入文件位置、操作步骤与预期结果。

## 1. 测试文件目录

- 用例点度量：`test/usecase_metric/`
  - `uc_case_basic.oom`
  - `manual_input_basic.json`
- 代码行度量：`test/loc_metric/`
  - `JavaCase.java`
  - `python_case.py`
  - `cpp_case.cpp`
  - `expected_loc_result.md`

## 2. 启动服务

1. 启动后端
   - 在 `backend/` 目录执行：
     - `python app.py`
2. 启动前端
   - 在 `frontend/` 目录执行：
     - `npm run dev`
   - 打开页面（若端口被占用，以终端输出为准）：
     - `http://localhost:3000` 或 `http://localhost:3001`

---

## 3. 用例点度量模块验证

### 3.1 文件解析 + 自动回填验证（.oom）

**输入文件**
- `test/usecase_metric/uc_case_basic.oom`

**步骤**
1. 左侧进入“用例点度量”页面。
2. 点击“选择文件”，选择 `uc_case_basic.oom`。
3. 点击“开始分析”。
4. 观察 UUC/UAW 输入框是否被自动回填。

**预期结果**
- 自动回填：
  - 用例：`simple=2, average=1, complex=1`
  - 角色：`simple=0, average=3, complex=0`
- 页面提示“解析成功，已回填 UUC/UAW 输入项”。

### 3.2 UCP 计算验证（默认因子）

**输入数据**
- 延续 3.1 的自动回填结果。
- TCF/EF 使用“加载默认因子”后保持各等级为 0。

**步骤**
1. 点击“加载默认因子”。
2. 确认 TCF/EF 各因子等级均为 0。
3. 点击“计算 UCP”。

**预期结果（按当前实现公式）**
- UUC = `2*5 + 1*10 + 1*15 = 35`
- UAW = `0*1 + 3*2 + 0*3 = 6`
- TCF = `0.6`
- EF = `1.4`
- UCP = `(35 + 6) * 0.6 * 1.4 = 34.44`

页面应显示：
- `UUC = 35`
- `UAW = 6`
- `TCF = 0.6`
- `EF = 1.4`
- `最终 UCP = 34.44`

### 3.3 手工录入验证（可选）

**参考文件**
- `test/usecase_metric/manual_input_basic.json`

**步骤**
1. 不上传文件，手工输入：
   - use_case_counts: `1,1,1`
   - actor_counts: `1,2,0`
2. TCF/EF 因子全部设置为 0。
3. 点击“计算 UCP”。

**预期结果**
- UUC = `30`
- UAW = `5`
- TCF = `0.6`
- EF = `1.4`
- UCP = `29.4`

---

## 4. 代码行度量模块验证

### 4.1 单文件验证

**输入文件**
- `test/loc_metric/JavaCase.java`
- `test/loc_metric/python_case.py`
- `test/loc_metric/cpp_case.cpp`

**步骤（每个文件重复一次）**
1. 左侧进入“代码行度量”页面。
2. 仅上传一个测试文件。
3. 语言保持“自动识别”。
4. 点击“开始分析”。
5. 核对表格与汇总卡片数据。

**预期结果**
- `JavaCase.java`：49 / 7 / 0 / 42（总行/空行/注释行/有效代码行）
- `python_case.py`：23 / 7 / 2 / 14
- `cpp_case.cpp`：22 / 2 / 1 / 19

### 4.2 多文件汇总验证

**输入文件**
- 同时上传：`JavaCase.java` + `python_case.py` + `cpp_case.cpp`

**步骤**
1. 选择三个文件一起上传。
2. 点击“开始分析”。
3. 核对“汇总结果”。

**预期结果**
- total_lines = `91`
- blank_lines = `14`
- comment_lines = `3`
- code_lines = `74`
- comment_ratio = `0.033`（前端显示约 `3%`）
- class_count = `1`
- method_count = `6`

### 4.3 代码辅助度量结果验证（Java）

**输入文件**
- `JavaCase.java`（可单独上传）

**步骤**
1. 进入“代码行度量”页面。
2. 上传 `JavaCase.java`。
3. 点击“开始分析”。
4. 核对新增的三个区域：
   - 代码行分析结果（文字摘要）
   - 抽象语法树分析结果（类级）
   - 抽象语法树分析结果（方法级）

**预期结果**
- 文字摘要：
  - 类 1 个、方法 6 个、判断语句 4 处、循环语句 1 处。
- 类级表（`JavaCase`）：
  - 方法数 6、字段数 3、RFC=9、LCOM=0。
- 方法级表：
  - `formatProfile` 的“调用的方法”包含 `computeLevel`。
  - `exportSummary` 的“调用的方法”包含 `normalizeName`、`formatProfile`。

---

## 5. 导出验证

### 5.1 用例点度量导出
1. 完成一次 UCP 计算。
2. 点击“导出 CSV”。
3. 打开下载文件检查是否包含：`UUC/UAW/TCF/EF/UCP`。

### 5.2 代码行度量导出
1. 完成一次代码行统计。
2. 点击“导出 CSV”。
3. 打开下载文件检查是否包含每个文件的统计列。

---

## 6. 常见异常验证（建议）

1. 用例点页不选 `.oom` 直接点“开始分析”
   - 预期：提示“请先选择 .oom 文件”。
2. 代码行页不上传文件直接点“开始分析”
   - 预期：提示“请先选择代码文件”。
3. 上传不支持后缀文件到代码行页
   - 预期：后端返回“不支持的文件类型”。
