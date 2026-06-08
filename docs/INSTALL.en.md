# Installation Guide

This document explains how to install `sporttery-odds-feishu` on a local machine.

## 1. Get the project

```bash
git clone <your-repo-url> sporttery-odds-feishu
cd sporttery-odds-feishu
```

If you are using the existing local directory on the current machine, the path example is:

```bash
cd /Users/mac/Projects/sporttery-odds-feishu
```

## 2. Create a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Install and log in to lark-cli

First confirm that `lark-cli` is available:

```bash
lark-cli version
```

Log in:

```bash
lark-cli auth login
```

If sending messages later fails because of missing permissions:

```bash
lark-cli auth login --scope "im:message.send_as_user"
```

## 5. Get the target Feishu group chat_id

```bash
lark-cli im +chat-list
```

or:

```bash
lark-cli im +chat-search --name "your group name"
```

## 6. Verify the installation

Show CLI help:

```bash
python -m odds_tool.main --help
```

Run tests:

```bash
python -m pytest tests -q
```

## 7. First query examples

Query by team name:

```bash
python -m odds_tool.main fetch --team Canada
```

Query by match number:

```bash
python -m odds_tool.main fetch --match-num 周五204
```

Feishu gateway query entry:

```bash
python -m odds_tool.main feishu-query --text "查询 法国"
```
