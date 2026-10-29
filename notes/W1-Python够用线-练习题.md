# W1 · Python 够用线 · 练习题（Day 2–3）

> 配套教程：[W1-Python够用线教程.md](./W1-Python够用线教程.md)
> 参考答案：[W1-Python够用线-练习题-答案.md](./W1-Python够用线-练习题-答案.md)
> **规则**：先自己写，跑通并对照「验收」后再看答案。每题 10–20 行，不抄 `step*.py`。

## 0. 准备

```bash
cd /home/sky/Documents/ai-learning-notes/projects/demo2
source .venv/bin/activate
mkdir -p exercises
# 每题一个文件：exercises/a1_top_words.py、b1_default_arg.py …
python exercises/a1_top_words.py
```

- 环境：Python 3.10.12，pydantic **v2**（2.14），httpx（0.28）。
- `exercises/` 里只放你自己的代码；`step*.py` 是示例，先别看。
- 只标 ★ 的是 4 小时版必做；☆ 是当天有余力再补。

## 题目索引

| 编号 | 主题 | 教程 | 预计 | 必做 |
|---|---|---|---|---|
| A1 | 词频统计 Top-3（dict + 排序） | §3.4 §3.7 | 10 min | ★ |
| A2 | 保序去重 + 集合差集 | §3.5 | 8 min | ★ |
| A3 | 切片实现分块 | §3.3 | 7 min | ★ |
| A4 | 浅拷贝 vs 深拷贝 | §3.8 | 8 min | ☆ |
| B1 | 修可变默认参数的 bug | §4.2 | 8 min | ★ |
| B2 | `*args` / `**kwargs` | §4.3 | 10 min | ★ |
| B3 | 闭包晚绑定 | §4.6 | 10 min | ★ |
| B4 | `sorted(key=...)` 多字段排序 | §4.4 | 7 min | ☆ |
| C1 | `@dataclass` Message + 手动校验 | §5.2 §6.2 | 12 min | ★ |
| C2 | `ChatSession` + `default_factory` | §5.2 | 12 min | ★ |
| C3 | typing 运行时到底管不管 | §6.2 | 5 min | ☆ |
| D1 | 自定义异常 + 异常链 | §7.2 §7.3 | 12 min | ★ |
| D2 | JSON 读写 + pathlib | §8.1 §8.2 | 12 min | ★ |
| D3 | 找茬：异常处理三大禁忌 | §7.4 | 8 min | ☆ |
| D4 | venv / uv 命令序列 | §1 | 5 min | ★ |
| E1 | pydantic 模型 + 约束 + 校验器 | §9.2 §9.4 | 12 min | ★ |
| E2 | 嵌套模型 + 脏 JSON | §9.3 | 12 min | ★ |
| E3 | 校验失败 → 回灌 → 重试 | §9.6 | 15 min | ★ |
| E4 | 生成 JSON Schema | §9.2 | 5 min | ☆ |
| E5 | pydantic-settings 读配置 | §9.5 | 10 min | ☆ |
| F1 | 串行 vs `gather` | §10.3 | 8 min | ★ |
| F2 | `Semaphore` 限流 | §10.4 | 10 min | ★ |
| F3 | 超时 + 重试 + 容错 | §10.5–10.7 | 15 min | ★ |
| F4 | 阻塞代码拖垮事件循环 | §10.6 | 8 min | ☆ |
| F5 | 找茬：async 代码 4 个 bug | §10.2–10.6 | 8 min | ☆ |
| G1 | 手写 SSE 流式解析 | §11.3 | 12 min | ★ |
| G2 | httpx 请求 + 错误映射 | §11.2 | 10 min | ★ |
| G3 | 异步 httpx 并发 | §11.4 | 10 min | ☆ |
| G4 | requests vs httpx 选型 | §11.1 | 3 min | ☆ |
| H1 | 综合：批量结构化抽取（无 Key） | §9.6 §10.7 | 30 min | ★ |
| H2 | 拆包重构 | §12 | 20 min | ☆ |

---

## A. 数据结构（§3）

### A1 ★ 词频 Top-3

给定文本：

```python
TEXT = "The quick brown fox jumps over the lazy dog. The dog barks; the fox runs. A quick fox!"
```

