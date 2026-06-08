import time
import unittest

from odds_tool.main import watch_once


class FakeStore:
    def __init__(self, old=None):
        self.old = old
        self.saved = None

    def get_snapshot(self, match_id):
        return self.old

    def save_snapshot(self, match_id, snapshot):
        self.saved = snapshot


class WatchOnceTests(unittest.TestCase):
    def test_watch_once_sends_message_on_change(self):
        old = {
            "match_id": 2040121,
            "home_team": "圣安东尼奥马刺",
            "away_team": "纽约尼克斯",
            "match_time": "2026-06-06 08:30:00",
            "mnl": {"home": 1.34, "away": 2.31},
            "hdc": {"goal_line": -5.5, "home": 1.65, "away": 1.75},
            "hilo": {"goal_line": 215.5, "high": 1.70, "low": 1.70},
        }
        new = {
            **old,
            "mnl": {"home": 1.36, "away": 2.25},
        }

        sent = {}

        class FakeNotifier:
            def send_text(self, target, text):
                sent["target"] = target
                sent["text"] = text

        store = FakeStore(old=old)

        watch_once(
            match_id=2040121,
            target="oc_test_chat",
            store=store,
            notifier=FakeNotifier(),
            fetch_snapshot=lambda _match_id: new,
        )

        self.assertEqual(sent["target"], "oc_test_chat")
        self.assertIn("主胜 1.34 → 1.36", sent["text"])
        self.assertEqual(store.saved, new)

    def test_watch_once_initial_baseline_only_saves(self):
        new = {
            "match_id": 2040121,
            "home_team": "圣安东尼奥马刺",
            "away_team": "纽约尼克斯",
            "match_time": "2026-06-06 08:30:00",
            "mnl": {"home": 1.34, "away": 2.31},
            "hdc": {"goal_line": -5.5, "home": 1.65, "away": 1.75},
            "hilo": {"goal_line": 215.5, "high": 1.70, "low": 1.70},
        }

        class FakeNotifier:
            def send_text(self, target, text):
                raise AssertionError("首次基线不应发送消息")

        store = FakeStore(old=None)
        watch_once(
            match_id=2040121,
            target="oc_test_chat",
            store=store,
            notifier=FakeNotifier(),
            fetch_snapshot=lambda _match_id: new,
        )
        self.assertEqual(store.saved, new)


if __name__ == "__main__":
    unittest.main()
