import unittest
from unittest.mock import patch

from odds_tool.main import fetch_by_match_num, fetch_by_team


class MultiMatchRenderingTests(unittest.TestCase):
    def setUp(self):
        self.matches = [
            {
                "match_id": 1,
                "match_num": "周四201",
                "home_team": "日本U23",
                "away_team": "韩国U23",
                "league": "亚洲杯",
                "match_date": "2026-06-05",
                "match_time": "18:00:00",
                "had": {"win": 2.1, "draw": 3.1, "lose": 2.9},
                "hhad": {"goal_line": -1.0, "win": 4.2, "draw": 3.6, "lose": 1.57},
            },
            {
                "match_id": 2,
                "match_num": "周四205",
                "home_team": "日本",
                "away_team": "印尼",
                "league": "世预赛",
                "match_date": "2026-06-05",
                "match_time": "20:00:00",
                "had": {"win": 1.31, "draw": 4.2, "lose": 7.8},
                "hhad": {"goal_line": -2.0, "win": 2.48, "draw": 3.55, "lose": 2.22},
            },
        ]

    def test_fetch_by_team_renders_all_matches_when_keyword_hits_multiple_matches(self):
        with patch("odds_tool.main.fetch_today_matches", return_value=self.matches):
            text = fetch_by_team("日")

        self.assertIn("查询关键词：球队 日", text)
        self.assertIn("共匹配到 2 场比赛", text)
        self.assertIn("周四201", text)
        self.assertIn("日本U23 vs 韩国U23", text)
        self.assertIn("亚洲杯", text)
        self.assertIn("2026-06-05 18:00:00", text)
        self.assertIn("胜平负", text)
        self.assertIn("让球胜平负", text)
        self.assertIn("周四205", text)
        self.assertIn("日本 vs 印尼", text)
        self.assertIn("世预赛", text)
        self.assertIn("2026-06-05 20:00:00", text)

    def test_fetch_by_match_num_keeps_single_match_output_unchanged(self):
        with patch("odds_tool.main.fetch_today_matches", return_value=[self.matches[1]]):
            text = fetch_by_match_num("周四205")

        self.assertIn("【竞彩足球当前赔率】", text)
        self.assertIn("周四205", text)
        self.assertIn("日本 vs 印尼", text)
        self.assertNotIn("共匹配到", text)


if __name__ == "__main__":
    unittest.main()
