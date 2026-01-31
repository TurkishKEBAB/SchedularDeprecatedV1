"""
Tests for schedule metrics and scoring.

This module tests the schedule analysis and scoring functions in schedule_metrics.py.
"""
import pytest
from course_scheduler.app.utils.schedule_metrics import (
    SchedulerPrefs, ScheduleStats, analyze_day, is_quasi_free_day,
    compute_schedule_stats, score_schedule, meets_weekly_hours_constraint,
    meets_daily_hours_constraint, meets_free_day_constraint
)
from course_scheduler.app.data.models import Course, Schedule


@pytest.fixture
def test_courses():
    """Create a set of test courses with known schedules."""
    return [
        # Monday-Wednesday morning course
        Course(
            code="CS101.1",
            main_code="CS101",
            name="Introduction to CS",
            ects=5,
            course_type="lecture",
            schedule=[("M", 1), ("M", 2), ("W", 1)],
            teacher="Dr. Smith",
            has_lecture=True
        ),
        # Monday-Wednesday afternoon course
        Course(
            code="MATH101.1",
            main_code="MATH101",
            name="Calculus",
            ects=6,
            course_type="lecture",
            schedule=[("M", 5), ("M", 6), ("W", 5)],
            teacher="Dr. Johnson",
            has_lecture=True
        ),
        # Tuesday all day course
        Course(
            code="PHYS101.1",
            main_code="PHYS101",
            name="Physics",
            ects=5,
            course_type="lecture",
            schedule=[("T", 2), ("T", 3), ("T", 4), ("T", 5)],
            teacher="Dr. Brown",
            has_lecture=True
        ),
        # Thursday with gaps
        Course(
            code="CHEM101.1",
            main_code="CHEM101",
            name="Chemistry",
            ects=5,
            course_type="lecture",
            schedule=[("Th", 1), ("Th", 4), ("Th", 6)],
            teacher="Dr. Garcia",
            has_lecture=True
        ),
        # Friday early morning only
        Course(
            code="ENG101.1",
            main_code="ENG101",
            name="English",
            ects=3,
            course_type="lecture",
            schedule=[("F", 1)],
            teacher="Dr. Wilson",
            has_lecture=True
        )
    ]


@pytest.fixture
def compact_schedule(test_courses):
    """Create a compact schedule with classes on fewer days."""
    return Schedule([test_courses[0], test_courses[2]])  # Mon-Wed + Tuesday courses


@pytest.fixture
def spread_schedule(test_courses):
    """Create a spread-out schedule with classes on many days."""
    return Schedule([test_courses[0], test_courses[3], test_courses[4]])  # Mon-Wed + Thursday + Friday


@pytest.fixture
def busy_schedule(test_courses):
    """Create a busy schedule with no free days."""
    return Schedule(test_courses)  # All courses, all days


def test_analyze_day(busy_schedule):
    """Test the analyze_day function."""
    # Monday has 4 slots (1, 2, 5, 6) = 4 slots, 1 gap (between 2-5), longest consecutive block = 2
    slots_used, gaps, longest_block = analyze_day(busy_schedule, "M")
    assert slots_used == 4
    assert gaps == 2  # gap between 2-5 (slots 3, 4)
    assert longest_block == 2  # slots 1-2 and 5-6 are both consecutive pairs

    # Tuesday has 4 slots (2, 3, 4, 5) = 4 slots, 0 gaps, longest consecutive block = 4
    slots_used, gaps, longest_block = analyze_day(busy_schedule, "T")
    assert slots_used == 4
    assert gaps == 0  # no gaps
    assert longest_block == 4  # slots 2-5 are consecutive

    # Thursday has 3 slots (1, 4, 6) = 3 slots, 3 gaps, longest consecutive block = 1
    slots_used, gaps, longest_block = analyze_day(busy_schedule, "Th")
    assert slots_used == 3
    assert gaps == 3  # gaps between 1-4 (slots 2, 3) and 4-6 (slot 5)
    assert longest_block == 1  # no consecutive slots

    # Saturday has no classes
    slots_used, gaps, longest_block = analyze_day(busy_schedule, "Sa")
    assert slots_used == 0
    assert gaps == 0
    assert longest_block == 0


def test_is_quasi_free_day():
    """Test the is_quasi_free_day function."""
    # Empty schedule
    empty_schedule = Schedule([])
    assert is_quasi_free_day(empty_schedule, "M") == True

    # Schedule with early classes only
    early_course = Course(
        code="CS101.1",
        main_code="CS101",
        name="Introduction to CS",
        ects=5,
        course_type="lecture",
        schedule=[("M", 1)],
        teacher="Dr. Smith",
        has_lecture=True
    )
    early_schedule = Schedule([early_course])
    assert is_quasi_free_day(early_schedule, "M") == True

    # Schedule with two early classes
    early_course2 = Course(
        code="MATH101.1",
        main_code="MATH101",
        name="Calculus",
        ects=6,
        course_type="lecture",
        schedule=[("M", 2)],
        teacher="Dr. Johnson",
        has_lecture=True
    )
    early_schedule2 = Schedule([early_course, early_course2])
    assert is_quasi_free_day(early_schedule2, "M") == True

    # Schedule with more than 2 early classes
    early_course3 = Course(
        code="PHYS101.1",
        main_code="PHYS101",
        name="Physics",
        ects=5,
        course_type="lecture",
        schedule=[("M", 1), ("M", 2), ("M", 3)],
        teacher="Dr. Brown",
        has_lecture=True
    )
    early_schedule3 = Schedule([early_course3])
    assert is_quasi_free_day(early_schedule3, "M") == False

    # Schedule with later classes
    late_course = Course(
        code="CS102.1",
        main_code="CS102",
        name="Advanced CS",
        ects=5,
        course_type="lecture",
        schedule=[("M", 3)],
        teacher="Dr. Smith",
        has_lecture=True
    )
    late_schedule = Schedule([late_course])
    assert is_quasi_free_day(late_schedule, "M") == False


