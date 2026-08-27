import requests
import base64
import re
import socket
import json
import concurrent.futures

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

# TG 实时频道源
tg_channels = [
    "https://t.me/s/v2ray_share",
    "https://t.me/s/v2raypro",
    "https://t.me/s/V2List"
]

# 把海量大本营源全加回来
static_urls = [
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub1.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub2.txt",
    "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
]

def safe_b64decode(s):
    s = str(s).strip()
    s += '=' * ((4 - len(s) % 4) % 4)
    try:
        return base64.b64decode(s).decode("utf-8", errors="ignore")
    except:
        return ""

def check_node(node):
    """放宽测试条件：超时时间提升到 3.5 秒"""
    try:
        ip, port = "", 0
        if node.lower().startswith("vmess://"):
            b64_str = node[8:]
            b64_str += "=" * ((4 - len(b64_str) % 4) % 4)
            info = json.loads(base64.b64decode(b64_str).decode('utf-8', 'ignore'))
            ip, port = info.get("add"), info.get("port")
        else:
            match = re.search(r'@([^:]+):(\d+)', node)
            if match:
                ip, port = match.groups()
        
        if ip and port:
            # 宽容模式：3.5秒超时
            socket.create_connection((ip, int(port)), timeout=3.5).close()
            return node
    except Exception:
        pass
    return None

def save_to_file(nodes, filename):
    """保存为 Base64 格式的文件"""
    if not nodes:
        return
    final_str = "\n".join(nodes)
    res = base64.b64encode(final_str.encode("utf-8")).decode("utf-8")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(res)
    except Exception as e:
        print(f"写入 {filename} 失败: {e}")

def main():
    merged_link = []

    print("抓取 TG 实时节点...")
    for url in tg_channels:
        try:
            rq = requests.get(url, headers=HEADERS, timeout=10)
            nodes = re.findall(r'(?:vmess|vless|trojan|ss|ssr|hysteria2?)://[^\s\'"<br>]+', rq.text, re.IGNORECASE)
            merged_link.extend(nodes)
        except:
            pass

    print("抓取 GitHub 基础大本营...")
    for url in static_urls:
        try:
            rq = requests.get(url, headers=HEADERS, timeout=10)
            content = safe_b64decode(rq.text) if "://" not in rq.text else rq.text
            # 兼容更多格式的正则
            nodes = re.findall(r'(?:vmess|vless|trojan|ss|ssr|hysteria2?)://[^\s\'"<br>]+', content, re.IGNORECASE)
            merged_link.extend(nodes)
        except:
            pass

    unique_nodes = list(dict.fromkeys(merged_link))
    print(f"抓取完成，共获得 {len(unique_nodes)} 个初始节点。")
    
    # 存一份没过滤的底包
    save_to_file(unique_nodes, 'node_all.txt')
    print("已生成全量保底文件：node_all.txt")

    print("开启多线程测活 (超时限制: 3.5秒)...")
    alive_nodes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(check_node, unique_nodes)
        for res in results:
            if res:
                alive_nodes.append(res)

    # 存一份过滤后的高优包
    save_to_file(alive_nodes, 'node.txt')
    print(f"\n测活完毕！得到 {len(alive_nodes)} 个连通节点，已生成：node.txt")

if __name__ == '__main__':
    main()
