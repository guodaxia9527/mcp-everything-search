# Everything Search MCP Server (PRO Edition)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for Windows. This tool leverages the native **Everything SDK** to provide AI models with ultra-fast file search, statistical analysis, and disk usage insights.

## 🚀 Features

- **Ultra-Fast Search**: Powered by `Everything64.dll`, searching millions of files in milliseconds.
- **AI-Intent Autopilot**: Intelligent guidance and specialized tools (`find_largest_folders`, `find_most_files`) designed to prevent AI models from choosing inefficient search paths.
- **Smart Diagnostics**: Proactively reports indexing status and provides actionable hints if a drive is not indexed.
- **Unicode/UTF-8 Ready**: Native support for Chinese characters and special symbols, resolving common Windows encoding issues.
- **Self-Healing**: Automatically handles common model errors like redundant wildcards or overly strict path filters.
- **Zero Configuration**: Built-in portable Everything engine that can run silently if the main software is not installed.

## 🛠 Tools

| Tool | Description |
| :--- | :--- |
| `everything_search` | Metadata search (name, path, extension). Fast and accurate. |
| `everything_stats` | Statistical analysis of file distribution and size. |
| `find_largest_folders` | Dedicated tool for disk space analysis (Largest directories). |
| `find_most_files` | Find directories containing the highest number of files. |
| `get_engine_status` | Check indexed drives and engine health. |

## 📦 Installation (End-User)

1. Download the latest `mcp-everything-search.zip` from the [Releases](https://github.com/guodaxia9527/mcp-everything-search/releases) page.
2. Extract the folder to a permanent location.
3. Double-click `install.exe`.
4. Restart your MCP Client (e.g., OpenCode, Claude Desktop).

## 👨‍💻 Authors

- **guodaxia9527** - Lead Developer
- **Gemini Flash Latest** - AI System Architect & Co-Author

## 📜 Credits & License

- **Everything SDK**: This project uses the Everything SDK, a product of **voidtools** (https://www.voidtools.com/).
- **License**: This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---
*Note: This tool requires Administrator privileges (UAC) to access NTFS USN Journals if the Everything service is not already running.*
