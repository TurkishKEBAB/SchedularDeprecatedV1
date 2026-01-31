"""
Schedule utilities for handling time slots and schedule parsing.

This module provides utilities for parsing schedule strings, mapping day codes to full names,
and converting between schedule notation and human-readable time formats.
"""
import re
import unicodedata
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd

# Maps day codes to their full names
DAY_CODES = {
    "M": "Monday",
    "T": "Tuesday",
    "W": "Wednesday",
    "Th": "Thursday",
    "F": "Friday",
    "Sa": "Saturday",
    "Su": "Sunday"
}

# Maps day codes to short display formats
DAY_SHORT_CODES = {
    "M": "Mon",
    "T": "Tue",
    "W": "Wed",
    "Th": "Thu",
    "F": "Fri",
    "Sa": "Sat",
    "Su": "Sun"
}

# Maps Turkish day names/abbreviations to day codes
TURKISH_DAY_MAPPING = {
    "PZT": "M",
    "PAZARTESI": "M",
    "PAZARTESİ": "M",
    "SAL": "T",
    "SALI": "T",
    "ÇALI": "T",
    "CAR": "W",
    "ÇAR": "W",
    "CARSAMBA": "W",
    "ÇARŞAMBA": "W",
    "PER": "Th",
    "PERSEMBE": "Th",
    "PERŞEMBE": "Th",
    "CUM": "F",
    "CUMA": "F",
    "CMT": "Sa",
    "CUMARTESİ": "Sa",
    "CUMARTESI": "Sa",
    "PAZ": "Su",
    "PAZAR": "Su"
}

# Maps slot numbers to time ranges
SLOT_TIMES = {
    1: "08:30-09:20",
    2: "09:30-10:20",
    3: "10:30-11:20",
    4: "11:30-12:20",
    5: "12:30-13:20",
    6: "13:30-14:20",
    7: "14:30-15:20",
    8: "15:30-16:20",
    9: "16:30-17:20",
    10: "17:30-18:20",
    11: "18:30-19:20",
    12: "19:30-20:20"
}

# Default order of days for display
DAY_ORDER = ["M", "T", "W", "Th", "F", "Sa", "Su"]


def get_all_days() -> List[str]:
    """
    Get all available day codes.

    Returns:
        List of all day codes (M, T, W, Th, F, Sa, Su)
    """
    return list(DAY_CODES.keys())


def get_all_slots() -> List[int]:
    """
    Get all available slot numbers.

    Returns:
        List of all slot numbers (1-12)
    """
    return list(SLOT_TIMES.keys())


def get_short_day_name(day_code: str) -> str:
    """
    Get the short name for a day code.

    Args:
        day_code: Day code (M, T, W, Th, F, Sa, Su)

    Returns:
        Short day name (Mon, Tue, Wed, etc.)
    """
    return DAY_SHORT_CODES.get(day_code, day_code)


def get_full_day_name(day_code: str) -> str:
    """
    Get the full name for a day code.

    Args:
        day_code: Day code (M, T, W, Th, F, Sa, Su)

    Returns:
        Full day name (Monday, Tuesday, Wednesday, etc.)
    """
    return DAY_CODES.get(day_code, day_code)


def get_time_for_slot(slot: int) -> str:
    """
    Get the time range for a slot number.

    Args:
        slot: Slot number (1-12)

    Returns:
        Time range string (e.g., "08:30-09:20")
    """
    return SLOT_TIMES.get(slot, f"Unknown-{slot}")


def format_slot(day_code: str, slot: int) -> str:
    """
    Format a day code and slot into a human-readable string.

    Args:
        day_code: Day code (M, T, W, Th, F, Sa, Su)
        slot: Slot number (1-12)

    Returns:
        Formatted string like "Thu 09:30-10:20"
    """
    day_name = get_short_day_name(day_code)
    time_range = get_time_for_slot(slot)
    return f"{day_name} {time_range}"


