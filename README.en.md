# sporttery-odds-feishu

> China Sports Lottery football odds query, watch, and Feishu notification tool.

[中文 README](./README.md) · [Install Guide](./docs/INSTALL.en.md) · [Deployment Guide](./docs/DEPLOY.en.md)

## Overview

`sporttery-odds-feishu` is an automation tool built around the official structured data behind China Sports Lottery football pages.

Typical use cases:
- query today's football odds
- search target matches by team name or match number
- monitor odds changes for a target team's match on the same day
- push scheduled odds updates into a Feishu group
- run the tool long-term on macOS with `launchctl`

## Why this project

Compared with repeatedly checking the official website manually, this project is more suitable for automation:
- uses structured official data instead of fragile DOM scraping
- supports fast lookup by team name or match number
- supports watch mode and only notifies when odds change
- supports scheduled send for recurring group updates
- uses `lark-cli` as the Feishu delivery channel so it fits existing workflows well

## Prerequisites

Before installing this project, install and configure `lark-cli` first:

- GitHub: <https://github.com/larksuite/cli>

This project uses `lark-cli` as the Feishu message delivery channel. Without `lark-cli`, Feishu notifications will not work.

Environment requirements:
- macOS recommended, because the project includes a `launchctl` deployment path
- Python 3.11+
- authenticated `lark-cli`

## Core Capabilities

### 1. Query today's odds
Two supported query styles:
- team name, for example: `Canada`
- match number, for example: `周四201`

Supported odds types:
- win-draw-lose `had`
- handicap win-draw-lose `hhad`

### 2. Watch odds changes
Build a baseline for the target team's same-day match and poll continuously:
- the first run only builds the baseline and sends nothing
- later messages are sent only when odds change

### 3. Scheduled send
Default send windows in Beijing time:
- `08:00`
- `21:00`

Scheduling strategy:
- let `launchctl` trigger the program every hour
- let the program decide whether the current hour is a valid send slot

### 4. Feishu group integration
The project can serve as the downstream query executor for Hermes / Feishu gateway integration, using fixed command formats such as:
- `@机器人 查询 法国`
- `@机器人 查询 周四201`

## Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url> sporttery-odds-feishu
cd sporttery-odds-feishu
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Install and log in to lark-cli

This project depends on `lark-cli` for Feishu message delivery, so install and configure `lark-cli` first:

- GitHub: <https://github.com/larksuite/cli>

After installation, confirm the command is available:

```bash
lark-cli version
```

Log in:

```bash
lark-cli auth login
```

If message sending later fails because of missing permissions:

```bash
lark-cli auth login --scope "im:message.send_as_user"
```

### 4. Get the target Feishu group chat_id

```bash
lark-cli im +chat-list
```

or:

```bash
lark-cli im +chat-search --name "your group name"
```

## Common Commands

### Query today's odds

By team name:

```bash
python -m odds_tool.main fetch --team Canada
```

By match number:

```bash
python -m odds_tool.main fetch --match-num 周五204
```

Send the result to a Feishu group:

```bash
python -m odds_tool.main fetch --team Canada --notify --target oc_xxx
```

### Watch odds changes for a team

```bash
python -m odds_tool.main watch-team --team Canada --interval 60 --target oc_xxx
```

### Scheduled send

```bash
python -m odds_tool.main scheduled-send --team Japan --target oc_demo
```

### Hermes / Feishu gateway query entry

```bash
python -m odds_tool.main feishu-query --text "查询 法国"
```

## Documentation

- Chinese install guide: [`docs/INSTALL.md`](./docs/INSTALL.md)
- Chinese deploy guide: [`docs/DEPLOY.md`](./docs/DEPLOY.md)
- Chinese README: [`README.md`](./README.md)
- English install guide: [`docs/INSTALL.en.md`](./docs/INSTALL.en.md)
- English deploy guide: [`docs/DEPLOY.en.md`](./docs/DEPLOY.en.md)
- Feishu group query integration notes: [`docs/plans/2026-06-04-feishu-group-query-gateway-notes.md`](./docs/plans/2026-06-04-feishu-group-query-gateway-notes.md)

## Project Structure

```text
sporttery-odds-feishu/
├── odds_tool/                  # core source code
├── tests/                      # test suite
├── launchd/                    # launchctl template
├── docs/                       # install / deploy / notes
├── .github/                    # CI, Issue, and PR templates
├── config.example.json         # example config
├── requirements.txt            # Python dependencies
├── run_watch.sh                # watch-mode launcher
├── run_scheduled_send.sh       # scheduled-send launcher
├── install_launch_agent.sh     # launch agent installer
├── README.md                   # Chinese README
├── README.en.md                # English README
└── LICENSE                     # license
```

## FAQ

### Why can the tool not find a match?

Common reasons:
- the team has no match today
- there are no sellable matches today
- the keyword did not match today's games

The project tries to distinguish between:
- no games / no selling today
- games exist today, but the keyword did not match
- real system errors

### Why does the first watch run send nothing?

Because the first run only builds the baseline so the initial fetch is not treated as an odds change.

### Why did scheduled-send run but no message arrive?

Because `scheduled-send` only sends during configured Beijing-time windows. If the current time is outside those windows, the program exits silently.

### How do I change the scheduled send times?

Modify:
- file: `odds_tool/main.py`
- constant: `SCHEDULED_SEND_HOURS_BEIJING = [8, 21]`

Example:

```python
SCHEDULED_SEND_HOURS_BEIJING = [9, 18, 22]
```

## Development and Testing

Run tests:

```bash
python -m pytest tests -q
```

Show CLI help:

```bash
python -m odds_tool.main --help
```

## Data Source Notes

This project uses the structured API behind the official China Sports Lottery football pages.
It is suitable for query, watch, and Feishu notification workflows. Replacing it with fragile DOM scraping is not recommended.

## Disclaimer

This project is for information lookup, learning, and automation only. It does not constitute betting advice.
Always refer to official China Sports Lottery pages and actual selling information.
