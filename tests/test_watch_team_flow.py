import unittest

from odds_tool.main import watch_team_once


class FakeStore:
    def __init__(self, old=None):
        self.old = old
        self.saved = None

    def get_snapshot(self, key):
        return self.old

    def save_snapshot(self, key, snapshot):
        self.saved = snapshot


class FakeNotifier:
    def __init__(self):
        self.sent = []

    def send_text(self, target, text):
        self.sent.append({"target": target, "text": text})


class WatchTeamFlowTests(unittest.TestCase):
    def make_match(self, had_win=1.5):
        return {
            "match_id": 1,
            "match_num": "周四201",
            "home_team": "日本",
            "away_team": "印尼",
            "league": "国际赛",
            "match_date": "2026-06-05",
            "match_time": "18:00:00",
            "had": {"win": had_win, "draw": 3.2, "lose": 5.1},
            "hhad": {"goal_line": -1.0, "win": 2.3, "draw": 3.1, "lose": 2.8},
        }

    def test_watch_team_not_found_is_silent(self):
        store = FakeStore(old=None)
        notifier = FakeNotifier()

        result = watch_team_once(
            team="日本",
            target="oc_xxx",
            store=store,
            notifier=notifier,
            fetch_today_matches=lambda: [],
        )

        self.assertEqual(result["status"], "not_found")
        self.assertIsNone(store.saved)
        self.assertEqual(notifier.sent, [])

    def test_watch_team_initial_baseline(self):
        store = FakeStore(old=None)
        notifier = FakeNotifier()

        result = watch_team_once(
            team="日本",
            target="oc_xxx",
            store=store,
            notifier=notifier,
            fetch_today_matches=lambda: [self.make_match()],
        )

        self.assertEqual(result["status"], "baseline_saved")
        self.assertEqual(store.saved["match_num"], "周四201")
        self.assertEqual(notifier.sent, [])

    def test_watch_team_sends_message_when_odds_change(self):
        old = self.make_match(had_win=1.5)
        store = FakeStore(old=old)
        notifier = FakeNotifier()

        result = watch_team_once(
            team="日本",
            target="oc_xxx",
            store=store,
            notifier=notifier,
            fetch_today_matches=lambda: [self.make_match(had_win=1.48)],
        )

        self.assertEqual(result["status"], "changed")
        self.assertEqual(len(notifier.sent), 1)
        self.assertEqual(notifier.sent[0]["target"], "oc_xxx")
        self.assertIn("胜 1.5 → 1.48", notifier.sent[0]["text"])
        self.assertEqual(store.saved["had"]["win"], 1.48)

    def test_watch_team_ambiguous_is_silent(self):
        store = FakeStore(old=None)
        notifier = FakeNotifier()
        matches = [
            self.make_match(),
            {
                **self.make_match(),
                "match_id": 2,
                "match_num": "周四208",
                "away_team": "日本U23",
            },
        ]

        result = watch_team_once(
            team="日本",
            target="oc_xxx",
            store=store,
            notifier=notifier,
            fetch_today_matches=lambda: matches,
        )

        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(len(result["matches"]), 2)
        self.assertIsNone(store.saved)
        self.assertEqual(notifier.sent, [])


if __name__ == "__main__":
    unittest.main()
