# sporttery-odds-feishu

一个基于中国体彩竞彩足球官方数据的飞书通知工具。

这个项目可以：
- 查询当天竞彩足球比赛赔率
- 按球队名或场次号搜索比赛
- 监控指定球队当天比赛赔率变化
- 在固定时间将赔率信息推送到飞书群
- 通过 macOS `launchctl` 长期运行
- 当关键词命中多场比赛时，多场比赛一次性展示

适合场景：
- 在飞书群里接收指定球队的赔率更新
- 每天固定时间查看某支球队当天比赛赔率
- 将中国体彩竞彩足球赔率查询封装为可复用脚本工具

## 前置要求

在安装本项目前，请先安装并完成 `lark-cli` 配置：

- GitHub：<https://github.com/larksuite/cli>

本项目使用 `lark-cli` 作为飞书消息发送通道；如果未先安装 `lark-cli`，本项目无法正常发送飞书消息。

## 功能特性

- 官方数据源：使用中国体彩竞彩足球官方接口
- 支持两种查询方式：球队名、场次号
- 默认优先按球队名匹配，精确匹配优先，模糊匹配兜底
- 支持赔率展示：
  - 胜平负 `had`
  - 让球胜平负 `hhad`
- 支持单次查询、轮询监控、定时推送
- 使用 `lark-cli` 作为飞书消息发送通道
- 支持 macOS `launchctl` 部署

## 目录结构

```text
sporttery-odds-feishu/
├── odds_tool/                  # 核心源码
├── tests/                      # 测试代码
├── launchd/                    # launchctl 模板
├── config.example.json         # 示例配置
├── requirements.txt            # Python 依赖
├── run_watch.sh                # 监控启动脚本
├── run_scheduled_send.sh       # 定时推送启动脚本
├── install_launch_agent.sh     # 安装 launch agent 的脚本
├── README.md                   # 项目说明
├── LICENSE                     # 开源协议
└── .gitignore                  # Git 忽略规则
```

## 环境要求

- macOS（推荐，因项目内置了 `launchctl` 部署方案）
- Python 3.11 或更高版本
- 已安装并可用的 `lark-cli`
- 飞书账号，并已完成 `lark-cli` 登录授权

## 安装步骤

项目当前本地目录示例：

```bash
cd /Users/mac/Projects/sporttery-odds-feishu
```

### 1. 克隆仓库

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

如果你还没有安装 `lark-cli`，请先完成它的安装，并确保命令可直接执行：

```bash
lark-cli version
```

然后完成登录授权，例如：

```bash
lark-cli auth login
```

如果发送消息时报权限不足，可补充授权：

```bash
lark-cli auth login --scope "im:message.send_as_user"
```

### 4. 确认飞书群 chat_id

可以使用以下命令查询群：

```bash
lark-cli im +chat-list
```

或者：

```bash
lark-cli im +chat-search --name "你的群名称"
```

拿到目标群的 `chat_id` 后，用于后续通知和定时推送。

## 快速开始

### 1. 按球队名查询当天赔率

```bash
python -m odds_tool.main fetch --team 加拿大
```

### 2. 按场次号查询当天赔率

```bash
python -m odds_tool.main fetch --match-num 周五204
```

### 3. 发送查询结果到飞书群

```bash
python -m odds_tool.main fetch --team 加拿大 --notify --target oc_xxx
```

### 4. 供 Hermes / 飞书网关调用的查询入口

```bash
python -m odds_tool.main feishu-query --text "查询 法国"
```

群里推荐交互格式：
- `@机器人 查询 法国`
- `@机器人 查询 周四201`

## 监控指定球队赔率变化

轮询监控指定球队当天比赛，只有赔率变化时才发送消息。

```bash
python -m odds_tool.main watch-team --team 加拿大 --interval 60 --target oc_xxx
```

参数说明：
- `--team`：要监控的球队名
- `--interval`：轮询间隔，单位秒，默认 `60`
- `--target`：飞书群 `chat_id`
- `--cache`：缓存文件路径，默认 `cache/odds_cache.json`

