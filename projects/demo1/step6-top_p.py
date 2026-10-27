# top_p 示例：同样的 prompt，不同 top_p 的差异
# 运行前设置：export DEEPSEEK_API_KEY="你的key"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com",
)

prompt = "给一家奶茶店起 3 个名字，每个名字 2-4 个字"

# 注意：top_p 和 temperature 二选一调，不要同时改
for p in [0.1, 0.5, 1.0]:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        top_p=p,
        stream=False,
    )
    print(f"--- top_p={p} ---")
    print(response.choices[0].message.content)
    print()
