# sporttery-odds-feishu

> 中国体彩竞彩足球赔率查询、监控与飞书通知工具。

[English README](./README.en.md) · [安装文档](./docs/INSTALL.md) · [部署文档](./docs/DEPLOY.md)

## 项目简介

`sporttery-odds-feishu` 是一个围绕中国体彩竞彩足球官方数据构建的自动化工具。

它适合以下场景：
- 查询当天竞彩足球比赛赔率
- 按球队名或比赛编号搜索目标比赛
- 监控指定球队当天比赛的赔率变化
- 在固定时段将赔率信息推送到飞书群
- 通过 `launchctl` 在 macOS 上长期运行
- 关键词命中多场时，多场比赛一次性展示

## 为什么用它

相比手动打开网页反复查询，这个项目更适合自动化使用：
- 使用官方结构化接口，不依赖脆弱的网页 DOM 抓取
- 支持按球队名或场次号快速定位比赛
- 支持轮询监控，只在赔率变化时推送
- 支持定时推送，适合固定时段群内播报
- 使用 `lark-cli` 作为飞书消息通道，便于接入现有工作流

## 前置要求

在安装本项目前，请先安装并完成 `lark-cli` 配置：

- GitHub：<https://github.com/larksuite/cli>

本项目使用 `lark-cli` 作为飞书消息发送通道；如果未先安装 `lark-cli`，本项目无法正常发送飞书消息。

环境要求：
- macOS（推荐，项目内置 `launchctl` 部署方式）
- Python 3.11+
- 已完成登录授权的 `lark-cli`

## 核心能力

### 1. 查询当天赔率
支持两种查询方式：
- 球队名，例如：`加拿大`
- 比赛编号，例如：`周四201`

覆盖赔率类型：
- 胜平负 `had`
- 让球胜平负 `hhad`

### 2. 监控赔率变化
针对指定球队当天比赛建立基线并轮询：
- 首次运行只建基线，不发告警
- 后续仅在赔率发生变化时推送消息

### 3. 定时推送
默认按北京时间整点窗口发送：
- `08:00`
- `21:00`

限制说明：
- 仅支持整点小时
- 使用 24 小时制
- 按北京时间判断是否到点发送

调度策略：
- 建议每小时触发一次
- 推荐让 `launchctl` 每小时触发一次
- 由程序内部判断当前时段是否需要发送

### 4. 飞书群接入
项目可作为飞书群查询能力的下游执行器，支持固定命令形式：
- `@机器人 查询 法国`
- `@机器人 查询 周四201`

## 快速开始

### 1. 克隆仓库

当前本地目录示例：

```bash
cd /Users/mac/Projects/sporttery-odds-feishu
```

```bash
git clone <your-repo-url> sporttery-odds-feishu
cd sporttery-odds-feishu
```

### 2. 创建虚拟环境并安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 安装并登录 lark-cli

本项目依赖 `lark-cli` 发送飞书消息，因此请先安装并配置 `lark-cli`：

- GitHub：<https://github.com/larksuite/cli>

安装完成后确认命令可用：

```bash
lark-cli version
```

登录：

```bash
lark-cli auth login
```

如果后续发消息报权限不足：

```bash
lark-cli auth login --scope "im:message.send_as_user"
```

### 4. 获取目标飞书群 chat_id

```bash
lark-cli im +chat-list
```

或：

```bash
lark-cli im +chat-search --name "你的群名称"
```

## 常用命令

### 查询当天赔率

按球队名：

```bash
python -m odds_tool.main fetch --team 加拿大
```

按场次号：

```bash
python -m odds_tool.main fetch --match-num 周五204
```

发送到飞书群：

```bash
python -m odds_tool.main fetch --team 加拿大 --notify --target oc_xxx
```

### 监控指定球队赔率变化

```bash
python -m odds_tool.main watch-team --team 加拿大 --interval 60 --target oc_xxx
```

### 定时推送

```bash
python -m odds_tool.main scheduled-send --team 日本 --target oc_demo
```

### Hermes / 飞书网关查询入口

```bash
python -m odds_tool.main feishu-query --text "查询 法国"
```

## 文档导航

- 中文安装文档：[`docs/INSTALL.md`](./docs/INSTALL.md)
- 中文部署文档：[`docs/DEPLOY.md`](./docs/DEPLOY.md)
- 英文 README：[`README.en.md`](./README.en.md)
- English install guide: [`docs/INSTALL.en.md`](./docs/INSTALL.en.md)
- English deploy guide: [`docs/DEPLOY.en.md`](./docs/DEPLOY.en.md)
- 飞书群查询接入说明：[`docs/plans/2026-06-04-feishu-group-query-gateway-notes.md`](./docs/plans/2026-06-04-feishu-group-query-gateway-notes.md)

## launchctl 快速部署示例

推荐每小时触发一次，由程序内部判断是否到点发送。

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.herry.sporttery-football-odds.plist 2>/dev/null || true
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.herry.sporttery-football-odds.plist
launchctl kickstart -k gui/$(id -u)/com.herry.sporttery-football-odds
launchctl print gui/$(id -u)/com.herry.sporttery-football-odds
log stream --predicate 'process == "python" OR eventMessage CONTAINS "com.herry.sporttery-football-odds"' --style compact
```

## 项目结构

```text
sporttery-odds-feishu/
├── odds_tool/                  # 核心源码
├── tests/                      # 测试代码
├── launchd/                    # launchctl 模板
├── docs/                       # 安装 / 部署 / 说明文档
├── .github/                    # CI、Issue、PR 模板
├── config.example.json         # 示例配置
├── requirements.txt            # Python 依赖
├── run_watch.sh                # 监控启动脚本
├── run_scheduled_send.sh       # 定时推送启动脚本
├── install_launch_agent.sh     # 安装 launch agent 的脚本
├── README.md                   # 中文 README
├── README.en.md                # 英文 README
└── LICENSE                     # 开源协议
```

## FAQ

### 为什么查询不到比赛？

常见原因：
- 当天没有该球队比赛
- 当天官方没有可售比赛
- 关键词未命中当天场次

项目会尽量区分：
- 当天无比赛 / 无销售
- 当天有比赛，但没匹配到关键词
- 真实系统错误

### 为什么第一次监控没有推送？

因为第一次运行只建立基线，避免把首次抓取当作赔率变化。

### 为什么 scheduled-send 执行了但没有消息？

因为 `scheduled-send` 只会在配置的北京时间窗口内发送；如果当前不在窗口内，程序会静默退出。

### 如何修改整点推送时间？

修改：
- 文件：`odds_tool/main.py`
- 常量：`SCHEDULED_SEND_HOURS_BEIJING = [8, 21]`
- 通过修改源码中的 `SCHEDULED_SEND_HOURS_BEIJING` 改时间

例如：

```python
SCHEDULED_SEND_HOURS_BEIJING = [9, 18, 22]
```

## 开发与测试

运行测试：

```bash
python -m pytest tests -q
```

查看 CLI 帮助：

```bash
python -m odds_tool.main --help
```

## 数据来源说明

本项目使用中国体彩竞彩足球官方页面背后的结构化接口数据进行处理。
适合作为查询、监控和飞书通知工具，不建议替换成基于网页 DOM 的脆弱抓取方案。

## 免责声明

本项目仅用于信息查询、学习与自动化通知，不构成任何投注建议。
请以中国体彩官方页面与实际售卖信息为准。
