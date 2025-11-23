"""
测试流式请求
"""
import requests
import json

def test_stream():
    """测试流式聊天补全"""
    url = "http://localhost:8000/v1/chat/completions"

    payload = {
        "messages": [
            {"role": "user", "content": "请用三句话介绍Python语言"}
        ],
        "stream": True
    }

    print("发送流式请求...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}\n")

    try:
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()

        print("接收流式响应:\n" + "="*60)

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]  # 去掉 'data: ' 前缀
                    if data == '[DONE]':
                        print("\n" + "="*60)
                        print("流式响应完成")
                        break
                    try:
                        chunk = json.loads(data)
                        # 提取内容
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                print(content, end='', flush=True)
                    except json.JSONDecodeError as e:
                        print(f"\n[警告] JSON解析错误: {e}")
                        print(f"原始数据: {data}")

        print("\n\n✅ 流式请求测试成功!")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"状态码: {e.response.status_code}")
            print(f"响应内容: {e.response.text}")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")

def test_non_stream():
    """测试非流式聊天补全（对比）"""
    url = "http://localhost:8000/v1/chat/completions"

    payload = {
        "messages": [
            {"role": "user", "content": "请用三句话介绍Python语言"}
        ],
        "stream": False  # 或不传
    }

    print("\n" + "="*60)
    print("发送非流式请求（对比）...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}\n")

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        content = result['choices'][0]['message']['content']

        print("接收非流式响应:\n" + "="*60)
        print(content)
        print("="*60)
        print("\n✅ 非流式请求测试成功!")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"状态码: {e.response.status_code}")
            print(f"响应内容: {e.response.text}")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")

if __name__ == "__main__":
    # 测试流式请求
    test_stream()

    # 测试非流式请求（对比）
    test_non_stream()