实现 `top_words(text: str, n: int = 3) -> list[tuple[str, int]]`：

1. 转小写，只保留字母和 `'`（用 `re.findall`）。
2. 用普通 `dict` 计数，**不要用 `collections.Counter`**。
3. 按「次数降序、同次数按单词字典序升序」排序，取前 `n` 个。

**验收**

```python
assert top_words(TEXT) == [("the", 4), ("fox", 3), ("dog", 2)]
assert top_words(TEXT, 1) == [("the", 4)]
```

- 同次数时 `fox`(3) 没问题，但 `dog` 和 `quick` 都是 2，必须输出 `dog`。
- 代码里不允许出现 `for i in range(len(...))`。

**提示**：排序 key 是 `lambda kv: (-kv[1], kv[0])`。

---

### A2 ★ 保序去重 + 集合运算

```python
a = ["u3", "u1", "u2", "u1", "u3", "u4"]
b = ["u2", "u2", "u5"]
```

实现 `compare(a, b) -> tuple[list[str], list[str], list[str]]`，返回：

1. `unique_a`：`a` 保序去重（保留首次出现的位置）。
2. `only_a`：只在 `a` 里出现的元素，**保持 `a` 的顺序**。
3. `both`：交集，**升序排序**。

**验收**

```python
assert compare(a, b) == (
    ["u3", "u1", "u2", "u4"],
    ["u3", "u1", "u4"],
    ["u2"],
)
```

- 去重必须用 `dict.fromkeys`。
- 判断「是否在 b 里」必须用 `set`，不要写 `b.count(x) == 0`。
- 想一下：为什么 `list(set(a) - set(b))` 不满足「保持顺序」？

---

### A3 ★ 切片实现分块

实现 `chunk(xs: list[int], n: int) -> list[list[int]]`：

- 每 `n` 个元素一组，最后一组可以不满。
- `n <= 0` 抛 `ValueError`。
- **不能修改原列表**，只能用切片 + `range`。

**验收**

```python
xs = [1, 2, 3, 4, 5, 6, 7]
assert chunk(xs, 3) == [[1, 2, 3], [4, 5, 6], [7]]
assert xs == [1, 2, 3, 4, 5, 6, 7]
assert chunk([], 3) == []
try:
    chunk(xs, 0)
except ValueError:
    pass
else:
    raise AssertionError("n=0 应该报错")
```

---

### A4 ☆ 浅拷贝 vs 深拷贝

先**预测**下面输出，再运行验证：

```python
matrix = [[1, 2], [3, 4]]
shallow = matrix.copy()
shallow[0].append(99)
print(matrix)
```

然后实现 `safe_append(matrix: list[list[int]], row: int, value: int) -> list[list[int]]`：返回追加后的**新矩阵**，原 `matrix` 不能被改动。

**验收**

```python
m = [[1, 2], [3, 4]]
m2 = safe_append(m, 0, 99)
assert m == [[1, 2], [3, 4]]
assert m2 == [[1, 2, 99], [3, 4]]
```

用 `copy.deepcopy` 和自己重建各写一版，比较哪个更直观。

---

## B. 函数（§4）

### B1 ★ 修可变默认参数的 bug

下面函数第二次调用会带上第一次的数据：

```python
def add_tag(tag, tags=[]):
    tags.append(tag)
    return tags
```

1. 修好它，使两次调用互不影响。
2. 用一句话解释：默认值是在什么时候创建、被谁共享的。
3. 如果调用方明确传入 `tags`，函数应该就地修改并返回它吗？说明你的选择。

**验收**

```python
assert add_tag("a") == ["a"]
assert add_tag("b") == ["b"]
shared = []
assert add_tag("c", shared) is shared
```

---

### B2 ★ `*args` / `**kwargs`

实现：

```python
def stats(name: str, *numbers: float, round_to: int = 2, **labels: str) -> dict:
    ...
```

返回：

```python
{
    "name": name,
    "count": 数字个数,
    "sum": 总和（保留 round_to 位）,
    "avg": 平均值（无数字时为 None）,
    "min": 最小值（无数字时为 None）,
    "max": 最大值（无数字时为 None）,
    "labels": labels,   # 原样 dict
}
```

**验收**

