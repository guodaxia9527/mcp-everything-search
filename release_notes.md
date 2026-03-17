# [Windows Only / 仅限 Windows 平台]

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
- **Fixed False Error**: Resolved issue where searching a non-existent path (e.g., `D:\Music`) incorrectly reported "Drive D: is NOT indexed"
- **Improved Diagnostics**: Now correctly displays "Path does not exist" for invalid directories
- **Fixed get_engine_status**: `indexed_drives` now correctly shows all indexed drives (was returning empty array)

### 🇨🇳 中文版
#### v1.6.4 Bug 修复版本
- **修复错误提示**：解决了搜索不存在路径（如 `D:\Music`）时错误显示"D 盘未索引"的问题
- **改进诊断信息**：现在正确显示"路径不存在"而非误报驱动器未索引
- **修复 get_engine_status**：`indexed_drives` 现在正确显示所有已索引的驱动器（之前返回空数组）

---

### 🇺🇸 English Version
#### v1.6.3 Update: Global & Multi-Client Support
- **Multi-Client Installer**: `install.exe` now automatically detects and configures both **OpenCode** and **Claude Desktop**.
- **Platform Badge**: Added official "Windows Only" and "MIT" status to the repository.
- **Improved Docs**: Complete bilingual README (CN/EN) for global users.
- **AI Autopilot**: Reinforced instructions to prevent models from using slow shell commands.
- **Specialized Tools**: `find_largest_folders` and `find_most_files` are now standard.

### 🇨🇳 中文版
#### v1.6.3 更新：多客户端支持与国际化
- **多客户端安装**：`install.exe` 现支持自动识别并配置 **OpenCode** 和 **Claude Desktop**。
- **平台标识**：正式增加"仅限 Windows"和"MIT 许可证"标识。
- **双语文档**：全新的中英双语 README，方便全球用户参考。
- **AI 自动导航**：强化指令集，从根源杜绝模型调用缓慢的系统命令。
- **专用统计工具**：内置专为大文件夹和文件堆积设计的统计接口。

---

### 👨‍💻 Authors / 作者
- Developed by **guodaxia9527** & **Gemini Flash Latest**.
- Special thanks to **voidtools** for the Everything SDK.
