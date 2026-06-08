import unittest

from odds_tool.main import parse_feishu_query_text


class FeishuQueryParserTests(unittest.TestCase):
    def test_parse_team_query(self):
        result = parse_feishu_query_text("查询 法国")
        self.assertEqual(
            result,
            {"status": "ok", "lookup_type": "team", "lookup_value": "法国"},
        )

    def test_parse_match_num_query(self):
        result = parse_feishu_query_text("查询 周四201")
        self.assertEqual(
            result,
            {"status": "ok", "lookup_type": "match_num", "lookup_value": "周四201"},
        )

    def test_parse_query_trims_whitespace(self):
        result = parse_feishu_query_text("  查询   周四201  ")
        self.assertEqual(
            result,
            {"status": "ok", "lookup_type": "match_num", "lookup_value": "周四201"},
        )

    def test_parse_query_requires_keyword(self):
        self.assertEqual(
            parse_feishu_query_text("查询"),
            {"status": "invalid", "error": "查询格式错误：请输入查询关键词"},
        )
        self.assertEqual(
            parse_feishu_query_text("查询   "),
            {"status": "invalid", "error": "查询格式错误：请输入查询关键词"},
        )

    def test_parse_query_ignores_non_query_prefix(self):
        self.assertEqual(
            parse_feishu_query_text("hello"),
            {"status": "ignored"},
        )


if __name__ == "__main__":
    unittest.main()