def normalize_string(s: str) -> str:
    """
    Normalize a string by removing diacritics and converting to uppercase.

    Args:
        s: Input string

    Returns:
        Normalized string
    """
    if not s:
        return ""

    # Remove diacritics
    normalized = unicodedata.normalize('NFD', s)
    without_diacritics = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')

    # Convert to uppercase and strip
    return without_diacritics.upper().strip()


def parse_schedule(schedule_str: str) -> List[Tuple[str, int]]:
    """
    Parse a schedule string into a list of (day_code, slot) tuples.

    Supports various formats:
    - Simple: "M1", "Th2", "Sa12"
    - With spaces: "M 1", "Th 2"
    - Ranges: "M1-3" (expands to M1, M2, M3)
    - Lists: "M(1,3,5)" or "M1,2"
    - Turkish names: "Pzt1", "Per2", "Çar3"
    - Mixed separators: commas, semicolons, newlines

    Args:
        schedule_str: Raw schedule string from Excel

    Returns:
        List of (day_code, slot) tuples
    """
    if not schedule_str or pd.isna(schedule_str):
        return []

    # Normalize the string
    schedule_str = str(schedule_str).strip()
    if not schedule_str:
        return []

    # Replace newlines and normalize separators
    schedule_str = re.sub(r'[\n\r]+', ',', schedule_str)
    schedule_str = re.sub(r'[;/]+', ',', schedule_str)
    schedule_str = re.sub(r'\s+', ' ', schedule_str)

    result = []

    # Enhanced regex pattern that handles Turkish days and various formats
    # Order matters: Th before T, Sa before S, etc.
    pattern = r'(?:Th|Sa|Su|M|T|W|F|PZT|PAZARTESİ?|SAL[IİÇ]?|ÇAR|ÇARŞAMBA|PER|PERŞEMBE|CUM[A]?|CMT|CUMARTESİ?|PAZ|PAZAR)\s*(?:\d+(?:-\d+)?|\(\d+(?:,\d+)*\))'

    # Case insensitive matching
    matches = re.finditer(pattern, schedule_str, re.IGNORECASE)

    for match in matches:
        match_str = match.group().strip()

        # Extract day part and slot part
        day_match = re.match(r'(Th|Sa|Su|M|T|W|F|PZT|PAZARTESİ?|SAL[IİÇ]?|ÇAR|ÇARŞAMBA|PER|PERŞEMBE|CUM[A]?|CMT|CUMARTESİ?|PAZ|PAZAR)', match_str, re.IGNORECASE)
        if not day_match:
            continue

        day_part = normalize_string(day_match.group())

        # Map Turkish to English
        day_code = TURKISH_DAY_MAPPING.get(day_part, day_part)

        # Validate day code
        if day_code not in DAY_CODES:
            continue

        # Extract slot part
        slot_part = match_str[len(day_match.group()):].strip()

        # Parse different slot formats
        if '(' in slot_part and ')' in slot_part:
            # Format: (1,3,5)
            slots_str = slot_part.strip('()')
            slots = [int(x.strip()) for x in slots_str.split(',') if x.strip().isdigit()]
        elif '-' in slot_part:
            # Format: 1-3
            parts = slot_part.split('-')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                start, end = int(parts[0]), int(parts[1])
                slots = list(range(start, end + 1))
            else:
                continue
        elif ',' in slot_part:
            # Format: 1,2,3
            slots = [int(x.strip()) for x in slot_part.split(',') if x.strip().isdigit()]
        else:
            # Format: 1
            if slot_part.isdigit():
                slots = [int(slot_part)]
            else:
                continue

        # Validate and add slots
        for slot in slots:
            if 1 <= slot <= 12:
                result.append((day_code, slot))

    return result


def get_schedule_conflicts(schedules: List[List[Tuple[str, int]]]) -> List[Tuple[str, int]]:
    """
    Find time slot conflicts between multiple schedules.

    Args:
        schedules: List of schedule lists, each containing (day_code, slot) tuples

    Returns:
        List of conflicting (day_code, slot) tuples
    """
    slot_count = {}

    for schedule in schedules:
        for day_code, slot in schedule:
            key = (day_code, slot)
            slot_count[key] = slot_count.get(key, 0) + 1

    # Return slots that appear in more than one schedule
    return [key for key, count in slot_count.items() if count > 1]


