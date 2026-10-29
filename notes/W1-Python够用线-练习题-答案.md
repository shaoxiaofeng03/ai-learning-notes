# W1 · Python 够用线 · 练习题答案

> 先做题，再对答案。答案不是唯一解，**对照验收标准**，能解释为什么这么写才算过。
> 题目：[W1-Python够用线-练习题.md](./W1-Python够用线-练习题.md)

---

## A. 数据结构

### A1 词频 Top-3

```python
import re

TEXT = "The quick brown fox jumps over the lazy dog. The dog barks; the fox runs. A quick fox!"

def top_words(text: str, n: int = 3) -> list[tuple[str, int]]:
    words = re.findall(r"[a-z']+", text.lower())
    counts: dict[str, int] = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]

if __name__ == "__main__":
    print(top_words(TEXT))       # [('the', 4), ('fox', 3), ('dog', 2)]
    print(top_words(TEXT, 1))    # [('the', 4)]
```

**为什么**

- `counts.get(w, 0) + 1` 是 dict 计数最基础的写法；`Counter` 只是封装。
- `sorted` 的 key 返回元组，Python 按元组逐项比较：先比 `-次数`（降序），再比单词（升序）。
- `dog` 和 `quick` 同为 2，`dog < quick`，所以 `dog` 进前三。

---

### A2 保序去重 + 集合运算

```python
def compare(a: list[str], b: list[str]) -> tuple[list[str], list[str], list[str]]:
    unique_a = list(dict.fromkeys(a))
    b_set = set(b)
    only_a = [x for x in unique_a if x not in b_set]
    both = sorted(set(a) & b_set)
    return unique_a, only_a, both

a = ["u3", "u1", "u2", "u1", "u3", "u4"]
b = ["u2", "u2", "u5"]
print(compare(a, b))
# (['u3', 'u1', 'u2', 'u4'], ['u3', 'u1', 'u4'], ['u2'])
```

**为什么**

- `dict` 保留插入顺序，`fromkeys` 正好做顺序去重。
- `list(set(a) - set(b))` 会丢顺序（set 无序），差集只适合「只要集合、不要顺序」的场景。
- 判断成员用 `set`，`list` 的 `in` 是 O(n)。

---

### A3 切片分块

```python
def chunk(xs: list[int], n: int) -> list[list[int]]:
    if n <= 0:
        raise ValueError("n 必须大于 0")
    return [xs[i:i + n] for i in range(0, len(xs), n)]
```

**为什么**

- `range(0, len(xs), n)` 直接给出每块的起点。
- 切片越界不会报错，最后一块自动截断。
- 切片产生新 list，原列表不变。

---

### A4 浅拷贝 vs 深拷贝

```python
import copy

matrix = [[1, 2], [3, 4]]
shallow = matrix.copy()
shallow[0].append(99)
print(matrix)      # [[1, 2, 99], [3, 4]]  ← 被连带修改

def safe_append(matrix: list[list[int]], row: int, value: int) -> list[list[int]]:
    new = copy.deepcopy(matrix)
    new[row].append(value)
    return new

m = [[1, 2], [3, 4]]
m2 = safe_append(m, 0, 99)
print(m)            # [[1, 2], [3, 4]]
print(m2)           # [[1, 2, 99], [3, 4]]
```

**为什么**

- `list.copy()` / `[:]` 只复制外层 list，内层子列表还是同一批对象。
- `deepcopy` 递归复制；数据不深时也可以用 `[row.copy() for row in matrix]`。

---

## B. 函数

### B1 可变默认参数

```python
def add_tag(tag: str, tags: list[str] | None = None) -> list[str]:
    if tags is None:
        tags = []
    tags.append(tag)
    return tags
```

**为什么**

- 默认值在 `def` 执行时求值一次，之后所有调用共享同一个 list。
- `None` 是哨兵，真正的新 list 在每次调用时创建。
- 传入 `tags` 时就地修改并返回是合理的（调用方知道自己在传对象）；不想改调用方就 `tags = list(tags)` 先复制。

---

### B2 `*args` / `**kwargs`

```python
def stats(name: str, *numbers: float, round_to: int = 2, **labels: str) -> dict:
    total = sum(numbers)
    count = len(numbers)
    return {
        "name": name,
        "count": count,
        "sum": round(total, round_to),
        "avg": round(total / count, round_to) if count else None,
        "min": min(numbers) if numbers else None,
        "max": max(numbers) if numbers else None,
        "labels": labels,
    }
```

**为什么**

