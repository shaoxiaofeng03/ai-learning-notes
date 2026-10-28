# notes/siyuan/ — 思源笔记导出目录（自动生成）

⚠️ **这里的 `.md` 是思源笔记的镜像，不要直接编辑**——下次导出会被覆盖。
要改内容，请改思源里的原文，然后重新导出。

## 重新导出

```bash
python3 scripts/siyuan_export.py            # 导出
python3 scripts/siyuan_export.py --prune    # 同时删除思源里已删除的文档
python3 scripts/siyuan_export.py --dry-run  # 只看会写哪些文件
```

前提：思源桌面端正在运行（内核监听 `127.0.0.1:6806`）。

配置读取顺序：

| 变量 | 默认值 |
|---|---|
| `SIYUAN_WORKSPACE` | `~/Documents/sy` |
| `SIYUAN_PORT` | `conf.json` 的 `system.port`，再退到 `6806` |
| `SIYUAN_TOKEN` | `conf.json` 的 `api.token` |

## 目录约定

```
notes/siyuan/
├── <笔记本名>/<层级路径>/<文档名>.md
└── assets/                      # 思源 data/assets 里的全部资源
```

导出时会自动把 `assets/xxx.png` 改写成正确的相对路径，图片能直接在站点里显示。

## 边界

| 目录 | 谁维护 | 可否手改 |
|---|---|---|
| `notes/*.md` | 你 / AI | ✅ |
| `notes/siyuan/**` | 思源导出脚本 | ❌ 会被覆盖 |
| `projects/**` | 代码练习 | ✅ |

思源 → 仓库是**单向**的。仓库里的改动不会回流到思源。
