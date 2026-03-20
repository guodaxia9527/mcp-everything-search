# [Windows Only / 仅限 Windows 平台]

### 🇺🇸 English Version
#### v1.7.3 Structured JSON & Stability Update
- **RESTRUCTURE**: All responses now return structured JSON with `status`, `total_files_found`, `results_returned`, `truncated`, `counting_tip`
- **BUGFIX**: Everything SDK SetMax state persists across queries — now reset to 0xFFFFFFFF after each query
- **OPT**: Added `STATS_SCAN_LIMIT = 200_000` to prevent OOM on massive drives
- **OPT**: Unified error handling with `ok()` and `err()` helper functions
- **OPT**: Tool definitions extracted to `TOOLS` constant for easier maintenance
- **OPT**: Improved timezone handling in file timestamps

### 🇨🇳 中文版
#### v1.7.3 结构化 JSON 与稳定性更新
- **重构**：所有响应现在返回结构化 JSON，包含 `status`, `total_files_found`, `results_returned`, `truncated`, `counting_tip`
- **Bug修复**：Everything SDK 的 SetMax 状态会在查询间持久化 — 现在每次查询后重置为 0xFFFFFFFF
- **优化**：添加 `STATS_SCAN_LIMIT = 200_000` 防止大型磁盘 OOM
- **优化**：使用 `ok()` 和 `err()` 辅助函数统一错误处理
- **优化**：工具定义提取到 `TOOLS` 常量，便于维护
- **优化**：改进文件时间戳的时区处理

---

### 🇺🇸 English Version
#### v1.6.5 Performance & Stability Update
- **Performance**: Added `Everything_SetMax` to limit results loaded into RAM (prevents memory overflow on large queries)
- **Fixed**: Default limit now matches tool schema (20 instead of 100)
- **Fixed**: Path now supports both forward slash (/) and backslash (\)
- **Fixed**: Extension detection now correctly handles dots in folder names
- **Fixed**: Unicode/Chinese characters now preserved in JSON output
- **Improved**: Added result count header so AI knows when results are truncated

### 🇨🇳 中文版
#### v1.6.5 性能与稳定性更新
- **性能优化**：添加 `Everything_SetMax` 限制加载到内存的结果数量（防止大查询导致内存溢出）
- **修复**：默认 limit 现在与工具描述一致（20 而非 100）
- **修复**：路径现在同时支持正斜杠 (/) 和反斜杠 (\)
- **修复**：扩展名检测现在正确处理文件夹名中的点
- **修复**：JSON 输出现在正确保留 Unicode/中文字符
- **改进**：添加结果计数头部，让 AI 知道结果何时被截断

---

### 🇺🇸 English Version
#### v1.6.4 Bugfix Release
- **Fixed False Error**: Resolved issue where searching a non-existent path incorrectly reported "Drive not indexed"
- **Improved Diagnostics**: Now correctly displays "Path does not exist" for invalid directories

### 🇨🇳 中文版
#### v1.6.4 Bug 修复版本
- **修复错误提示**：解决了搜索不存在路径时错误显示"D 盘未索引"的问题
- **改进诊断信息**：现在正确显示"路径不存在"而非误报驱动器未索引

---

### 👨‍💻 Authors / 作者
- Developed by **guodaxia9527** & **Gemini Flash Latest**.
- Special thanks to **voidtools** for the Everything SDK.