- `*numbers` 收集成 `tuple`，`**labels` 收集成 `dict`。
- `round_to` 写在 `*numbers` 后面，自动变成 keyword-only，不会混进 `numbers`。
- 空输入要显式处理，`sum(())` 是 0 但 `sum/0` 会炸。

输出：

```python
stats("demo", 1, 2, 3, 4)
# {'name': 'demo', 'count': 4, 'sum': 10, 'avg': 2.5, 'min': 1, 'max': 4, 'labels': {}}
stats("empty")
# {'name': 'empty', 'count': 0, 'sum': 0, 'avg': None, 'min': None, 'max': None, 'labels': {}}
```

---

### B3 闭包晚绑定

```python
# 默认参数版
funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])      # [0, 1, 2]

# 工厂函数版
def make_const(i: int):
    def inner() -> int:
        return i
    return inner

funcs = [make_const(i) for i in range(3)]
print([f() for f in funcs])      # [0, 1, 2]
```

**为什么**

- lambda 体里引用的是变量 `i`，循环结束时 `i == 2`，三个函数看到的是同一个变量。
- 默认参数在**定义函数时**求值，`lambda i=i` 每次都把当时的 `i` 存进各自的默认值。
- 工厂函数每次调用创建新的局部变量 `i`，每个 `inner` 捕获各自的闭包。

---

### B4 `sorted` 的 key

```python
rows = [
    {"name": "alice", "score": 90},
    {"name": "bob", "score": 90},
    {"name": "carol", "score": 80},
]

def sort_rows(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=lambda r: (-r["score"], r["name"]))

def best_row(rows: list[dict]) -> dict:
    return min(rows, key=lambda r: (-r["score"], r["name"]))

print([r["name"] for r in sort_rows(rows)])   # ['alice', 'bob', 'carol']
print(best_row(rows)["name"])                 # alice
```

**为什么**

- `sorted` 返回新 list，原列表不动。
- key 返回元组，逐项比较；`-score` 实现降序，`name` 实现同分升序。
- 不用 `-score` 也可以用 `reverse=True`，但那样 `name` 也会跟着反向，所以元组方案更稳。

---

## C. 类、dataclass、typing

### C1 `@dataclass Message`

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class Message:
    role: Literal["system", "user", "assistant"]
    content: str
    name: str | None = None

    def __post_init__(self) -> None:
        if self.role not in ("system", "user", "assistant"):
            raise ValueError(f"非法 role: {self.role}")
        if not self.content.strip():
            raise ValueError("content 不能为空")

    @property
    def is_user(self) -> bool:
        return self.role == "user"

    def to_api(self) -> dict:
        data = {"role": self.role, "content": self.content}
        if self.name is not None:
            data["name"] = self.name
        return data
```

**为什么**

- `Literal` 不会在运行时校验，`Message("tool", "x")` 照样构造成功，所以必须 `__post_init__` 手动检查。
- `__post_init__` 在 `__init__` 末尾自动调用，是 dataclass 的校验入口。
- `to_api` 不输出 `"name": None`，避免 API 把 `null` 当成字段处理。

---

### C2 `ChatSession`

```python
from dataclasses import dataclass, field

@dataclass
class ChatSession:
    messages: list[Message] = field(default_factory=list)

    def add(self, role: str, content: str, name: str | None = None) -> Message:
        msg = Message(role=role, content=content, name=name)
        self.messages.append(msg)
        return msg

    @property
    def last_user(self) -> Message | None:
        for msg in reversed(self.messages):
            if msg.is_user:
                return msg
        return None

    @property
    def total_chars(self) -> int:
        return sum(len(m.content) for m in self.messages)
```

**为什么**

- `dataclass` 会拒绝 `messages: list[Message] = []`，直接报 `ValueError: mutable default`；`default_factory` 每次实例化调用一次，天然隔离。
- `reversed()` 比「先过滤再取 `[-1]`」少一趟拷贝。
- 返回 `None` 而不是抛异常，是这个方法的调用约定；调用方自己判空。

---

### C3 typing 运行时

```python
from collections.abc import Callable

def add(a: int, b: int) -> int:
    return a + b

def parse_ids(raw: str) -> list[int]:
    return [int(x) for x in raw.split(",")]

def pick_first(xs: list[int], key: Callable[[int], int]) -> int | None:
    return min(xs, key=key) if xs else None

