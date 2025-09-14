"""
Core rules engine for the course scheduler.

This module implements conflict detection, overlap policy enforcement,
credit calculations, and filtering logic.
"""
import logging
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict

from .models import Course, Schedule, CourseSelection, SelectionState, Config

logger = logging.getLogger(__name__)


def conflict_cost(schedule: List[Course]) -> int:
    """
    Calculate the conflict cost for a schedule.

    Args:
        schedule: List of courses

    Returns:
        Number of conflicting time slots
    """
    slot_counts = defaultdict(int)
    for course in schedule:
        for slot in course.schedule:
            slot_counts[slot] += 1

    return sum(max(0, count - 1) for count in slot_counts.values())


def overlap_policy_ok(schedule: List[Course]) -> bool:
    """
    Check if schedule satisfies overlap policy:
    - At most 1 overlapping hour per course (main_code)
    - Overlaps across at most 2 distinct courses total

    Args:
        schedule: List of courses to check

    Returns:
        True if overlap policy is satisfied
    """
    # Track overlaps per main_code
    main_code_overlaps = defaultdict(int)
    courses_with_overlaps = set()

    # Group courses by main_code
    courses_by_main = defaultdict(list)
    for course in schedule:
        courses_by_main[course.main_code].append(course)

    # Check overlaps within each main_code group
    for main_code, courses in courses_by_main.items():
        overlaps = _count_overlaps_in_group(courses)
        if overlaps > 1:  # More than 1 overlapping hour per course
            return False
        if overlaps > 0:
            main_code_overlaps[main_code] = overlaps
            courses_with_overlaps.add(main_code)

    # Check global overlap limit (at most 2 courses with overlaps)
    if len(courses_with_overlaps) > 2:
        return False

    return True


def _count_overlaps_in_group(courses: List[Course]) -> int:
    """Count overlapping time slots within a group of courses."""
    all_slots = []
    for course in courses:
        all_slots.extend(course.schedule)

    slot_counts = defaultdict(int)
    for slot in all_slots:
        slot_counts[slot] += 1

    return sum(max(0, count - 1) for count in slot_counts.values())


def get_effective_credit(course: Course, frequency_prefs: Dict[str, int],
                        count_optional: bool) -> int:
    """
    Calculate effective credit for a course based on frequency preferences.

    Args:
        course: Course to evaluate
        frequency_prefs: Dictionary mapping main_code to frequency (0-3)
        count_optional: Whether to count optional courses

    Returns:
        Effective credit value
    """
    frequency = frequency_prefs.get(course.main_code, 3)  # Default to "Always"

    # If frequency is less than "Always" (3) and we're not counting optional
    if frequency < 3 and not count_optional:
        return 0

    return course.ects


def no_conflict(existing_schedule: List[Course], new_courses: List[Course]) -> bool:
    """
    Check if adding new courses would create conflicts with existing schedule.

    Args:
        existing_schedule: Current courses in schedule
        new_courses: Courses to potentially add

    Returns:
        True if no conflicts would be created
    """
    occupied_slots = set()
    for course in existing_schedule:
        for slot in course.schedule:
            occupied_slots.add(slot)

    for course in new_courses:
        for slot in course.schedule:
            if slot in occupied_slots:
                return False

    return True


def apply_tri_state_filtering(course_groups: Dict[str, List[Course]],
                             selections: Dict[str, CourseSelection]) -> Dict[str, List[Course]]:
    """
    Apply tri-state filtering to course groups.

    Args:
        course_groups: Dictionary mapping main_code to course list
        selections: Dictionary mapping main_code to selection state

    Returns:
        Filtered course groups
    """
    filtered_groups = {}

    for main_code, courses in course_groups.items():
        selection = selections.get(main_code)

        if selection and selection.state == SelectionState.EXCLUDE:
            # Exclude: remove entirely from options
            continue
        elif selection and selection.state == SelectionState.INCLUDE:
            # Include: keep in mandatory set
            filtered_groups[main_code] = courses
        else:
            # Neutral: keep as optional
            filtered_groups[main_code] = courses

    return filtered_groups


