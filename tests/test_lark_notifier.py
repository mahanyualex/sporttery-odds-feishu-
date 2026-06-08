import unittest
from unittest.mock import Mock, patch

from odds_tool.lark_notifier import LarkNotifier


class LarkNotifierTests(unittest.TestCase):
    @patch("odds_tool.lark_notifier.subprocess.run")
    def test_lark_notifier_sends_text(self, mock_run):
        mock_run.return_value = Mock(returncode=0, stdout="ok", stderr="")

        notifier = LarkNotifier()
        notifier.send_text("oc_test_chat", "hello")

        cmd = mock_run.call_args[0][0]
        self.assertEqual(cmd[0], "lark-cli")
        self.assertEqual(cmd[1:4], ["im", "+messages-send", "--chat-id"])
        self.assertIn("hello", cmd)

    @patch("odds_tool.lark_notifier.subprocess.run")
    def test_lark_notifier_raises_on_failure(self, mock_run):
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="boom")
        notifier = LarkNotifier()

        with self.assertRaises(RuntimeError):
            notifier.send_text("oc_test_chat", "hello")


if __name__ == "__main__":
    unittest.main()