说明：
- 首次运行只建立基线，不发送变化通知
- 后续只有赔率变化时才发送消息
- 默认只比较当天命中的目标比赛

## 定时推送当前球队赔率

每天固定时段向飞书群推送当前球队当天比赛赔率。

```bash
python -m odds_tool.main scheduled-send --team 日本 --target oc_demo
```

参数说明：
- `--team`：球队名
- `--target`：飞书群 `chat_id`
- `--cache`：兼容参数，默认 `cache/odds_cache.json`
- `--state`：定时发送状态文件，默认 `cache/scheduled_send_state.json`

当前默认发送时间：
- 北京时间 `08:00`
- 北京时间 `21:00`

限制说明：
- 仅支持整点小时
- 使用 24 小时制
- 按北京时间判断是否到点发送

时间配置位置：
- 文件：`odds_tool/main.py`
- 常量：`SCHEDULED_SEND_HOURS_BEIJING = [8, 21]`
- 通过修改源码中的 `SCHEDULED_SEND_HOURS_BEIJING` 改时间

如果你要修改整点推送时间，直接修改这个列表即可，例如：

```python
SCHEDULED_SEND_HOURS_BEIJING = [9, 18, 22]
```

## macOS launchctl 部署

推荐方式：让 `launchctl` 每小时整点触发一次，由程序内部判断是否到点发送。
也就是说，建议每小时触发一次，不要只在 08:00 和 21:00 各触发一次。

### 1. 生成 LaunchAgent

```bash
./install_launch_agent.sh 加拿大 oc_xxx
```

如果要自定义缓存和状态文件：

```bash
./install_launch_agent.sh 加拿大 oc_xxx cache/odds_cache.json cache/scheduled_send_state.json
```

默认会生成：

```text
~/Library/LaunchAgents/com.herry.sporttery-football-odds.plist
```

### 2. 加载服务

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.herry.sporttery-football-odds.plist 2>/dev/null || true
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.herry.sporttery-football-odds.plist
```

### 3. 立即触发一次

```bash
launchctl kickstart -k gui/$(id -u)/com.herry.sporttery-football-odds
```

### 4. 查看服务状态

```bash
launchctl print gui/$(id -u)/com.herry.sporttery-football-odds
```

### 5. 查看日志

```bash
tail -f logs/sporttery-football-odds.out.log logs/sporttery-football-odds.err.log
log stream --predicate 'process == "python" OR eventMessage CONTAINS "com.herry.sporttery-football-odds"' --style compact
```

### 6. 卸载服务

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.herry.sporttery-football-odds.plist
```

## 常见问题

### 1. 为什么查询不到比赛？

常见原因：
- 当天没有该球队比赛
- 当天官方没有可售比赛
- 关键词未匹配到当天场次

项目会尽量区分：
- 当天无比赛 / 无销售
- 当天有比赛，但没匹配到关键词
- 系统级错误

### 2. 为什么第一次监控没有推送？

因为第一次运行只建立基线，避免把首次抓取当作赔率变化。

### 3. 为什么定时推送命令执行了但没有消息？

因为 `scheduled-send` 只会在配置的北京时间整点窗口发消息。
如果当前时间不在窗口内，程序会静默退出。

### 4. 发送飞书消息时报 `missing_scope`

重新授权：

```bash
lark-cli auth login --scope "im:message.send_as_user"
```

### 5. 我不知道飞书群 chat_id

可以用：

```bash
lark-cli im +chat-list
```

或：

```bash
lark-cli im +chat-search --name "你的群名称"
```

## 开发与测试

### 运行测试

```bash
python -m pytest tests -q
```

### 查看 CLI 帮助

```bash
python -m odds_tool.main --help
```

## 数据来源说明

本项目使用中国体彩竞彩足球官方网页背后的结构化接口数据进行处理。
适合作为查询、监控和飞书通知工具，不建议改为基于页面 DOM 的脆弱爬虫实现。

## 免责声明

本项目仅用于信息查询、学习和自动化通知，不构成任何投注建议。
请以中国体彩官方页面与实际售卖信息为准。
