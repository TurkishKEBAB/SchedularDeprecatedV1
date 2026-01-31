"""
Diagnostic tool for analyzing schedule parsing.

This script generates a report on how schedule strings are parsed,
helping identify and fix parsing issues.
"""
import argparse
import csv
import logging
import os
import sys
from typing import List, Dict, Any

# Add the parent directory to path so we can import from the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from course_scheduler.app.data.excel_loader import process_excel
from course_scheduler.app.utils.schedule_utils import parse_schedule


def generate_parsing_report(courses: List[Any]) -> List[Dict[str, Any]]:
    """
    Generate a detailed report on how schedule strings are parsed.
    
    Args:
        courses: List of course objects
        
    Returns:
        List of dictionaries containing parsing report data
    """
    report = []
    
    for course in courses:
        raw_schedule = getattr(course, 'raw_schedule', 'N/A')
        parsed_schedule = getattr(course, 'schedule', [])
        
        report.append({
            'code': course.code,
            'name': course.name,
            'raw_schedule': raw_schedule,
            'parsed_schedule': str(parsed_schedule),
            'slot_count': len(parsed_schedule),
            'course_type': course.course_type,
            'teacher': course.teacher
        })
    
    return report


def setup_logging():
    """Configure logging for the diagnostic tool."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('parsing_diagnostic.log')
        ]
    )


def create_parsing_report(excel_file: str, sheet_name: str, output_file: str):
    """
    Create a CSV report detailing how each course's schedule was parsed.

    Args:
        excel_file: Path to the Excel file with course data
        sheet_name: Name of the Excel sheet to process
        output_file: Path to save the CSV report
    """
    logger = logging.getLogger("parsing_report")
    logger.info(f"Processing Excel file: {excel_file}, sheet: {sheet_name}")

    try:
        # Load courses from Excel
        courses = process_excel(excel_file, sheet_name)
        logger.info(f"Successfully loaded {len(courses)} courses")

        # Generate parsing report
        report = generate_parsing_report(courses)
        logger.info(f"Generated parsing report for {len(report)} courses")

        # Count courses with empty schedules
        empty_schedules = [item for item in report if item['slot_count'] == 0]
        logger.info(f"Found {len(empty_schedules)} courses with empty schedules")

        # Write report to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if not report:
                logger.error("No data to write to report")
                return

            fieldnames = report[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for item in report:
                writer.writerow(item)

        logger.info(f"Report written to {output_file}")

        # Print summary to console
        print(f"\nParsing Report Summary:")
        print(f"Total courses: {len(courses)}")
        print(f"Courses with empty schedules: {len(empty_schedules)}")

        # Print details of courses with empty schedules
        if empty_schedules:
            print("\nCourses with empty schedules:")
            for item in empty_schedules:
                print(f"  - {item['code']}: Raw schedule = '{item['raw_schedule']}'")

    except Exception as e:
        logger.error(f"Error creating parsing report: {e}", exc_info=True)
        raise


def main():
    """Main entry point for the parsing report tool."""
    parser = argparse.ArgumentParser(description="Generate a report on schedule parsing")
    parser.add_argument("excel_file", help="Path to Excel file with course data")
    parser.add_argument("--sheet", "-s", default="Sheet1", help="Excel sheet name (default: Sheet1)")
    parser.add_argument("--output", "-o", default="parsing_report.csv", help="Output CSV file (default: parsing_report.csv)")

    args = parser.parse_args()
    setup_logging()

    create_parsing_report(args.excel_file, args.sheet, args.output)


if __name__ == "__main__":
    main()
