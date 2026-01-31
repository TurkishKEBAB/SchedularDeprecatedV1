"""
Tests for schedule parsing and time slot functionality.

This module tests the schedule parsing utilities and time slot mappings.
"""
import pytest
from course_scheduler.app.utils.schedule_utils import (
    parse_schedule,
    get_time_for_slot,
    format_slot,
    get_full_day_name,
    get_short_day_name
)


def test_parse_schedule_simple():
    """Test parsing simple schedule strings."""
    # Test basic day-hour combinations
    assert parse_schedule("M1") == [("M", 1)]
    assert parse_schedule("T2") == [("T", 2)]
    assert parse_schedule("W3") == [("W", 3)]
    assert parse_schedule("F4") == [("F", 4)]


def test_parse_schedule_multi_character_days():
    """Test parsing schedule strings with multi-character day codes."""
    # Test special multi-character day codes
    assert parse_schedule("Th5") == [("Th", 5)]
    assert parse_schedule("Sa6") == [("Sa", 6)]
    assert parse_schedule("Su7") == [("Su", 7)]


def test_parse_schedule_multiple_slots():
    """Test parsing schedule strings with multiple slots."""
    # Test multiple slots in one string
    assert parse_schedule("M1,W3,F5") == [("M", 1), ("W", 3), ("F", 5)]
    assert parse_schedule("Th2,Sa4,Su6") == [("Th", 2), ("Sa", 4), ("Su", 6)]
    assert parse_schedule("M1,T1,W1,Th1,F1,Sa1,Su1") == [
        ("M", 1), ("T", 1), ("W", 1), ("Th", 1), ("F", 1), ("Sa", 1), ("Su", 1)
    ]


def test_parse_schedule_edge_cases():
    """Test parse_schedule with edge cases."""
    # Test empty/invalid inputs
    assert parse_schedule("") == []
    assert parse_schedule(None) == []
    import numpy as np
    import pandas as pd
    assert parse_schedule(pd.NA) == []
    assert parse_schedule(np.nan) == []

    # Test with unusual formatting
    assert parse_schedule(" M1 , W2 ") == [("M", 1), ("W", 2)]
    assert parse_schedule("M1,W2,invalid") == [("M", 1), ("W", 2)]


def test_time_slot_mapping():
    """Test mapping between slot numbers and time strings."""
    # Test mapping of slots to time strings
    assert get_time_for_slot(1) == "08:30-09:20"
    assert get_time_for_slot(5) == "12:30-13:20"
    assert get_time_for_slot(12) == "19:30-20:20"

    # Test invalid slot
    assert get_time_for_slot(13) == ""
    assert get_time_for_slot(-1) == ""


def test_day_name_mapping():
    """Test mapping between day codes and full/short day names."""
    # Test full day names
    assert get_full_day_name("M") == "Monday"
    assert get_full_day_name("T") == "Tuesday"
    assert get_full_day_name("W") == "Wednesday"
    assert get_full_day_name("Th") == "Thursday"
    assert get_full_day_name("F") == "Friday"
    assert get_full_day_name("Sa") == "Saturday"
    assert get_full_day_name("Su") == "Sunday"

    # Test short day names
    assert get_short_day_name("M") == "Mon"
    assert get_short_day_name("Th") == "Thu"
    assert get_short_day_name("Su") == "Sun"


def test_format_slot():
    """Test formatting day and slot into human-readable strings."""
    # Test with full day names
    assert format_slot("M", 1) == "Monday 08:30-09:20"
    assert format_slot("Th", 5) == "Thursday 12:30-13:20"
    assert format_slot("Su", 12) == "Sunday 19:30-20:20"

    # Test with short day names
    assert format_slot("M", 1, True) == "Mon 08:30-09:20"
    assert format_slot("Th", 5, True) == "Thu 12:30-13:20"

    # Test with invalid slot
    assert format_slot("M", 15) == "Monday Slot 15"

    # Test with invalid day
    assert format_slot("X", 1) == "X 08:30-09:20"
