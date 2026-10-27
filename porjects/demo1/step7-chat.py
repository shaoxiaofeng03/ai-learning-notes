# 多轮对话聊天机器人：维护 messages 历史，支持多轮上下文
# 运行前设置：export DEEPSEEK_API_KEY="你的key"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com",
)

# 系统提示：设定机器人的角色和语气
SYSTEM_PROMPT = "你是一个乐于助人的助手，回答简洁、友好。"

# 对话历史，最初只包含系统提示。多轮上下文的秘诀就是：
# 每次请求都把完整的 messages 历史传回给模型（模型本身无状态）
messages = [{"role": "system", "content": SYSTEM_PROMPT}]

print("命令行聊天机器人已启动。")
print("命令：/exit 退出，/clear 清空上下文")
print("-" * 40)

while True:
    try:
        user_input = input("你: ").strip()
    except (EOFError, KeyboardInterrupt):  # Ctrl+D / Ctrl+C 退出
        print("\n再见！")
        break

    if not user_input:
        continue

    if user_input in ("/exit", "exit", "quit"):
        print("再见！")
        break

    if user_input == "/clear":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        print("上下文已清空。")
        continue

    # 把用户输入加入历史
    messages.append({"role": "user", "content": user_input})

    # 调用模型，流式输出（打字机效果）
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=True,
    )

    print("AI: ", end="", flush=True)
    answer = ""
    for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            print(delta.content, end="", flush=True)
            answer += delta.content
    print()

    # 把 AI 回复也加入历史，下一轮才能"记得"刚才说了什么
    messages.append({"role": "assistant", "content": answer})
