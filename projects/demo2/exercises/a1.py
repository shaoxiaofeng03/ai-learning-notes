# 实现 `top_words(text: str, n: int = 3) -> list[tuple[str, int]]`：
#
# 1. 转小写，只保留字母和 `'`（用 `re.findall`）。
# 2. 用普通 `dict` 计数，**不要用 `collections.Counter`**。
# 3. 按「次数降序、同次数按单词字典序升序」排序，取前 `n` 个。
# assert top_words(TEXT) == [("the", 4), ("fox", 3), ("dog", 2)]
# assert top_words(TEXT, 1) == [("the", 4)]
import re

TEXT = "The quick brown fox jumps over the lazy dog. The dog barks; the fox runs. A quick fox!"


def top_words(text: str, n: int = 3) -> list[tuple[str, int]]:
    words = re.findall(r"[a-z']+", text.lower())
    counts: dict[str, int] = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return items[:n]


assert top_words(TEXT) == [("the", 4), ("fox", 3), ("dog", 2)]
assert top_words(TEXT, 1) == [("the", 4)]
