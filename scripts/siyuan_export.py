#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
思源笔记 → 当前仓库 notes/siyuan/ 单向导出

用法:
    python3 scripts/siyuan_export.py            # 导出
    python3 scripts/siyuan_export.py --prune    # 导出并删除已不存在的旧文件
    python3 scripts/siyuan_export.py --dry-run  # 只看会写哪些文件

前提: 思源桌面端正在运行（内核监听 127.0.0.1:6806）。

配置来源（优先级从高到低）:
    SIYUAN_WORKSPACE  工作空间目录，默认 ~/Documents/sy
    SIYUAN_PORT       内核端口，默认读 conf.json，再默认 6806
    SIYUAN_TOKEN      API Token，默认读 conf.json 的 api.token

注意: 这是单向同步。在 notes/siyuan/ 里手改的内容，下次导出会被覆盖。
      要改内容请改思源里的原文。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEST_ROOT = REPO_ROOT / "notes" / "siyuan"
KEEP_FILES = {"README.md"}

BAD_CHARS = re.compile(r'[<>:"\\|?*\x00-\x1f]')


def load_config() -> tuple[Path, int, str]:
    ws = Path(os.environ.get("SIYUAN_WORKSPACE", "~/Documents/sy")).expanduser()
    conf_path = ws / "conf" / "conf.json"
    conf = {}
    if conf_path.exists():
        conf = json.loads(conf_path.read_text(encoding="utf-8"))

    port = os.environ.get("SIYUAN_PORT") or (conf.get("system") or {}).get("port") or 6806
    token = os.environ.get("SIYUAN_TOKEN") or (conf.get("api") or {}).get("token") or ""
    return ws, int(port), token


def api(port: int, token: str, path: str, payload: dict | None = None):
    body = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=body,
        headers={"Authorization": f"Token {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        sys.exit(f"连不上思源内核 (127.0.0.1:{port})，请确认桌面端已启动: {exc}")
    if result.get("code") != 0:
        raise RuntimeError(f"{path} 失败: {result.get('msg')}")
    return result.get("data")


def safe_name(name: str) -> str:
    name = BAD_CHARS.sub("_", name).strip().strip(".")
    return name or "_"


def rewrite_assets(content: str, depth: int) -> str:
    """把 assets/xxx 改成相对 notes/siyuan/ 的正确层级。"""
    prefix = "../" * depth + "assets/"
    content = content.replace("](assets/", f"]({prefix}")
    content = content.replace('src="assets/', f'src="{prefix}')
    return content


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prune", action="store_true", help="删除本次未导出的旧 .md")
    parser.add_argument("--dry-run", action="store_true", help="只打印不写入")
    args = parser.parse_args()

    ws, port, token = load_config()
    if not token:
        sys.exit("找不到 API Token：请在思源 设置 → 关于 → API token 里复制，或设置 SIYUAN_TOKEN")

    notebooks = [
        nb for nb in api(port, token, "/api/notebook/lsNotebooks")["notebooks"]
        if not nb.get("closed") and not nb.get("encrypted")
    ]
    if not notebooks:
        sys.exit("没有可导出的笔记本（全部关闭或加密）")

    written: set[Path] = set()
    total = 0

    for nb in notebooks:
        stmt = (
            "SELECT id, hpath FROM blocks WHERE type='d' "
            f"AND box='{nb['id']}' ORDER BY hpath"
        )
        docs = api(port, token, "/api/query/sql", {"stmt": stmt})
        for doc in docs:
            parts = [p for p in doc["hpath"].strip("/").split("/") if p]
            if not parts:
                continue
            target = DEST_ROOT.joinpath(safe_name(nb["name"]), *[safe_name(p) for p in parts[:-1]])
            target = target / f"{safe_name(parts[-1])}.md"

            content = api(port, token, "/api/export/exportMdContent", {"id": doc["id"]})["content"]
            content = rewrite_assets(content, depth=len(parts))

            written.add(target)
            total += 1
            print(f"  {doc['hpath']}  →  {target.relative_to(REPO_ROOT)}")
            if not args.dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")

    # 资源文件：思源的 data/assets 是全局目录，统一放到 notes/siyuan/assets/
    src_assets = ws / "data" / "assets"
    dst_assets = DEST_ROOT / "assets"
    copied = 0
    if src_assets.is_dir():
        for item in src_assets.iterdir():
            if not item.is_file():
                continue
            target = dst_assets / item.name
            if target.exists() and target.stat().st_size == item.stat().st_size:
                continue
            if not args.dry_run:
                dst_assets.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)
            copied += 1

    # 清理已删除文档留下的孤儿文件
    removed = 0
    if args.prune and not args.dry_run and DEST_ROOT.exists():
        for path in DEST_ROOT.rglob("*.md"):
            if path in written or path.name in KEEP_FILES:
                continue
            path.unlink()
            removed += 1

    print(f"\n导出完成: {total} 篇文档, {copied} 个新资源" + (f", 清理 {removed} 个旧文件" if removed else ""))
    if args.dry_run:
        print("（--dry-run，未写入任何文件）")


if __name__ == "__main__":
    main()
