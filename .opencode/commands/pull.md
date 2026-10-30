---
description: 从 GitHub 拉取并合并；有冲突立即中止、不改动工作区
---

从**主仓库 GitHub** 拉取 `main` 并合并到本地。只碰 `github`，不动 `origin`（GitCode 只是镜像，推送时由 `/push` 同步）。**遇到冲突必须中止**，绝不尝试自动解决冲突，留给用户手动处理。

1. `git status --short`：如果有未提交改动，**停止**，告诉用户先提交或 `git stash`，不要动工作区。

2. 确认当前在 `main` 分支（`git rev-parse --abbrev-ref HEAD`）。不是则停止，不要自动切换。

3. `git fetch github main`

4. `git rev-list --count main..github/main`：为 0 表示远端没有新提交 → 回复「已是最新」并结束。

5. 先无侵入预检冲突（不改工作区）：

   ```
   git merge-tree --write-tree --name-only main github/main
   ```

   - 退出码为 0 → 无冲突，进入第 6 步。
   - 退出码非 0 → **检测到冲突**，输出冲突文件列表（该命令 stdout 的最后一节），然后报告：
     - 冲突文件列表
     - 「检测到冲突，已停止，工作区未做任何改动，请手动处理」
     - **不要**执行合并、不要改文件、不要给自动合并方案。
   - 如果 `git merge-tree` 不支持（老版本 git，报错 unknown option）→ 跳过预检，直接进入第 6 步，靠第 7 步兜底。

6. 正式合并（`--no-commit` 便于干净回滚）：

   ```
   git merge --no-commit --no-ff github/main
   ```

7. 判断结果：

   - `Already up to date` → 结束。
   - 有冲突（`git diff --name-only --diff-filter=U` 有输出）→ `git merge --abort`，然后报告冲突文件列表 + 「检测到冲突，已中止合并，工作区已还原，请手动处理」。
   - 无冲突但停在合并中（`.git/MERGE_HEAD` 存在）→ `git commit --no-edit` 完成合并。

8. 成功后 `git log --oneline -3` 展示结果，并提示用户可以再执行 `/push` 把合并结果同步到 GitCode 镜像。

全程**不要** `git push`，不要切换分支，不要 `git reset --hard`，不要自动解决冲突。