```python
assert stats("demo", 1, 2, 3, 4) == {
    "name": "demo", "count": 4, "sum": 10, "avg": 2.5,
    "min": 1, "max": 4, "labels": {},
}
assert stats("empty")["avg"] is None
assert stats("empty")["count"] == 0
assert stats("demo", 1, 2, 3, round_to=1, env="test")["labels"] == {"env": "test"}
```

- `round_to` 必须是**仅关键字**参数，不能混进 `numbers`。
- 空输入不能触发 `ZeroDivisionError`。
- 说出 `numbers` 和 `labels` 在函数体内各是什么类型。

---

### B3 ★ 闭包晚绑定

下面的输出是 `[2, 2, 2]`，但需求是 `[0, 1, 2]`：

```python
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])
```

1. 先运行确认输出，并解释为什么不是 `[0, 1, 2]`。
2. 用**默认参数**改一版。
3. 用**工厂函数/闭包**改一版。
4. 说明两种写法分别是怎么把 `i` 「固定」住的。

**验收**

```python
assert [f() for f in funcs] == [0, 1, 2]
```

---

### B4 ☆ `sorted` 的 key 与多字段排序

```python
rows = [
    {"name": "alice", "score": 90},
    {"name": "bob", "score": 90},
    {"name": "carol", "score": 80},
]
```

1. 按 `score` 降序、同分按 `name` 升序排序。
2. 找出 `score` 最高的一行（同分取 `name` 字典序最小的）。
3. 解释为什么排序结果里 `alice` 在 `bob` 前面。

**验收**

```python
assert [r["name"] for r in sort_rows(rows)] == ["alice", "bob", "carol"]
assert best_row(rows)["name"] == "alice"
assert rows[0]["name"] == "alice"   # 原列表不能被排序修改
```

---

## C. 类、dataclass、typing（§5、§6）

### C1 ★ `@dataclass Message`（带手动校验）

实现：

```python
@dataclass
class Message:
    role: Literal["system", "user", "assistant"]
    content: str
    name: str | None = None
```

要求：

1. `is_user` 属性：`role == "user"` 时为 `True`。
2. `to_api()`：返回 API 用的 dict，**`name` 为 `None` 时不要出现这个键**。
3. `__post_init__` 中：`role` 不在三个值里、或 `content` 去空白后为空，抛 `ValueError`。

> 关键认知：`Literal` 只是 typing 注解，**dataclass 运行时不会拦**。所以 `Message("tool", "x")` 默认能构造成功，你必须手动校验。

**验收**

```python
m = Message("user", "hello", name="sky")
assert m.is_user
assert m.to_api() == {"role": "user", "content": "hello", "name": "sky"}
assert Message("assistant", "hi").to_api() == {"role": "assistant", "content": "hi"}

for bad in [("tool", "x"), ("user", "   ")]:
    try:
        Message(*bad)
    except ValueError:
        pass
    else:
        raise AssertionError(f"{bad} 应该报错")
```

---

### C2 ★ `ChatSession` 与 `field(default_factory=...)`

实现：

```python
@dataclass
class ChatSession:
    messages: list[Message] = field(default_factory=list)
```

方法/属性：

1. `add(role, content, name=None) -> Message`：构造并追加，返回该消息。
2. `last_user -> Message | None`：最后一条 `role == "user"` 的消息。
3. `total_chars -> int`：所有 `content` 长度之和。

**验收**

```python
s1, s2 = ChatSession(), ChatSession()
s1.add("system", "你是助手")
s1.add("user", "什么是 RAG?")
s1.add("assistant", "检索增强生成")
s2.add("user", "x")

assert s1.last_user.content == "什么是 RAG?"
assert s1.total_chars == len("你是助手") + len("什么是 RAG?") + len("检索增强生成")
assert len(s2.messages) == 1          # 两个 session 不能共享 list
assert ChatSession().last_user is None
```

- 必须用 `field(default_factory=list)`，写 `messages: list[Message] = []` 会直接报错（dataclass 会拦可变默认值），想一下它为什么比 B1 更严格。

---

### C3 ☆ typing 运行时到底管不管

给下面三个函数补全类型注解（用 `Callable`、`dict[str, list[int]]`、`int | None`）：

```python
def add(a, b):
    return a + b

def parse_ids(raw):
    return [int(x) for x in raw.split(",")]

def pick_first(xs, key):
    return min(xs, key=key) if xs else None
```