def apply_teacher_filtering(courses: List[Course], preferred_teacher: Optional[str]) -> List[Course]:
    """
    Filter courses by preferred teacher.

    Args:
        courses: List of courses to filter
        preferred_teacher: Preferred teacher name (None for no filtering)

    Returns:
        Filtered list of courses
    """
    if not preferred_teacher or preferred_teacher == "Default":
        return courses

    return [course for course in courses if course.teacher == preferred_teacher]


def build_course_groups(courses: List[Course]) -> Dict[str, List[Course]]:
    """
    Group courses by main_code.

    Args:
        courses: List of all courses

    Returns:
        Dictionary mapping main_code to course list
    """
    groups = defaultdict(list)
    for course in courses:
        groups[course.main_code].append(course)

    return dict(groups)


def generate_valid_group_selections(course_group: List[Course],
                                  constraints: Dict[str, bool],
                                  teacher_filter: Optional[str] = None) -> List[List[Course]]:
    """
    Generate valid course selections for a group, respecting constraints and teacher preferences.

    Args:
        course_group: List of courses in the group
        constraints: Dictionary with 'must_ps' and 'must_lab' flags
        teacher_filter: Optional teacher preference

    Returns:
        List of valid course combinations
    """
    # Apply teacher filtering first
    if teacher_filter:
        course_group = apply_teacher_filtering(course_group, teacher_filter)

    # Separate by type
    lectures = [c for c in course_group if c.has_lecture]
    ps_sections = [c for c in course_group if c.type.value == "ps"]
    lab_sections = [c for c in course_group if c.type.value == "lab"]

    if not lectures:
        return []

    valid_selections = []
    must_ps = constraints.get("must_ps", False)
    must_lab = constraints.get("must_lab", False)

    # Check if constraints can be satisfied
    if must_ps and not ps_sections:
        return []
    if must_lab and not lab_sections:
        return []

    for lecture in lectures:
        base_selection = [lecture]

        # Determine PS options
        ps_options = ps_sections if must_ps else [None] + ps_sections

        # Determine Lab options
        lab_options = lab_sections if must_lab else [None] + lab_sections

        # Generate all combinations
        for ps in ps_options:
            for lab in lab_options:
                selection = base_selection.copy()
                if ps is not None:
                    selection.append(ps)
                if lab is not None:
                    selection.append(lab)

                valid_selections.append(selection)

    return valid_selections


def validate_schedule_constraints(schedule: List[Course], config: Config) -> Tuple[bool, List[str]]:
    """
    Validate that a schedule meets all constraints.

    Args:
        schedule: Schedule to validate
        config: Configuration with constraints

    Returns:
        Tuple of (is_valid, list_of_violations)
    """
    violations = []

    # Check ECTS limit
    total_credits = sum(course.ects for course in schedule)
    if total_credits > config.max_ects:
        violations.append(f"Exceeds ECTS limit: {total_credits} > {config.max_ects}")

    # Check conflict limit
    conflicts = conflict_cost(schedule)
    if conflicts > config.allow_conflict:
        violations.append(f"Exceeds conflict limit: {conflicts} > {config.allow_conflict}")

    # Check overlap policy
    if not overlap_policy_ok(schedule):
        violations.append("Violates overlap policy")

    return len(violations) == 0, violations


def calculate_schedule_score(schedule: List[Course], config: Config) -> float:
    """
    Calculate a quality score for a schedule.

    Args:
        schedule: Schedule to score
        config: Configuration

    Returns:
        Score (higher is better)
    """
    total_credits = sum(course.ects for course in schedule)
    conflicts = conflict_cost(schedule)

    # Base score: prefer schedules closer to max ECTS
    score = 1000 - abs(config.max_ects - total_credits) * 10

    # Penalty for conflicts
    score -= conflicts * 100

    # Bonus for variety (different main codes)
    unique_codes = len(set(course.main_code for course in schedule))
    score += unique_codes * 5

    return score


def auto_generate_constraints(courses: List[Course]) -> Dict[str, Dict[str, bool]]:
    """
    Auto-generate constraints based on available course types.

    Args:
        courses: List of all courses

    Returns:
        Dictionary mapping main_code to constraint dict
    """
    groups = build_course_groups(courses)
    constraints = {}

    for main_code, group in groups.items():
        has_ps = any(c.type.value == "ps" for c in group)
        has_lab = any(c.type.value == "lab" for c in group)

        constraints[main_code] = {
            "must_ps": has_ps,
            "must_lab": has_lab
        }

    return constraints
