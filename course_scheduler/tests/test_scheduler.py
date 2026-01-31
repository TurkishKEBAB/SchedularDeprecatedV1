"""
Tests for the scheduling algorithms.
"""
import pytest
from course_scheduler.app.data.models import Course, Schedule, build_course_groups
from course_scheduler.app.scheduler.constraints import ConstraintUtils
from course_scheduler.app.scheduler.dfs import DFSScheduler


def test_constraints_generation(sample_courses):
    """Test auto-generating constraints from course data."""
    constraints = ConstraintUtils.auto_generate_constraints(sample_courses)

    # CS101 should have problem session but no lab
    assert constraints["CS101"]["must_ps"] is True
    assert constraints["CS101"]["must_lab"] is False

    # MATH201 should have problem session but no lab
    assert constraints["MATH201"]["must_ps"] is True
    assert constraints["MATH201"]["must_lab"] is False

    # PHY101 should have lab but no problem session
    assert constraints["PHY101"]["must_ps"] is False
    assert constraints["PHY101"]["must_lab"] is True


def test_valid_group_selections(sample_courses):
    """Test generating valid selections for course groups."""
    course_groups = build_course_groups(sample_courses)
    constraints = ConstraintUtils.auto_generate_constraints(sample_courses)

    # Test CS101 group - should generate combinations with lecture and optional PS
    cs_group = course_groups["CS101"].courses
    selections = ConstraintUtils.generate_valid_group_selections(cs_group, constraints)

    assert len(selections) == 2  # Should have 2 options: [lecture] or [lecture, PS]

    # Each selection should have at least the lecture
    for selection in selections:
        assert any(c.code == "CS101.1" for c in selection)

    # At least one selection should have the problem session
    has_ps = any(any(c.code == "CS101-PS1" for c in selection) for selection in selections)
    assert has_ps


def test_build_group_options(sample_courses):
    """Test building group options for scheduling."""
    course_groups = build_course_groups(sample_courses)
    mandatory_codes = {"CS101", "MATH201"}

    group_valid_selections, group_options = ConstraintUtils.build_group_options(
        course_groups, mandatory_codes, "sections"
    )

    # Mandatory courses should not have None option
    assert None not in group_options["CS101"]
    assert None not in group_options["MATH201"]

    # Optional course should have None option
    assert None in group_options["PHY101"]

    # Test with replacement_target="course"
    _, course_options = ConstraintUtils.build_group_options(
        course_groups, mandatory_codes, "course"
    )

    # Each mandatory course should have exactly one option (first valid option)
    assert len(course_options["CS101"]) == 1
    assert course_options["CS101"][0] is not None


def test_dfs_scheduler(sample_courses):
    """Test the DFS scheduler algorithm."""
    # Create scheduler
    scheduler = DFSScheduler(
        max_ects=20,
        allow_conflict=0,
        max_results=5
    )

    # Build course groups
    course_groups = build_course_groups(sample_courses)
    mandatory_set = {"CS101"}

    # Generate constraints and options
    group_valid_selections, group_options = ConstraintUtils.build_group_options(
        course_groups, mandatory_set, "sections"
    )

    # Sort keys by priority
    sorted_group_keys = list(course_groups.keys())

    # Generate schedules
    schedules = scheduler.generate_schedules(
        group_keys=sorted_group_keys,
        group_options=group_options,
        mandatory_set=mandatory_set,
        freq_prefs={},
        count_optional=True,
        group_valid_selections=group_valid_selections
    )

    # Check if schedules were generated
    assert len(schedules) > 0

    # Check if all schedules include the mandatory course
    for schedule in schedules:
        has_mandatory = False
        for course in schedule.courses:
            if course.main_code == "CS101":
                has_mandatory = True
                break
        assert has_mandatory

    # Check if schedules have no conflicts
    for schedule in schedules:
        assert schedule.conflict_count == 0


def test_schedule_failure_analysis():
    """Test analyzing reasons for scheduling failures."""
    # Create an empty valid selections dictionary
    group_valid_selections = {
        "CS101": [],  # No valid selections
        "MATH201": [["some_selection"]]  # Has valid selections
    }
    mandatory_set = {"CS101", "MATH201"}

    reasons = ConstraintUtils.analyze_schedule_failure(group_valid_selections, mandatory_set)

    assert len(reasons) == 2
    assert any("No valid sections available" in reason for reason in reasons)
    assert any("Check for conflicts" in reason for reason in reasons)
