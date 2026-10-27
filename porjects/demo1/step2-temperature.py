# temperature 示例：同样的 prompt，不同 temperature 的差异
# 运行前设置：export DEEPSEEK_API_KEY="你的key"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com",
)

prompt = "给一家奶茶店起 3 个名字，每个名字 2-4 个字"

for temp in [0.0, 1.0, 1.5]:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=temp,
        stream=False,
    )
    print(f"--- temperature={temp} ---")
    print(response.choices[0].message.content)
    print()
