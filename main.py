import requests
import json
import base64
import re
import time

# 配置项：保持你的源不动
sub_url = [
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
    "https://raw.githubusercontent.com/ermaozi/get_falcao_near/main/v2ray",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/v2raypool/v2raypool/main/v2ray.txt",
    "https://raw.githubusercontent.com/zk4/free/main/v2ray"
]

def safe_b64decode(s):
    """安全解码，别再让缺失的等号搞崩你的程序了"""
    s = str(s).strip()
    missing_padding = len(s) % 4
    if missing_padding:
        s += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(s).decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[解码报错] 忽略该错误跳过: {e}")
        return ""

sub_link = []
for url in sub_url:
    try:
        rq = requests.get(url, timeout=10) # 加上超时，别死等
        if rq.status_code != 200:
            print(f"[GET Code {rq.status_code}] 下载失败: {url}")
            continue
        print(f"成功抓取订阅源: {url}")
        sub_link.append(safe_b64decode(rq.text))
    except Exception as e:
        print(f"[抓取异常] {url} - {e}")

country_count = {}
merged_link = []

print("\n开始解析并测试节点...")
for content in sub_link:
    for line in content.splitlines():
        line = line.strip()
        if not line: 
            continue
        
        # 兼容 vmess 并执行你的重命名逻辑
        if line.startswith("vmess://"):
            try:
                node_str = safe_b64decode(line[8:])
                if not node_str: 
                    continue
                node = json.loads(node_str)
                
                # 你非要查 IP，那就查，但给我加上延迟防封！
                rq = requests.get(f"http://ip-api.com/json/{node['add']}?lang=zh-CN", timeout=5)
                ip_info = rq.json()
                
                if ip_info.get('status') == 'success':
                    ip_country = ip_info.get('country', 'Unknown')
                    country_count[ip_country] = country_count.get(ip_country, 0) + 1
                    
                    # 容错处理 org 为空的情况
                    org_name = re.split(',| ', ip_info.get('org', 'Unknown'))[0]
                    newname = f"{ip_country} {country_count[ip_country]:02d} {org_name}"
                    
                    print(f"重命名节点: {node.get('ps', '未命名')} -> {newname}")
                    node['ps'] = newname
                
                # 重新打包回 vmess 格式
                bs = "vmess://" + base64.b64encode(json.dumps(node, ensure_ascii=False).encode("utf-8")).decode("utf-8")
                merged_link.append(bs)
                
                # 必须休眠，否则 API 会拉黑你
                time.sleep(1.5) 
                
            except Exception as e:
                print(f"[Vmess 解析/测试失败] {e}")
        
        # 兼容 vless / trojan / ss (直接收录，跳过 API 查询防止慢死)
        elif re.match(r'^(vless|trojan|ss)://', line):
            merged_link.append(line)
            print(f"直接收录非 Vmess 协议节点: {line[:30]}...")

# 写入文件
try:
    final_str = "\n".join(merged_link)
    res = base64.b64encode(final_str.encode("utf-8")).decode("utf-8")
    with open('node.txt', 'w', encoding='utf-8') as f:
        f.write(res)
    print(f"\n大功告成！整理合并成功，共收录 {len(merged_link)} 个节点。")
except Exception as e:
    print(f"写入文件失败: {e}")
