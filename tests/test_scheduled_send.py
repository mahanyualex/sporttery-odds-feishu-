import json
import unittest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from zoneinfo import ZoneInfo

from odds_tool.main import (
    SCHEDULED_SEND_HOURS_BEIJING,
    get_current_send_slot,
    load_scheduled_send_state,
    save_scheduled_send_state,
    should_send_in_current_slot,
)


class ScheduledSendTests(unittest.TestCase):
    def test_default_scheduled_send_hours_are_beijing_8_and_21(self):
        self.assertEqual(SCHEDULED_SEND_HOURS_BEIJING, [8, 21])

    def test_should_send_at_beijing_08_00(self):
        now = datetime(2026, 6, 5, 8, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai"))

        should_send, slot = should_send_in_current_slot(now, SCHEDULED_SEND_HOURS_BEIJING, {})

        self.assertTrue(should_send)
        self.assertEqual(slot, "2026-06-05-08")

    def test_should_send_at_beijing_21_00(self):
        now = datetime(2026, 6, 5, 21, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai"))

        should_send, slot = should_send_in_current_slot(now, SCHEDULED_SEND_HOURS_BEIJING, {})

        self.assertTrue(should_send)
        self.assertEqual(slot, "2026-06-05-21")

    def test_should_not_send_outside_scheduled_hours(self):
        now = datetime(2026, 6, 5, 9, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai"))

        should_send, slot = should_send_in_current_slot(now, SCHEDULED_SEND_HOURS_BEIJING, {})

        self.assertFalse(should_send)
        self.assertIsNone(slot)

    def test_should_not_send_twice_in_same_day_same_hour(self):
        now = datetime(2026, 6, 5, 8, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
        state = {"last_sent_slot": "2026-06-05-08"}

        should_send, slot = should_send_in_current_slot(now, SCHEDULED_SEND_HOURS_BEIJING, state)

        self.assertFalse(should_send)
        self.assertEqual(slot, "2026-06-05-08")

    def test_state_file_records_slot_string(self):
        with TemporaryDirectory() as tmp_dir:
            state_path = Path(tmp_dir) / "scheduled_send_state.json"
            state = {"last_sent_slot": "2026-06-05-21"}

            save_scheduled_send_state(state_path, state)
            loaded = load_scheduled_send_state(state_path)

            self.assertEqual(loaded["last_sent_slot"], "2026-06-05-21")
            self.assertEqual(json.loads(state_path.read_text(encoding="utf-8")), state)

    def test_get_current_send_slot_rejects_non_zero_minute(self):
        now = datetime(2026, 6, 5, 8, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai"))

        slot = get_current_send_slot(now)

        self.assertIsNone(slot)

    def test_get_current_send_slot_allows_any_second_within_scheduled_hour_boundary(self):
        now = datetime(2026, 6, 5, 8, 0, 59, tzinfo=ZoneInfo("Asia/Shanghai"))

        slot = get_current_send_slot(now)

        self.assertEqual(slot, "2026-06-05-08")


if __name__ == "__main__":
    unittest.main()