然后故意犯错：

```python
print(add("1", "2"))          # 输出什么？
print(parse_ids(123))         # 会怎样？
```

**验收**：你能不看文档回答——类型注解在运行时做什么？pydantic 补的是哪一段？为什么 `add("1", "2")` 不报错？

---

## D. 异常、JSON、文件、环境（§1、§7、§8）

### D1 ★ 自定义异常 + 异常链

实现：

```python
class ConfigError(Exception): ...

def load_config(path: str | Path) -> dict: ...
```

三种失败分别转成 `ConfigError`：

| 情况 | 消息里要有 | `__cause__` |
|---|---|---|
| 文件不存在 | 路径 | `FileNotFoundError` |
| 内容不是合法 JSON | 路径 + 行号 | `json.JSONDecodeError` |
| 缺少 `"model"` 字段 | 路径 + 字段名 | `None` |

成功时返回解析后的 dict。

**验收**

```python
try:
    load_config("nope.json")
except ConfigError as e:
    assert e.__cause__ is not None
    assert isinstance(e.__cause__, FileNotFoundError)
    print("根因:", type(e.__cause__).__name__)
```

用 `tempfile.TemporaryDirectory()` 造三种坏文件，逐一打印 `e` 和 `e.__cause__` 的类型。

- 必须用 `raise ConfigError(...) from e`，不能用 `raise e`，也不要 `except:`。
- 解释：`e.__cause__` 和 `e.__context__` 的区别（提示：显式链 vs 隐式链）。

---

### D2 ★ JSON 读写 + pathlib

实现三个函数：

```python
def save_json(path: str | Path, obj) -> None: ...
def load_json(path: str | Path, default=None): ...
def scan_json_dir(dir_path: str | Path) -> dict[str, int | str]: ...
```

1. `save_json`：UTF-8、`ensure_ascii=False`、`indent=2`、末尾换行。
2. `load_json`：文件不存在返回 `default`，不抛异常。
3. `scan_json_dir`：遍历目录下 `*.json`，值为该文件顶层列表的长度；JSON 解析失败的值写成 `"invalid: <原因>"`；按文件名排序返回。

**验收**

```python
with tempfile.TemporaryDirectory() as td:
    td = Path(td)
    save_json(td / "items.json", [{"id": 1, "name": "中文"}])
    assert "中文" in (td / "items.json").read_text(encoding="utf-8")   # 没被转义成 \uXXXX
    assert load_json(td / "items.json") == [{"id": 1, "name": "中文"}]
    assert load_json(td / "missing.json", default=[]) == []
    (td / "broken.json").write_text("{nope", encoding="utf-8")
    result = scan_json_dir(td)
    assert result["items"] == 1
    assert result["broken"].startswith("invalid")
```

- 所有文件操作都要显式 `encoding="utf-8"`（Windows 默认不是 UTF-8，部署会踩）。
- 不要用 `os.path.join`，统一 `pathlib.Path`。

---

### D3 ☆ 找茬：异常处理三大禁忌

下面两段代码各有问题，**逐条列出**并重写。

```python
# 版本 1
def load_all(paths):
    results = []
    for p in paths:
        try:
            results.append(json.loads(open(p).read()))
        except:
            pass
        return results
```

```python
# 版本 2
try:
    resp = client.get(url)
    resp.raise_for_status()
except Exception as e:
    print("出错")
    raise e
```

**验收**：重写后的版本满足：

- 单个坏文件不影响其他文件，但坏文件要能被调用方知道（返回/收集错误，而不是静默吞掉）。
- 文件必须关闭（`with` 或 `Path.read_text`）。
- 只捕获预期的异常；`raise` 时保留原始 traceback。
- `KeyboardInterrupt` 不能被捕获。

---

### D4 ★ venv / uv 命令序列

不看笔记，写出从「新机器 clone 仓库」到「运行 `exercises/a1_top_words.py`」的完整命令（假设 `requirements.txt` 已存在），并回答：

1. `pip freeze > requirements.txt` 和 `uv add openai` 分别改了什么文件？各适合什么场景？
2. 为什么 `.venv/` 和 `.env` 必须进 `.gitignore`？
3. `uv run script.py` 和「先 `source .venv/bin/activate` 再 `python script.py`」的关系是什么？

