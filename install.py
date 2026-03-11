import os
import json
import sys
import io

# 强制使用 UTF-8 输出，防止 Windows 终端乱码
if sys.stdout:
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass

def update_opencode(exe_path):
    config_dir = os.path.expanduser("~/.config/opencode")
    config_file = os.path.join(config_dir, "opencode.json")
    
    mcp_entry = {
        "everything-search": {
            "type": "local",
            "command": [exe_path],
            "enabled": True
        }
    }
    
    print(f"正在尝试配置 OpenCode: {config_file}")
    
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        
    if not os.path.exists(config_file):
        config = {"$schema": "https://opencode.ai/config.json", "mcp": mcp_entry}
    else:
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            if "mcp" not in config: config["mcp"] = {}
            config["mcp"]["everything-search"] = mcp_entry["everything-search"]
        except Exception as e:
            print(f"  [!] 更新失败: {e}")
            return

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("  [v] 成功更新 OpenCode 配置。")

def update_claude_desktop(exe_path):
    appdata = os.environ.get("APPDATA")
    if not appdata: return
    
    config_file = os.path.join(appdata, "Claude", "claude_desktop_config.json")
    print(f"正在尝试配置 Claude Desktop: {config_file}")
    
    if not os.path.exists(os.path.dirname(config_file)):
        print("  [i] 未检测到 Claude Desktop 安装。")
        return

    mcp_entry = {
        "command": exe_path,
        "args": []
    }

    if not os.path.exists(config_file):
        config = {"mcpServers": {"everything-search": mcp_entry}}
    else:
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            if "mcpServers" not in config: config["mcpServers"] = {}
            config["mcpServers"]["everything-search"] = mcp_entry
        except Exception as e:
            print(f"  [!] 更新失败: {e}")
            return

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("  [v] 成功更新 Claude Desktop 配置。")

def main():
    # 获取当前执行目录
    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
    exe_path = os.path.join(script_dir, "server", "server.exe")
    
    print("=" * 50)
    print("  Everything Search MCP Multi-Client Installer")
    print("=" * 50)
    print(f"程序路径: {exe_path}")
    print()

    if not os.path.exists(exe_path):
        print(f"错误: 找不到 server.exe，请确保在 dist 目录下运行本程序。")
        input("\n按回车键退出...")
        return

    # 更新各个客户端
    update_opencode(exe_path)
    update_claude_desktop(exe_path)

    print("\n" + "-" * 50)
    print("对于 Cursor / Windsurf 用户:")
    print("请在设置中手动添加 MCP 服务器:")
    print(f"Name: everything-search")
    print(f"Command: {exe_path}")
    print("-" * 50)

    print("\n安装完成！请重启您的 AI 客户端。")
    print()
    input("按回车键退出...")

if __name__ == "__main__":
    main()
