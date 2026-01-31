"""
Tests for the enhanced schedule parsing functionality.

This module tests the various schedule format parsing capabilities,
including different day formats, time slots, ranges, and separators.
"""
import pytest
from course_scheduler.app.utils.schedule_utils import (
    parse_schedule, DAY_ORDER, SLOT_TIMES, format_slot
)


def test_basic_schedule_formats():
    """Test parsing of basic schedule formats like M1, W2, Th3."""
    assert parse_schedule("M1") == [("M", 1)]
    assert parse_schedule("Th3") == [("Th", 3)]
    assert parse_schedule("Sa12") == [("Sa", 12)]
    assert parse_schedule("Su11") == [("Su", 11)]

    # Test with spaces
    assert parse_schedule("M 1") == [("M", 1)]
    assert parse_schedule("Th 3") == [("Th", 3)]


def test_range_formats():
    """Test parsing of range formats like M1-3."""
    # Single day ranges
    assert parse_schedule("M1-3") == [("M", 1), ("M", 2), ("M", 3)]
    assert parse_schedule("W2-4") == [("W", 2), ("W", 3), ("W", 4)]
    assert parse_schedule("T 3-5") == [("T", 3), ("T", 4), ("T", 5)]

    # Range with spaces
    assert parse_schedule("F 1 - 3") == [("F", 1), ("F", 2), ("F", 3)]

    # Range validation (should limit to 1-12)
    assert parse_schedule("M0-2") == [("M", 1), ("M", 2)]  # 0 clamped to 1
    assert parse_schedule("M11-14") == [("M", 11), ("M", 12)]  # 14 clamped to 12


def test_list_formats():
    """Test parsing of list formats like M(1,3,5) or W1,3."""
    # Parenthesized lists
    assert parse_schedule("M(1,3,5)") == [("M", 1), ("M", 3), ("M", 5)]
    assert parse_schedule("W(2,4,6)") == [("W", 2), ("W", 4), ("W", 6)]

    # Space-separated lists within parentheses
    assert parse_schedule("T(1, 3, 5)") == [("T", 1), ("T", 3), ("T", 5)]

    # Multiple slots without parentheses
    assert parse_schedule("M1,M3") == [("M", 1), ("M", 3)]


def test_mixed_separators():
    """Test parsing with mixed separators."""
    # Commas, semicolons, newlines
    mixed_input = "M1, W2; Th3\nF4"
    assert parse_schedule(mixed_input) == [("M", 1), ("W", 2), ("Th", 3), ("F", 4)]

    # Slashes
    assert parse_schedule("M1/W2/F3") == [("M", 1), ("W", 2), ("F", 3)]

    # Mixed with ranges
    assert parse_schedule("M1-3; W5, F7") == [
        ("M", 1), ("M", 2), ("M", 3), ("W", 5), ("F", 7)
    ]


def test_turkish_day_names():
    """Test parsing of Turkish day names and abbreviations."""
    # Standard abbreviations
    assert parse_schedule("Pzt 1") == [("M", 1)]
    assert parse_schedule("Sal 2") == [("T", 2)]
    assert parse_schedule("Çar 3") == [("W", 3)]
    assert parse_schedule("Per 4") == [("Th", 4)]
    assert parse_schedule("Cum 5") == [("F", 5)]
    assert parse_schedule("Cmt 6") == [("Sa", 6)]
    assert parse_schedule("Paz 7") == [("Su", 7)]

    # Full names (case insensitive)
    assert parse_schedule("Pazartesi 1") == [("M", 1)]
    assert parse_schedule("SALI 2") == [("T", 2)]
    assert parse_schedule("çarşamba 3") == [("W", 3)]
    assert parse_schedule("PERŞEMBE 4") == [("Th", 4)]
    assert parse_schedule("cuma 5") == [("F", 5)]

    # With diacritics removal
    assert parse_schedule("Çarşamba 3") == [("W", 3)]
    assert parse_schedule("Persembe 4") == [("Th", 4)]


def test_mixed_formats():
    """Test parsing of complex mixed formats."""
    complex_input = "Pzt 1-2, Sal(3,5); Çar 4, Per 1-3, Cum 5"
    expected = [
        ("M", 1), ("M", 2),          # Pzt 1-2
        ("T", 3), ("T", 5),          # Sal(3,5)
        ("W", 4),                    # Çar 4
        ("Th", 1), ("Th", 2), ("Th", 3),  # Per 1-3
        ("F", 5)                     # Cum 5
    ]
    assert parse_schedule(complex_input) == expected


def test_invalid_inputs():
    """Test handling of invalid or edge case inputs."""
    # Empty inputs
    assert parse_schedule("") == []
    assert parse_schedule(None) == []
    assert parse_schedule("nan") == []

    # Invalid day codes should be skipped
    assert parse_schedule("X1, Y2, Z3") == []

    # Valid days with invalid slots should keep valid slots only
    assert parse_schedule("M13, M0, M5") == [("M", 5)]  # Only 5 is valid (1-12)

    # Mixed valid and invalid
    assert parse_schedule("X1, M2, Y3") == [("M", 2)]


def test_format_slot():
    """Test the format_slot function for human-readable output."""
    assert format_slot("M", 1) == "Monday 08:30-09:20"
    assert format_slot("T", 2) == "Tuesday 09:30-10:20"
    assert format_slot("W", 3) == "Wednesday 10:30-11:20"
    assert format_slot("Th", 4) == "Thursday 11:30-12:20"
    assert format_slot("F", 5) == "Friday 12:30-13:20"

    # With short day names
    assert format_slot("M", 1, use_short_day=True) == "Mon 08:30-09:20"
    assert format_slot("Th", 4, use_short_day=True) == "Thu 11:30-12:20"


def test_day_order_consistency():
    """Test that DAY_ORDER contains all necessary day codes in the right order."""
    assert DAY_ORDER == ["M", "T", "W", "Th", "F", "Sa", "Su"]

    # Ensure all day codes have time mappings
    for slot in range(1, 13):
        assert slot in SLOT_TIMES
        assert ":" in SLOT_TIMES[slot]  # Should have a time format
