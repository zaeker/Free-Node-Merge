import requests
import base64
import re

# 配置：大幅增加高频更新的节点源
sub_url = [
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
    "https://raw.githubusercontent.com/ermaozi/get_falcao_near/main/v2ray",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/v2raypool/v2raypool/main/v2ray.txt",
    "https://raw.githubusercontent.com/zk4/free/main/v2ray",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/mftv/Free-Nodes/main/v2ray",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/manual/v2ray.txt"
]

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
print("开始极速抓取节点...")

for url in sub_url:
    try:
        # 缩短超时时间，遇到死链直接跳过，不浪费时间
        rq = requests.get(url, timeout=8)
        if rq.status_code != 200:
            continue
        
        content = rq.text.strip()
        # 尝试整体 Base64 解码，判断是普通文本还是 Base64 订阅
        decoded_content = safe_b64decode(content)
        if "vmess://" in decoded_content or "vless://" in decoded_content or "trojan://" in decoded_content:
            lines = decoded_content.splitlines()
        else:
            lines = content.splitlines()

        for line in lines:
            line = line.strip()
            # 只要是标准协议，无脑收录，绝不浪费时间去测 IP
            if re.match(r'^(vmess|vless|trojan|ss|ssr|hysteria|hy2)://', line):
                merged_link.append(line)
                
        print(f"成功抓取并解析: {url}")
    except Exception as e:
        print(f"抓取失败跳过: {url}")

# 极速去重（利用字典键的唯一性瞬间完成去重，并保持原有顺序）
unique_nodes = list(dict.fromkeys(merged_link))

# 重新打包成 Base64 并写入文件
try:
    final_str = "\n".join(unique_nodes)
    res = base64.b64encode(final_str.encode("utf-8")).decode("utf-8")
    with open('node.txt', 'w', encoding='utf-8') as f:
        f.write(res)
    print(f"\n大功告成！极速抓取并去重完成，共收录 {len(unique_nodes)} 个有效节点。")
except Exception as e:
    print(f"写入文件失败: {e}")
