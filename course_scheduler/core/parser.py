"""
Robust Excel parser with Turkish/English header and day normalization.
Handles various Excel formats and Turkish course data.
"""

import pandas as pd
import re
import logging
from typing import List, Dict, Tuple, Optional

from .models import Course, CourseType

logger = logging.getLogger(__name__)

# Header normalization mappings (TR/EN synonyms) - Updated for actual Excel format
HEADER_MAPPINGS = {
    "code": ["Ders Kodu", "Code", "Kod", "Course Code", "Şube"],
    "name": ["Başlık", "Ders Adı", "Ders Adı (Türkçe)", "Lecture Name", "Ad", "Name", "Course Name"],
    "ects": ["AKTS Kredisi", "AKTS", "ECTS", "Credit", "Kredi", "Credits"],
    "local_credit": ["Yerel Kredi", "Local Credit", "Kredi"],
    "schedule": ["Ders Saati", "Ders Saati(leri)", "Saat", "Zaman", "Hour", "Schedule", "Time", "Gn"],  # Changed order - "Ders Saati" first
    "instructor_first": ["Eğitmen Adı", "Instructor First Name", "First Name"],
    "instructor_last": ["Eğitmen Soyadı", "Instructor Last Name", "Last Name"],
    "instructor": ["Öğretim Üyesi", "Öğretim Elemanı", "Eğitmen", "Instructor", "Lecture Instructor", "Teacher"],
    "faculty": ["Fakülte Adı", "Faklte Adı", "Fakülte", "Faculty"],  # Added "Faklte Adı" for typo
    "department": ["Bölüm Adı", "Bölüm", "Department", "Dept", "Program"],
    "campus": ["Kampüs", "Kamps", "Yerleşke", "Campus"],  # Added "Kamps" for typo
    "email": ["E-Posta", "Email", "E-mail"],
    "quota_remaining": ["Kalan /", "Kalan", "Remaining"],
    "quota_total": ["Toplam Kota", "Total Quota", "Quota", "Kota"],
    "live_section": ["Live Section", "Canlı Bölüm"]
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
    "T": "T", "Tuesday": "T",
    "W": "W", "Wednesday": "W",
    "Th": "Th", "Thursday": "Th",
    "F": "F", "Friday": "F",
    "Sa": "Sa", "Saturday": "Sa",
    "Su": "Su", "Sunday": "Su"
}


def normalize_header(df: pd.DataFrame) -> Dict[str, str]:
    """Normalize column headers to standard names."""
    column_map = {}
    df_columns = list(df.columns)

    for standard_name, synonyms in HEADER_MAPPINGS.items():
        for synonym in synonyms:
            for col in df_columns:
                if str(col).strip().lower() == synonym.lower():
                    column_map[standard_name] = col
                    break
            if standard_name in column_map:
                break

    logger.info(f"Header mapping: {column_map}")
    return column_map


def parse_credit_safely(credit_value) -> int:
    """Parse credit value safely, handling comma decimals and various formats."""
    try:
        if pd.isna(credit_value):
            return 0

        credit_str = str(credit_value).strip()
        credit_str = credit_str.replace(',', '.')

        match = re.search(r'\d+\.?\d*', credit_str)
        if match:
            return int(float(match.group()))

        return 0

    except (ValueError, TypeError):
        logger.warning(f"Could not parse credit value: {credit_value}")
        return 0


def normalize_day_name(day_str: str) -> str:
    """Normalize Turkish/English day names to standard short codes."""
    day_clean = day_str.strip()

    if day_clean in DAY_MAPPINGS:
        return DAY_MAPPINGS[day_clean]

    # Try partial matching for common variations
    for key, value in DAY_MAPPINGS.items():
        if key.lower() in day_clean.lower() or day_clean.lower() in key.lower():
            return value

    logger.warning(f"Unknown day format: '{day_str}' -> using as-is")
    return day_clean


