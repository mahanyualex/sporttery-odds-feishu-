# 安装说明

本文档面向第一次接触该项目的用户，说明如何完成本地安装。

## 1. 获取项目

```bash
git clone <your-repo-url> sporttery-odds-feishu
cd sporttery-odds-feishu
```

如果你是在当前机器上的既有目录中使用，目录示例为：

```bash
cd /Users/mac/Projects/sporttery-odds-feishu
```

## 2. 创建 Python 虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 4. 安装并登录 lark-cli

先确认 `lark-cli` 可用：

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

## 5. 获取飞书群 chat_id

```bash
lark-cli im +chat-list
```

或者：

```bash
lark-cli im +chat-search --name "你的群名称"
```

## 6. 验证安装

查看 CLI 帮助：

```bash
python -m odds_tool.main --help
```

跑基础测试：

```bash
python -m pytest tests -q
```

## 7. 第一次查询

按球队名查询：

```bash
python -m odds_tool.main fetch --team 加拿大
```

按场次号查询：

```bash
python -m odds_tool.main fetch --match-num 周五204
```

飞书查询入口：

```bash
python -m odds_tool.main feishu-query --text "查询 法国"
```