print(add("1", "2"))    # "12" —— 没报错，字符串拼接
print(parse_ids(123))   # AttributeError: 'int' object has no attribute 'split'
```

**要点**

- 类型注解在运行时**完全不生效**，只给 IDE、mypy、pyright 看。
- `add("1", "2")` 能跑，因为 Python 是动态类型，`+` 对 str 合法。
- pydantic 才是运行时校验/转换；typing 管不了脏数据。

---

## D. 异常、JSON、文件、环境

### D1 自定义异常 + 异常链

```python
import json
from pathlib import Path

class ConfigError(Exception):
    pass

def load_config(path: str | Path) -> dict:
    p = Path(path)
    try:
        raw = p.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise ConfigError(f"配置文件不存在: {p}") from e

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ConfigError(f"JSON 解析失败: {p} (第 {e.lineno} 行)") from e

    if "model" not in data:
        raise ConfigError(f"缺少必填字段 model: {p}")

    return data

if __name__ == "__main__":
    try:
        load_config("nope.json")
    except ConfigError as e:
        print(e, "| 根因:", type(e.__cause__).__name__)   # FileNotFoundError
```

**为什么**

- `raise ... from e` 建立显式异常链，`e.__cause__` 能拿到根因；`raise e` 会重置 traceback 的起点。
- 缺少字段是我们主动发现的，没有底层异常，`__cause__` 自然是 `None`。
- `__context__` 是「在 except 里抛新异常」时自动挂上的隐式链，`from` 是显式声明。

---

### D2 JSON 读写 + pathlib

```python
import json
from pathlib import Path

def save_json(path: str | Path, obj) -> None:
    Path(path).write_text(
        json.dumps(obj, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

def load_json(path: str | Path, default=None):
    p = Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))

