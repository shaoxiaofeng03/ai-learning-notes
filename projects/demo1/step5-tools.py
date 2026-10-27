# tools 示例：函数调用（function calling）完整闭环
# 运行前设置：export DEEPSEEK_API_KEY="你的key"
import json
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com",
)

# 1. 定义一个工具：查询天气
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的当前天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，如：南京"}
                },
                "required": ["city"],
            },
        },
    }
]

# 2. 告诉模型有哪些工具可用，让它决定是否调用
messages = [{"role": "user", "content": "南京今天天气怎么样？"}]

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,
    stream=False,
)

msg = response.choices[0].message

# 3. 判断模型是要调用工具，还是直接回答
if msg.tool_calls:
    tool_call = msg.tool_calls[0]
    print("模型想调用工具：", tool_call.function.name)
    args = json.loads(tool_call.function.arguments)
    print("调用参数：", args)

    # 4. 由你自己真正执行这个函数（这里用假数据模拟）
    weather = f"{args['city']}今天晴，25°C"

    # 5. 把工具结果作为 tool 消息传回，注意要先带上模型的 tool_calls 消息
    messages.append(msg)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": weather,
    })

    # 6. 再次请求，让模型基于工具结果给出最终回答
    final = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False,
    )
    print("模型最终回答：", final.choices[0].message.content)
else:
    print("模型直接回答：", msg.content)