def parse_schedule_robust(schedule_str: str) -> List[Tuple[str, int]]:
    """Parse schedule string with robust Turkish/English day handling."""
    if pd.isna(schedule_str) or not str(schedule_str).strip():
        return []

    schedule_clean = str(schedule_str).strip()
    parsed_schedule = []

    # Enhanced regex patterns for various formats
    patterns = [
        # Turkish format: "Pzt 1-2, Çrş 3-4"
        r'(\w+)\s*(\d+)(?:-(\d+))?',
        # Time ranges: "Pzt 09:30-11:20"
        r'(\w+)\s*(\d{1,2}):?(\d{0,2})-(\d{1,2}):?(\d{0,2})',
        # Simple format: "M1,T2"
        r'([A-Za-zÇçĞğıİÖöŞşÜü]+)(\d+)',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, schedule_clean)
        if matches:
            for match in matches:
                try:
                    if len(match) >= 2:
                        day_raw = match[0]
                        day_normalized = normalize_day_name(day_raw)

                        # Handle different hour formats
                        if len(match) == 2:  # Simple format
                            hour = int(match[1])
                            parsed_schedule.append((day_normalized, hour))
                        elif len(match) >= 3:  # Range format
                            start_hour = int(match[1])
                            end_hour = int(match[2]) if match[2] else start_hour

                            for hour in range(start_hour, end_hour + 1):
                                parsed_schedule.append((day_normalized, hour))

                except (ValueError, IndexError) as e:
                    logger.warning(f"Error parsing schedule component '{match}': {e}")
                    continue
            break

    if not parsed_schedule:
        logger.warning(f"Could not parse schedule: '{schedule_str}'")

    return parsed_schedule


def determine_course_type(code: str, name: str) -> CourseType:
    """Determine course type from code and name."""
    code_lower = code.lower()
    name_lower = name.lower()

    # Check for lab indicators
    if any(indicator in code_lower for indicator in ['lab', 'laboratuvar', 'uygulama']):
        return CourseType.LAB

    if any(indicator in name_lower for indicator in ['laboratuvar', 'lab', 'uygulama']):
        return CourseType.LAB

    # Check for PS (Problem Session) indicators
    if any(indicator in code_lower for indicator in ['ps', 'problem', 'çözüm']):
        return CourseType.PS

    if any(indicator in name_lower for indicator in ['problem', 'çözüm', 'alıştırma']):
        return CourseType.PS

    # Default to lecture
    return CourseType.LECTURE


def extract_main_code(full_code: str) -> str:
    """Extract main course code from full code (remove section indicators)."""
    if not full_code:
        return ""

    # Remove common section indicators
    main_code = re.sub(r'[.\-_]\d+$', '', full_code)  # Remove .01, -02, _03 etc.
    main_code = re.sub(r'[A-Z]{2,3}$', '', main_code)  # Remove PS, LAB suffixes

    return main_code.strip()


def process_excel_robust(file_path: str, sheet_name: str = "Sheet1") -> List[Course]:
    """
    Robust Excel processing with comprehensive error handling and validation.
    """
    try:
        logger.info(f"Loading Excel file: {file_path}, sheet: {sheet_name}")

        # Read Excel file with multiple encoding attempts
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
        except UnicodeDecodeError:
            logger.warning("UTF-8 failed, trying latin-1 encoding")
            df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl', encoding='latin-1')

        logger.info(f"Loaded {len(df)} rows from Excel")

        # Normalize headers
        header_map = normalize_header(df)

        # Validate required columns
        required_fields = ['code', 'name', 'ects', 'schedule']
        missing_fields = [field for field in required_fields if field not in header_map]

        if missing_fields:
            raise ValueError(f"Missing required columns: {missing_fields}")

        courses = []
        skipped_rows = 0

        for idx, row in df.iterrows():
            try:
                # Extract basic course info
                code = str(row[header_map['code']]).strip() if 'code' in header_map else f"COURSE_{idx}"
                name = str(row[header_map['name']]).strip() if 'name' in header_map else "Unknown Course"

                # Skip empty rows
                if not code or code in ['nan', 'NaN', ''] or not name or name in ['nan', 'NaN', '']:
                    skipped_rows += 1
                    continue

                # Parse ECTS credits
                ects = 0
                if 'ects' in header_map:
                    ects = parse_credit_safely(row[header_map['ects']])
                elif 'local_credit' in header_map:
                    ects = parse_credit_safely(row[header_map['local_credit']])

                # Parse schedule
                schedule = []
                if 'schedule' in header_map:
                    schedule_raw = row[header_map['schedule']]
                    schedule = parse_schedule_robust(schedule_raw)

                # Extract additional info with defaults
                teacher = "Unknown"
                if 'instructor' in header_map:
                    teacher = str(row[header_map['instructor']]).strip()
                elif 'instructor_first' in header_map and 'instructor_last' in header_map:
                    first = str(row[header_map['instructor_first']]).strip()
                    last = str(row[header_map['instructor_last']]).strip()
                    teacher = f"{first} {last}".strip()

                faculty = str(row[header_map['faculty']]).strip() if 'faculty' in header_map else "Unknown Faculty"
                department = str(row[header_map['department']]).strip() if 'department' in header_map else "Unknown Department"
                campus = str(row[header_map['campus']]).strip() if 'campus' in header_map else "Main Campus"

                # Clean up extracted data
                if teacher in ['nan', 'NaN', '']:
                    teacher = "Unknown"
                if faculty in ['nan', 'NaN', '']:
                    faculty = "Unknown Faculty"
                if department in ['nan', 'NaN', '']:
                    department = "Unknown Department"
                if campus in ['nan', 'NaN', '']:
                    campus = "Main Campus"

                # Determine course type and main code
                course_type = determine_course_type(code, name)
                main_code = extract_main_code(code)

                # Create course object
                course = Course(
                    code=code,
                    main_code=main_code,
                    name=name,
                    ects=ects,
                    course_type=course_type,
                    schedule=schedule,
                    teacher=teacher,
                    faculty=faculty,
                    department=department,
                    campus=campus
                )

                courses.append(course)

            except Exception as e:
                logger.warning(f"Error processing row {idx}: {e}")
                skipped_rows += 1
                continue

        logger.info(f"Successfully processed {len(courses)} courses, skipped {skipped_rows} rows")
        return courses

    except Exception as e:
        logger.error(f"Critical error processing Excel file: {e}")
        raise


