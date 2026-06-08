# sporttery-odds-feishu

A Feishu notification tool built on official China Sports Lottery football odds data.

This project helps you:
- query today's China Sports Lottery football odds
- search matches by team name or match number
- monitor odds changes for a target team on the same day
- send odds updates to a Feishu group on a fixed schedule
- run the tool long-term with macOS `launchctl`
- show all matched games at once when a keyword matches multiple matches

Typical use cases:
- receive odds updates for a target team in a Feishu group
- check the odds of a team's match at fixed times every day
- wrap China Sports Lottery football odds lookup into a reusable automation tool

## Features

- Official data source: uses the structured API behind the China Sports Lottery football pages
- Two query modes: team name and match number
- Team-name search is prioritized by default, with exact match first and fuzzy match as fallback
- Supported odds types:
  - win-draw-lose `had`
  - handicap win-draw-lose `hhad`
- Supports one-off query, watch mode, and scheduled send
- Uses `lark-cli` as the Feishu delivery channel
- Supports macOS `launchctl` deployment

## Project Structure

```text
sporttery-odds-feishu/
├── odds_tool/                  # core source code
├── tests/                      # test suite
├── launchd/                    # launchctl template
├── config.example.json         # example config
├── requirements.txt            # Python dependencies
├── run_watch.sh                # watch-mode launcher
├── run_scheduled_send.sh       # scheduled-send launcher
├── install_launch_agent.sh     # launch agent installer
├── README.md                   # Chinese README
├── README.en.md                # English README
├── LICENSE                     # license
└── .gitignore                  # Git ignore rules
```

## Requirements

- macOS recommended, because the project includes a `launchctl` deployment path
- Python 3.11 or newer
- `lark-cli` installed and available in PATH
- A Feishu account with completed `lark-cli` login / authorization

## Installation

Local directory example on the current machine:

```bash
cd /Users/mac/Projects/sporttery-odds-feishu
```

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

First make sure `lark-cli` is available:

```bash
lark-cli version
```

Then log in:

```bash
lark-cli auth login
```

If sending messages later fails because of missing permissions:

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

Use the target `chat_id` in notification and scheduled-send commands.

## Quick Start

### 1. Query today's odds by team name

```bash
python -m odds_tool.main fetch --team Canada
```

### 2. Query today's odds by match number

```bash
python -m odds_tool.main fetch --match-num 周五204
```

### 3. Send query results to a Feishu group

```bash
python -m odds_tool.main fetch --team Canada --notify --target oc_xxx
```

### 4. Query entry used by Hermes / Feishu gateway

```bash
python -m odds_tool.main feishu-query --text "查询 法国"
```

Recommended in-group message format:
- `@机器人 查询 法国`
- `@机器人 查询 周四201`

## Watch Odds Changes for a Team

Watch the target team's match on the same day and only send a message when odds change.

```bash
python -m odds_tool.main watch-team --team Canada --interval 60 --target oc_xxx
```

Parameters:
- `--team`: target team name
- `--interval`: polling interval in seconds, default `60`
- `--target`: Feishu group `chat_id`
- `--cache`: cache file path, default `cache/odds_cache.json`

Notes:
- The first run only creates the baseline and does not send a change alert
- Later messages are sent only when odds change
- By default the tool only compares the matched game for the current day

## Scheduled Send

Send the current odds of a target team to a Feishu group at fixed times.

```bash
python -m odds_tool.main scheduled-send --team Japan --target oc_demo
```

Parameters:
- `--team`: team name
- `--target`: Feishu group `chat_id`
- `--cache`: compatibility argument, default `cache/odds_cache.json`
- `--state`: scheduled-send state file, default `cache/scheduled_send_state.json`

Default send time:
- Beijing time `08:00`
- Beijing time `21:00`

Limits:
- only whole-hour schedules are supported
- uses a 24-hour clock
- send windows are evaluated in Beijing time

Time configuration:
- file: `odds_tool/main.py`
- constant: `SCHEDULED_SEND_HOURS_BEIJING = [8, 21]`
- change the send times by editing `SCHEDULED_SEND_HOURS_BEIJING` in source code

Example:

```python
SCHEDULED_SEND_HOURS_BEIJING = [9, 18, 22]
```

## macOS launchctl Deployment

Recommended pattern: let `launchctl` trigger once every hour, and let the program decide whether the current hour is a send window.
In other words, schedule hourly execution instead of trying to trigger only at `08:00` and `21:00` in the scheduler itself.

### 1. Generate the LaunchAgent

```bash
./install_launch_agent.sh Canada oc_xxx
```

To customize cache and state files:

```bash
./install_launch_agent.sh Canada oc_xxx cache/odds_cache.json cache/scheduled_send_state.json
```

The default generated file is:

```text
~/Library/LaunchAgents/com.herry.sporttery-football-odds.plist
```

### 2. Load the service

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.herry.sporttery-football-odds.plist 2>/dev/null || true
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.herry.sporttery-football-odds.plist
```

### 3. Trigger it immediately

```bash
launchctl kickstart -k gui/$(id -u)/com.herry.sporttery-football-odds
```

### 4. Check service status

```bash
launchctl print gui/$(id -u)/com.herry.sporttery-football-odds
```

### 5. View logs

```bash
tail -f logs/sporttery-football-odds.out.log logs/sporttery-football-odds.err.log
log stream --predicate 'process == "python" OR eventMessage CONTAINS "com.herry.sporttery-football-odds"' --style compact
```

### 6. Unload the service

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.herry.sporttery-football-odds.plist
```

## FAQ

### 1. Why can the tool not find a match?

Common reasons:
- the team has no match today
- there are no sellable matches today on the official side
- the keyword did not match today's games

The project tries to distinguish between:
- no games / no selling today
- games exist today, but the keyword did not match
- real system error

### 2. Why does the first watch run send nothing?

Because the first run only builds the baseline, so the first fetch is not treated as an odds change.

### 3. Why did `scheduled-send` exit without sending a message?

Because `scheduled-send` only sends during configured Beijing-time windows.
If the current time is outside the allowed window, it exits silently.

### 4. Why do I get `missing_scope` when sending Feishu messages?

Re-authorize:

```bash
lark-cli auth login --scope "im:message.send_as_user"
```

### 5. I do not know the Feishu group chat_id

Use:

```bash
lark-cli im +chat-list
```

or:

```bash
lark-cli im +chat-search --name "your group name"
```

## Development and Testing

### Run tests

```bash
python -m pytest tests -q
```

### Show CLI help

```bash
python -m odds_tool.main --help
```

## Data Source Notes

This project uses the structured API behind official China Sports Lottery football pages.
It is suitable for query, watch, and Feishu notification workflows. It is not recommended to replace this with fragile DOM scraping.

## Disclaimer

This project is for information lookup, learning, and automation only. It does not constitute betting advice.
Always refer to the official China Sports Lottery pages and actual selling information.
