"""
Robust Excel parser with Turkish/English header and day normalization.
Handles various Excel formats and Turkish course data.
"""

import pandas as pd
import re
import logging
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# Header normalization mappings (TR/EN synonyms)
HEADER_MAPPINGS = {
    "code": ["Ders Kodu", "Code", "Kod", "Course Code"],
    "name": ["Ders Adı", "Ders Adı (Türkçe)", "Başlık", "Lecture Name", "Ad", "Name", "Course Name"],
    "ects": ["AKTS", "AKTS Kredisi", "ECTS", "Credit", "Kredi", "Credits"],
    "schedule": ["Ders Saati(leri)", "Saat", "Zaman", "Hour", "Schedule", "Time"],
    "instructor": ["Öğretim Üyesi", "Öğretim Elemanı", "Eğitmen", "Instructor", "Lecture Instructor", "Teacher"],
    "faculty": ["Fakülte", "Faculty"],
    "department": ["Bölüm", "Department", "Dept"],
    "campus": ["Kampüs", "Yerleşke", "Campus"]
}

# Turkish day name normalization (TR → short EN codes)
DAY_MAPPINGS = {
    # Turkish days
    "Pzt": "M", "Pazartesi": "M",
    "Sal": "T", "Salı": "T",
    "Çrş": "W", "Çarşamba": "W",
    "Per": "Th", "Perşembe": "Th",
    "Cum": "F", "Cuma": "F",
    "Cmt": "Sa", "Cumartesi": "Sa",
    "Paz": "Su", "Pazar": "Su",

    # English days (already normalized)
    "M": "M", "Monday": "M",
    "T": "T", "Tuesday": "T",  # Note: T maps to Tuesday by default
    "W": "W", "Wednesday": "W",
    "Th": "Th", "Thursday": "Th",  # Explicit Thursday
    "F": "F", "Friday": "F",
    "Sa": "Sa", "Saturday": "Sa",
    "Su": "Su", "Sunday": "Su"
}


def normalize_header(df: pd.DataFrame) -> Dict[str, str]:
    """
    Normalize column headers to standard names.

    Args:
        df: Input DataFrame

    Returns:
        Dict mapping standard names to actual column names
    """
    column_map = {}
    df_columns = list(df.columns)

    for standard_name, synonyms in HEADER_MAPPINGS.items():
        for synonym in synonyms:
            # Case-insensitive search
            for col in df_columns:
                if str(col).strip().lower() == synonym.lower():
                    column_map[standard_name] = col
                    break
            if standard_name in column_map:
                break

    logger.info(f"Header mapping: {column_map}")
    return column_map


def parse_credit_safely(credit_value) -> int:
    """
    Parse credit value safely, handling comma decimals and various formats.

    Args:
        credit_value: Raw credit value from Excel

    Returns:
        Integer credit value
    """
    try:
        if pd.isna(credit_value):
            return 0

        # Convert to string and clean
        credit_str = str(credit_value).strip()

        # Handle comma as decimal separator
        credit_str = credit_str.replace(',', '.')

        # Extract first number found
        match = re.search(r'\d+\.?\d*', credit_str)
        if match:
            return int(float(match.group()))

        return 0

    except (ValueError, TypeError):
        logger.warning(f"Could not parse credit value: {credit_value}")
        return 0


def normalize_day_name(day_str: str) -> str:
    """
    Normalize Turkish/English day names to standard short codes.

    Args:
        day_str: Day name (e.g., "Pzt", "Pazartesi", "Monday")

    Returns:
        Normalized day code (e.g., "M", "Th")
    """
    day_clean = day_str.strip()

    # Direct lookup in mappings
    if day_clean in DAY_MAPPINGS:
        return DAY_MAPPINGS[day_clean]

    # Case-insensitive lookup
    for key, value in DAY_MAPPINGS.items():
        if day_clean.lower() == key.lower():
            return value

    # Handle "Tuesday"/"Thursday" ambiguity explicitly
    if day_clean.lower() in ["tuesday", "tue"]:
        return "T"
    elif day_clean.lower() in ["thursday", "thu"]:
        return "Th"

    logger.warning(f"Unknown day name: {day_str}")
    return day_str  # Return as-is if not recognized


def parse_schedule_robust(schedule_str) -> List[Tuple[str, int]]:
    """
    Parse schedule string with robust Turkish/English day handling.

    Args:
        schedule_str: Schedule string (e.g., "Pzt3,Per7" or "M3,Th7")

    Returns:
        List of (day, hour) tuples
    """
    if not schedule_str or pd.isna(schedule_str):
        return []

    schedule_clean = str(schedule_str).strip()
    if schedule_clean.lower() == "nan":
        return []

    schedule = []

    # Split by common separators
    blocks = re.split(r'[,;\s]+', schedule_clean)

    for block in blocks:
        if not block.strip():
            continue

        # Extract day and hour patterns
        # Pattern 1: Turkish days like "Pzt3", "Per7"
        match = re.match(r'([A-Za-zçÇğĞıİöÖşŞüÜ]+)(\d+)', block.strip())
        if match:
            day_part, hour_part = match.groups()
            normalized_day = normalize_day_name(day_part)
            try:
                hour = int(hour_part)
                schedule.append((normalized_day, hour))
            except ValueError:
                logger.warning(f"Invalid hour in schedule: {block}")
            continue

        # Pattern 2: Separate day and hour (e.g., "Pzt 3")
        parts = block.strip().split()
        if len(parts) >= 2:
            day_part = parts[0]
            hour_part = parts[1]
            normalized_day = normalize_day_name(day_part)
            try:
                hour = int(hour_part)
                schedule.append((normalized_day, hour))
            except ValueError:
                logger.warning(f"Invalid hour in schedule: {block}")
            continue

        # Pattern 3: Day only (assume hour 1)
        if len(parts) == 1 and parts[0].isalpha():
            normalized_day = normalize_day_name(parts[0])
            schedule.append((normalized_day, 1))

    return schedule


