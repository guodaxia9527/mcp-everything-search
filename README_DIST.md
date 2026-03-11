# Everything Search MCP 服务器 (All-in-One 极速版)

本文档记录了基于 Everything SDK 原生调用且内置搜索引擎的分发包说明。

## 1. 核心特性
- **内置引擎**：自带绿色版 `Everything.exe`，MCP 启动时若检测到引擎未运行，将自动静默拉起。
- **极速性能**：通过 `Everything64.dll` 原生调用，绕过命令行解析，全盘统计毫秒级响应。
- **免安装**：解压即用，一键运行 `install.exe` 自动配置 `opencode.json`。
- **完美路径**：原生支持 Unicode/UTF-8，彻底解决中文乱码问题。
- **智能诊断**：自动识别驱动器索引状态，提供环境修复引导。

## 2. 交付包结构 (dist 目录)
```text
dist/
├── install.exe        # 一键安装/配置程序
├── server/            # MCP 服务核心
│   ├── server.exe     # MCP 主程序 (v1.6.0-SMART)
│   ├── Everything.exe # 内置极速搜索引擎 (x64 绿色版)
│   ├── Everything.lng # 引擎多语言支持
│   ├── Everything64.dll # 原生 SDK 驱动
│   ├── es.exe         # 兼容性命令行工具
│   └── _internal/     # Python 运行环境依赖
└── README.txt         # 用户快速入门
```

## 3. 工具列表
- **everything_search**：根据元数据（名称、路径、后缀）极速找文件。内置 AI 引导逻辑，防止低效搜索。
- **everything_stats**：分析磁盘空间占用、文件夹大小排名。比手动计数快 1000 倍。
- **get_engine_status**：查看当前 Everything 索引了哪些盘符以及引擎健康状态。

## 4. 安装与权限说明
1. **自动配置**：运行 `install.exe`，它将自动识别路径并注册到 OpenCode。
2. **UAC 权限 (重要)**：
   - 首次启动 MCP 服务或内置 `Everything.exe` 时，Windows 可能会弹出 **UAC 管理员权限请求**。
   - **请务必点击“是”**，以便 Everything 引擎能够读取 NTFS 磁盘日志以实现毫秒级索引。

## 5. 常见问题
- **如果搜索返回“Everything engine is NOT running”**：请手动运行目录下的 `Everything.exe` 并确保其处于管理员运行状态。
- **多实例共存**：本工具会自动连接已有的 Everything 服务。若系统中已有安装版在运行，将优先使用已有的，不会冲突。
