import unittest
from unittest.mock import patch

from odds_tool.main import handle_feishu_query_text
from odds_tool.sporttery_client import NoMatchSaleError


class FeishuQueryHandlerTests(unittest.TestCase):
    @patch("odds_tool.main.fetch_by_team")
    def test_handle_team_query_dispatches_to_fetch_by_team(self, mock_fetch_by_team):
        mock_fetch_by_team.return_value = "team result"

        result = handle_feishu_query_text("查询 法国")

        self.assertEqual(result, "team result")
        mock_fetch_by_team.assert_called_once_with("法国")

    @patch("odds_tool.main.fetch_by_match_num")
    def test_handle_match_num_query_dispatches_to_fetch_by_match_num(self, mock_fetch_by_match_num):
        mock_fetch_by_match_num.return_value = "match result"

        result = handle_feishu_query_text("查询 周四201")

        self.assertEqual(result, "match result")
        mock_fetch_by_match_num.assert_called_once_with("周四201")

    def test_handle_query_returns_format_hint_for_empty_keyword(self):
        self.assertEqual(
            handle_feishu_query_text("查询   "),
            "查询格式错误：请输入查询关键词",
        )

    def test_handle_query_ignores_non_query_prefix(self):
        self.assertIsNone(handle_feishu_query_text("hello"))

    @patch("odds_tool.main.fetch_by_team")
    def test_handle_query_returns_friendly_business_message_when_no_matches_on_sale(self, mock_fetch_by_team):
        mock_fetch_by_team.side_effect = NoMatchSaleError("今天暂无竞彩足球可售比赛")

        self.assertEqual(
            handle_feishu_query_text("查询 法国"),
            "今天暂无竞彩足球可售比赛",
        )

    @patch("odds_tool.main.fetch_by_team")
    def test_handle_query_returns_friendly_error_when_fetch_raises(self, mock_fetch_by_team):
        mock_fetch_by_team.side_effect = RuntimeError("boom")

        self.assertEqual(
            handle_feishu_query_text("查询 法国"),
            "查询失败，请稍后重试",
        )

    @patch("odds_tool.main.fetch_by_team")
    def test_handle_query_returns_lookup_error_details_when_match_not_found(self, mock_fetch_by_team):
        mock_fetch_by_team.side_effect = ValueError("未找到球队为 法国 的比赛")

        self.assertEqual(
            handle_feishu_query_text("查询 法国"),
            "未找到球队为 法国 的比赛",
        )


if __name__ == "__main__":
    unittest.main()
