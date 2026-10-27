# demo2 · Python 够用线动手练习

对应学习路线图 W1「Python 够用线」（[W1-Python够用线教程.md](../../notes/W1-Python够用线教程.md)）的 Day 2–3 执行清单。目标不是精通 Python，而是**能写评测脚本、能调 SDK、能读开源项目、能写 RAG/Agent 服务**。

每个 step 都是可独立运行的脚本，Java 开发者对照注释，建议**自己敲一遍**，不要复制粘贴。

## 环境

```bash
cd /home/sky/Documents/AI/projects/demo2
source .venv/bin/activate          # 虚拟环境已存在
pip install -r requirements.txt    # 依赖已装好（openai / httpx / pydantic / python-dotenv）
```

## 步骤清单

| 文件 | 主题 | 需要 Key |
|---|---|---|
| [step1-data.py](step1-data.py) | 变量/真值、字符串、list/dict/set/tuple、切片、推导式、可变 vs 不可变 | ❌ |
| [step2-function.py](step2-function.py) | 函数、可变默认参数坑、`*args/**kwargs`、lambda、闭包坑 | ❌ |
| [step3-class.py](step3-class.py) | 类、`@dataclass`（≈ record）、`field(default_factory)`、typing | ❌ |
| [step4-exception-json.py](step4-exception-json.py) | 异常处理、`raise ... from`、`with`、JSON、pathlib | ❌ |
| [step5-pydantic.py](step5-pydantic.py) | pydantic BaseModel、Field 约束、`model_validate_json`、自定义校验 | ❌ |
| [step6-async.py](step6-async.py) | `asyncio.run`/`await`/`gather`/`Semaphore`/`wait_for` | ❌ |
| [step7-pydantic-llm.py](step7-pydantic-llm.py) | 结构化输出：pydantic + LLM + 校验 + 错误回灌 + 重试 | ✅ |
| [step8-async-llm.py](step8-async-llm.py) | 并发调模型：`AsyncOpenAI` + 限流 + 超时 + 指数退避 | ✅ |
| [step9-httpx-stream.py](step9-httpx-stream.py) | httpx 同步请求 + 手写 SSE 流式解析 | ✅ |

## 运行

```bash
# 纯 Python 部分（直接跑）
python step1-data.py
python step2-function.py
python step3-class.py
python step4-exception-json.py
python step5-pydantic.py
python step6-async.py

# LLM 部分（先设 key）
export DEEPSEEK_API_KEY="sk-xxx"
# 或 cp .env.example .env 并填入 key（脚本会自动 load_dotenv）
python step7-pydantic-llm.py
python step8-async-llm.py
python step9-httpx-stream.py
```

## 做完的标志

能不看文档写出「带 pydantic 校验的 LLM 调用 + 并发批量 + 错误重试」，并能解释每一步为什么这么写。
