# Git上传项目到GitHub操作指南

本文档记录了如何将本地项目上传到GitHub仓库的完整流程。

## 前提条件

- 已在GitHub上创建远程仓库
- 本地已安装Git
- 本地项目已初始化为Git仓库

## 操作步骤

### 1. 检查Git远程仓库配置

首先检查当前项目是否已配置远程仓库：

```bash
git remote -v
```

**输出示例：**
```
origin  https://github.com/majiayong/newMonitorRobustWIN.git (fetch)
origin  https://github.com/majiayong/newMonitorRobustWIN.git (push)
```

**说明：**
- `origin` 是远程仓库的默认名称
- `fetch` 表示从远程仓库拉取代码的地址
- `push` 表示推送代码到远程仓库的地址

**如果没有配置远程仓库，需要添加：**
```bash
git remote add origin https://github.com/用户名/仓库名.git
```

### 2. 查看当前文件状态

检查哪些文件被修改或需要添加：

```bash
git status
```

**输出示例：**
```
On branch main
Your branch is ahead of 'origin/main' by 1 commit.

Changes not staged for commit:
  modified:   .github/workflows/build.yml
  modified:   README-RUNNER.md
  modified:   buildozer.spec

Untracked files:
  .claude/
  WINDOWS_SETUP.md
  WIN需要的安装.txt
```

**状态说明：**
- `Changes not staged for commit`: 已修改但未添加到暂存区的文件
- `Untracked files`: 新文件，Git还未跟踪
- `Your branch is ahead of 'origin/main' by X commits`: 本地分支领先远程分支X个提交

### 3. 配置.gitignore（重要）

在上传前，需要排除不应该上传的文件和目录。编辑`.gitignore`文件：

```bash
# 常见的应该忽略的内容

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# IDE配置
.idea/
.vscode/

# Claude Code配置（不应上传）
.claude/

# 构建产物
build/
dist/
*.egg-info/

# 日志文件
*.log

# 系统文件
.DS_Store
Thumbs.db
```

**为什么要使用.gitignore？**
- 避免上传敏感信息（如密钥、配置文件）
- 避免上传临时文件和构建产物
- 保持仓库干净，只包含源代码
- 减小仓库体积

### 4. 添加文件到暂存区

将需要上传的文件添加到暂存区：

```bash
# 添加单个文件
git add 文件名

# 添加多个文件
git add 文件1 文件2 文件3

# 添加所有修改的文件（不包括.gitignore中的文件）
git add .

# 添加所有已跟踪文件的修改
git add -u
```

**本次操作示例：**
```bash
git add .gitignore .github/workflows/build.yml README-RUNNER.md buildozer.spec WINDOWS_SETUP.md "WIN需要的安装.txt" "WIN的java环境不如意排查.txt"
```

**注意：**
- 文件名包含空格时需要用引号括起来
- 使用`git add .`会添加所有未被.gitignore忽略的文件

再次查看状态确认：
```bash
git status
```

输出会显示哪些文件在暂存区（准备提交）：
```
Changes to be committed:
  modified:   .github/workflows/build.yml
  modified:   .gitignore
  new file:   WINDOWS_SETUP.md
  ...
```

### 5. 创建提交（Commit）

将暂存区的文件提交到本地仓库：

```bash
git commit -m "提交说明"
```

**良好的提交说明格式：**

```bash
git commit -m "$(cat <<'EOF'
标题：简短描述本次修改（50字以内）

详细说明：
- 修改点1
- 修改点2
- 修改点3

相关信息：
- 修复的issue编号
- 相关文档链接
EOF
)"
```

