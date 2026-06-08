import unittest
from pathlib import Path

from odds_tool.main import build_parser


class LaunchdFilesTests(unittest.TestCase):
    def test_build_parser_supports_watch_team_command(self):
        parser = build_parser()

        args = parser.parse_args(
            [
                "watch-team",
                "--team",
                "日本",
                "--interval",
                "60",
                "--target",
                "oc_xxx",
                "--cache",
                "cache/odds_cache.json",
            ]
        )

        self.assertEqual(args.command, "watch-team")
        self.assertEqual(args.team, "日本")
        self.assertEqual(args.interval, 60)
        self.assertEqual(args.target, "oc_xxx")
        self.assertEqual(args.cache, "cache/odds_cache.json")

    def test_run_scheduled_send_script_uses_scheduled_send(self):
        content = Path("run_scheduled_send.sh").read_text(encoding="utf-8")

        self.assertIn("scheduled-send", content)
        self.assertIn('--target "$CHAT_ID"', content)
        self.assertIn('--cache "$CACHE_PATH"', content)
        self.assertNotIn("watch-team", content)
        self.assertNotIn("--interval", content)

    def test_launchd_template_contains_hourly_start_calendar_interval(self):
        content = Path("launchd/com.herry.sporttery-football-odds.plist.template").read_text(encoding="utf-8")

        self.assertIn("com.herry.sporttery-football-odds", content)
        self.assertIn("run_scheduled_send.sh", content)
        self.assertIn("<key>RunAtLoad</key>", content)
        self.assertIn("<true/>", content)
        self.assertIn("<key>StartCalendarInterval</key>", content)
        self.assertIn("<key>Minute</key>", content)
        self.assertIn("<integer>0</integer>", content)
        self.assertIn("{{TEAM}}", content)
        self.assertIn("{{TARGET}}", content)
        self.assertNotIn("<key>KeepAlive</key>", content)
        self.assertNotIn("{{INTERVAL}}", content)

    def test_install_script_mentions_bootstrap_usage_for_hourly_launchagent(self):
        content = Path("install_launch_agent.sh").read_text(encoding="utf-8")

        self.assertIn("run_scheduled_send.sh", content)
        self.assertIn('launchctl bootstrap gui/$(id -u)', content)
        self.assertIn('launchctl bootout gui/$(id -u)', content)
        self.assertNotIn("INTERVAL=", content)
        self.assertIn("TEAM=", content)

    def test_readme_documents_launchctl_usage(self):
        content = Path("README.md").read_text(encoding="utf-8")

        self.assertIn("launchctl bootstrap", content)
        self.assertIn("launchctl bootout", content)
        self.assertIn("launchctl kickstart", content)
        self.assertIn("launchctl print", content)
        self.assertIn("log stream", content)
        self.assertIn("watch-team", content)

    def test_config_example_includes_team_field(self):
        content = Path("config.example.json").read_text(encoding="utf-8")

        self.assertIn('"team"', content)
        self.assertNotIn('"match_ids"', content)


if __name__ == "__main__":
    unittest.main()
