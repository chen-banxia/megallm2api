#!/usr/bin/env python3
"""
API 测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """测试健康检查"""
    print("测试健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()


def test_root():
    """测试根路径"""
    print("测试根路径...")
    response = requests.get(f"{BASE_URL}/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()


def test_chat_completion():
    """测试聊天补全"""
    print("测试聊天补全...")

    payload = {
        "model": "openai-gpt-oss-120b",
        "messages": [
            {"role": "user", "content": "你好，请用一句话介绍自己"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }

    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        json=payload
    )

    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"模型: {result.get('model')}")
        print(f"回复: {result['choices'][0]['message']['content']}")
        print(f"用量: {result.get('usage')}")
    else:
        print(f"错误: {response.text}")

    print()


def test_models():
    """测试模型列表"""
    print("测试模型列表...")
    response = requests.get(f"{BASE_URL}/v1/models")
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"可用模型: {len(result.get('data', []))} 个")
        for model in result.get('data', []):
            print(f"  - {model['id']}")
    else:
        print(f"错误: {response.text}")

    print()


if __name__ == "__main__":
    print("=" * 50)
    print("MegaLLM Proxy API 测试")
    print("=" * 50)
    print()

    try:
        test_root()
        test_health()
        test_models()
        test_chat_completion()

        print("=" * 50)
        print("所有测试完成！")
        print("=" * 50)

    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务")
        print("请确保服务已启动: python main.py")
    except Exception as e:
        print(f"错误: {e}")