**本次操作示例：**
```bash
git commit -m "$(cat <<'EOF'
更新Windows配置文件和文档

- 更新GitHub Actions构建配置
- 更新Runner文档
- 更新buildozer配置
- 添加Windows设置文档和安装说明
- 将.claude/目录添加到.gitignore

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

**提交说明最佳实践：**
- 第一行是简短的标题（不超过50个字符）
- 空一行后是详细说明
- 使用列表说明具体修改内容
- 使用现在时态（"添加"而非"添加了"）
- 说明为什么修改，而不仅仅是修改了什么

### 6. 推送到远程仓库

将本地提交推送到GitHub：

```bash
git push origin main
```

**命令说明：**
- `git push`: 推送命令
- `origin`: 远程仓库名称
- `main`: 分支名称（有些仓库可能是`master`）

**首次推送可能需要：**
```bash
# 设置上游分支并推送
git push -u origin main

# 或者如果远程没有main分支
git push --set-upstream origin main
```

**输出示例：**
```
To https://github.com/majiayong/newMonitorRobustWIN.git
 * [new branch]      main -> main
```

### 7. 验证上传结果

推送成功后，可以：

1. 访问GitHub仓库网址查看文件
2. 使用命令检查：

```bash
# 查看最近的提交历史
git log --oneline -5

# 查看远程分支状态
git remote show origin

# 确认本地和远程分支同步
git status
```

**成功的状态应该显示：**
```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

## 常见问题和解决方案

### 问题1：推送时提示权限错误

**错误信息：**
```
Permission denied (publickey)
```

**解决方案：**
1. 配置SSH密钥或使用HTTPS方式
2. 使用GitHub个人访问令牌（Personal Access Token）

```bash
# 使用HTTPS推送（会提示输入用户名和密码/令牌）
git push https://github.com/用户名/仓库名.git main
```

### 问题2：推送被拒绝（远程有更新）

**错误信息：**
```
! [rejected]        main -> main (fetch first)
error: failed to push some refs to 'https://github.com/...'
```

**解决方案：**
```bash
# 先拉取远程更新
git pull origin main

# 如果有冲突，解决后再推送
git push origin main
```

### 问题3：不小心添加了不该上传的文件

**解决方案：**
```bash
# 从暂存区移除（文件仍保留在工作目录）
git reset HEAD 文件名

# 或者从Git完全删除（文件也从工作目录删除）
git rm --cached 文件名

# 然后将文件添加到.gitignore
echo "文件名" >> .gitignore
```

### 问题4：想撤销上一次提交

```bash
# 撤销提交但保留修改（修改回到暂存区）
git reset --soft HEAD~1

# 撤销提交和暂存（修改回到工作区）
git reset HEAD~1

# 完全撤销提交和修改（危险操作！）
git reset --hard HEAD~1
```

## Git工作流程图

```
工作目录（Working Directory）
    ↓ git add
暂存区（Staging Area）
    ↓ git commit
本地仓库（Local Repository）
    ↓ git push
远程仓库（Remote Repository - GitHub）
```

## 常用Git命令速查表

| 命令 | 说明 |
|------|------|
| `git status` | 查看当前状态 |
| `git add <file>` | 添加文件到暂存区 |
| `git add .` | 添加所有文件到暂存区 |
| `git commit -m "message"` | 提交到本地仓库 |
| `git push origin main` | 推送到远程main分支 |
| `git pull origin main` | 拉取远程main分支 |
| `git log` | 查看提交历史 |
| `git diff` | 查看修改内容 |
| `git branch` | 查看分支 |
| `git checkout -b <branch>` | 创建并切换分支 |
| `git remote -v` | 查看远程仓库 |

## 最佳实践建议

1. **频繁提交**：小步快跑，每完成一个功能点就提交
2. **清晰的提交信息**：让其他人（和未来的自己）能快速理解修改内容
3. **推送前先拉取**：避免冲突
4. **使用分支**：主分支保持稳定，在功能分支上开发
5. **定期同步**：及时推送本地修改，避免长时间不同步
6. **检查.gitignore**：确保不上传敏感信息和临时文件
7. **推送前检查**：使用`git status`和`git diff`确认修改内容

## 参考资源

- [Git官方文档](https://git-scm.com/doc)
- [GitHub官方指南](https://docs.github.com/)
- [Git可视化学习](https://learngitbranching.js.org/)

---

**文档创建日期**: 2025-12-18
**适用版本**: Git 2.x