def validate_course_data(courses: List[Course]) -> List[str]:
    """Validate parsed course data and return list of issues."""
    issues = []

    if not courses:
        issues.append("No courses found in data")
        return issues

    # Check for duplicate codes
    codes = [c.code for c in courses]
    duplicates = set([code for code in codes if codes.count(code) > 1])
    if duplicates:
        issues.append(f"Duplicate course codes found: {list(duplicates)[:5]}")

    # Check for courses without schedules
    no_schedule_count = sum(1 for c in courses if not c.schedule)
    if no_schedule_count > 0:
        issues.append(f"{no_schedule_count} courses have no schedule information")

    # Check for courses with zero ECTS
    zero_ects_count = sum(1 for c in courses if c.ects == 0)
    if zero_ects_count > 0:
        issues.append(f"{zero_ects_count} courses have zero ECTS credits")

    # Check for unusual ECTS values
    high_ects_courses = [c.code for c in courses if c.ects > 10]
    if high_ects_courses:
        issues.append(f"Courses with unusually high ECTS (>10): {high_ects_courses[:5]}")

    # Check for courses with no teacher information
    no_teacher_count = sum(1 for c in courses if c.teacher in ["Unknown", "Default", ""])
    if no_teacher_count > 0:
        issues.append(f"{no_teacher_count} courses have no teacher information")

    # Faculty/Department distribution check
    faculties = set(c.faculty for c in courses)
    if len(faculties) == 1 and "Unknown Faculty" in faculties:
        issues.append("All courses have unknown faculty information")

    departments = set(c.department for c in courses)
    if len(departments) == 1 and "Unknown Department" in departments:
        issues.append("All courses have unknown department information")

    return issues


def export_course_data_summary(courses: List[Course]) -> Dict:
    """Generate a summary of parsed course data for debugging."""
    if not courses:
        return {"error": "No courses to analyze"}

    summary = {
        "total_courses": len(courses),
        "course_types": {},
        "faculties": {},
        "departments": {},
        "ects_distribution": {},
        "schedule_coverage": 0,
        "sample_courses": []
    }

    # Course type distribution
    for course in courses:
        type_name = course.course_type.value
        summary["course_types"][type_name] = summary["course_types"].get(type_name, 0) + 1

    # Faculty distribution
    for course in courses:
        faculty = course.faculty
        summary["faculties"][faculty] = summary["faculties"].get(faculty, 0) + 1

    # Department distribution
    for course in courses:
        dept = course.department
        summary["departments"][dept] = summary["departments"].get(dept, 0) + 1

    # ECTS distribution
    for course in courses:
        ects = course.ects
        summary["ects_distribution"][str(ects)] = summary["ects_distribution"].get(str(ects), 0) + 1

    # Schedule coverage
    courses_with_schedule = sum(1 for c in courses if c.schedule)
    summary["schedule_coverage"] = round((courses_with_schedule / len(courses)) * 100, 2)

    # Sample courses for debugging
    summary["sample_courses"] = [
        {
            "code": c.code,
            "name": c.name[:30] + "..." if len(c.name) > 30 else c.name,
            "ects": c.ects,
            "type": c.course_type.value,
            "schedule_count": len(c.schedule),
            "faculty": c.faculty,
            "department": c.department
        }
        for c in courses[:5]
    ]

    return summary

