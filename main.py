import requests
import base64
import re
import socket
import json
import concurrent.futures

# 伪装请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

# TG 实时频道源 (带 /s/ 后缀可绕过登录)
tg_channels = [
    "https://t.me/s/v2ray_share",
    "https://t.me/s/v2raypro",
    "https://t.me/s/V2List"
]

# 保底的静态超大源
static_urls = [
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub1.txt"
]

def safe_b64decode(s):
    """安全解码 Base64"""
    s = str(s).strip()
    s += '=' * ((4 - len(s) % 4) % 4)
    try:
        return base64.b64decode(s).decode("utf-8", errors="ignore")
    except:
        return ""

def check_node(node):
    """核心存活检测：只敲门不进屋，1.5秒定生死"""
    try:
        ip, port = "", 0
        # 解析 Vmess
        if node.lower().startswith("vmess://"):
            b64_str = node[8:]
            b64_str += "=" * ((4 - len(b64_str) % 4) % 4)
            info = json.loads(base64.b64decode(b64_str).decode('utf-8', 'ignore'))
            ip, port = info.get("add"), info.get("port")
        # 解析 Vless / Trojan / SS 等
        else:
            match = re.search(r'@([^:]+):(\d+)', node)
            if match:
                ip, port = match.groups()
        
        # TCP 并发测活
        if ip and port:
            socket.create_connection((ip, int(port)), timeout=1.5).close()
            return node
    except Exception:
        pass
    return None

def main():
    merged_link = []

    print("第一阶段：抓取 TG 实时热乎节点...")
    for url in tg_channels:
        try:
            rq = requests.get(url, headers=HEADERS, timeout=10)
            nodes = re.findall(r'(?:vmess|vless|trojan|ss|ssr|hysteria2?)://[^\s\'"<br>]+', rq.text, re.IGNORECASE)
            merged_link.extend(nodes)
            print(f" -> 成功从 {url} 提取 {len(nodes)} 个节点")
        except:
            pass

    print("\n第二阶段：抓取 GitHub 基础大本营...")
    for url in static_urls:
        try:
            rq = requests.get(url, headers=HEADERS, timeout=10)
            content = safe_b64decode(rq.text) if "://" not in rq.text else rq.text
            nodes = re.findall(r'(?:vmess|vless|trojan|ss|ssr|hysteria2?)://[^\s\'"<br>]+', content, re.IGNORECASE)
            merged_link.extend(nodes)
            print(f" -> 成功从 {url} 提取 {len(nodes)} 个节点")
        except:
            pass

    # 极速去重
    unique_nodes = list(dict.fromkeys(merged_link))
    print(f"\n第三阶段：多线程死神模式启动！共 {len(unique_nodes)} 个节点准备受死...")

    alive_nodes = []
    # 开启 50 个并发线程，速度飙升 50 倍
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(check_node, unique_nodes)
        for res in results:
            if res:
                alive_nodes.append(res)

    print(f"\n======================================")
    print(f"大功告成！并发淘汰后，斩获 {len(alive_nodes)} 个高优可用节点。")
    print(f"======================================")

    # 重新打包成 Base64 并写入文件
    if alive_nodes:
        final_str = "\n".join(alive_nodes)
        res = base64.b64encode(final_str.encode("utf-8")).decode("utf-8")
        try:
            with open('node.txt', 'w', encoding='utf-8') as f:
                f.write(res)
        except Exception as e:
            print(f"写入文件失败: {e}")

if __name__ == '__main__':
    main()
