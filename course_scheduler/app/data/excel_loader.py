"""
Excel data loading and processing for the course scheduler application.

This module provides functions for loading course data from Excel files,
parsing schedule information, and converting between different data formats.
"""
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from ..data.models import Course
from ..utils.schedule_utils import parse_schedule
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Default values for missing columns
DEFAULT_FACULTY = "Unknown Faculty"
DEFAULT_DEPARTMENT = "Unknown Department"
DEFAULT_CAMPUS = "Main"


def process_excel(file_path: str, sheet_name: str) -> List[Course]:
    """
    Load courses from an Excel file and convert to Course objects.

    Now supports additional columns: Faculty, Department, and Campus.
    If these columns are not present, default values will be used.

    Args:
        file_path: Path to the Excel file
        sheet_name: Name of the sheet to load

    Returns:
        List of Course objects

    Raises:
        ValueError: If the file cannot be processed or required columns are missing
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # Normalize column names (handle both English and Turkish)
        df = normalize_columns(df)

        # Fall back to legacy format handling if the expected columns aren't found
        if "Code" not in df.columns:
            raise ValueError("Expected column 'Code' or 'Ders Kodu' not found.")
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")

        # Try fallback approach with header=None
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            if df.shape[1] >= 5:
                df.columns = ["Code", "Lecture Name", "Credit", "Hour", "Lecture Instructor"] + \
                             [f"Extra{i}" for i in range(df.shape[1]-5)]
            else:
                df.columns = ["Code", "Lecture Name", "Credit", "Hour"]

            # Add missing Faculty, Department, Campus columns with defaults
            df = add_missing_columns(df)
        except Exception as e2:
            logger.error(f"Fallback Excel reading failed: {e2}")
            raise ValueError(f"Could not process Excel file: {e}") from e

    teacher_col = "Lecture Instructor" if "Lecture Instructor" in df.columns else None
    courses = []

    for idx, row in df.iterrows():
        try:
            course_dict = _process_row(row, teacher_col)
            course = Course.from_dict(course_dict)
            courses.append(course)
        except Exception as e:
            logger.warning(f"Error processing row {idx}: {e}")
            continue

    return courses


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names, handling both English and Turkish names.
    Also ensures that Faculty, Department, and Campus columns are present.

    Args:
        df: DataFrame with original column names

    Returns:
        DataFrame with normalized column names
    """
    # Map Turkish column names to English
    column_mapping = {
        # Core columns
        "Ders Kodu": "Code",
        "Başlık": "Lecture Name",
        "AKTS Kredisi": "Credit",
        "Ders Saati(leri)": "Hour",
        "Ders Saati": "Hour", # Alternative name

        # New columns with possible Turkish variants
        "Fakülte Adı": "Faculty",
        "Fakülte": "Faculty",
        "Kampüs": "Campus",
        "Bölüm": "Department",

        # Additional columns from the real data format
        "Yerel Kredi": "Local Credit",
        "Kalan /": "Remaining",
        "Toplam Kota": "Total Quota",
        "Live Section": "Live Section"
    }

    # Rename columns according to mapping
    df = df.rename(columns=column_mapping)

    # Handle instructor information
    if "Eğitmen Adı" in df.columns and "Eğitmen Soyadı" in df.columns:
        df["Lecture Instructor"] = df["Eğitmen Adı"] + " " + df["Eğitmen Soyadı"]

    # Normalize the Hour column by replacing newlines and standardizing separators
    if "Hour" in df.columns:
        df["Hour"] = df["Hour"].astype(str).replace(r'\n', ', ', regex=True)
        df["Hour"] = df["Hour"].replace(r'[;/]', ', ', regex=True)

    # Add missing Faculty, Department, Campus columns with defaults
    return add_missing_columns(df)


