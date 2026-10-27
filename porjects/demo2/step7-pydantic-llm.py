# -*- coding: utf-8 -*-
"""
step7-pydantic-llm.py · 结构化输出实战（需要 API Key）

把「pydantic 校验 + LLM 输出」串成完整闭环：校验 → 截断检查 → 错误回灌 → 重试。
这是 W3「结构化输出」的核心，也是 Agent 的地基。

运行前设置（二选一）：
    export DEEPSEEK_API_KEY="sk-xxx"
    或复制 .env.example 为 .env 并填入你的 key（本脚本会自动 load_dotenv）

运行：python step7-pydantic-llm.py
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

load_dotenv()  # 读项目根目录 .env（若存在）


# ---------- 1. 定义目标结构 ----------
class Ticket(BaseModel):
    """客服工单抽取结果。description 会写进 JSON Schema，LLM 能读懂。"""
    category: str = Field(description="工单类型：退款/物流/其他")
    priority: int = Field(ge=1, le=5, description="紧急程度，1 最低 5 最高")
    summary: str = Field(description="一句话概括用户诉求")


# ---------- 2. 抽取 + 校验 + 错误回灌 + 重试 ----------
def extract(client: OpenAI, text: str, max_retries: int = 2) -> Ticket:
    schema = json.dumps(Ticket.model_json_schema(), ensure_ascii=False)
    messages = [
        {"role": "system", "content": f"把用户输入抽取成 JSON，严格符合这个 schema：{schema}"},
        {"role": "user", "content": text},
    ]

    last_err = "未知错误"
    for attempt in range(max_retries + 1):
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            response_format={"type": "json_object"},   # 强制 JSON 输出
            temperature=0,
            max_tokens=500,
        )
        choice = resp.choices[0]

        # ① 先看是不是被截断
        if choice.finish_reason == "length":
            last_err = "输出被截断"
            continue

        raw = choice.message.content or ""

        # ② 解析 + 校验
        try:
            return Ticket.model_validate_json(raw)
        except (ValidationError, json.JSONDecodeError) as e:
            last_err = str(e)
            # ③ 把错误回灌给模型，让它修正（关键技巧）
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": f"上面的输出不合法：{e}。请只输出修正后的 JSON，不要解释。",
            })

    raise RuntimeError(f"抽取失败，重试 {max_retries} 次仍不合法：{last_err}")


def main() -> None:
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        print("❌ 未检测到 DEEPSEEK_API_KEY。")
        print("   请先运行：export DEEPSEEK_API_KEY='sk-xxx'")
        print("   或：cp .env.example .env 并填入你的 key。")
        raise SystemExit(1)

    client = OpenAI(api_key=key, base_url="https://api.deepseek.com")

    text = "我昨天买的手机壳还没发货，赶紧给我退款！"
    ticket = extract(client, text)
    print("抽取结果：")
    print(json.dumps(ticket.model_dump(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
