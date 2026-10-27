# -*- coding: utf-8 -*-
"""
step9-httpx-stream.py · httpx 请求 + 手写 SSE 流式（需要 API Key）

手写一次流式，你就知道 SDK 的 stream=True 到底在帮你做什么。
面试问「流式怎么实现」，你能答出 SSE 帧格式，而不是「调个参数」。

SSE 帧格式（Server-Sent Events）：
    data: {"choices":[{"delta":{"content":"你"}}]}\n\n
    data: {"choices":[{"delta":{"content":"好"}}]}\n\n
    ...
    data: [DONE]\n\n

运行前设置：
    export DEEPSEEK_API_KEY="sk-xxx"    或   复制 .env.example 为 .env
运行：python step9-httpx-stream.py
"""

import json
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.deepseek.com/chat/completions"


def main() -> None:
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        print("❌ 未检测到 DEEPSEEK_API_KEY，请先 export 或配置 .env")
        raise SystemExit(1)

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "用 30 字介绍什么是大语言模型"}],
        "stream": True,
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    # ---------- 1. 同步请求（非流式，先看基本用法） ----------
    with httpx.Client(timeout=30) as client:
        r = client.post(BASE_URL, headers=headers, json={**payload, "stream": False})
        r.raise_for_status()             # ← 4xx/5xx 抛异常，别忘了
        data = r.json()
        print("同步回答：", data["choices"][0]["message"]["content"], "\n")

    # ---------- 2. 手写流式解析（SSE） ----------
    print("流式回答：", end="", flush=True)
    with httpx.Client(timeout=60) as client:
        with client.stream("POST", BASE_URL, headers=headers, json=payload) as resp:
            for line in resp.iter_lines():
                if not line.startswith("data: "):
                    continue
                payload_str = line[len("data: "):]   # 去掉 "data: " 前缀
                if payload_str == "[DONE]":          # 结束标记
                    break
                chunk = json.loads(payload_str)
                delta = chunk["choices"][0]["delta"].get("content")
                if delta:
                    print(delta, end="", flush=True)  # 边生成边打印
    print()


if __name__ == "__main__":
    main()
