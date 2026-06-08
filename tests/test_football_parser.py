import json
import unittest
from pathlib import Path

from odds_tool.odds_parser import parse_football_match_list_payload


class FootballParserTests(unittest.TestCase):
    def test_parse_football_match_list_payload(self):
        fixture = Path("tests/fixtures/sporttery_football_match_list_sample.json")
        payload = json.loads(fixture.read_text(encoding="utf-8"))

        matches = parse_football_match_list_payload(payload)
        first = matches[0]

        self.assertEqual(first["match_id"], 2040091)
        self.assertEqual(first["match_num"], "周四201")
        self.assertEqual(first["home_team"], "斯洛文尼亚")
        self.assertEqual(first["away_team"], "塞浦路斯")
        self.assertEqual(first["had"]["win"], 1.30)
        self.assertEqual(first["had"]["draw"], 4.30)
        self.assertEqual(first["had"]["lose"], 7.85)
        self.assertEqual(first["hhad"]["goal_line"], -1.0)
        self.assertEqual(first["hhad"]["win"], 2.19)
        self.assertEqual(first["hhad"]["draw"], 3.02)
        self.assertEqual(first["hhad"]["lose"], 2.93)

    def test_parse_football_match_list_payload_supports_legacy_fixed_goal_field(self):
        fixture = Path("tests/fixtures/sporttery_football_match_list_sample.json")
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        payload["value"]["matchInfoList"][0]["subMatchList"][0]["hhad"] = {
            "fixedGoal": "-1",
            "h": "2.19",
            "d": "3.02",
            "a": "2.93",
            "updateDate": "2026-06-04",
            "updateTime": "14:30:38",
        }

        matches = parse_football_match_list_payload(payload)

        self.assertEqual(matches[0]["hhad"]["goal_line"], -1.0)

    def test_parse_football_match_list_payload_supports_odds_list_fallback(self):
        fixture = Path("tests/fixtures/sporttery_football_match_list_sample.json")
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        match = payload["value"]["matchInfoList"][0]["subMatchList"][0]
        match["had"] = {}
        match["hhad"] = {}
        match["oddsList"] = [
            {
                "poolCode": "HHAD",
                "goalLine": "-1",
                "goalLineValue": "-1.00",
                "h": "2.25",
                "d": "2.96",
                "a": "2.88",
                "updateDate": "2026-06-04",
                "updateTime": "19:15:14",
            },
            {
                "poolCode": "HAD",
                "goalLine": "",
                "goalLineValue": "",
                "h": "1.31",
                "d": "4.20",
                "a": "7.80",
                "updateDate": "2026-06-04",
                "updateTime": "19:15:06",
            },
        ]

        matches = parse_football_match_list_payload(payload)

        self.assertEqual(matches[0]["had"]["win"], 1.31)
        self.assertEqual(matches[0]["had"]["draw"], 4.20)
        self.assertEqual(matches[0]["had"]["lose"], 7.80)
        self.assertEqual(matches[0]["hhad"]["goal_line"], -1.0)
        self.assertEqual(matches[0]["hhad"]["win"], 2.25)

    def test_parse_football_match_list_payload_skips_matches_without_complete_had_hhad(self):
        fixture = Path("tests/fixtures/sporttery_football_match_list_sample.json")
        payload = json.loads(fixture.read_text(encoding="utf-8"))
        payload["value"]["matchInfoList"][0]["subMatchList"].append(
            {
                "matchId": "2040093",
                "matchNumStr": "周四203",
                "leagueAllName": "国际赛",
                "homeTeamAllName": "西班牙",
                "awayTeamAllName": "伊拉克",
                "matchDate": "2026-06-05",
                "matchTime": "03:00:00",
                "matchStatus": "Selling",
                "had": {},
                "hhad": {
                    "goalLine": "-3",
                    "goalLineValue": "-3.00",
                    "h": "2.21",
                    "d": "4.20",
                    "a": "2.28",
                    "updateDate": "2026-06-04",
                    "updateTime": "17:18:00",
                },
                "oddsList": [
                    {
                        "poolCode": "HHAD",
                        "goalLine": "-3",
                        "goalLineValue": "-3.00",
                        "h": "2.21",
                        "d": "4.20",
                        "a": "2.28",
                        "updateDate": "2026-06-04",
                        "updateTime": "17:18:00",
                    }
                ],
            }
        )

        matches = parse_football_match_list_payload(payload)

        self.assertEqual(len(matches), 1)


if __name__ == "__main__":
    unittest.main()
