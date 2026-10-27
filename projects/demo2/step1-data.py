# -*- coding: utf-8 -*-
"""
step1-data.py · 语法与数据结构（Java 开发者对照版）

覆盖：变量/真值、字符串、list/dict/set/tuple、切片、推导式、可变 vs 不可变。
运行：python step1-data.py   （纯 Python，不需要 API Key）

Java → Python 速查：
    List<String>       → list[str]
    Map<K, V>          → dict
    Set<T>             → set          （注意 {} 是空 dict，空 set 写 set()）
    stream().map(f)    → [f(x) for x in xs]
    null               → None         （判断用 is None）
    x.equals(y)        → x == y       （Python 的 == 就是值比较）
    x == y（引用比较）   → x is y
"""


def section(title: str) -> None:
    print("\n" + "=" * 52)
    print(title)
    print("=" * 52)


if __name__ == "__main__":
    # ---------- 1. 变量、类型、真值 ----------
    section("变量、类型、真值")
    name, age, price = "sky", 30, 19.9   # 一次赋多个
    nothing = None

    a, b = 1, 2
    a, b = b, a                          # 交换，无需临时变量
    print(f"交换后 a={a}, b={b}")

    print(type(age))                     # <class 'int'>
    print(isinstance(age, int))          # True  ← Java 的 instanceof

    print(type(name))
    print(isinstance(name, str))

    # 真值（falsy）：None / 0 / "" / [] / {} / set() 全部为 False
    print(bool(None), bool(0), bool(""), bool([]), bool({}))   # 全 False

    items: list = []
    if items:                            # ✅ Pythonic，别写 len(items) > 0
        print("有元素")
    else:
        print("空列表等价于 False")

    # ---------- 2. 字符串 ----------
    section("字符串与 f-string")
    name, score = "sky", 95.678
    print(f"{name} 得分 {score:.1f}")    # sky 得分 95.7
    print(f"{score:>10.2f}")             # 右对齐，宽 10
    print(f"{name=}")                    # name='sky'，调试神器

    # 拼接：用 join，绝不要在循环里 s += x（O(n²)）
    parts = [f"第{i}条" for i in range(3)]
    text = "\n".join(parts)
    print(text)

    s = "hello,world"
    print("ell" in s)                    # True  ← 用 in 判断包含
    print(s.split(","))                  # ['hello', 'world']
    print(",".join(["a", "b"]))          # 'a,b'

    # ---------- 3. list（≈ ArrayList） ----------
    section("list 操作与切片")
    nums = [3, 1, 2]
    nums.append(4)                       # 尾部加 → [3,1,2,4]
    nums.sort()                          # 原地排序
    print(nums)                          # [1, 2, 3, 4]

    xs = [0, 1, 2, 3, 4, 5]
    print(xs[0:2])                       # [0, 1]  左闭右开
    print(xs[:2])                        # [0, 1]
    print(xs[2:])                        # [2, 3, 4, 5]
    print(xs[-1])                        # 5        倒数第一个
    print(xs[-3:])                       # [3, 4, 5]
    print(xs[::-1])                      # [5,4,3,2,1,0] 反转

    # 解包
    first, *rest = [1, 2, 3]
    print(first, rest)                   # 1 [2, 3]

    # ---------- 4. dict（≈ HashMap，用得最多） ----------
    section("dict 操作")
    user = {"name": "sky", "age": 30}
    print(user["name"])                  # 取值，key 不存在会 KeyError
    print(user.get("email"))             # None，不报错 ← 优先用 get
    print(user.get("email", "无"))       # 给默认值
    print("name" in user)                # True

    for k, v in user.items():            # key + value，最常用
        print(f"  {k} -> {v}")

    # 合并（3.9+）
    merged = {**user, "city": "南京"}
    print(merged)

    # ---------- 5. set（≈ HashSet） + 保序去重 ----------
    section("set 与去重")
    s = {1, 2, 3}                        # 空集合必须写 set()，{} 是空 dict
    s.add(4)
    print(3 in s)                        # True, O(1)

    items = ["b", "a", "b", "c", "a"]
    print(list(dict.fromkeys(items)))    # ['b','a','c'] 保序去重 ← 记住这个
    print(list(set(items)))              # 不保序去重

    # ---------- 6. tuple（不可变，≈ 只读 record） ----------
    section("tuple")
    point = (1, 2)
    x, y = point                         # 解包
    print(x, y)

    def parse(t: str):                   # 返回多个值 = 返回一个 tuple
        a, b = t.split("-")
        return int(a), int(b)

    print(parse("1-2"))                  # (1, 2)

    # ---------- 7. 推导式（Python 最标志性的写法） ----------
    section("推导式")
    squares = [x * x for x in range(5)]          # [0,1,4,9,16]
    evens = [x for x in range(10) if x % 2 == 0]  # 过滤
    labels = [x if x > 0 else 0 for x in [-1, 3]]  # 变换（if-else 位置不同）
    d = {x: x * x for x in range(3)}              # 字典推导式
    print(squares)
    print(evens)
    print(labels)
    print(d)

    # ---------- 8. 可变 vs 不可变（最重要的坑） ----------
    section("可变 vs 不可变（引用陷阱）")
    a = [1, 2]
    b = a                              # ❌ 不是拷贝！b 和 a 是同一个对象
    b.append(3)
    print("a =", a)                    # [1, 2, 3]  ← a 也被改了！

    c = a.copy()                       # ✅ 浅拷贝（或 a[:] 或 list(a)）
    c.append(99)
    print("a =", a, "c =", c)          # a 不变

    print("\n✅ 本步完成。核心记住：b = a 是引用不是拷贝；空集合写 set()。")
