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

def main():
    # 获取当前执行目录
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    # 指向同一目录下的 server/server.exe
    exe_path = os.path.join(script_dir, "server", "server.exe").replace("\\", "\\\\")
    
    # 配置文件路径
    config_dir = os.path.expanduser("~/.config/opencode")
    config_file = os.path.join(config_dir, "opencode.json")
    
    print("=" * 40)
    print("  Everything Search MCP 安装程序")
    print("=" * 40)
    print()
    print(f"程序路径: {exe_path}")
    print(f"配置文件: {config_file}")
    print()
    
    # 定义 MCP 条目
    mcp_entry = {
        "everything-search": {
            "type": "local",
            "command": [exe_path],
            "enabled": True
        }
    }
    
    # 确保配置目录存在
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    # 追加模式更新配置
    if not os.path.exists(config_file):
        config = {
            "$schema": "https://opencode.ai/config.json",
            "mcp": mcp_entry
        }
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("已创建新的配置文件！")
    else:
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            if "mcp" not in config:
                config["mcp"] = {}
            
            # 追加或覆盖
            config["mcp"]["everything-search"] = mcp_entry["everything-search"]
            
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print("已成功添加到现有配置文件！")
        except json.JSONDecodeError:
            print("错误：配置文件不是有效的 JSON。")
            print("请手动添加以下内容：")
            print(json.dumps(mcp_entry, indent=2))
    
    print()
    print("安装完成！请重启 OpenCode 以加载配置。")
    print()
    input("按回车键退出...")

if __name__ == "__main__":
    main()
