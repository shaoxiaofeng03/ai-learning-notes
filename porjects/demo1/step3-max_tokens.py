# max_tokens 示例：限制输出长度，观察回答被截断
# 运行前设置：export DEEPSEEK_API_KEY="你的key"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com",
)

prompt = "详细介绍一下机器学习的三个主要分支"

for max_tokens in [10, 50, 200]:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        stream=False,
    )
    # finish_reason="length" 表示因为达到长度上限被截断
    finish = response.choices[0].finish_reason
    print(f"--- max_tokens={max_tokens} (finish_reason={finish}) ---")
    print(response.choices[0].message.content)
    print()
