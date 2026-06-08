# Contributing

感谢你对 `sporttery-odds-feishu` 的关注。

本项目当前聚焦：
- 中国福利彩票体育彩票竞彩足球官方数据查询
- 飞书消息通知
- 定时推送与 macOS `launchctl` 部署

如果你要贡献代码，建议先阅读：
- `README.md`
- `docs/INSTALL.md`
- `docs/DEPLOY.md`

## 开发原则

- 保持数据源稳定，优先使用官方结构化接口
- 不把核心逻辑改成脆弱的 HTML / DOM 抓取
- 命令行入口保持统一：
  - `python -m odds_tool.main ...`
- 飞书发送通道保持简单，继续使用 `lark-cli`
- 新增功能优先补测试

## 本地开发

### 1. 创建环境

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 运行测试

```bash
python -m pytest tests -q
```

### 3. 查看 CLI 帮助

```bash
python -m odds_tool.main --help
```

## 提交建议

推荐提交前自查：
- README 中命令示例是否仍然正确
- 定时推送说明是否与 `SCHEDULED_SEND_HOURS_BEIJING` 一致
- launchctl 说明是否与脚本保持一致
- 如果修改了查询行为，是否同时更新了飞书群查询说明

## Pull Request 建议

请在 PR 描述中说明：
- 修改目的
- 影响范围
- 测试结果
- 是否影响 README / docs

## 不建议的改动

- 直接把项目改造成网页爬虫式 DOM 解析
- 引入复杂且不必要的框架
- 改掉现有 CLI 主入口风格
- 在未更新文档的情况下变更用户命令