**验收**：命令能在你的机器上原样跑通；三个问题的答案能说给别人听。

---

## E. pydantic（§9，重点）

### E1 ★ 模型 + 约束 + 自定义校验器

定义 `Item`：

| 字段 | 类型 | 约束 |
|---|---|---|
| `sku` | `str` | 必须匹配 `^SKU-\d{4}$` |
| `name` | `str` | 1–50 字符，去空白后不能为空 |
| `price` | `float` | `> 0` |
| `quantity` | `int` | `>= 1` |
| `category` | `Literal["book", "food", "digital"]` | 只能三选一 |
| `tags` | `list[str]` | 默认空列表 |

要求：

- 用 `Field` 表达能用声明式表达的约束；`name` 的「去空白后为空」用 `field_validator`。
- 准备 4 个非法输入：`sku` 格式错、`price=0`、`category="toy"`、`name="   "`。
- 每个都捕获 `ValidationError`，打印 `[(err["loc"], err["type"]) for err in e.errors()]`。

**验收**：4 个非法输入分别定位到 `sku` / `price` / `category` / `name` 字段；合法输入能自动补 `tags=[]`。

- 注意：`name="   "` 能通过 `min_length=1`，所以 validator 里**去空白后要再判空**。
- 不要用 `@validator`（v1 API），用 `@field_validator` + `@classmethod`。

---

### E2 ★ 嵌套模型 + 脏 JSON

定义：

```python
class Customer(BaseModel):
    name: str            # 至少 1 字符
    email: str           # validator：必须包含 "@"

class Order(BaseModel):
    order_id: str        # ^ORD-\d+$
    customer: Customer
    items: list[Item]    # 至少 1 个（复用 E1）
    created_at: datetime
```

解析这段**脏 JSON**（数字是字符串、时间也是字符串）：

```python
raw = """{
  "order_id": "ORD-1001",
  "customer": {"name": "Sky", "email": "sky@example.com"},
  "items": [
    {"sku": "SKU-0001", "name": "Python 书", "price": "39.9",
     "quantity": "2", "category": "book"}
  ],
  "created_at": "2026-10-28T10:00:00"
}"""
```

**验收**

```python
order = Order.model_validate_json(raw)
assert order.items[0].price == 39.9          # float，不是 "39.9"
assert order.items[0].quantity == 2          # int，不是 "2"
assert order.items[0].tags == []
assert order.created_at.year == 2026
```

再把 `price` 改成 `-1`，确认错误定位是 `("items", 0, "price")`。

- 解释 `model_validate_json` 与 `json.loads` + `model_validate` 的关系。
- 想想：为什么不能对 LLM 的输出直接 `json.loads` 就用？

---

### E3 ★ 校验失败 → 回灌错误 → 重试

定义 `Ticket`（`category` 三选一、`priority` 1–5、`summary` 1–200、`order_id` 可选），实现：

```python
class ExtractError(Exception): ...

def extract_with_retry(raw: str, max_attempts: int = 3) -> Ticket: ...
```

流程：

1. `Ticket.model_validate_json(raw)`。
2. 捕获 `ValidationError`，把 `str(e)` 作为 feedback 交给「修复函数」，拿到新的 JSON 字符串，再试。
3. 超过次数抛 `ExtractError`，用 `from e` 保留最后一次 `ValidationError`。

修复函数自己 mock 即可：

```python
FIXES = {
    "bad_priority": '{"category":"refund","priority":3,"summary":"想退货","order_id":"ORD-1"}',
    "bad_category": '{"category":"other","priority":2,"summary":"咨询","order_id":null}',
}
```

**验收**

- 输入 `priority=9` → 第 2 次成功，且修复函数确实收到了错误信息。
- 输入 `category="complaint"` → 第 2 次成功。
- 输入一个修不好的 → 抛 `ExtractError`，`e.__cause__` 是 `ValidationError`。
- 不允许 `except Exception: pass`。

- 想一下：真实场景里 feedback 应该只给错误摘要，还是整段 `str(e)`？为什么？

---

### E4 ☆ 生成 JSON Schema

