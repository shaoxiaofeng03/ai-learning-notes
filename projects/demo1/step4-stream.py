# stream 示例：流式输出，边生成边打印（打字机效果）
# 运行前设置：export DEEPSEEK_API_KEY="你的key"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com",
)

# stream=True 时，返回的是一个迭代器，需要循环读取
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "用 50 字介绍什么是大语言模型"}],
    stream=True,
)

print("回答：", end="", flush=True)
for chunk in response:
    # 每个 chunk 只包含一小段文本
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)
print()
