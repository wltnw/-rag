"""快速 API 测试"""
import requests
import json

questions = [
    "水泵需要多久维护一次？",
    "大棚里温度多少度的时候需要启动风扇？",
    "那个温湿度传感器的电源电压范围是多少？",
    "DHT22 传感器的温度测量精度是多少？",
    "ERR_002 是什么故障？应该怎么处理？",
    "DHT22 和 SHT31 这两个传感器成本差多少？",
]

print("🚀 快速测试开始\n")

for i, q in enumerate(questions, 1):
    print(f"[{i}/6] 问题：{q}")
    try:
        r = requests.post("http://localhost:8000/ask", json={"question": q}, timeout=15)
        print(f"      状态码：{r.status_code}")
        print(f"      原始长度：{len(r.text)} 字符")
        
        if r.status_code == 200 and r.text:
            data = r.json()
            print(f"      意图：{data.get('intent')}")
            print(f"      答案前50字：{data.get('answer', '')[:50]}")
        else:
            print(f"      ❌ 空响应")
    except Exception as e:
        print(f"      ❌ 错误：{e}")
    print()

print("✅ 测试完成")