1. 打印 E1 `Item` 的 `model_json_schema()`（`indent=2`，`ensure_ascii=False`）。
2. 指出 `required`、`properties`，以及 `description` 在哪。
3. 简答：调用模型时怎么用这份 schema 约束输出？`response_format` 里放的是什么？

**验收**：schema 里能看到 `sku` 的 `pattern`、`price` 的 `exclusiveMinimum`、`category` 的 `enum`。

- 提示：`Field(description="...")` 会进 schema，LLM 能读到，**写清楚描述能显著提升抽取准确率**。

---

### E5 ☆ pydantic-settings 读配置

```bash
pip install pydantic-settings
```

定义 `Settings`：

- `deepseek_api_key: str`（必填，从环境变量读）
- `deepseek_base_url: str = "https://api.deepseek.com"`
- `model: str = "deepseek-chat"`
- `timeout_seconds: int = 60`
- 自动读 `.env`，忽略多余字段。

**验收**

```bash
DEEPSEEK_API_KEY=sk-test timeout_seconds=30 python exercises/e5_settings.py
# 输出：deepseek-chat https://api.deepseek.com 30
```

- 不要打印 key 本身（只打印前 3 位 + `***` 可以）。
- 环境变量名和字段名如何对应？大小写敏感吗？

---

## F. async/await（§10）

### F1 ★ 串行 vs `gather`

```python
async def fetch(name: str, delay: float = 0.5) -> str:
    await asyncio.sleep(delay)
    return f"{name}-result"
```

写 `main()`：先串行 `await` 3 次，再用 `asyncio.gather` 并发 3 次，分别用 `time.perf_counter()` 计时并打印。

**验收**

```text
串行 ≈ 1.50s，并发 ≈ 0.50s
assert concurrent < 1.0
```

- 入口必须是 `asyncio.run(main())`。
- 动态任务列表用 `gather(*(fetch(n) for n in names))`，注意 `*`。
- 回答：并发时总共用了几个线程？（提示：事件循环是单线程）

---

### F2 ★ `Semaphore` 限流

20 个任务，每个 `await asyncio.sleep(0.1)`，并发上限 3。

要求统计**实际达到的最大并发数** `max_active` 并打印总耗时。

**验收**

```text
max_active = 3
总耗时 ≈ 0.7s（20 / 3 向上取整 × 0.1）
```

- 用 `async with sem:` 包住整个任务体。
- 计数器的 `+= 1` / `-= 1` 要放在正确位置，`-= 1` 建议放 `finally`。
- 回答：为什么不能用「创建 20 个 task」代替限流？

---

### F3 ★ 超时 + 重试 + 容错

实现 5 个任务，每个最多尝试 3 次：

| 任务 | 行为 |
|---|---|
| `i=0` | 第 1 次故意 `sleep(10)`（用 `asyncio.wait_for(..., timeout=0.2)` 截断），第 2 次成功 |
| `i=1` | 前 2 次抛 `RuntimeError("上游 503")`，第 3 次成功 |
| `i=2`、`i=3` | 直接成功 |
| `i=4` | 每次都抛 `ValueError("脏数据")`（不在重试范围内） |

要求：

- 单次尝试超时用 `asyncio.wait_for`（3.10 没有 `asyncio.timeout`）。
- 失败后指数退避：`await asyncio.sleep(0.01 * 2 ** (attempt - 1))`。
- `gather(..., return_exceptions=True)`，最后把异常条目统一转成 `{"ok": False, "error": ...}`。

**验收**

```text
{'i': 0, 'ok': True, 'attempts': 2}
{'i': 1, 'ok': True, 'attempts': 3}
{'i': 2, 'ok': True, 'attempts': 1}
{'i': 3, 'ok': True, 'attempts': 1}
{'ok': False, 'error': 'ValueError: 脏数据'}
```

- 跑完不能有未捕获异常。
- 回答：为什么 `i=4` 的 `ValueError` 不应该被重试？

---

### F4 ☆ 阻塞事件循环

写两个版本，各并发跑 3 个「0.3 秒」任务并计时：

- `bad`：任务体里 `time.sleep(0.3)`。
- `good`：任务体里 `await asyncio.sleep(0.3)`。

**验收**

```text
bad  ≈ 0.9s   （三个阻塞串成一条线）
good ≈ 0.3s
```

