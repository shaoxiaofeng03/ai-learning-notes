# -*- coding: utf-8 -*-
"""
step3-class.py · 类、dataclass 与 typing（Java 开发者对照版）

覆盖：普通类、@dataclass（≈ Java record）、field(default_factory)、typing 类型注解。
运行：python step3-class.py   （纯 Python，不需要 API Key）

Java → Python：
    record        → @dataclass
    this          → self（必须显式写在参数里）
    new Order()   → Order()（调用不带 new）
    toString()    → __str__ / __repr__
    equals()      → __eq__
    List<String>  → list[str]
    Optional<T>   → T | None
"""

from dataclasses import dataclass, field
from typing import Any, Literal


def section(title: str) -> None:
    print("\n" + "=" * 52)
    print(title)
    print("=" * 52)


# ---------- 1. 普通类 ----------
class Order:
    currency = "CNY"                 # 类属性（所有实例共享）

    def __init__(self, order_id: str, amount: float):
        self.order_id = order_id     # 实例属性
        self.amount = amount

    def total(self, tax_rate: float = 0.0) -> float:
        return self.amount * (1 + tax_rate)

    def __str__(self) -> str:        # ≈ toString()
        return f"Order({self.order_id}, {self.amount})"

    def __repr__(self) -> str:       # 调试显示（比 __str__ 更精确）
        return f"Order(order_id={self.order_id!r}, amount={self.amount!r})"


# ---------- 2. @dataclass（写数据类首选，≈ record） ----------
@dataclass
class Message:
    role: str
    content: str
    tokens: int = 0
    tags: list[str] = field(default_factory=list)   # 可变默认值必须这样写！


@dataclass(frozen=True)              # 不可变（≈ record），创建后不能改
class Point:
    x: int
    y: int


# ---------- 3. typing 类型注解 ----------
def process(items: list[str], limit: int = 10) -> dict[str, Any]:
    """类型注解只给 IDE/静态检查看，运行时完全不生效。"""
    return {"count": len(items), "limit": limit}


if __name__ == "__main__":
    section("普通类")
    o = Order("ORD-001", 99.5)
    print(o.total(0.1))              # 109.45
    print(o)                         # Order(ORD-001, 99.5)  ← 走 __str__
    print(repr(o))                   # Order(order_id='ORD-001', amount=99.5)
    print(o.currency)                # CNY

    section("@dataclass")
    msgs = [
        Message("system", "你是助手"),
        Message("user", "你好"),
    ]
    print(msgs[0].role)              # system
    print(msgs[0])                   # 自动生成 __repr__

    # 每个实例都有自己的 list（field(default_factory) 的作用）
    m1 = Message("user", "hi")
    m2 = Message("user", "hi")
    m1.tags.append("a")
    print("m1.tags =", m1.tags, " m2.tags =", m2.tags)   # m2 不受影响

    p = Point(1, 2)
    print(p)
    # p.x = 3                         # ❌ 会抛 FrozenInstanceError

    section("typing 类型注解")
    print(process(["a", "b"]))       # {'count': 2, 'limit': 10}

    # 关键认知：typing 运行时完全不生效
    def add(a: int, b: int) -> int:
        return a + b

    print(add("1", "2"))             # 返回 "12"，不报错！

    # Literal 约束可选值（给 IDE 提示）
    def set_mode(mode: Literal["fast", "safe"]) -> str:
        return f"mode={mode}"

    print(set_mode("fast"))

    print("\n✅ 本步完成。核心记住：数据类用 @dataclass；可变默认值用 field(default_factory=...)。")