def foundation_main_code(code: str) -> str:
    """Extract main course code from full code."""
    code = str(code).strip()
    if "-PS" in code:
        return code.split("-PS")[0]
    elif "-L" in code:
        return code.split("-L")[0]
    elif "." in code:
        return code.split(".")[0]
    else:
        return code


def foundation_tour(code: str) -> str:
    """Determine course type from code."""
    if "-PS" in code:
        return "ps"
    elif "-L" in code:
        return "lab"
    else:
        return "lecture"


def process_excel_robust(file_path: str, sheet_name: str = "Sheet2") -> List[Dict]:
    """
    Process Excel file with robust Turkish/English parsing.

    Args:
        file_path: Path to Excel file
        sheet_name: Sheet name to read

    Returns:
        List of course dictionaries
    """
    try:
        # Try reading with header detection
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # Normalize headers
        header_map = normalize_header(df)

        # Check if we found required columns
        if "code" not in header_map or "name" not in header_map:
            logger.warning("Required columns not found, trying fallback parsing")
            # Fallback to positional parsing
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            if df.shape[1] >= 4:
                df.columns = ["Code", "Name", "ECTS", "Schedule"] + [f"Extra{i}" for i in range(df.shape[1]-4)]
                header_map = {
                    "code": "Code",
                    "name": "Name",
                    "ects": "ECTS",
                    "schedule": "Schedule"
                }
            else:
                raise ValueError("Excel file format not recognized")

        courses = []
        duplicates = 0

        for idx, row in df.iterrows():
            try:
                # Extract basic course info
                code = str(row[header_map["code"]]).strip()
                if not code or code.lower() == "nan":
                    continue

                name = str(row[header_map["name"]]).strip()

                # Parse credit safely
                credit_raw = row[header_map.get("ects", header_map.get("credit", ""))] if header_map.get("ects") else 0
                credit = parse_credit_safely(credit_raw)

                # Parse schedule
                schedule_raw = row[header_map.get("schedule", "")] if header_map.get("schedule") else ""
                schedule_list = parse_schedule_robust(schedule_raw)

                # Extract course structure info
                main_code = foundation_main_code(code)
                course_type = foundation_tour(code)
                has_lecture = course_type == "lecture"

                # Extract optional fields with defaults
                teacher = str(row[header_map.get("instructor", "")]).strip() if header_map.get("instructor") and not pd.isna(row[header_map.get("instructor", "")]) else "Default"
                faculty = str(row[header_map.get("faculty", "")]).strip() if header_map.get("faculty") and not pd.isna(row[header_map.get("faculty", "")]) else "Unknown Faculty"
                department = str(row[header_map.get("department", "")]).strip() if header_map.get("department") and not pd.isna(row[header_map.get("department", "")]) else "Unknown Department"
                campus = str(row[header_map.get("campus", "")]).strip() if header_map.get("campus") and not pd.isna(row[header_map.get("campus", "")]) else "Main Campus"

                # Check for duplicates
                existing_codes = [c["code"] for c in courses]
                if code in existing_codes:
                    duplicates += 1
                    logger.warning(f"Duplicate course code: {code} (keeping last occurrence)")
                    # Remove previous occurrence
                    courses = [c for c in courses if c["code"] != code]

                course = {
                    "code": code,
                    "main_code": main_code,
                    "name": name,
                    "ECTS": credit,
                    "type": course_type,
                    "schedule": schedule_list,
                    "hasLecture": has_lecture,
                    "teacher": teacher,
                    "faculty": faculty,
                    "department": department,
                    "campus": campus
                }

                courses.append(course)

            except Exception as e:
                logger.error(f"Error processing row {idx}: {e}")
                continue

        if duplicates > 0:
            logger.info(f"Found {duplicates} duplicate course codes (kept last occurrence)")

        logger.info(f"Successfully parsed {len(courses)} courses from {file_path}")
        return courses

    except Exception as e:
        logger.error(f"Failed to process Excel file {file_path}: {e}")
        raise


def validate_course_data(courses: List[Dict]) -> List[str]:
    """
    Validate parsed course data and return list of issues found.

    Args:
        courses: List of course dictionaries

    Returns:
        List of validation error messages
    """
    issues = []

    if not courses:
        issues.append("No courses found in data")
        return issues

    # Check for required fields
    required_fields = ["code", "main_code", "name", "ECTS", "type"]
    for course in courses:
        for field in required_fields:
            if field not in course or not course[field]:
                issues.append(f"Course {course.get('code', 'UNKNOWN')} missing required field: {field}")

    # Check for invalid ECTS values
    invalid_ects = [c for c in courses if c.get("ECTS", 0) <= 0]
    if invalid_ects:
        issues.append(f"{len(invalid_ects)} courses have invalid ECTS values")

    # Check for courses without schedules
    no_schedule = [c for c in courses if not c.get("schedule")]
    if no_schedule:
        issues.append(f"{len(no_schedule)} courses have no schedule information")

    # Check for duplicate codes
    codes = [c.get("code") for c in courses]
    duplicates = len(codes) - len(set(codes))
    if duplicates > 0:
        issues.append(f"{duplicates} duplicate course codes found")

    return issues