再写一个 `good2`：用 `await asyncio.to_thread(time.sleep, 0.3)`，观察它也能并发。

- 解释：`time.sleep` 阻塞的是谁？为什么 `to_thread` 能救回来？
- 真实场景：`requests.get()` 在 async 函数里应该怎么处理？

---

### F5 ☆ 找茬：async 代码的 4 个 bug

```python
import asyncio, time, httpx

async def fetch(name):
    time.sleep(0.1)
    async with httpx.AsyncClient() as c:
        r = await c.get("https://example.com")
    return r.json()

async def main():
    tasks = [fetch(n) for n in ["a", "b"]]
    results = await asyncio.gather(tasks)
    print(results)

asyncio.run(main())
```

**验收**：列出至少 4 个问题并修复（提示：阻塞调用、`gather` 参数、状态码、超时/连接复用）。修完能解释每个改动的理由。

---

## G. httpx 与流式（§11）

### G1 ★ 手写 SSE 流式解析

实现：

```python
def parse_sse(lines: Iterable[str]) -> str: ...
```

规则：

1. 跳过空行、以 `:` 开头的注释行、不以 `data:` 开头的行。
2. 去掉 `data:` 前缀和两端空白；`[DONE]` 立即结束循环（后面的内容不要）。
3. `json.loads` 失败、缺字段、`delta.content` 为空时跳过，不能让整个流崩。
4. 拼接所有 `delta.content` 返回。

输入：

```python
LINES = [
    'data: {"choices":[{"delta":{"role":"assistant"}}]}',
    'data: {"choices":[{"delta":{"content":"你好"}}]}',
    ': keep-alive',
    '',
    'data: {"choices":[{"delta":{"content":"，世界"}}]}',
    'data: [DONE]',
    'data: {"choices":[{"delta":{"content":"这段不应出现"}}]}',
]
```

**验收**

```python
assert parse_sse(LINES) == "你好，世界"
```

- 这题不联网，`lines` 可以是 list，也可以是 `resp.iter_lines()`。
- 回答：SSE 的帧格式是什么？`[DONE]` 是我们自己的协议还是 SSE 标准？

---

### G2 ★ httpx 请求 + 错误映射（离线）

实现：

```python
class ApiError(Exception): ...

def get_json(client: httpx.Client, url: str) -> dict: ...
```

要求：

- `raise_for_status()`，4xx/5xx 转成 `ApiError("HTTP <code>: <url>")`。
- `httpx.TimeoutException` 转成 `ApiError("请求超时: <url>")`。
- 用 `raise ... from e` 保留根因。

用 `httpx.MockTransport` 模拟（不需要网络）：

```python
def handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/ok":
        return httpx.Response(200, json={"ok": True, "page": request.url.params.get("page")})
    if request.url.path == "/slow":
        raise httpx.TimeoutException("模拟超时", request=request)
    return httpx.Response(503, text="upstream down")

with httpx.Client(transport=httpx.MockTransport(handler), timeout=2) as client:
    ...
```

**验收**

```text
/ok?page=2  → {'ok': True, 'page': '2'}
/down       → ApiError: HTTP 503 ...，__cause__ 是 HTTPStatusError
/slow       → ApiError: 请求超时 ...，__cause__ 是 TimeoutException
```

- 回答：为什么要复用 `httpx.Client` 而不是每次 `httpx.get`？
- 回答：`MockTransport` 在真实项目里有什么用？

---

### G3 ☆ 异步 httpx 并发

用 `httpx.AsyncClient` + `httpx.MockTransport` 并发请求 4 个路径：

```python
async def handler(request: httpx.Request) -> httpx.Response:
    await asyncio.sleep(0.2 if request.url.path == "/slow" else 0.05)
    return httpx.Response(200, json={"path": request.url.path})
```

**验收**

```text
[{'path': '/a'}, {'path': '/b'}, {'path': '/slow'}, {'path': '/c'}]
耗时 ≈ 0.2s（不是 0.5s）
```

- 结果顺序和 `gather` 参数顺序一致，不是完成顺序。
- 回答：一个 `AsyncClient` 能不能同时被多个协程使用？

---

### G4 ☆ 选型简答

