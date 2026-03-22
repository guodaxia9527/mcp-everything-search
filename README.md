# Everything Search MCP Server (PRO)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](#)
[![Only Windows](https://img.shields.io/badge/Windows-Only-red.svg)](#)

[中文版](#chinese-version) | [English Version](#english-version)

[![mcp-everything-search MCP server](https://glama.ai/mcp/servers/guodaxia9527/mcp-everything-search/badges/card.svg)](https://glama.ai/mcp/servers/guodaxia9527/mcp-everything-search)

---

<a name="chinese-version"></a>
## 🇨🇳 中文版

一款专为 Windows 打造的高性能 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 服务器。本工具利用原生的 **Everything SDK**，为 AI 模型（如 Claude、GPT、Gemini）提供毫秒级的文件搜索、统计分析及磁盘空间洞察能力。

### 🚀 核心特性

- **极致速度**：基于 `Everything64.dll` 原生调用，数百万个文件搜索仅需毫秒级响应。
- **AI 意图自动引导 (Autopilot)**：内置运行时意图拦截与专用工具（如 `find_largest_folders`），防止 AI 模型在处理大数据量任务时陷入低效的递归扫描。
- **智能环境诊断**：主动检测磁盘索引状态，并在驱动器未索引时提供精确的修复引导。
- **完美支持中文**：原生解决 Windows 环境下的中文乱码问题，确保路径处理 100% 准确。
- **多客户端适配**：安装程序支持自动配置 **OpenCode** 和 **Claude Desktop**。

### 🛠 包含工具

| 工具名称 | 功能描述 |
| :--- | :--- |
| `everything_search` | 元数据搜索（名称、路径、后缀）。极致速度且精准。 |
| `everything_stats` | 文件分布与大小的深度统计分析。 |
| `find_largest_folders` | 磁盘空间分析专用工具（查找占用空间最大的目录）。 |
| `find_most_files` | 查找包含文件数量最多的目录。 |
| `get_engine_status` | 查看已索引驱动器列表及引擎健康状态。 |

### 📦 安装指引 (Windows)

1. 从 [Releases](https://github.com/guodaxia9527/mcp-everything-search/releases) 页面下载最新的 `mcp-everything-search.zip`。
2. 将压缩包解压到您的本地固定目录。
3. 双击运行 `install.exe`。程序将自动尝试为 OpenCode 和 Claude Desktop 完成配置。
4. 重启您的 AI 客户端。

---

<a name="english-version"></a>
## 🇺🇸 English Version

A high-performance [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server built for **Windows**. Leveraging the native **Everything SDK**, it provides AI models (like Claude, GPT, Gemini) with millisecond-speed file searching, statistical analysis, and disk usage insights.

### 🚀 Key Features

- **Ultra-Fast Search**: Powered by `Everything64.dll`, searching millions of files in milliseconds.
- **AI-Intent Autopilot**: Features runtime intent interception and specialized tools (e.g., `find_largest_folders`) to prevent AI models from falling into inefficient recursive scans.
- **Smart Diagnostics**: Proactively monitors indexing status and provides actionable hints for unindexed drives.
- **Full Unicode Support**: Native resolution for Chinese characters and special symbols on Windows.
- **Multi-Client Support**: The installer automatically configures **OpenCode** and **Claude Desktop**.

### 🛠 Tools Available

- `everything_search`: Lightning-fast metadata search.
- `everything_stats`: Statistical analysis of file distribution.
- `find_largest_folders`: Dedicated tool for disk usage analysis.
- `find_most_files`: Locate directories with the highest file counts.
- `get_engine_status`: Check indexing status and drive coverage.

### 📦 Installation (Windows Only)

1. Download `mcp-everything-search.zip` from [Releases](https://github.com/guodaxia9527/mcp-everything-search/releases).
2. Extract to a permanent local directory.
3. Run `install.exe`. It will automatically configure **OpenCode** and **Claude Desktop**.
4. Restart your AI client.

---

## 👨‍💻 Authors / 作者

- **guodaxia9527** - Lead Developer / 首席开发
- **Gemini Flash Latest** - AI System Architect / AI 架构师

## 📜 Credits & License / 鸣谢与许可证

- **Everything SDK**: A product of **voidtools** (https://www.voidtools.com/).
- **License**: This project is licensed under the **MIT License**.

---
*Note: This tool requires Windows and may request Administrator privileges (UAC) to access NTFS USN Journals if the Everything service is not running.*