def add_missing_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Faculty, Department, and Campus columns with defaults if they don't exist.

    Args:
        df: DataFrame to check and modify

    Returns:
        DataFrame with all required columns
    """
    # Add Faculty column if missing
    if "Faculty" not in df.columns:
        df["Faculty"] = DEFAULT_FACULTY

    # Add Department column if missing
    if "Department" not in df.columns:
        df["Department"] = DEFAULT_DEPARTMENT

    # Add Campus column if missing
    if "Campus" not in df.columns:
        df["Campus"] = DEFAULT_CAMPUS

    return df


def _process_row(row: pd.Series, teacher_col: Optional[str]) -> Dict[str, Any]:
    """
    Process a single row from the Excel dataframe.

    Args:
        row: Pandas Series representing a row from the dataframe
        teacher_col: Name of the column containing teacher information

    Returns:
        Dictionary with course information
    """
    code = str(row["Code"]).strip()
    course_name = str(row["Lecture Name"]).strip()

    # Handle credit as either integer or float
    try:
        credit = int(row["Credit"])
    except ValueError:
        try:
            credit = int(float(row["Credit"]))
        except ValueError:
            credit = 0
            logger.warning(f"Could not convert credit value '{row['Credit']}' to number for course {code}. Using default 0.")

    # Handle schedule parsing - improved fix for pandas Series issue
    schedule_str = ""
    try:
        # Safe way to check if Hour column exists and has value
        if "Hour" in row.index:
            hour_value = row["Hour"]

            # Check if it's a pandas Series (multiple Hour columns)
            if isinstance(hour_value, pd.Series):
                # Get first non-null value from the series
                valid_values = hour_value.dropna()
                if not valid_values.empty:
                    schedule_str = str(valid_values.iloc[0]).strip()
                else:
                    schedule_str = ""
            else:
                # Single value - check if it's not null
                if pd.notna(hour_value):
                    schedule_str = str(hour_value).strip()
                else:
                    schedule_str = ""
        else:
            schedule_str = ""

    except Exception as e:
        logger.warning(f"Error extracting schedule for course {code}: {e}")
        schedule_str = ""

    # Clean up schedule string
    if schedule_str and schedule_str.lower() not in ["nan", "none", ""]:
        # Parse schedule with improved parser
        schedule_list = parse_schedule(schedule_str)
    else:
        schedule_list = []

    main_code = get_main_code(code)
    course_type = get_course_type(code)
    has_lecture = True if course_type == "lecture" else False

    teacher = str(row[teacher_col]).strip() if teacher_col and teacher_col in row.index and pd.notna(row[teacher_col]) else "Default"

    # Get additional fields with defaults if missing
    try:
        faculty = str(row["Faculty"]) if "Faculty" in row.index and pd.notna(row["Faculty"]) else DEFAULT_FACULTY
        department = str(row["Department"]) if "Department" in row.index and pd.notna(row["Department"]) else DEFAULT_DEPARTMENT
        campus = str(row["Campus"]) if "Campus" in row.index and pd.notna(row["Campus"]) else DEFAULT_CAMPUS
    except Exception as e:
        logger.warning(f"Error extracting faculty/department/campus for course {code}: {e}")
        faculty = DEFAULT_FACULTY
        department = DEFAULT_DEPARTMENT
        campus = DEFAULT_CAMPUS

    # Log warning if schedule couldn't be parsed but we had a valid string
    if not schedule_list and schedule_str and schedule_str.lower() not in ["nan", "none", ""]:
        logger.warning(f"Could not parse schedule '{schedule_str}' for course {code}")

    return {
        "code": code,
        "main_code": main_code,
        "course_name": course_name,
        "credit": credit,
        "schedule": schedule_list,
        "teacher": teacher,
        "course_type": course_type,
        "has_lecture": has_lecture,
        "faculty": faculty,
        "department": department,
        "campus": campus,
        "raw_schedule": schedule_str  # Keep raw for debugging
    }


def get_main_code(code: str) -> str:
    """
    Extract the main course code from a full course code.

    Args:
        code: Full course code (e.g., "CS101-PS1")

    Returns:
        Main course code (e.g., "CS101")
    """
    code = str(code).strip()
    if "-PS" in code:
        return code.split("-PS")[0]
    elif "-L" in code:
        return code.split("-L")[0]
    elif "." in code:
        return code.split(".")[0]
    else:
        return code


def get_course_type(code: str) -> str:
    """
    Determine the course type from the course code.

    Args:
        code: Course code

    Returns:
        Course type: "ps", "lab", or "lecture"
    """
    if "-PS" in code:
        return "ps"
    elif "-L" in code:
        return "lab"
    else:
        return "lecture"


def parse_schedule(schedule_str: str) -> List[Tuple[str, int]]:
    """
    Parse a schedule string into a list of time slots.

    Args:
        schedule_str: String representing a schedule (e.g., "M1,W2,Th3")

    Returns:
        List of tuples (day, period)
    """
    s = str(schedule_str).strip()
    if not s or s.lower() == "nan":
        return []

    blocks = s.split(",")
    schedule = []

    for block in blocks:
        b = block.strip()
        i = 0
        while i < len(b):
            if b[i] == 'T' and i + 1 < len(b) and b[i + 1] == 'h':
                day = "Th"
                i += 2
            elif b[i] in ['M', 'W', 'F', 'T']:
                day = b[i]
                i += 1
            else:
                i += 1
                continue

            hour_str = ""
            while i < len(b) and b[i].isdigit():
                hour_str += b[i]
                i += 1

            if hour_str:
                schedule.append((day, int(hour_str)))

    return schedule
