# Everything Search MCP 服务器 (PRO 专业版)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一款专为 Windows 打造的高性能 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 服务器。本工具利用原生的 **Everything SDK**，为 AI 模型（如 Claude、GPT、Gemini）提供毫秒级的文件搜索、统计分析及磁盘空间洞察能力。

## 🚀 核心特性

- **极致速度**：基于 `Everything64.dll` 原生调用，数百万个文件搜索仅需毫秒级响应。
- **AI 意图自动引导 (Autopilot)**：内置运行时意图拦截与专用工具（如 `find_largest_folders`），防止 AI 模型在处理大数据量任务时陷入低效的递归扫描。
- **智能环境诊断**：主动检测磁盘索引状态，并在驱动器未索引时提供精确的修复引导。
- **完美支持中文 (Unicode/UTF-8)**：原生解决 Windows 环境下的中文乱码问题，确保路径处理 100% 准确。
- **自愈功能**：自动纠正模型常见的语法错误（如冗余通配符或过于严格的过滤条件）。
- **零配置启动**：内置便携版 Everything 引擎，即使系统未安装 Everything 软件也能静默运行。

## 🛠 包含工具

| 工具名称 | 功能描述 |
| :--- | :--- |
| `everything_search` | 元数据搜索（名称、路径、后缀）。极致速度且精准。 |
| `everything_stats` | 文件分布与大小的深度统计分析。 |
| `find_largest_folders` | 磁盘空间分析专用工具（查找占用空间最大的目录）。 |
| `find_most_files` | 查找包含文件数量最多的目录。 |
| `get_engine_status` | 查看已索引驱动器列表及引擎健康状态。 |

## 📦 安装指引 (最终用户)

1. 从 [Releases](https://github.com/guodaxia9527/mcp-everything-search/releases) 页面下载最新的 `mcp-everything-search.zip`。
2. 将压缩包解压到您的本地固定目录。
3. 双击运行 `install.exe`。
4. 重启您的 MCP 客户端（如 OpenCode, Claude Desktop）。

## 👨‍💻 作者

- **guodaxia9527** - 首席开发者
- **Gemini Flash Latest** - AI 系统架构师 & 联合署名作者

## 📜 鸣谢与许可证

- **Everything SDK**：本项目使用了由 **voidtools** (https://www.voidtools.com/) 提供的 Everything SDK。
- **许可证**：本项目采用 **MIT 许可证** 开源 - 详情请参阅 [LICENSE](LICENSE) 文件。

---
*注：如果系统未开启 Everything 服务，本工具启动内置引擎时可能需要管理员权限 (UAC) 以读取 NTFS USN 日志。*