def scan_json_dir(dir_path: str | Path) -> dict[str, int | str]:
    result: dict[str, int | str] = {}
    for p in sorted(Path(dir_path).glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            result[p.stem] = len(data)
        except json.JSONDecodeError as e:
            result[p.stem] = f"invalid: {e.msg}"
    return result
```

**为什么**

- `ensure_ascii=False` 让中文原样输出，日志和 diff 都可读。
- `indent=2` 方便人看和 review；机器传输可以不缩进。
- 显式 `encoding="utf-8"` 防止平台默认编码差异。

---

### D3 找茬

**版本 1 的问题**

1. 裸 `except:` 会吞掉 `KeyboardInterrupt`、`SystemExit` 和所有编程错误。
2. `except: pass` 静默失败，坏文件永远没人知道。
3. `open()` 没有 `with`，文件描述符可能泄漏。
4. `return results` 缩进在循环里，第一轮就返回。
5. 没有指定 `encoding`。

```python
def load_all(paths: list[str]) -> tuple[list[dict], dict[str, str]]:
    results: list[dict] = []
    errors: dict[str, str] = {}
    for p in paths:
        try:
            results.append(json.loads(Path(p).read_text(encoding="utf-8")))
        except FileNotFoundError as e:
            errors[p] = f"文件不存在: {e}"
        except json.JSONDecodeError as e:
            errors[p] = f"JSON 非法: {e.msg} (第 {e.lineno} 行)"
    return results, errors
```

**版本 2 的问题**

1. `except Exception` 连代码 bug、参数错误一起吞，应该只抓 `httpx.HTTPError`。
2. `raise e` 重置 traceback，应该 `raise`。
3. `print("出错")` 没有上下文，也不该在库代码里直接 print，应该带 URL/状态码抛或记录日志。

```python
try:
    resp = client.get(url, timeout=10)
    resp.raise_for_status()
except httpx.HTTPStatusError as e:
    raise ApiError(f"HTTP {e.response.status_code}: {url}") from e
except httpx.TimeoutException as e:
    raise ApiError(f"请求超时: {url}") from e
```

---

### D4 venv / uv 命令

```bash
git clone <repo> && cd <repo>

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python exercises/a1_top_words.py

# 退出
deactivate
```

uv 版：

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
# 或者：uv sync（有 pyproject.toml 时）
```

**三个问题**

1. `pip freeze` 把**当前环境所有包**的确切版本写进 `requirements.txt`；`uv add` 只往 `pyproject.toml` 加直接依赖，并生成/更新 `uv.lock` 锁全量版本。前者简单但容易带进无关包，后者更适合项目。
2. `.venv/` 是几百 MB 的本机环境，不能跨机器复用；`.env` 里有密钥，提交就等于泄露。
3. `uv run script.py` 自动使用项目环境，**等价于**激活 venv 后执行 `python script.py`，只是不用手动 activate。

---

## E. pydantic

### E1 模型 + 约束 + 校验器

```python
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator

class Item(BaseModel):
    sku: str = Field(pattern=r"^SKU-\d{4}$")
    name: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0)
    quantity: int = Field(ge=1)
    category: Literal["book", "food", "digital"]
    tags: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name 不能只含空白")
        return v

if __name__ == "__main__":
    bad_inputs = [
        {"sku": "SKU-12", "name": "x", "price": 1, "quantity": 1, "category": "book"},
        {"sku": "SKU-0001", "name": "x", "price": 0, "quantity": 1, "category": "book"},
        {"sku": "SKU-0001", "name": "x", "price": 1, "quantity": 1, "category": "toy"},
        {"sku": "SKU-0001", "name": "   ", "price": 1, "quantity": 1, "category": "book"},
    ]
    for b in bad_inputs:
        try:
            Item(**b)
        except ValidationError as e:
            print([(err["loc"], err["type"]) for err in e.errors()])
```

输出：

```text
[(('sku',), 'string_pattern_mismatch')]
[(('price',), 'greater_than')]
[(('category',), 'literal_error')]
[(('name',), 'value_error')]
```

**为什么**

- `Field` 声明式约束能在 schema 里体现，LLM 和前端都能直接读到。
- validator 默认在类型转换之后运行，所以 `"   "` 已经通过 `min_length`，必须在里面 strip 后再判空。
- pydantic v2 用 `@field_validator`；网上 v1 的 `@validator` 已经过时。

---

### E2 嵌套模型 + 脏 JSON

```python
from datetime import datetime

from pydantic import BaseModel, Field, ValidationError, field_validator

# 复用 E1 的 Item，不再重复定义
class Customer(BaseModel):
    name: str = Field(min_length=1)
    email: str

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("email 缺少 @")
        return v

class Order(BaseModel):
    order_id: str = Field(pattern=r"^ORD-\d+$")
    customer: Customer
    items: list[Item] = Field(min_length=1)
    created_at: datetime

raw = """{
  "order_id": "ORD-1001",
  "customer": {"name": "Sky", "email": "sky@example.com"},
  "items": [
    {"sku": "SKU-0001", "name": "Python 书", "price": "39.9",
     "quantity": "2", "category": "book"}
  ],
  "created_at": "2026-10-28T10:00:00"
}"""

order = Order.model_validate_json(raw)
print(order.items[0].price)      # 39.9
print(order.model_dump_json())   # 规范化后的 JSON

try:
    Order.model_validate_json(raw.replace('"39.9"', '"-1"'))
except ValidationError as e:
    print([(err["loc"], err["type"]) for err in e.errors()])
```

输出：

```text
39.9
[(('items', 0, 'price'), 'greater_than')]
```

**为什么**

- pydantic v2 默认宽松转换：`"39.9"` → `float`，`"2"` → `int`，ISO 字符串 → `datetime`。
- `model_validate_json` = `json.loads` + `model_validate`，少一步且错误定位更细。
- `json.loads` 只能保证「是合法 JSON」，管不了字段缺失、类型错误、业务约束；LLM 输出必须再过 pydantic。

---

### E3 校验失败 → 回灌 → 重试

```python
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

class Ticket(BaseModel):
    category: Literal["refund", "logistics", "other"]
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=1, max_length=200)
    order_id: str | None = None

class ExtractError(Exception):
    pass

FIXED = {
    "bad_priority": '{"category":"refund","priority":3,"summary":"想退货","order_id":"ORD-1"}',
    "bad_category": '{"category":"other","priority":2,"summary":"咨询","order_id":null}',
}

def mock_repair(raw: str, feedback: str, attempt: int) -> str:
    print(f"  第 {attempt} 次失败，回灌给模型:", feedback.splitlines()[0])
    if "ticket" in raw:
        return raw                      # 模拟「模型怎么修都修不对」
    if "complaint" in raw:
        return FIXED["bad_category"]
    return FIXED["bad_priority"]

def extract_with_retry(raw: str, max_attempts: int = 3) -> Ticket:
    last: ValidationError | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return Ticket.model_validate_json(raw)
        except ValidationError as e:
            last = e
            if attempt == max_attempts:
                break
            raw = mock_repair(raw, str(e), attempt)

    assert last is not None
    raise ExtractError(f"模型输出在 {max_attempts} 次尝试后仍不合法") from last

if __name__ == "__main__":
    print(extract_with_retry('{"category":"refund","priority":9,"summary":"想退货"}'))
    # 第 1 次失败 → 修复 → 第 2 次成功

    try:
        extract_with_retry('{"category":"ticket","priority":2,"summary":"x"}')
    except ExtractError as e:
        print("失败:", e, "| 根因:", type(e.__cause__).__name__)
```

**为什么**

- 校验失败不是终点，`errors()` 是给模型看的「修改说明」。
- `raise ... from last` 保留最后一次校验错误，排查时能看到缺哪个字段。
- 每次重试都用新的 `raw`，否则只是重复校验同一段错误内容。
- 反馈建议给精简摘要（字段 + 原因），整段 `str(e)` 也能用，但 token 更多。

---

### E4 JSON Schema

```python
import json

print(json.dumps(Item.model_json_schema(), ensure_ascii=False, indent=2))
```

关键片段：

```json
{
  "required": ["sku", "name", "price", "quantity", "category"],
  "properties": {
    "sku": {"pattern": "^SKU-\\d{4}$", "title": "Sku", "type": "string"},
    "price": {"exclusiveMinimum": 0, "title": "Price", "type": "number"},
    "category": {"enum": ["book", "food", "digital"], "title": "Category", "type": "string"}
  }
}
```

**怎么用**

- OpenAI 兼容接口的 `response_format={"type": "json_schema", "json_schema": {...}}` 直接放这份 schema，模型会被约束成合法 JSON。
- `Field(description=...)` 会进 `properties.*.description`，是写给模型看的提示，**写清楚能提高抽取准确率**。
- schema 只保证结构/类型，业务校验（比如「退款必须有 order_id」）仍然要在 validator 里做。

---

### E5 pydantic-settings

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    deepseek_api_key: str
    deepseek_base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    timeout_seconds: int = 60

if __name__ == "__main__":
    s = Settings()
    print(s.model, s.deepseek_base_url, s.timeout_seconds)
    print(s.deepseek_api_key[:3] + "***")
```

运行：

```bash
DEEPSEEK_API_KEY=sk-test timeout_seconds=30 python exercises/e5_settings.py
# deepseek-chat https://api.deepseek.com 30
# sk-***
```

**为什么**

- 字段名 `deepseek_api_key` 对应环境变量 `DEEPSEEK_API_KEY`，pydantic-settings 默认**大小写不敏感**。
- 环境变量优先级高于 `.env`，方便容器/CI 覆盖。
- `extra="ignore"` 防止 `.env` 里多出来的变量导致启动失败。
- 类型转换也顺带做了：`timeout_seconds="30"` → `30`。

---

## F. async/await

### F1 串行 vs `gather`

```python
import asyncio
import time

async def fetch(name: str, delay: float = 0.5) -> str:
    await asyncio.sleep(delay)
    return f"{name}-result"

async def main() -> None:
    start = time.perf_counter()
    for i in range(3):
        await fetch(f"q{i}")
    serial = time.perf_counter() - start

    start = time.perf_counter()
    results = await asyncio.gather(*(fetch(f"q{i}") for i in range(3)))
    concurrent = time.perf_counter() - start

    print(results)
    print(f"串行 {serial:.2f}s，并发 {concurrent:.2f}s")
    assert concurrent < 1.0

asyncio.run(main())
```

输出：

```text
['q0-result', 'q1-result', 'q2-result']
串行 1.50s，并发 0.50s
```

**为什么**

- 串行时每次 `await` 都等满 0.5 秒。
- `gather` 把 3 个协程注册进事件循环，等 IO 时切换，几乎同时完成。
- **单线程**：并发不是多线程，是事件循环在 IO 等待期间切任务。

---

### F2 `Semaphore` 限流

```python
import asyncio
import time

async def main() -> None:
    sem = asyncio.Semaphore(3)
    active = 0
    max_active = 0

    async def worker(i: int) -> int:
        nonlocal active, max_active
        async with sem:
            active += 1
            max_active = max(max_active, active)
            try:
                await asyncio.sleep(0.1)
                return i
            finally:
                active -= 1

    start = time.perf_counter()
    results = await asyncio.gather(*(worker(i) for i in range(20)))
    elapsed = time.perf_counter() - start

    print(len(results), "max_active =", max_active, f"{elapsed:.2f}s")
    assert max_active <= 3

asyncio.run(main())
```

输出：

```text
20 max_active = 3 0.70s
```

**为什么**

- `async with sem` 拿到令牌才进入，释放后下一个才能进。
- 20 个任务仍然全部创建，但同一时刻最多 3 个在跑；`Semaphore` 限的是**在途请求数**。
- `finally` 保证异常时也归还令牌，否则会死锁。

---

### F3 超时 + 重试 + 容错

```python
import asyncio

async def call(i: int) -> dict:
    for attempt in range(1, 4):
        try:
            if i == 0 and attempt == 1:
                await asyncio.wait_for(asyncio.sleep(10), timeout=0.2)  # 单次尝试超时
            if i == 1 and attempt < 3:
                raise RuntimeError("上游 503")
            if i == 4:
                raise ValueError("脏数据，重试也没用")
            await asyncio.sleep(0.05)
            return {"i": i, "ok": True, "attempts": attempt}
        except (asyncio.TimeoutError, RuntimeError) as e:
            if attempt == 3:
                return {"i": i, "ok": False, "error": f"{type(e).__name__}: {e}"}
            await asyncio.sleep(0.01 * 2 ** (attempt - 1))

async def main() -> None:
    results = await asyncio.gather(*(call(i) for i in range(5)), return_exceptions=True)
    for r in results:
        if isinstance(r, Exception):
            r = {"ok": False, "error": f"{type(r).__name__}: {r}"}
        print(r)

asyncio.run(main())
```

输出：

```text
{'i': 0, 'ok': True, 'attempts': 2}
{'i': 1, 'ok': True, 'attempts': 3}
{'i': 2, 'ok': True, 'attempts': 1}
{'i': 3, 'ok': True, 'attempts': 1}
{'ok': False, 'error': 'ValueError: 脏数据，重试也没用'}
```

**为什么**

- `wait_for` 只截断**单次**尝试，外面还有重试循环，所以 `i=0` 第二次能成功。
- 只重试「可能恢复」的错误（超时、503）；`ValueError` 是数据问题，重试只会浪费配额。
- `return_exceptions=True` 把漏网的异常放进结果列表，保证主流程不被单个任务炸掉。

---

### F4 阻塞事件循环

```python
import asyncio
import time

async def bad(seconds: float) -> None:
    time.sleep(seconds)

async def good(seconds: float) -> None:
    await asyncio.sleep(seconds)

async def good2(seconds: float) -> None:
    await asyncio.to_thread(time.sleep, seconds)

async def main() -> None:
    for fn, label in [(bad, "bad"), (good, "good"), (good2, "good2")]:
        start = time.perf_counter()
        await asyncio.gather(*(fn(0.3) for _ in range(3)))
        print(label, f"{time.perf_counter() - start:.2f}s")

asyncio.run(main())
```

输出：

```text
bad 0.90s
good 0.30s
good2 0.30s
```

**为什么**

- `time.sleep` 阻塞整个线程，事件循环没法切任务，3 个 0.3 秒只能串起来。
- `to_thread` 把阻塞调用丢进线程池，事件循环继续跑；IO 等待会释放 GIL，所以线程池有效。
- 真实代码里优先用 `httpx.AsyncClient`；没得选再用 `asyncio.to_thread`。

---

### F5 async 找茬

```python
import asyncio
import httpx

async def fetch(name: str, client: httpx.AsyncClient) -> dict:
    await asyncio.sleep(0.1)                      # 1. 不再用 time.sleep
    r = await client.get("https://example.com", timeout=10)   # 2. 复用 client + 超时
    r.raise_for_status()                          # 3. 检查状态码
    return r.json()

async def main() -> None:
    async with httpx.AsyncClient() as client:
        tasks = [fetch(n, client) for n in ["a", "b"]]
        results = await asyncio.gather(*tasks)    # 4. 解包
    print(results)

asyncio.run(main())
```

**四个问题**

1. `time.sleep` 阻塞事件循环。
2. `asyncio.gather(tasks)` 把 list 当成一个参数，应该 `gather(*tasks)`。
3. 没有 `raise_for_status()`，4xx/5xx 会被当成成功解析。
4. 没设超时；而且每个请求都新建 `AsyncClient`，连接池没用上（改成一个 client 复用）。

---

## G. httpx 与流式

### G1 SSE 解析

```python
import json
from collections.abc import Iterable

def parse_sse(lines: Iterable[str]) -> str:
    parts: list[str] = []
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith(":"):
            continue
        if not line.startswith("data:"):
            continue
        payload = line[len("data:"):].strip()
        if payload == "[DONE]":
            break
        try:
            chunk = json.loads(payload)
            delta = chunk["choices"][0]["delta"].get("content")
        except (json.JSONDecodeError, KeyError, IndexError):
            continue
        if delta:
            parts.append(delta)
    return "".join(parts)
```

输出：

```text
'你好，世界'
```

**为什么**

- 注释行以 `:` 开头，是 keep-alive，不是数据。
- `[DONE]` 是 OpenAI 兼容接口的约定，不是 SSE 标准；SSE 标准只有 `data:` 帧。
- 流式 JSON 可能不完整或字段缺失，解析失败要跳过而不是让整个流崩。

---

### G2 httpx 请求 + 错误映射

```python
import httpx

class ApiError(Exception):
    pass

def get_json(client: httpx.Client, url: str) -> dict:
    try:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.json()
    except httpx.TimeoutException as e:
        raise ApiError(f"请求超时: {url}") from e
    except httpx.HTTPStatusError as e:
        raise ApiError(f"HTTP {e.response.status_code}: {url}") from e
```

**为什么**

- `raise_for_status` 把 4xx/5xx 变成异常，否则 `r.json()` 可能解析出一段错误页。
- 转成自己的 `ApiError`，上层只依赖一个异常类型；`from e` 保留原始类型。
- 复用 `Client` 能复用连接池和配置；`MockTransport` 让测试不依赖网络和真实服务。

---

### G3 异步 httpx 并发

```python
import asyncio
import time

import httpx

async def handler(request: httpx.Request) -> httpx.Response:
    await asyncio.sleep(0.2 if request.url.path == "/slow" else 0.05)
    return httpx.Response(200, json={"path": request.url.path})

async def main() -> None:
    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, timeout=2) as client:
        paths = ["/a", "/b", "/slow", "/c"]
        start = time.perf_counter()
        responses = await asyncio.gather(*(client.get(f"https://fake.test{p}") for p in paths))
        print([r.json() for r in responses], f"{time.perf_counter() - start:.2f}s")

