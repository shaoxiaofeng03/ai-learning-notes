---
description: 推送到三个仓库（主推 GitHub，触发 Pages 部署；同步 cnb + gitcode）
---

把当前目录的改动推送到三个远端。**主仓库是 GitHub**——GitHub Pages 从它构建发布；`cnb` 和 `origin`（gitcode）是镜像。

按顺序执行，任一环节失败立即停止并报告，不要重试、不要绕过：

0. 如果思源笔记桌面端在运行（`curl -s -m 3 -X POST http://127.0.0.1:6806/api/system/version` 有响应），先同步笔记：

   ```
   python3 scripts/siyuan_export.py
   ```

   - 成功 → 把 `notes/siyuan/` 的变更一起提交。
   - 连不上（思源没开）→ **跳过这一步**，不要报错中断，在最终报告里注明「思源未运行，本次未同步笔记」。

1. `git status --short` 检查工作区。
   - 如果输出里出现 `.env`、`*.key`、`token` 之类疑似密钥文件，**立即停止**并警告，不要提交。
   - 如果有未提交改动：先用一段话概括改动内容 + 拟用的中文 commit message，然后 `git add` 具体文件（不要无脑 `git add -A`，跳过 `.venv/`、`__pycache__/`、`.idea/`、`node_modules/`、`.vitepress/dist/`），`git commit`。
   - 如果工作区干净且本地没有领先提交（`git rev-list --count github/main..main` 为 0），直接回复「无需推送」并结束。

2. 依次推送，**GitHub 优先**（它决定线上站点何时更新）：

   ```
   git push github main
   git push cnb main
   git push origin main
   ```

   认证说明：`github` 和 `origin` 走 SSH 公钥，`cnb` 走 HTTPS + `~/.git-credentials` 里的 token。某个远端报认证失败时，只提示该远端怎么修，不要中断其他两个。

3. 核对：对每个远端执行 `git ls-remote --heads <remote> main`，与 `git rev-parse --short HEAD` 比对，输出对照表（远端 / 地址 / 提交 / 是否一致）。

4. 报告推送结果，并附上线上地址：

   ```
   https://shaoxiaofeng03.github.io/ai-learning-notes/
   ```

   GitHub 推送成功即会触发 Actions 部署，约 1–2 分钟后生效。**不要顺手改代码**，也不要执行提交以外的操作。
