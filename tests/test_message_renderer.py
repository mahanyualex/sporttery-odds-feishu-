import unittest

from odds_tool.message_renderer import render_diff_message


class MessageRendererTests(unittest.TestCase):
    def test_render_diff_message_contains_changed_sections_only(self):
        snapshot = {
            "match_id": 2040121,
            "home_team": "圣安东尼奥马刺",
            "away_team": "纽约尼克斯",
            "match_time": "2026-06-06 08:30:00",
        }
        diff = {
            "mnl": {
                "home": {"old": 1.34, "new": 1.36},
                "away": {"old": 2.31, "new": 2.25},
            }
        }

        text = render_diff_message(snapshot, diff)

        self.assertIn("【竞彩篮球赔率变动】", text)
        self.assertIn("纽约尼克斯 vs 圣安东尼奥马刺", text)
        self.assertIn("主胜 1.34 → 1.36", text)
        self.assertIn("客胜 2.31 → 2.25", text)
        self.assertNotIn("让分胜负", text)


if __name__ == "__main__":
    unittest.main()