asyncio.run(main())
```

输出：

```text
[{'path': '/a'}, {'path': '/b'}, {'path': '/slow'}, {'path': '/c'}] 0.20s
```

**为什么**

- 结果顺序 = `gather` 参数顺序，不是完成顺序（慢的 `/slow` 仍在第 3 位）。
- `AsyncClient` 支持并发使用，内部连接池会自动管理；**一个 client 全局复用**是推荐做法。

---

### G4 选型

1. httpx 同时支持同步/异步、HTTP/2，API 和 requests 接近，新项目没有理由选不能异步的 requests。
2. 老项目、只依赖 requests 的生态（部分插件、测试工具），或者维护旧代码时。
3. 同步是 `for line in resp.iter_lines()`；异步是 `async for line in resp.aiter_lines()`，且外层要 `async with client.stream(...)`。

---

## H. 综合实战

### H1 批量结构化抽取

```python
import asyncio
import time
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

class Ticket(BaseModel):
    category: Literal["refund", "logistics", "other"]
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=1, max_length=200)
    order_id: str | None = None

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

FIXED = {
    "q2": '{"category":"other","priority":2,"summary":"投诉","order_id":null}',
    "q3": '{"category":"logistics","priority":1,"summary":"物流慢","order_id":"ORD-3"}',
    "q4": '{"category":"other","priority":1,"summary":"咨询","order_id":"ORD-4"}',
}

