---
description: 从腾讯 cnb 拉取并合并；有冲突则中止不合并
---

从**腾讯 cnb** 拉取 `main` 并合并到本地。只碰 cnb，不动 origin / github。遇到冲突必须中止，绝不尝试自动解决冲突。

1. `git status --short`：如果有未提交改动，**停止**，告诉用户先提交或 `git stash`，不要动工作区。

2. `git fetch cnb main`

3. `git rev-list --count main..cnb/main`：为 0 表示远端没有新提交 → 回复「已是最新」并结束。

4. 预合并（可干净回滚）：

   ```
   git merge --no-commit --no-ff cnb/main
   ```

5. 判断结果：

   - 出现 `Already up to date` → 结束。
   - 有冲突（`git diff --name-only --diff-filter=U` 有输出）→ 执行 `git merge --abort`，然后报告：
     - 冲突文件列表
     - 「检测到冲突，已中止合并，工作区已还原，请手动处理」
     - **不要**给出自动合并方案，不要改文件。
   - 无冲突但停在合并中（`.git/MERGE_HEAD` 存在）→ `git commit --no-edit` 完成合并。

6. 成功后 `git log --oneline -3` 展示结果，并提示用户可以再执行 `/push` 同步到另外两个仓库。

全程**不要** `git push`，不要切换分支，不要 `git reset --hard`。
