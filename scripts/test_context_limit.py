"""
测试上下文长度限制功能
"""
import requests
import json


def test_get_model_info():
    """测试获取模型信息"""
    print("=" * 60)
    print("测试 1: 获取指定模型信息")
    print("=" * 60)

    models_to_test = [
        "openai-gpt-oss-120b",
        "qwen/qwen3-next-80b-a3b-instruct",
        "moonshotai/kimi-k2-instruct-0905",
        "llama3-8b-instruct"
    ]

    for model in models_to_test:
        url = f"http://localhost:8000/v1/models/{model}/info"
        try:
            response = requests.get(url)
            response.raise_for_status()
            info = response.json()

            print(f"\n模型: {info['id']}")
            print(f"  上下文长度: {info['context_length_formatted']}")
            if 'usable_limit_formatted' in info:
                print(f"  可用限制 (90%): {info['usable_limit_formatted']}")
            if 'note' in info:
                print(f"  备注: {info['note']}")

        except requests.exceptions.RequestException as e:
            print(f"\n❌ 获取模型 {model} 信息失败: {e}")


def test_context_within_limit():
    """测试正常对话（在上下文限制内）"""
    print("\n" + "=" * 60)
    print("测试 2: 正常对话（上下文在限制内）")
    print("=" * 60)

    url = "http://localhost:8000/v1/chat/completions"

    payload = {
        "model": "llama3-8b-instruct",
        "messages": [
            {"role": "system", "content": "你是一个有用的助手"},
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！有什么我可以帮助你的吗？"},
            {"role": "user", "content": "介绍一下Python"}
        ]
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        print("\n✅ 请求成功")
        print(f"模型: {result.get('model', 'N/A')}")
        print(f"响应: {result['choices'][0]['message']['content'][:100]}...")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"响应内容: {e.response.text}")


def test_context_exceeded():
    """测试超出上下文限制"""
    print("\n" + "=" * 60)
    print("测试 3: 超出上下文限制")
    print("=" * 60)

    url = "http://localhost:8000/v1/chat/completions"

    # 生成一个很长的对话历史
    messages = [{"role": "system", "content": "你是一个有用的助手"}]

    # 添加很多轮对话（每轮约 100 个 tokens）
    # llama3-8b-instruct 的上下文是 8000 tokens，生成 100 轮应该会超限
    for i in range(100):
        messages.append({
            "role": "user",
            "content": f"这是第 {i} 轮对话，请回答一些关于人工智能的问题。人工智能是什么？"
        })
        messages.append({
            "role": "assistant",
            "content": f"这是第 {i} 轮回答。人工智能（AI）是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。"
        })

    payload = {
        "model": "llama3-8b-instruct",
        "messages": messages
    }

    print(f"\n发送 {len(messages)} 条消息...")

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        print("\n⚠️  意外：请求成功了（可能是估算不准确）")
        print(f"模型: {result.get('model', 'N/A')}")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            error_detail = e.response.json()
            error_info = error_detail.get("detail", {}).get("error", {})

            print("\n✅ 正确捕获上下文超限错误")
            print(f"错误类型: {error_info.get('type', 'N/A')}")
            print(f"错误信息: {error_info.get('message', 'N/A')}")

            if 'param' in error_info:
                param = error_info['param']
                print(f"\n详细信息:")
                print(f"  模型: {param.get('model', 'N/A')}")
                print(f"  当前 tokens: {param.get('current_tokens', 'N/A'):,}")
                print(f"  上限 tokens: {param.get('limit', 'N/A'):,}")
                print(f"  使用率: {param.get('usage_percentage', 'N/A')}%")
        else:
            print(f"\n❌ 意外的 HTTP 错误: {e}")
            print(f"响应内容: {e.response.text}")

    except Exception as e:
        print(f"\n❌ 请求失败: {e}")


def test_get_all_models():
    """测试获取所有模型列表"""
    print("\n" + "=" * 60)
    print("测试 4: 获取所有模型列表（带上下文信息）")
    print("=" * 60)

    url = "http://localhost:8000/v1/models"

    try:
        response = requests.get(url)
        response.raise_for_status()

        result = response.json()
        models = result.get("data", [])

        print(f"\n共 {len(models)} 个模型:\n")

        # 按上下文长度排序
        sorted_models = sorted(
            models,
            key=lambda x: x.get("context_length", 0),
            reverse=True
        )

        for model in sorted_models:
            model_id = model.get("id", "N/A")
            context = model.get("context_length_formatted", "未知")
            print(f"  {model_id:<50} {context}")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ 获取模型列表失败: {e}")


if __name__ == "__main__":
    print("\n🧪 开始测试上下文限制功能\n")

    # 运行所有测试
    test_get_model_info()
    test_context_within_limit()
    test_context_exceeded()
    test_get_all_models()

    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)