async def mock_llm(question: str, feedback: str | None = None) -> str:
    if question == "q8":
        await asyncio.sleep(10)                 # 永远超时
    await asyncio.sleep(0.02)
    if feedback is not None and question in FIXED:
        return FIXED[question]                  # 模拟「模型看到错误后改对了」
    return RAW[question]

async def extract_one(question: str, sem: asyncio.Semaphore, stats: dict) -> dict:
    async with sem:
        stats["active"] += 1
        stats["max_active"] = max(stats["max_active"], stats["active"])
        try:
            feedback = None
            last_error: Exception | None = None
            for attempt in range(1, 4):
                try:
                    raw = await asyncio.wait_for(
                        mock_llm(question, feedback), timeout=0.3
                    )
                    ticket = Ticket.model_validate_json(raw)
                    return {
                        "q": question, "ok": True, "attempts": attempt,
                        "data": ticket.model_dump(),
                    }
                except ValidationError as e:
                    last_error = e
                    feedback = str(e)           # 把错误回灌给模型
                except asyncio.TimeoutError as e:
                    last_error = e
                    feedback = None
                await asyncio.sleep(0.01 * 2 ** (attempt - 1))

            return {
                "q": question, "ok": False,
                "error": f"{type(last_error).__name__}: {last_error}",
            }
        finally:
            stats["active"] -= 1

