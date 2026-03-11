# Everything Search MCP 服务器 (All-in-One 极速版)

本文档记录了基于 Everything SDK 原生调用且内置搜索引擎的分发包说明。

## 1. 核心特性
- **内置引擎**：自带绿色版 `Everything.exe`，MCP 启动时若检测到引擎未运行，将自动静默拉起。
- **极速性能**：通过 `Everything64.dll` 原生调用，绕过命令行解析，全盘统计毫秒级响应。
- **免安装**：解压即用，自动配置 `opencode.json`。
- **完美路径**：原生支持 Unicode，彻底解决中文路径乱码。

## 2. 交付包结构 (dist 目录)
```text
dist/
├── install.exe        # 一键安装/配置程序
├── server/            # MCP 服务核心
│   ├── server.exe     # MCP 主程序
│   ├── Everything.exe # 内置极速搜索引擎 (x64 绿色版)
│   ├── Everything.lng # 引擎多语言支持
│   ├── Everything64.dll # 原生 SDK 驱动
│   ├── es.exe         # 兼容性命令行工具
│   └── _internal/     # Python 运行环境依赖
└── README.txt         # 用户快速入门
```

## 3. 安装与权限说明
1. **自动配置**：运行 `install.exe`，它将自动识别路径并注册到 OpenCode。
2. **UAC 权限 (重要)**：
   - 首次启动 MCP 服务或内置 `Everything.exe` 时，Windows 可能会弹出 **UAC 管理员权限请求**。
   - **请务必点击“是”**，以便 Everything 引擎能够读取 NTFS 磁盘日志以实现毫秒级索引。
   - 若不赋予权限，搜索功能将无法获取磁盘数据。

## 4. 维护与打包 (开发者参考)
使用以下命令重新生成分发包：
```bash
pyinstaller --onedir ^
  --add-binary "Everything.exe;." ^
  --add-binary "Everything.lng;." ^
  --add-binary "Everything64.dll;." ^
  --add-binary "es.exe;." ^
  server.py
```

## 5. 常见问题
- **如果搜索返回“Everything engine is NOT running”**：请手动运行目录下的 `Everything.exe` 并确保其处于管理员运行状态。
- **多实例共存**：本工具会自动连接已有的 Everything 服务。若系统中已有安装版在运行，将优先使用已有的，不会冲突。
