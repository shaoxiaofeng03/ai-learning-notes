# -*- coding: utf-8 -*-
"""
step5-pydantic.py · pydantic：运行时校验（重点）

覆盖：BaseModel、Field 约束、model_validate_json、ValidationError、field_validator。
运行：python step5-pydantic.py   （纯 Python，不需要 API Key）

为什么需要它（Java 对照）：
    typing 类型注解 → 只给 IDE 提示，运行时完全不校验
    pydantic        → 运行时真的校验/转换，≈ Java 的 @Valid + Bean Validation

v2 关键 API（认准 v2，网上很多是 v1）：
    model_dump()         → 转 dict        （v1 是 .dict()）
    model_validate_json() → 解析+校验 JSON  （v1 是 .parse_obj()）
    model_json_schema()   → 生成 JSON Schema（给 LLM 用）
"""

from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator


def section(title: str) -> None:
    print("\n" + "=" * 52)
    print(title)
    print("=" * 52)


# ---------- 1. 基本模型 + Field 约束 ----------
class Ticket(BaseModel):
    category: Literal["refund", "logistics", "other"]          # 只能取这几个值
    priority: int = Field(ge=1, le=5, description="1 最低，5 最高")
    summary: str = Field(min_length=1, max_length=200)
    order_id: str | None = None                                  # 可选字段


# ---------- 2. 自定义校验器 ----------
class Order(BaseModel):
    order_id: str
    amount: float

    @field_validator("order_id")
    @classmethod
    def check_prefix(cls, v: str) -> str:
        if not v.startswith("ORD-"):
            raise ValueError("order_id 必须以 ORD- 开头")
        return v

    @field_validator("amount")
    @classmethod
    def check_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("金额不能为负")
        return v


if __name__ == "__main__":
    section("typing 不校验，pydantic 校验")
    def f(x: int) -> int:
        return x
    print("typing 注解 f('abc') 不报错：", f("abc"))

    try:
        Ticket(category="refund", priority=99, summary="要退货")
    except ValidationError:
        print("pydantic 校验：priority=99 超出 ge=1/le=5，抛 ValidationError ✅")

    t = Ticket(category="refund", priority=3, summary="要退货")
    print("自动宽松转换：", Ticket(category="refund", priority="3", summary="x"))
    # priority="3"（字符串）被自动转成 int 3

    section("model_dump / model_dump_json / schema")
    t = Ticket(category="refund", priority=3, summary="要退货", order_id=None)
    print(t.model_dump())              # {'category': 'refund', 'priority': 3, ...}
    print(t.model_dump_json())         # JSON 字符串
    print("JSON Schema（可喂给 LLM）：")
    print(Ticket.model_json_schema())

    section("从 JSON 字符串解析（LLM 场景核心）")
    raw = '{"category":"refund","priority":3,"summary":"要退货"}'
    parsed = Ticket.model_validate_json(raw)     # 解析 + 校验一次完成
    print("解析成功：", parsed)

    bad = '{"category":"wrong","priority":9}'
    try:
        Ticket.model_validate_json(bad)
    except ValidationError as e:
        # e.errors() 给出结构化错误列表，可回灌给 LLM
        for err in e.errors():
            print("  错误字段：", err["loc"], "原因：", err["msg"])

    section("自定义校验器")
    try:
        Order(order_id="ABC-1", amount=10)
    except ValidationError as e:
        print("校验失败：", e.errors()[0]["msg"])

    ok = Order(order_id="ORD-1", amount=10)
    print("通过：", ok)

    print("\n✅ 本步完成。核心记住：typing 管写代码提示，pydantic 管运行时真校验。")