async def batch(questions: list[str], concurrency: int = 3) -> dict:
    sem = asyncio.Semaphore(concurrency)
    stats = {"active": 0, "max_active": 0}
    start = time.perf_counter()

    results = await asyncio.gather(
        *(extract_one(q, sem, stats) for q in questions),
        return_exceptions=True,
    )
    normalized = [
        r if not isinstance(r, Exception)
        else {"q": "?", "ok": False, "error": f"UNEXPECTED {r!r}"}
        for r in results
    ]

    return {
        "elapsed": round(time.perf_counter() - start, 2),
        "max_active": stats["max_active"],
        "success": [r for r in normalized if r["ok"]],
        "failed": [r for r in normalized if not r["ok"]],
    }

if __name__ == "__main__":
    report = asyncio.run(batch(list(RAW)))
    print("elapsed", report["elapsed"], "max_active", report["max_active"])
    print("success", len(report["success"]),
          [(r["q"], r["attempts"]) for r in report["success"]])
    print("failed", len(report["failed"]),
          [(r["q"], r["error"].splitlines()[0]) for r in report["failed"]])
```

输出：

```text
elapsed 1.05 max_active 3
success 6 [('q1', 1), ('q2', 2), ('q3', 2), ('q4', 2), ('q5', 1), ('q6', 1)]
failed 2 [('q7', 'ValidationError: 1 validation error for Ticket'), ('q8', 'TimeoutError: ')]
```

**接真实 API 时改哪里**

- 只替换 `mock_llm`：内部改成 `AsyncOpenAI` + `chat.completions.create`，把 `str(e)` 拼进 messages 再发一次。
- 超时按模型 p99 设（如 30–60s），别用 0.3；重试次数 2–3 次足够，退避从 1s 起。
- `Semaphore` 按账号 RPM/TPM 设置，通常 5–20。

---

### H2 拆包重构

`exercises/h2_pkg/models.py`：

```python
from typing import Literal

