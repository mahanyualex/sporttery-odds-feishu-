# README / 文档改版实施计划

> **For implementer:** Use TDD throughout. Write failing test first. Watch it fail. Then implement.

**Goal:** 重构 `sporttery-odds-feishu` 的 GitHub 仓库首页与核心文档，使其更美观、更适合公开展示，并保持现有功能说明、安装说明、部署说明和中英文双语入口完整可用。

**Architecture:** 采用“信息架构重排 + 文案重写 + 导航补强 + 不改核心代码”的方式，只改 README 和文档层。优先提升首页可读性、安装路径清晰度和新用户理解成本。

**Tech Stack:** Markdown, GitHub README conventions, existing repository docs.

---

### Task 1: 重写中文 README 首页结构

**Files:**
- Modify: `README.md`
- Test: 人工检查 + 现有 README 相关测试

### Task 2: 重写英文 README 首页结构

**Files:**
- Modify: `README.en.md`
- Test: 人工检查

### Task 3: 优化安装与部署文档导航

**Files:**
- Modify: `docs/INSTALL.md`
- Modify: `docs/DEPLOY.md`
- Modify: `docs/INSTALL.en.md`
- Modify: `docs/DEPLOY.en.md`

### Task 4: 验证、提交并推送

**Files:**
- Verify docs and tests
- Commit and push to `origin/main`
