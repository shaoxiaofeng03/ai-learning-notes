# -*- coding: utf-8 -*-
"""
step4-exception-json.py · 异常处理、JSON 与文件（Java 开发者对照版）

覆盖：try/except/finally、自定义异常 + raise from、with 上下文、JSON、pathlib。
运行：python step4-exception-json.py   （纯 Python，不需要 API Key）

Java → Python：
    try/catch/finally          → try/except/finally
    throw new XxxException(msg) → raise RuntimeError(msg)
    异常链 new X(msg, e)        → raise ... from e
    try-with-resources         → with ...（自动关闭）
    ObjectMapper               → json 模块
    java.nio.file.Path         → pathlib.Path
"""

import json
from pathlib import Path


def section(title: str) -> None:
    print("\n" + "=" * 52)
    print(title)
    print("=" * 52)


# ---------- 1. 自定义异常 ----------
class LLMError(Exception):
    """所有 LLM 相关异常的基类"""


class OutputTruncated(LLMError):
    """模型输出被截断（finish_reason == 'length'）"""


# ---------- 2. 一个会解析 JSON 的函数 ----------
def parse_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        # raise ... from e：保留原始异常堆栈（≈ Java 的 new Xxx(msg, e)）
        raise OutputTruncated("模型输出的 JSON 不合法") from e


# ---------- 3. JSON 三个必设参数 ----------
def to_pretty(obj) -> str:
    return json.dumps(
        obj,
        ensure_ascii=False,   # 中文不转 \uXXXX（必设）
        indent=2,             # 格式化
        default=str,          # 遇到 datetime 等不可序列化对象的兜底
    )


if __name__ == "__main__":
    section("try/except/else/finally")
    try:
        result = parse_json('{"ok": true}')
    except LLMError as e:
        print(f"解析失败：{e}")
    else:
        print("成功，无异常才执行", result)   # else：Java 没有，很少用
    finally:
        print("一定执行（≈ finally）")

    # 异常链：捕获到根因
    try:
        parse_json('{不是合法 JSON}')
    except OutputTruncated as e:
        print(f"捕获到：{e.__class__.__name__}：{e}")

    section("JSON 序列化")
    data = {"name": "sky", "city": "南京", "score": 95.5}
    print(to_pretty(data))

    # 用 get 替代 try/except 做流程控制（三大禁忌之一）
    d = {"a": 1}
    v = d.get("b", 0)           # ✅ 而不是 try: d["b"] except KeyError
    print("d.get('b', 0) =", v)

    section("with 上下文管理器（≈ try-with-resources）")
    # with 退出自动 close，等价 Java 的 try-with-resources
    out = Path("step4-demo.json")
    out.write_text(to_pretty(data), encoding="utf-8")

    with open(out, encoding="utf-8") as f:
        loaded = json.load(f)
    print("读回文件：", loaded)

    section("pathlib（别用 os.path）")
    p = Path(".")
    print("当前目录 .py 文件：", [f.name for f in p.glob("*.py")])
    print("step4-demo.json 存在：", out.exists())

    # 清理演示文件
    out.unlink(missing_ok=True)
    print("已删除临时文件 step4-demo.json")

    print("\n✅ 本步完成。核心记住：raise ... from e 保留根因；with 自动关闭；JSON 必设 ensure_ascii=False。")