def test_compute_schedule_stats(compact_schedule, spread_schedule, busy_schedule):
    """Test compute_schedule_stats function."""
    # Test compact schedule (Mon-Wed + Tuesday)
    stats_compact = compute_schedule_stats(compact_schedule)
    assert stats_compact.days_used == {"M", "T", "W"}
    assert stats_compact.free_days == {"Th", "F", "Sa", "Su"}
    assert stats_compact.weekly_slots == 7  # 3 slots M+W, 4 slots T

    # Test spread schedule (Mon-Wed + Thursday + Friday)
    stats_spread = compute_schedule_stats(spread_schedule)
    assert stats_spread.days_used == {"M", "W", "Th", "F"}
    assert stats_spread.free_days == {"T", "Sa", "Su"}
    assert stats_spread.weekly_slots == 7  # 3 slots M+W, 3 slots Th, 1 slot F

    # Test busy schedule (all days M-F)
    stats_busy = compute_schedule_stats(busy_schedule)
    assert stats_busy.days_used == {"M", "T", "W", "Th", "F"}
    assert stats_busy.free_days == {"Sa", "Su"}
    assert stats_busy.weekly_slots == 12  # All slots from all courses

    # Test desired free days with compact schedule
    stats_compact_desired = compute_schedule_stats(compact_schedule, desired_free_days=["T", "Th", "F"])
    assert stats_compact_desired.satisfied_desired_free_days == {"Th", "F"}  # T is not free


def test_score_schedule(compact_schedule, spread_schedule):
    """Test score_schedule function with different preference settings."""
    # Create preferences with compression enabled
    compress_prefs = SchedulerPrefs(
        compress_classes=True,
        desired_free_days=[],
        strict_free_days=True,
        weight_compression=1.0,
        weight_gaps=1.0
    )

    # Compact schedule should score better when compression is preferred
    compact_score = score_schedule(compact_schedule, compress_prefs)
    spread_score = score_schedule(spread_schedule, compress_prefs)
    assert compact_score < spread_score  # Lower score is better

    # Create preferences with specific free days
    free_day_prefs = SchedulerPrefs(
        compress_classes=True,
        desired_free_days=["T", "F"],
        strict_free_days=True
    )

    # Spread schedule has free Tuesday, compact doesn't
    compact_score = score_schedule(compact_schedule, free_day_prefs)
    spread_score = score_schedule(spread_schedule, free_day_prefs)
    assert compact_score > spread_score  # Spread scores better (has free Tuesday)


def test_meets_weekly_hours_constraint(compact_schedule, busy_schedule):
    """Test weekly hours constraint checking."""
    # Compact schedule has 7 slots
    assert meets_weekly_hours_constraint(compact_schedule, 10) == True
    assert meets_weekly_hours_constraint(compact_schedule, 7) == True
    assert meets_weekly_hours_constraint(compact_schedule, 6) == False

    # Busy schedule has 12 slots
    assert meets_weekly_hours_constraint(busy_schedule, 15) == True
    assert meets_weekly_hours_constraint(busy_schedule, 12) == True
    assert meets_weekly_hours_constraint(busy_schedule, 10) == False


def test_meets_daily_hours_constraint(compact_schedule, busy_schedule):
    """Test daily hours constraint checking."""
    # Compact schedule has max 4 slots on Tuesday
    assert meets_daily_hours_constraint(compact_schedule, 5) == True
    assert meets_daily_hours_constraint(compact_schedule, 4) == True
    assert meets_daily_hours_constraint(compact_schedule, 3) == False

    # Busy schedule has max 4 slots per day
    assert meets_daily_hours_constraint(busy_schedule, 4) == True
    assert meets_daily_hours_constraint(busy_schedule, 3) == False


def test_meets_free_day_constraint():
    """Test free day constraint checking."""
    # Create schedules with known free days
    mon_only_course = Course(
        code="CS101.1",
        main_code="CS101",
        name="Introduction to CS",
        ects=5,
        course_type="lecture",
        schedule=[("M", 1), ("M", 2)],
        teacher="Dr. Smith",
        has_lecture=True
    )

    tue_only_course = Course(
        code="MATH101.1",
        main_code="MATH101",
        name="Calculus",
        ects=6,
        course_type="lecture",
        schedule=[("T", 1), ("T", 2)],
        teacher="Dr. Johnson",
        has_lecture=True
    )

    wed_early_course = Course(
        code="ENG101.1",
        main_code="ENG101",
        name="English",
        ects=3,
        course_type="lecture",
        schedule=[("W", 1)],
        teacher="Dr. Wilson",
        has_lecture=True
    )

    mon_tue_schedule = Schedule([mon_only_course, tue_only_course])
    mon_wed_schedule = Schedule([mon_only_course, wed_early_course])

    # Test with strict mode
    assert meets_free_day_constraint(mon_tue_schedule, ["W", "Th", "F"], strict=True) == True
    assert meets_free_day_constraint(mon_tue_schedule, ["T", "W"], strict=True) == False

    # Test with relaxed mode
    assert meets_free_day_constraint(mon_wed_schedule, ["W", "Th"], strict=False) == True  # W has early class only
    assert meets_free_day_constraint(mon_tue_schedule, ["T"], strict=False) == False  # T has normal classes
