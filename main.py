import requests
import base64
import re

# 配置：替换为目前全网最大的几个白嫖聚合源
sub_url = [
    "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub1.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub2.txt",
    "https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list.txt",
    "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
    "https://raw.githubusercontent.com/ermaozi/get_falcao_near/main/v2ray",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/manual/v2ray.txt"
]

# 增加请求头伪装，防止被源站的防爬墙直接拦截
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

def safe_b64decode(s):
    """安全解码，补齐缺失的 '='"""
    s = str(s).strip()
    missing_padding = len(s) % 4
    if missing_padding:
        s += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(s).decode("utf-8", errors="ignore")
    except:
        return ""

merged_link = []
print("开始极速抓取超级节点源...")

for url in sub_url:
    try:
        # 加上 headers 伪装
        rq = requests.get(url, headers=HEADERS, timeout=10)
        if rq.status_code != 200:
            print(f"请求失败 (状态码 {rq.status_code}): {url}")
            continue
        
        content = rq.text.strip()
        decoded_content = safe_b64decode(content)
        
        # 智能判断：如果是 base64 解码后包含节点标识，就用解码后的；否则用原始文本
        if any(protocol in decoded_content for protocol in ["vmess://", "vless://", "trojan://", "ss://"]):
            lines = decoded_content.splitlines()
        else:
            lines = content.splitlines()

        count = 0
        for line in lines:
            line = line.strip()
            # 放宽正则匹配，兼容更多协议格式
            if re.match(r'^(vmess|vless|trojan|ss|ssr|hysteria|hy2|tuic)://', line, re.IGNORECASE):
                merged_link.append(line)
                count += 1
                
        print(f"成功抓取 {count} 个节点来自: {url}")
    except Exception as e:
        print(f"抓取异常跳过: {url} | 错误: {e}")

# 极速去重
unique_nodes = list(dict.fromkeys(merged_link))

# 重新打包成 Base64 并写入文件
try:
    final_str = "\n".join(unique_nodes)
    res = base64.b64encode(final_str.encode("utf-8")).decode("utf-8")
    with open('node.txt', 'w', encoding='utf-8') as f:
        f.write(res)
    print(f"\n======================================")
    print(f"大功告成！共合并去重得到 {len(unique_nodes)} 个有效节点。")
    print(f"======================================")
except Exception as e:
    print(f"写入文件失败: {e}")
