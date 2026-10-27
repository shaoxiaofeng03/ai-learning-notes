# -*- coding: utf-8 -*-
"""
step6-async.py · async/await 并发基础（Java 开发者对照版）

覆盖：asyncio.run、await、gather（并发）、Semaphore 限流、wait_for 超时。
运行：python step6-async.py   （纯 Python，用 asyncio.sleep 模拟 IO，不需要 API Key）

Java → Python：
    CompletableFuture<T>     → asyncio.Task
    future.get()             → await task
    CompletableFuture.allOf  → asyncio.gather(...)
    ExecutorService(10)      → asyncio.Semaphore(10)
    Thread.sleep(1000)       → await asyncio.sleep(1)

三条铁律：
    1. async def 定义协程函数，直接调用它不会执行，返回协程对象，必须 await。
    2. await 只能在 async def 里面用。
    3. 程序入口用 asyncio.run(main())。
"""

import asyncio
import time


def section(title: str) -> None:
    print("\n" + "=" * 52)
    print(title)
    print("=" * 52)


# 模拟一次 IO 调用（真实场景换成 httpx.AsyncClient / AsyncOpenAI）
async def fetch(name: str) -> str:
    await asyncio.sleep(1)          # 模拟 1 秒网络等待
    return f"{name}-result"


# 串行版本（对照用）
async def run_serial() -> float:
    start = time.perf_counter()
    results = []
    for name in ["A", "B", "C"]:
        results.append(await fetch(name))   # 一个一个等
    print("串行结果：", results)
    return time.perf_counter() - start


# 并发版本：gather
async def run_concurrent() -> float:
    start = time.perf_counter()
    results = await asyncio.gather(fetch("A"), fetch("B"), fetch("C"))
    print("并发结果：", results)
    return time.perf_counter() - start


# 限流 + 超时 + 容错（生产级骨架）
async def run_batch() -> None:
    sem = asyncio.Semaphore(2)      # 最多 2 个同时进行

    async def bounded(name: str) -> str:
        async with sem:             # 拿到信号量才能进
            return await fetch(name)

    tasks = [bounded(f"q{i}") for i in range(5)]
    results = await asyncio.gather(*tasks, return_exceptions=True)  # 一个失败不影响其他

    for r in results:
        if isinstance(r, Exception):
            print("失败：", r)
        else:
            print("成功：", r)


async def main() -> None:
    section("单个 await")
    print(await fetch("A"))

    section("串行 vs 并发（gather）")
    t1 = await run_serial()
    t2 = await run_concurrent()
    print(f"串行耗时 {t1:.2f}s，并发耗时 {t2:.2f}s（3 个任务同时等）")

    section("Semaphore 限流")
    await run_batch()

    section("wait_for 超时（3.10 兼容写法）")
    async def slow() -> str:
        await asyncio.sleep(10)
        return "too slow"

    try:
        await asyncio.wait_for(slow(), timeout=1)
    except asyncio.TimeoutError:
        print("超时了 ✅")

    section("常见错误：忘了 await")
    coro = fetch("X")                # ❌ 没 await，只是拿到协程对象
    print(coro)                      # <coroutine object fetch at ...>


if __name__ == "__main__":
    asyncio.run(main())              # ← 入口，只调用一次
    print("\n✅ 本步完成。核心记住：IO 密集用 asyncio；并发用 gather；限流用 Semaphore。")
