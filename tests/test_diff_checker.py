import unittest

from odds_tool.diff_checker import diff_odds


def make_snapshot():
    return {
        "match_id": 2040121,
        "had": {"win": 1.30, "draw": 4.30, "lose": 7.85},
        "hhad": {"goal_line": -1.0, "win": 2.19, "draw": 3.02, "lose": 2.93},
    }


class DiffCheckerTests(unittest.TestCase):
    def test_diff_odds_returns_no_alert_for_initial_baseline(self):
        changed, diff = diff_odds(None, make_snapshot())
        self.assertFalse(changed)
        self.assertEqual(diff["reason"], "initial_baseline")

    def test_diff_odds_detects_had_change(self):
        old = make_snapshot()
        new = make_snapshot()
        new["had"]["win"] = 1.28

        changed, diff = diff_odds(old, new)

        self.assertTrue(changed)
        self.assertEqual(diff["had"]["win"], {"old": 1.30, "new": 1.28})

    def test_diff_odds_detects_hhad_changes(self):
        old = make_snapshot()
        new = make_snapshot()
        new["hhad"]["goal_line"] = -0.5
        new["hhad"]["draw"] = 3.15
        new["hhad"]["lose"] = 2.88

        changed, diff = diff_odds(old, new)

        self.assertTrue(changed)
        self.assertEqual(diff["hhad"]["goal_line"], {"old": -1.0, "new": -0.5})
        self.assertEqual(diff["hhad"]["draw"], {"old": 3.02, "new": 3.15})
        self.assertEqual(diff["hhad"]["lose"], {"old": 2.93, "new": 2.88})


if __name__ == "__main__":
    unittest.main()