def count_weekly_hours(schedule: List[Tuple[str, int]]) -> int:
    """
    Count total unique weekly hours (slots) in a schedule.

    Args:
        schedule: List of (day_code, slot) tuples

    Returns:
        Number of unique time slots
    """
    return len(set(schedule))


def get_days_used(schedule: List[Tuple[str, int]]) -> List[str]:
    """
    Get list of days that have classes in the schedule.

    Args:
        schedule: List of (day_code, slot) tuples

    Returns:
        List of day codes that have classes
    """
    return list(set(day for day, slot in schedule))


def get_free_days(schedule: List[Tuple[str, int]], all_days: Optional[List[str]] = None) -> List[str]:
    """
    Get list of days that are completely free.

    Args:
        schedule: List of (day_code, slot) tuples
        all_days: List of all possible days (defaults to all 7 days)

    Returns:
        List of day codes that have no classes
    """
    if all_days is None:
        all_days = get_all_days()

    used_days = set(get_days_used(schedule))
    return [day for day in all_days if day not in used_days]


def count_daily_gaps(schedule: List[Tuple[str, int]], day: str) -> int:
    """
    Count gaps (free periods between classes) in a single day.

    Args:
        schedule: List of (day_code, slot) tuples
        day: Day code to analyze

    Returns:
        Number of gaps in the day
    """
    day_slots = sorted([slot for d, slot in schedule if d == day])

    if len(day_slots) <= 1:
        return 0

    gaps = 0
    for i in range(len(day_slots) - 1):
        if day_slots[i + 1] - day_slots[i] > 1:
            gaps += 1

    return gaps


def get_longest_consecutive_block(schedule: List[Tuple[str, int]], day: str) -> int:
    """
    Get the longest consecutive block of classes in a day.

    Args:
        schedule: List of (day_code, slot) tuples
        day: Day code to analyze

    Returns:
        Length of longest consecutive block
    """
    day_slots = sorted([slot for d, slot in schedule if d == day])

    if not day_slots:
        return 0

    max_block = 1
    current_block = 1

    for i in range(1, len(day_slots)):
        if day_slots[i] == day_slots[i - 1] + 1:
            current_block += 1
            max_block = max(max_block, current_block)
        else:
            current_block = 1

    return max_block


def validate_schedule(schedule: List[Tuple[str, int]]) -> Tuple[bool, List[str]]:
    """
    Validate a schedule for correctness.

    Args:
        schedule: List of (day_code, slot) tuples

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    for day_code, slot in schedule:
        if day_code not in DAY_CODES:
            errors.append(f"Invalid day code: {day_code}")

        if not (1 <= slot <= 12):
            errors.append(f"Invalid slot number: {slot}")

    # Check for duplicate slots
    seen = set()
    for item in schedule:
        if item in seen:
            errors.append(f"Duplicate slot: {item}")
        seen.add(item)

    return len(errors) == 0, errors


def schedule_to_grid_data(courses: List[Any], day_order: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Convert course schedules to grid data for display.

    Args:
        courses: List of course objects with schedule data
        day_order: Order of days for display (defaults to M-Su)

    Returns:
        Dictionary with grid data structure
    """
    if day_order is None:
        day_order = get_all_days()

    slots = get_all_slots()

    # Initialize grid
    grid = {}
    for day in day_order:
        grid[day] = {slot: [] for slot in slots}

    # Populate grid
    for course in courses:
        if hasattr(course, 'schedule') and course.schedule:
            for day_code, slot in course.schedule:
                if day_code in grid and slot in grid[day_code]:
                    course_info = getattr(course, 'code', 'Unknown')
                    grid[day_code][slot].append(course_info)

    return {
        'grid': grid,
        'days': day_order,
        'slots': slots,
        'day_names': [get_short_day_name(day) for day in day_order],
        'slot_times': [get_time_for_slot(slot) for slot in slots]
    }
