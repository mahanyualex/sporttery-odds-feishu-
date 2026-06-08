import unittest
from argparse import Namespace
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zoneinfo import ZoneInfo

from odds_tool.main import build_parser, main, scheduled_send_once


class FakeNotifier:
    def __init__(self):
        self.sent = []

    def send_text(self, target, text):
        self.sent.append({"target": target, "text": text})


class ScheduledSendCommandTests(unittest.TestCase):
    def test_build_parser_supports_scheduled_send_subcommand(self):
        parser = build_parser()

        args = parser.parse_args([
            "scheduled-send",
            "--team",
            "日本",
            "--target",
            "oc_demo",
            "--cache",
            "cache/demo.json",
            "--state",
            "cache/state.json",
        ])

        self.assertEqual(args.command, "scheduled-send")
        self.assertEqual(args.team, "日本")
        self.assertEqual(args.target, "oc_demo")
        self.assertEqual(args.cache, "cache/demo.json")
        self.assertEqual(args.state, "cache/state.json")

    def test_scheduled_send_once_is_silent_outside_send_slot(self):
        notifier = FakeNotifier()
        now = datetime(2026, 6, 5, 9, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai"))

        with TemporaryDirectory() as tmp_dir:
            state_path = Path(tmp_dir) / "state.json"

            with patch("odds_tool.main.fetch_by_team") as mock_fetch:
                scheduled_send_once(
                    team="日本",
                    target="oc_demo",
                    cache_path="cache/unused.json",
                    state_path=str(state_path),
                    notifier=notifier,
                    now=now,
                )

        mock_fetch.assert_not_called()
        self.assertEqual(notifier.sent, [])
        self.assertFalse(state_path.exists())

    def test_scheduled_send_once_is_silent_when_slot_already_sent(self):
        notifier = FakeNotifier()
        now = datetime(2026, 6, 5, 8, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai"))

        with TemporaryDirectory() as tmp_dir:
            state_path = Path(tmp_dir) / "state.json"
            state_path.write_text('{"last_sent_slot": "2026-06-05-08"}', encoding="utf-8")

            with patch("odds_tool.main.fetch_by_team") as mock_fetch:
                scheduled_send_once(
                    team="日本",
                    target="oc_demo",
                    cache_path="cache/unused.json",
                    state_path=str(state_path),
                    notifier=notifier,
                    now=now,
                )

            self.assertEqual(state_path.read_text(encoding="utf-8"), '{"last_sent_slot": "2026-06-05-08"}')

        mock_fetch.assert_not_called()
        self.assertEqual(notifier.sent, [])

    def test_scheduled_send_once_fetches_sends_and_updates_state_in_slot(self):
        notifier = FakeNotifier()
        now = datetime(2026, 6, 5, 21, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai"))

        with TemporaryDirectory() as tmp_dir:
            state_path = Path(tmp_dir) / "state.json"

            with patch("odds_tool.main.fetch_by_team", return_value="赔率文本") as mock_fetch:
                scheduled_send_once(
                    team="日本",
                    target="oc_demo",
                    cache_path="cache/odds_cache.json",
                    state_path=str(state_path),
                    notifier=notifier,
                    now=now,
                )

            self.assertEqual(state_path.read_text(encoding="utf-8"), '{"last_sent_slot": "2026-06-05-21"}')

        mock_fetch.assert_called_once_with("日本")
        self.assertEqual(notifier.sent, [{"target": "oc_demo", "text": "赔率文本"}])

    @patch("odds_tool.main.scheduled_send_once")
    @patch("odds_tool.main.argparse.ArgumentParser.parse_args")
    def test_main_dispatches_scheduled_send_command(self, mock_parse_args, mock_scheduled_send_once):
        mock_parse_args.return_value = Namespace(
            command="scheduled-send",
            team="日本",
            target="oc_demo",
            cache="cache/custom.json",
            state="cache/custom-state.json",
        )

        main()

        mock_scheduled_send_once.assert_called_once_with(
            team="日本",
            target="oc_demo",
            cache_path="cache/custom.json",
            state_path="cache/custom-state.json",
        )


if __name__ == "__main__":
    unittest.main()
