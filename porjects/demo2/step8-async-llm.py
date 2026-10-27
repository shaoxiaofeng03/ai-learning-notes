# -*- coding: utf-8 -*-
"""
step8-async-llm.py · 并发调用 LLM（需要 API Key）

把 step6 的 asyncio 用到真实场景：AsyncOpenAI + 限流 + 超时 + 重试 + 指数退避。
跑完观察「串行 vs 并发」的耗时差——这就是评测/批量脚本的骨架。

运行前设置：
    export DEEPSEEK_API_KEY="sk-xxx"    或   复制 .env.example 为 .env
运行：python step8-async-llm.py
"""

import asyncio
import os
import time

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()


async def ask(client: AsyncOpenAI, question: str, sem: asyncio.Semaphore) -> dict:
    async with sem:                          # 限流：最多 concurrency 个同时
        for attempt in range(3):             # 重试
            try:
                resp = await asyncio.wait_for(     # 超时
                    client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": question}],
                        temperature=0,
                        max_tokens=200,
                    ),
                    timeout=30,
                )
                return {"q": question, "a": resp.choices[0].message.content}
            except asyncio.TimeoutError:
                if attempt == 2:
                    return {"q": question, "error": "超时"}
                await asyncio.sleep(2 ** attempt)   # 指数退避 1s, 2s
            except Exception as e:
                if attempt == 2:
                    return {"q": question, "error": str(e)}
                await asyncio.sleep(2 ** attempt)


async def batch(client: AsyncOpenAI, questions: list[str], concurrency: int = 5) -> list[dict]:
    sem = asyncio.Semaphore(concurrency)
    tasks = [ask(client, q, sem) for q in questions]
    return await asyncio.gather(*tasks)


async def main() -> None:
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        print("❌ 未检测到 DEEPSEEK_API_KEY，请先 export 或配置 .env")
        raise SystemExit(1)

    client = AsyncOpenAI(api_key=key, base_url="https://api.deepseek.com")

    questions = [
        "用一句话解释什么是 token",
        "用一句话解释什么是 RAG",
        "用一句话解释什么是 Agent",
    ]

    # 串行（对照）
    start = time.perf_counter()
    serial = [await ask(client, q, asyncio.Semaphore(1)) for q in questions]
    t_serial = time.perf_counter() - start

    # 并发
    start = time.perf_counter()
    results = await batch(client, questions, concurrency=5)
    t_concurrent = time.perf_counter() - start

    for r in results:
        print(f"Q: {r['q']}\nA: {r.get('a', r.get('error'))}\n")

    print(f"串行耗时 {t_serial:.2f}s，并发耗时 {t_concurrent:.2f}s")

    await client.close()                     # 记得关闭异步客户端


if __name__ == "__main__":
    asyncio.run(main())
