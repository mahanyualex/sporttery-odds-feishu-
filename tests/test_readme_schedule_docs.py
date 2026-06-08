from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
EXPECTED_PROJECT_DIR = "/Users/mac/Projects/sporttery-odds-feishu"
OLD_PROJECT_DIR = "/Users/mac/Documents/Project/sporttery-odds-feishu"


def test_readme_documents_multi_match_and_schedule_usage():
    content = README_PATH.read_text(encoding="utf-8")

    assert "多场比赛一次性展示" in content
    assert "08:00" in content
    assert "21:00" in content
    assert "SCHEDULED_SEND_HOURS_BEIJING" in content
    assert "通过修改源码中的 `SCHEDULED_SEND_HOURS_BEIJING` 改时间" in content
    assert "仅支持整点小时" in content
    assert "24 小时制" in content
    assert "北京时间" in content
    assert "python -m odds_tool.main scheduled-send --team 日本 --target oc_demo" in content
    assert "launchctl" in content
    assert "建议每小时触发一次" in content
    assert "由程序内部判断是否到点发送" in content


def test_readme_uses_current_project_directory():
    content = README_PATH.read_text(encoding="utf-8")

    assert EXPECTED_PROJECT_DIR in content
    assert f"cd {EXPECTED_PROJECT_DIR}" in content
    assert OLD_PROJECT_DIR not in content
