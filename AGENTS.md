---
description: Central configuration and documentation for all AI coding agents across repositories
---

# AI Agents Configuration

This file defines how AI coding agents (Cursor, Antigravity, Claude Code, GitHub Copilot, etc.) should behave across all repositories in this workspace.

## Cross-Session State (Read This First)

Before doing anything else, read `.agents/STATE.md` if it exists. It is the
handover from whoever worked here last, possibly from a different tool or
machine.

This workspace is worked on by multiple agents: Gemini CLI, Antigravity, Mistral
CLI, Kiro, Codex, Pi, Hermes, opencode, Claude Code, Cursor, and others. Sessions
can end abruptly when a free-tier limit is hit. No harness can read every other
harness's private session store, so durable state lives in plain files that all
of them can read.

The state directory is:

```text
.agents/
  STATE.md      current task, progress, next steps
  JOURNAL.md    append-only decisions and rationale
  handoffs/     detailed handoff documents
```

`.agents/` is committed deliberately so state reaches the other machines. Never
write secrets or personal details there. These files are permanent and
world-readable in public repositories.

Treat `.agents/` as shared project state, not personal scratch space. In team
repos, write only what another teammate or agent needs to resume the work:
current task, decisions, blockers, linked issues or PRs, and safe next steps.
Do not write private notes, credentials, customer data, local machine paths that
should stay private, or anything that would be unsafe in a public repository.

Your obligations:

1. On start, read `.agents/STATE.md` if it exists.
2. As you work, update `.agents/STATE.md` after each meaningful step.
3. For durable decisions, append one dated line to `.agents/JOURNAL.md`.
4. Before a long or risky stretch, write a handoff in `.agents/handoffs/`.

Keep `STATE.md` short and current. Put durable decisions in `JOURNAL.md`. Put
detailed resume notes in timestamped files under `.agents/handoffs/` so multiple
people do not overwrite one another.

Memory tools such as cognee or cavemem are optional local aids. Trust
`.agents/STATE.md` and `git log` over an empty memory-tool result.

## Agent Types and Roles

### 1. Primary Coding Agent (Cursor/Claude Code)
**Purpose**: Main development assistant for code changes
**Capabilities**: Full codebase access, file editing, terminal commands
**Behavior**: Follows all conventions in this file

### 2. Review Agent (GitHub PR Review)
**Purpose**: Automated code review on pull requests
**Capabilities**: Read-only access to PR changes
**Behavior**: Strict adherence to coding standards

### 3. Documentation Agent
**Purpose**: Maintains and updates documentation
**Capabilities**: Can modify markdown files
**Behavior**: Never creates new docs without explicit request

### 4. Security Agent (TruffleHog, CodeQL)
**Purpose**: Security scanning and vulnerability detection
**Capabilities**: Full codebase scan
**Behavior**: Blocks PRs on security issues

## Universal Rules (Apply to All Agents)

### 1. File Operations
- **NEVER** create new markdown files without explicit user request
- **ALWAYS** update existing documentation when possible
- **NEVER** delete files without confirmation
- **ALWAYS** preserve file history and git history

### 2. Code Style
- Follow language-specific conventions (see skill files)
- Use consistent naming patterns
- Keep functions small and focused
- Add type hints for Python, TypeScript interfaces for JS

### 3. Git Conventions
- Commit messages: `type: description`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `style`
- Keep commits atomic and focused
- Never force push to main branches

### 4. Communication
- Be concise and direct
- Explain complex changes briefly
- Admit uncertainty when present
- Ask for clarification when requirements are ambiguous

## Repository-Specific Overrides

### source-repo-code (Template/Source)
- **Purpose**: Source of truth for shared configurations
- **Special Rules**: Changes here should be synced to all repos

## Skill System

Do not assume project-level skills are present in target repositories. The
current sync intentionally removes `skills/`, `skills-lock.json`, and `docs/`
from target repos, and `.claude/` remains local-only because it can contain
session databases and credentials.

If a harness has local skills installed, it may use them, but shared repo
instructions must live in `AGENTS.md` and shared handoff state must live under
`.agents/`.

### MCP Configuration

MCP support varies by harness. Use local MCP configuration if present, but do
not assume one shared MCP config is read by every agent.

## Syncing Strategy

### Source of Truth
- **Primary**: sourcerepo 仓库作为唯一真源（Skills、MCP、通用配置、仓库设置）
- **Secondary**: 目标仓库保留仓库特定覆盖（需在 sync 后自行维护）

### Sync Workflows
- **仓库设置与通用配置**：[`sync-repo-settings.yml`](<kfile name="sync-repo-settings.yml" path=".github/workflows/sync-repo-settings.yml">.github/workflows/sync-repo-settings.yml</kfile>) 负责传播 GitHub Actions、Dependabot、labels、`AGENTS.md` 等

### Sync Process
1. 在 sourcerepo 中修改通用配置
2. 推送到 `main` 分支自动触发相应 workflow
3. workflow 会遍历所有非 archive/fork 仓库，复制变更并提交/开 PR
4. 定时任务每日/每日执行，覆盖未来新仓库

### New Repository Setup
当创建新仓库时：
1. 将 sourcerepo 中的配置同步过去（由定时任务或手动触发完成）
2. 如需仓库特定覆盖，同步后手动维护
3. Read `AGENTS.md`, then read `.agents/STATE.md` if present

## Maintenance

### Quarterly Reviews
- Review and update skill files
- Check for outdated action versions
- Verify agent behavior consistency
- Update this configuration as needed

### Automated Monitoring
- Use Dependabot for dependency updates
- Use TruffleHog for secret scanning
- Use custom scripts to detect outdated GitHub Actions

## Troubleshooting

### Agent Not Following Conventions
1. 检查仓库特定覆盖在 AGENTS.md 中
2. 检查 `.agents/STATE.md` 中是否有最新任务上下文
3. 审阅近期约定变更
4. 从源重新同步配置

### Sync Failures
1. 使用相应 workflow 的 `workflow_dispatch` 手动触发以观察日志
2. 检查目标仓库中的 git 冲突
3. 验证文件权限
4. 查看同步日志中的具体错误

## References

- [GitHub Skills Documentation](https://docs.github.com/en/contributing/collaborating-with-github-docs/using-skills)
- [Cursor AI Documentation](https://docs.cursor.com/)
- [Claude Code Documentation](https://docs.anthropic.com/claude/code)
- [Dependabot Configuration](https://docs.github.com/en/code-security/dependabot)
