import subprocess
import sys
import unittest
from argparse import Namespace
from unittest.mock import patch

from odds_tool.main import build_parser, main


class FeishuQueryCommandTests(unittest.TestCase):
    def test_build_parser_supports_feishu_query_subcommand(self):
        parser = build_parser()

        args = parser.parse_args(["feishu-query", "--text", "查询 法国"])

        self.assertEqual(args.command, "feishu-query")
        self.assertEqual(args.text, "查询 法国")

    @patch("odds_tool.main.handle_feishu_query_text")
    @patch("odds_tool.main.argparse.ArgumentParser.parse_args")
    @patch("builtins.print")
    def test_main_prints_handler_output_for_feishu_query(self, mock_print, mock_parse_args, mock_handle):
        mock_parse_args.return_value = Namespace(command="feishu-query", text="查询 法国")
        mock_handle.return_value = "赔率文本"

        main()

        mock_handle.assert_called_once_with("查询 法国")
        mock_print.assert_called_once_with("赔率文本")

    @patch("odds_tool.main.handle_feishu_query_text")
    @patch("odds_tool.main.argparse.ArgumentParser.parse_args")
    @patch("builtins.print")
    def test_main_keeps_silent_for_ignored_non_command_text(self, mock_print, mock_parse_args, mock_handle):
        mock_parse_args.return_value = Namespace(command="feishu-query", text="hello")
        mock_handle.return_value = None

        main()

        mock_handle.assert_called_once_with("hello")
        mock_print.assert_not_called()

    def test_cli_command_exits_zero_and_silently_ignores_non_query_text(self):
        completed = subprocess.run(
            [sys.executable, "-m", "odds_tool.main", "feishu-query", "--text", "hello"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(completed.stderr, "")


if __name__ == "__main__":
    unittest.main()
