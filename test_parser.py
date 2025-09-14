#!/usr/bin/env python3
"""Test script for parser functionality"""

from course_scheduler.core.parser import process_excel_robust
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)

def test_parser():
    try:
        print("Testing parser with updated header mapping...")
        courses = process_excel_robust('lisans-haftalik-ders-programi(1).xlsx')
        print(f'Total courses loaded: {len(courses)}')

        if courses:
            print('\nFirst 5 courses with detailed info:')
            for i, course in enumerate(courses[:5]):
                print(f'{i+1}. Code: {course.code}')
                print(f'   Name: {course.name}')
                print(f'   ECTS: {course.ects}')
                print(f'   Schedule: {course.schedule}')
                print(f'   Teacher: {course.teacher}')
                print(f'   Faculty: {course.faculty}')
                print(f'   Campus: {course.campus}')
                print()

            # Count courses with schedules
            courses_with_schedule = [c for c in courses if c.schedule]
            print(f'Courses with schedule info: {len(courses_with_schedule)}/{len(courses)}')

            if courses_with_schedule:
                print('\nSample courses with schedules:')
                for course in courses_with_schedule[:3]:
                    print(f'{course.code}: {course.name} - {course.schedule}')
        else:
            print('No courses loaded!')

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parser()