1. 新项目为什么优先 `httpx` 而不是 `requests`？
2. 什么情况下仍然会用 `requests`？
3. 同步流式和异步流式在 API 上的区别（`iter_lines` vs `aiter_lines`）？

**验收**：三题都能用一两句话答清楚，不查资料。

---

## H. 综合实战

### H1 ★★ 批量结构化抽取（不需要 API Key）

把 E3 + F2 + F3 合成一条流水线：**8 个问题 → mock LLM → pydantic 校验 → 错误回灌重试 → 限流并发 → 超时 → 汇总报告**。

数据（直接放进你的代码）：

```python
RAW = {
    "q1": '{"category":"refund","priority":3,"summary":"想退货","order_id":"ORD-1"}',
    "q2": '{"category":"complaint","priority":2,"summary":"投诉","order_id":null}',
    "q3": '{"category":"logistics","priority":0,"summary":"物流慢","order_id":"ORD-3"}',
    "q4": '{"category":"other","priority":1,"order_id":"ORD-4"}',
    "q5": '{"category":"other","priority":5,"summary":"咨询","order_id":null}',
    "q6": '{"category":"refund","priority":4,"summary":"退款没到账","order_id":"ORD-6"}',
    "q7": '{"category":"ticket","priority":2,"summary":"永远修不好","order_id":null}',
    "q8": '{"category":"other","priority":1,"summary":"永远超时","order_id":null}',
}

# 修复函数：收到 feedback（即 str(ValidationError)）时返回下面的正确答案
FIXED = {
    "q2": '{"category":"other","priority":2,"summary":"投诉","order_id":null}',
    "q3": '{"category":"logistics","priority":1,"summary":"物流慢","order_id":"ORD-3"}',
    "q4": '{"category":"other","priority":1,"summary":"咨询","order_id":"ORD-4"}',
}
```

mock LLM 的约定：

- `q8` 永远 `await asyncio.sleep(10)`（模拟超时）。
- 其它问题 `sleep(0.02)`；**只有收到 feedback 且该问题在 `FIXED` 里**才返回修复版，否则返回 `RAW[q]`。
- `q7` 不在 `FIXED` 里，所以永远修不好。

要求：

1. `Ticket` 用 E3 的模型。
2. 每个问题最多 3 次尝试，单次调用 `wait_for(..., timeout=0.3)`。
3. `ValidationError` → 把 `str(e)` 作为 feedback 重试；`TimeoutError` 也重试。
4. 指数退避（0.01 / 0.02 / 0.04 秒）。
5. `Semaphore(3)` 限流，并记录 `max_active`。
6. `gather(..., return_exceptions=True)`，返回结构：

```python
{
    "elapsed": float,
    "max_active": int,
    "success": [{"q": ..., "ok": True,  "attempts": ..., "data": {...}}, ...],
    "failed":  [{"q": ..., "ok": False, "error": "..."}, ...],
}
```

**验收**

```text
success 6 个：q1(1 次)、q2(2)、q3(2)、q4(2)、q5(1)、q6(1)
failed  2 个：q7(ValidationError)、q8(TimeoutError)
max_active ≤ 3
elapsed ≈ 1s 量级
```

- 不允许任何异常逃出 `asyncio.run`。
- 回答：如果要接真实 DeepSeek，只改哪一处？超时和重试参数应该怎么调？

---

### H2 ☆ 拆包重构

把 H1 拆成可导入的包（对应教程 §12）：

```text
exercises/h2_pkg/
├── __init__.py
├── models.py      # pydantic 模型，不 import httpx/asyncio
├── client.py      # mock_llm、extract_one、batch
└── main.py        # 只做编排和打印
```

**验收**

```bash
cd exercises && python -m h2_pkg.main
```

- `models.py` 里不出现 `asyncio` / `httpx`。
- `main.py` 里不出现 pydantic 校验逻辑。
- 没有循环 import。
- 回答：`python main.py` 和 `python -m h2_pkg.main` 在 import 上有什么区别？

---

## 做完的标志

- 30 分钟内能独立写出 H1 的骨架（不看答案）。
- 能解释清楚：`gather` 为什么快、`Semaphore` 限的是什么、pydantic 校验失败后为什么要把错误回灌。
- 踩过的坑能一句话说清（可变默认参数、闭包晚绑定、`time.sleep`、裸 `except`）。
