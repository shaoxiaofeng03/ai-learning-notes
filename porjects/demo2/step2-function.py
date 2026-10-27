# -*- coding: utf-8 -*-
"""
step2-function.py · 函数（Java 开发者对照版）

覆盖：基本形态、可变默认参数坑、*args/**kwargs、lambda 高阶函数、闭包坑、main 入口。
运行：python step2-function.py   （纯 Python，不需要 API Key）

Java → Python：
    方法 → def 函数
    Object... args → *args（tuple）
    （无对应）      → **kwargs（dict）
    Function<T,R>   → lambda / 函数是一等公民
    public static void main → if __name__ == "__main__":
"""


def section(title: str) -> None:
    print("\n" + "=" * 52)
    print(title)
    print("=" * 52)


# ---------- 1. 基本形态 ----------
def greet(name: str, greeting: str = "你好") -> str:
    """返回问候语。这是 docstring，写在函数体第一行。"""
    return f"{greeting}，{name}"


# ---------- 2. 可变默认参数：致命坑 ----------
# ❌ 错误：默认 list 在函数定义时只创建一次，之后所有调用共享同一个对象
def add_item_bad(item, bucket=[]):
    bucket.append(item)
    return bucket


# ✅ 正确：默认值用 None，函数内部创建
def add_item(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket


# ---------- 3. *args / **kwargs ----------
def log(level: str, *args, **kwargs):
    """*args 收集任意位置参数为 tuple；**kwargs 收集任意关键字参数为 dict。"""
    print(level, "args =", args, "kwargs =", kwargs)


# ---------- 4. 函数是一等公民 + lambda ----------
def apply(fn, value):
    return fn(value)


if __name__ == "__main__":
    section("基本形态")
    print(greet("sky"))                          # 位置参数
    print(greet(name="sky", greeting="hi"))      # 关键字参数（Java 没有）
    print(greet(greeting="hi", name="sky"))      # 顺序随意

    section("可变默认参数坑（面试常问）")
    print(add_item_bad(1))                       # [1]
    print(add_item_bad(2))                       # [1, 2]  ← 你以为会是 [2]！
    print(add_item(1))                           # [1]
    print(add_item(2))                           # [2]  ← 正确

    section("*args / **kwargs")
    log("INFO", "a", "b", user="sky")            # INFO args=('a','b') kwargs={'user':'sky'}

    # 反向使用：把容器展开成参数（LLM 代码里到处都是）
    def f(a, b, c):
        return a + b + c

    nums = [1, 2, 3]
    print(f(*nums))                              # 等价 f(1, 2, 3) → 6
    d = {"a": 1, "b": 2, "c": 3}
    print(f(**d))                                # 等价 f(a=1, b=2, c=3) → 6

    section("lambda 与高阶函数")
    print(apply(str.upper, "abc"))               # 'ABC'
    print(apply(lambda x: x * 2, 3))             # 6

    users = [{"name": "b", "age": 30}, {"name": "a", "age": 30}]
    users.sort(key=lambda u: (u["age"], u["name"]))   # 多字段排序，类似 Comparator
    print(users)

    nums = [3, 1, 2]
    print(sorted(nums, key=lambda x: -x))        # [3, 2, 1]
    print(list(map(str, nums)))                  # ['3', '1', '2']
    print(any(x > 2 for x in nums))              # True
    print(all(x > 0 for x in nums))              # True

    section("闭包坑（晚绑定）")
    funcs = [lambda: i for i in range(3)]
    print([f() for f in funcs])                  # [2, 2, 2]  ← 不是 [0, 1, 2]！

    funcs = [lambda i=i: i for i in range(3)]    # ✅ 用默认参数把当前值绑死
    print([f() for f in funcs])                  # [0, 1, 2]

    print("\n✅ 本步完成。核心记住：可变默认参数用 None；*args/**kwargs 会展开。")
