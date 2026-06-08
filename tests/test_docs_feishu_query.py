import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
GATEWAY_NOTES_PATH = (
    REPO_ROOT / "docs" / "plans" / "2026-06-04-feishu-group-query-gateway-notes.md"
)

REQUIRED_SNIPPETS = [
    "@机器人 查询 法国",
    "@机器人 查询 周四201",
    'python -m odds_tool.main feishu-query --text "查询 法国"',
]


class FeishuQueryDocsTests(unittest.TestCase):
    def test_readme_contains_required_examples(self):
        content = README_PATH.read_text(encoding="utf-8")

        for snippet in REQUIRED_SNIPPETS:
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, content)

    def test_gateway_notes_contains_required_examples(self):
        self.assertTrue(GATEWAY_NOTES_PATH.exists(), "gateway notes file should exist")
        content = GATEWAY_NOTES_PATH.read_text(encoding="utf-8")

        for snippet in REQUIRED_SNIPPETS:
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, content)


if __name__ == "__main__":
    unittest.main()
