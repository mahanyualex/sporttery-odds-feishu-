import unittest

from odds_tool.main import find_match_by_team, find_match_by_match_num


MATCHES = [
    {"match_num": "周四201", "home_team": "日本", "away_team": "印尼"},
    {"match_num": "周四208", "home_team": "日本U23", "away_team": "韩国U23"},
    {"match_num": "周四209", "home_team": "法国", "away_team": "德国"},
    {"match_num": "周四210", "home_team": "日本国奥", "away_team": "巴林"},
    {"match_num": "周四211", "home_team": "韩国国奥", "away_team": "沙特"},
]


class SearchMatcherTests(unittest.TestCase):
    def test_exact_team_name_first(self):
        result = find_match_by_team(MATCHES, "日本")
        self.assertEqual(result["status"], "unique")
        self.assertEqual(result["match"]["match_num"], "周四201")

    def test_fuzzy_fallback(self):
        result = find_match_by_team(MATCHES, "日本U")
        self.assertEqual(result["status"], "unique")
        self.assertEqual(result["match"]["match_num"], "周四208")

    def test_match_num_lookup(self):
        result = find_match_by_match_num(MATCHES, "周四209")
        self.assertEqual(result["status"], "unique")
        self.assertEqual(result["match"]["home_team"], "法国")

    def test_match_num_lookup_normalizes_spaces(self):
        result = find_match_by_match_num(MATCHES, "周四 209")
        self.assertEqual(result["status"], "unique")
        self.assertEqual(result["match"]["away_team"], "德国")

    def test_ambiguous_when_multiple_fuzzy_matches(self):
        result = find_match_by_team(MATCHES, "国奥")
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(
            [match["match_num"] for match in result["matches"]],
            ["周四210", "周四211"],
        )

    def test_not_found_when_no_match(self):
        result = find_match_by_team(MATCHES, "巴西")
        self.assertEqual(result["status"], "not_found")
        self.assertIsNone(result.get("match"))

    def test_ambiguous_when_multiple_exact_matches(self):
        matches = MATCHES + [{"match_num": "周四212", "home_team": "西班牙", "away_team": "日本"}]
        result = find_match_by_team(matches, "日本")
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(
            [match["match_num"] for match in result["matches"]],
            ["周四201", "周四212"],
        )


if __name__ == "__main__":
    unittest.main()
