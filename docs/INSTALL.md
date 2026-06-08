# 安装说明

> 适用于第一次接触 `sporttery-odds-feishu` 的用户。

[返回中文 README](../README.md) · [英文安装文档](./INSTALL.en.md) · [部署文档](./DEPLOY.md)

## 安装前先确认

在安装本项目之前，你需要先准备好：
- Python 3.11+
- `lark-cli`（本项目依赖它发送飞书消息）
- 已登录并授权的飞书账号

`lark-cli` 项目地址：
- <https://github.com/larksuite/cli>

## 步骤 1：获取项目

```bash
git clone <your-repo-url> sporttery-odds-feishu
cd sporttery-odds-feishu
```

如果你是在当前机器的既有目录中使用，路径示例：

```bash
cd /Users/mac/Projects/sporttery-odds-feishu
```

## 步骤 2：创建 Python 虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 步骤 3：安装依赖

```bash
pip install -r requirements.txt
```

## 步骤 4：安装并登录 lark-cli

本项目依赖 `lark-cli` 发送飞书消息，因此请先安装并配置 `lark-cli`：

- GitHub：<https://github.com/larksuite/cli>

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

## 步骤 5：获取目标飞书群 chat_id

```bash
lark-cli im +chat-list
```

或者：

```bash
lark-cli im +chat-search --name "你的群名称"
```

## 步骤 6：验证安装

查看 CLI 帮助：

```bash
python -m odds_tool.main --help
```

运行测试：

```bash
python -m pytest tests -q
```

## 第一次查询示例

按球队名查询：

```bash
python -m odds_tool.main fetch --team 加拿大
```

按场次号查询：

```bash
python -m odds_tool.main fetch --match-num 周五204
```

飞书群查询入口：

```bash
python -m odds_tool.main feishu-query --text "查询 法国"
```
