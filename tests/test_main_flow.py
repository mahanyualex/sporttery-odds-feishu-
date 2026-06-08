import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from odds_tool.cache_store import JsonCacheStore
from odds_tool.main import fetch_by_match_num, fetch_by_team
from odds_tool.sporttery_client import NoMatchSaleError, SportteryClient


class CacheAndClientTests(unittest.TestCase):
    def test_json_cache_store_roundtrip(self):
        tmp_dir = Path("tests/.tmp-cache")
        cache_file = tmp_dir / "cache.json"
        if cache_file.exists():
            cache_file.unlink()
        if tmp_dir.exists():
            for item in tmp_dir.iterdir():
                if item.is_file():
                    item.unlink()
        store = JsonCacheStore(cache_file)

        self.assertEqual(store.load_all(), {})

        snapshot = {"match_id": 2040121, "mnl": {"home": 1.34, "away": 2.31}}
        store.save_snapshot("2040121", snapshot)

        loaded = store.get_snapshot("2040121")
        self.assertEqual(loaded, snapshot)

    @patch("odds_tool.sporttery_client.urllib.request.urlopen")
    def test_sporttery_client_fetches_payload(self, mock_urlopen):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = b'{"errorCode": "0", "value": {}}'
        mock_urlopen.return_value = response

        client = SportteryClient()
        payload = client.fetch_fixed_bonus(2040121)

        self.assertEqual(payload["errorCode"], "0")
        request_obj = mock_urlopen.call_args[0][0]
        self.assertIn("matchId=2040121", request_obj.full_url)

    @patch("odds_tool.sporttery_client.urllib.request.urlopen")
    def test_sporttery_client_fetches_football_match_list_payload(self, mock_urlopen):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = b'{"errorCode": "0", "value": {"matchInfoList": []}}'
        mock_urlopen.return_value = response

        client = SportteryClient()
        payload = client.fetch_football_match_list()

        self.assertEqual(payload["errorCode"], "0")
        request_obj = mock_urlopen.call_args[0][0]
        self.assertIn("/football/getMatchCalculatorV1.qry", request_obj.full_url)
        self.assertIn("poolCode=hhad,had", request_obj.full_url)

    @patch("odds_tool.sporttery_client.urllib.request.urlopen")
    def test_sporttery_client_falls_back_when_calculator_payload_missing_match_info_list(self, mock_urlopen):
        first_response = Mock()
        first_response.__enter__ = Mock(return_value=first_response)
        first_response.__exit__ = Mock(return_value=False)
        first_response.read.return_value = b'{"errorCode": "0", "value": {"vtoolsConfig": {}}}'

        second_response = Mock()
        second_response.__enter__ = Mock(return_value=second_response)
        second_response.__exit__ = Mock(return_value=False)
        second_response.read.return_value = b'{"errorCode": "0", "value": {"matchInfoList": []}}'

        mock_urlopen.side_effect = [first_response, second_response]

        client = SportteryClient()
        payload = client.fetch_football_match_list()

        self.assertEqual(payload["value"]["matchInfoList"], [])
        self.assertEqual(mock_urlopen.call_count, 2)
        first_request = mock_urlopen.call_args_list[0][0][0]
        second_request = mock_urlopen.call_args_list[1][0][0]
        self.assertIn("/football/getMatchCalculatorV1.qry", first_request.full_url)
        self.assertIn("/football/getMatchResultV1.qry", second_request.full_url)

    @patch("odds_tool.sporttery_client.urllib.request.urlopen")
    def test_sporttery_client_raises_business_error_when_all_football_match_list_endpoints_miss_match_info_list(self, mock_urlopen):
        first_response = Mock()
        first_response.__enter__ = Mock(return_value=first_response)
        first_response.__exit__ = Mock(return_value=False)
        first_response.read.return_value = b'{"errorCode": "0", "value": {"vtoolsConfig": {}}}'

        second_response = Mock()
        second_response.__enter__ = Mock(return_value=second_response)
        second_response.__exit__ = Mock(return_value=False)
        second_response.read.return_value = b'{"errorCode": "0", "value": {}}'

        mock_urlopen.side_effect = [first_response, second_response]

        client = SportteryClient()

        with self.assertRaisesRegex(NoMatchSaleError, "今天暂无竞彩足球可售比赛"):
            client.fetch_football_match_list()


class FootballFetchTests(unittest.TestCase):
    def test_fetch_by_team_returns_rendered_message(self):
        matches = [{
            "match_id": 1,
            "match_num": "周四201",
            "home_team": "日本",
            "away_team": "印尼",
            "league": "国际赛",
            "match_date": "2026-06-05",
            "match_time": "18:00:00",
            "had": {"win": 1.5, "draw": 3.2, "lose": 5.1},
            "hhad": {"goal_line": -1.0, "win": 2.3, "draw": 3.1, "lose": 2.8},
        }]

        with patch("odds_tool.main.fetch_today_matches", return_value=matches):
            text = fetch_by_team("日本")

        self.assertIn("【竞彩足球当前赔率】", text)
        self.assertIn("周四201", text)
        self.assertIn("日本 vs 印尼", text)
        self.assertIn("胜平负", text)
        self.assertIn("让球胜平负", text)

    def test_fetch_by_match_num_returns_rendered_message(self):
        matches = [{
            "match_id": 2,
            "match_num": "周四209",
            "home_team": "法国",
            "away_team": "德国",
            "league": "国际赛",
            "match_date": "2026-06-05",
            "match_time": "21:00:00",
            "had": {"win": 2.1, "draw": 3.0, "lose": 2.9},
            "hhad": {"goal_line": 1.0, "win": 4.0, "draw": 3.5, "lose": 1.6},
        }]

        with patch("odds_tool.main.fetch_today_matches", return_value=matches):
            text = fetch_by_match_num("周四209")

        self.assertIn("【竞彩足球当前赔率】", text)
        self.assertIn("周四209", text)
        self.assertIn("法国 vs 德国", text)


if __name__ == "__main__":
    unittest.main()
