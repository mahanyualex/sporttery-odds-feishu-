import json
import unittest
from pathlib import Path

from odds_tool.odds_parser import parse_fixed_bonus_payload


class OddsParserTests(unittest.TestCase):
    def test_parse_fixed_bonus_payload_extracts_latest_odds(self):
        fixture = Path("tests/fixtures/sporttery_fixed_bonus_sample.json")
        payload = json.loads(fixture.read_text(encoding="utf-8"))

        result = parse_fixed_bonus_payload(payload)

        self.assertEqual(result["match_id"], 2040121)
        self.assertEqual(result["home_team"], "圣安东尼奥马刺")
        self.assertEqual(result["away_team"], "纽约尼克斯")
        self.assertEqual(result["mnl"]["home"], 1.34)
        self.assertEqual(result["mnl"]["away"], 2.31)
        self.assertEqual(result["hdc"]["goal_line"], -5.5)
        self.assertEqual(result["hdc"]["home"], 1.65)
        self.assertEqual(result["hdc"]["away"], 1.75)
        self.assertEqual(result["hilo"]["goal_line"], 215.5)
        self.assertEqual(result["hilo"]["high"], 1.70)
        self.assertEqual(result["hilo"]["low"], 1.70)


if __name__ == "__main__":
    unittest.main()