from pydantic import BaseModel, Field

class Ticket(BaseModel):
    category: Literal["refund", "logistics", "other"]
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=1, max_length=200)
    order_id: str | None = None
```

`client.py`（只放「怎么调模型」，不关心报告格式）：

```python
import asyncio

from pydantic import ValidationError

from .models import Ticket

RAW = {
    "q1": '{"category":"refund","priority":3,"summary":"想退货","order_id":"ORD-1"}',
    "q2": '{"category":"complaint","priority":2,"summary":"投诉","order_id":null}',
}
FIXED = {"q2": '{"category":"other","priority":2,"summary":"投诉","order_id":null}'}

async def mock_llm(question: str, feedback: str | None = None) -> str:
    await asyncio.sleep(0.01)
    if feedback is not None and question in FIXED:
        return FIXED[question]
    return RAW[question]

async def extract_one(question: str, sem: asyncio.Semaphore) -> dict:
    async with sem:
        feedback = None
        for attempt in range(1, 3):
            try:
                raw = await asyncio.wait_for(mock_llm(question, feedback), timeout=1)
                return {
                    "q": question, "ok": True, "attempts": attempt,
                    "data": Ticket.model_validate_json(raw).model_dump(),
                }
            except ValidationError as e:
                feedback = str(e)
        return {"q": question, "ok": False, "error": "invalid after retries"}
```

`main.py`：

```python
import asyncio
import json

from .client import extract_one

async def batch(questions: list[str], concurrency: int = 3) -> list[dict]:
    sem = asyncio.Semaphore(concurrency)
    return await asyncio.gather(*(extract_one(q, sem) for q in questions))

def main() -> None:
    results = asyncio.run(batch(["q1", "q2"]))
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
```

运行：

```bash
cd exercises
python -m h2_pkg.main
```

**为什么**

- `models.py` 不依赖 IO，任何层都能 import，不会循环。
- `python main.py` 把当前目录当模块搜索路径，包内相对 import 会失败；`python -m h2_pkg.main` 从父目录开始，`h2_pkg` 是一个完整包，相对 import 正常。
- 这正是教程 §12 想让你形成的项目结构。

---

## 最后自检

能不看答案完成 H1，并回答下面四个问题，就达到「够用线」：

1. `dict.get(k, 0)` 和 `d[k]` 的区别？
2. 为什么 `@dataclass` 的 list 字段必须 `default_factory`？
3. pydantic 的 `ValidationError.errors()` 里 `loc` 是做什么用的？
4. `asyncio.gather` 和 `Semaphore` 分别解决什么问题？
