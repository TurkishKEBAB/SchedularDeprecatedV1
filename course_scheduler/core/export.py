"""
Export functionality for schedules - JPEG, PDF generation and reports.
"""

import os
import math
import csv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
from typing import List, Dict, Tuple
import logging
import pandas as pd

from .models import Schedule, Course

logger = logging.getLogger(__name__)

# Time period mappings
PERIOD_TIMES = {
    1: "08:30-09:20", 2: "09:30-10:20", 3: "10:30-11:20", 4: "11:30-12:20",
    5: "12:30-13:20", 6: "13:30-14:20", 7: "14:30-15:20", 8: "15:30-16:20",
    9: "16:30-17:20", 10: "17:30-18:20", 11: "18:30-19:20", 12: "19:30-20:20"
}

DAYS = ["M", "T", "W", "Th", "F", "Sa", "Su"]
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class ScheduleExporter:
    """Handles schedule export functionality."""

    @staticmethod
    def get_schedule_grid_data(schedule: Schedule) -> List[List[str]]:
        """Convert schedule to grid format for display."""
        grid = []
        header = ["Time"] + DAYS
        grid.append(header)

        for period in range(1, 13):
            row = [PERIOD_TIMES.get(period, str(period))]
            row.extend([""] * len(DAYS))
            grid.append(row)

        for course in schedule.courses:
            display_str = course.code
            for (day, period) in course.schedule:
                if day in DAYS and 1 <= period <= 12:
                    row_index = period
                    col_index = header.index(day)
                    if grid[row_index][col_index]:
                        grid[row_index][col_index] += "\n" + display_str
                    else:
                        grid[row_index][col_index] = display_str

        return grid

    @staticmethod
    def save_schedule_as_jpeg(schedule: Schedule, filename: str = "schedule.jpg",
                             note_text: str = "") -> None:
        """Save schedule as JPEG image."""
        try:
            grid_data = ScheduleExporter.get_schedule_grid_data(schedule)
            col_labels = grid_data[0]
            data_rows = grid_data[1:]

            fig, ax = plt.subplots(figsize=(12, 8))
            ax.axis("tight")
            ax.axis("off")

            table = ax.table(cellText=data_rows, colLabels=col_labels,
                           loc="center", cellLoc="center")
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 1.5)

            plt.title("Course Schedule", fontsize=14)

            if note_text:
                plt.figtext(0.5, 0.01, note_text, wrap=True,
                          horizontalalignment="center", fontsize=10)

            plt.savefig(filename, dpi=300, bbox_inches="tight")
            plt.close()

            logger.info(f"Schedule JPEG saved as: {filename}")

        except Exception as e:
            logger.error(f"Failed to save schedule as JPEG: {e}")
            raise

    @staticmethod
    def create_selection_matrix(schedules: List[Schedule], all_courses: List[Course]) -> None:
        """Create selection matrix PDF showing course selections."""
        try:
            pdf_filename = "final_selection_matrices.pdf"

            # Remove existing file
            if os.path.exists(pdf_filename):
                os.remove(pdf_filename)

            with PdfPages(pdf_filename) as pdf:
                # Create course lookup
                course_dict = {course.code: course for course in all_courses}

                # Get unique main codes across all schedules
                all_main_codes = set()
                for schedule in schedules:
                    for course in schedule.courses:
                        all_main_codes.add(course.main_code)

                all_main_codes = sorted(list(all_main_codes))

                if not all_main_codes:
                    logger.warning("No courses found for selection matrix")
                    return

                # Create matrix data
                matrix_data = []
                for main_code in all_main_codes:
                    row = [main_code]
                    for i, schedule in enumerate(schedules):
                        # Find courses in this schedule with this main code
                        matching_courses = [c for c in schedule.courses if c.main_code == main_code]
                        if matching_courses:
                            # Show course codes separated by commas
                            codes = ", ".join([c.code for c in matching_courses])
                            row.append(codes)
                        else:
                            row.append("")
                    matrix_data.append(row)

                # Create headers
                headers = ["Course"] + [f"Schedule {i+1}" for i in range(len(schedules))]

                # Calculate optimal page layout
                max_cols_per_page = 6  # Including course name column
                pages_needed = math.ceil((len(headers) - 1) / (max_cols_per_page - 1))

                for page in range(pages_needed):
                    fig, ax = plt.subplots(figsize=(11, 8.5))  # Letter size
                    ax.axis("tight")
                    ax.axis("off")

                    # Calculate column range for this page
                    start_col = 1 + page * (max_cols_per_page - 1)
                    end_col = min(len(headers), start_col + max_cols_per_page - 1)

                    # Prepare data for this page
                    page_headers = [headers[0]] + headers[start_col:end_col]
                    page_data = []

                    for row in matrix_data:
                        page_row = [row[0]] + row[start_col:end_col]
                        page_data.append(page_row)

                    # Create table
                    table = ax.table(cellText=page_data, colLabels=page_headers,
                                   loc="center", cellLoc="center")
                    table.auto_set_font_size(False)
                    table.set_fontsize(8)
                    table.scale(1, 1.2)

                    # Style the table
                    for i in range(len(page_headers)):
                        table[(0, i)].set_facecolor('#4CAF50')
                        table[(0, i)].set_text_props(weight='bold', color='white')

                    plt.title(f"Course Selection Matrix - Page {page + 1}/{pages_needed}",
                             fontsize=14, fontweight='bold', pad=20)

                    # Add summary information
                    summary_text = f"Total Schedules: {len(schedules)}, Total Courses: {len(all_main_codes)}"
                    plt.figtext(0.5, 0.02, summary_text, ha='center', fontsize=10)

                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close()

            logger.info(f"Selection matrix saved as: {pdf_filename}")

        except Exception as e:
            logger.error(f"Failed to create selection matrix: {e}")
            raise

    @staticmethod
    def export_schedule_to_csv(schedule: Schedule, filename: str = "schedule.csv") -> None:
        """Export schedule to CSV format."""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Header
                writer.writerow(['Course Code', 'Course Name', 'ECTS', 'Type', 'Teacher',
                               'Faculty', 'Department', 'Schedule'])

                # Course data
                for course in schedule.courses:
                    schedule_str = ', '.join([f"{day}{hour}" for day, hour in course.schedule])
                    writer.writerow([
                        course.code,
                        course.name,
                        course.ects,
                        course.course_type.value,
                        course.teacher,
                        course.faculty,
                        course.department,
                        schedule_str
                    ])

                # Summary row
                writer.writerow([])
                writer.writerow(['SUMMARY'])
                writer.writerow(['Total ECTS', schedule.total_ects])
                writer.writerow(['Total Courses', len(schedule.courses)])
                writer.writerow(['Conflicts', schedule.conflict_cost])

            logger.info(f"Schedule CSV exported to: {filename}")

        except Exception as e:
            logger.error(f"Failed to export schedule to CSV: {e}")
            raise

    @staticmethod
    def export_all_schedules(schedules: List[Schedule], all_courses: List[Course]) -> None:
        """Export all schedules in various formats."""
        try:
            logger.info(f"Exporting {len(schedules)} schedules")

            # Export individual JPEG schedules
            for i, schedule in enumerate(schedules, 1):
                jpeg_filename = f"program{i}.jpg"
                note = (f"Schedule {i}/{len(schedules)} | "
                       f"ECTS: {schedule.total_ects} | "
                       f"Conflicts: {schedule.conflict_cost} | "
                       f"Courses: {len(schedule.courses)}")

                ScheduleExporter.save_schedule_as_jpeg(schedule, jpeg_filename, note)

            # Export detailed schedules with more information
            for i, schedule in enumerate(schedules, 1):
                detailed_filename = f"detailed_schedule_{i}.jpg"
                ScheduleExporter.create_detailed_schedule_image(schedule, detailed_filename)

            # Create selection matrix
            ScheduleExporter.create_selection_matrix(schedules, all_courses)

            # Export summary report
            ScheduleExporter.create_summary_report(schedules, all_courses)

            # Export individual CSV files
            for i, schedule in enumerate(schedules, 1):
                csv_filename = f"schedule_{i}.csv"
                ScheduleExporter.export_schedule_to_csv(schedule, csv_filename)

            logger.info("All schedules exported successfully")

        except Exception as e:
            logger.error(f"Failed to export schedules: {e}")
            raise

    @staticmethod
    def create_detailed_schedule_image(schedule: Schedule, filename: str) -> None:
        """Create a detailed schedule image with additional information."""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))

            # Left side: Schedule grid
            grid_data = ScheduleExporter.get_schedule_grid_data(schedule)
            col_labels = grid_data[0]
            data_rows = grid_data[1:]

            ax1.axis("tight")
            ax1.axis("off")

            table1 = ax1.table(cellText=data_rows, colLabels=col_labels,
                              loc="center", cellLoc="center")
            table1.auto_set_font_size(False)
            table1.set_fontsize(9)
            table1.scale(1, 1.3)

            ax1.set_title("Weekly Schedule", fontsize=14, fontweight='bold')

            # Right side: Course details
            ax2.axis("off")

            # Prepare course details
            course_details = []
            course_details.append(["Course Code", "Course Name", "ECTS", "Teacher"])

            for course in sorted(schedule.courses, key=lambda c: c.code):
                name_short = course.name[:25] + "..." if len(course.name) > 25 else course.name
                teacher_short = course.teacher[:15] + "..." if len(course.teacher) > 15 else course.teacher
                course_details.append([course.code, name_short, str(course.ects), teacher_short])

            table2 = ax2.table(cellText=course_details[1:], colLabels=course_details[0],
                              loc="center", cellLoc="left")
            table2.auto_set_font_size(False)
            table2.set_fontsize(8)
            table2.scale(1, 1.2)

            # Style course details table
            for i in range(len(course_details[0])):
                table2[(0, i)].set_facecolor('#2196F3')
                table2[(0, i)].set_text_props(weight='bold', color='white')

            ax2.set_title("Course Details", fontsize=14, fontweight='bold')

            # Add summary at the bottom
            summary_text = (f"Total ECTS: {schedule.total_ects} | "
                          f"Total Courses: {len(schedule.courses)} | "
                          f"Conflicts: {schedule.conflict_cost}")

            fig.suptitle("Detailed Course Schedule", fontsize=16, fontweight='bold')
            fig.text(0.5, 0.02, summary_text, ha='center', fontsize=12,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))

            plt.tight_layout()
            plt.savefig(filename, dpi=300, bbox_inches="tight")
            plt.close()

            logger.info(f"Detailed schedule saved as: {filename}")

        except Exception as e:
            logger.error(f"Failed to create detailed schedule image: {e}")
            raise

    @staticmethod
    def create_summary_report(schedules: List[Schedule], all_courses: List[Course]) -> None:
        """Create a comprehensive summary report."""
        try:
            report_filename = "schedule_summary_report.txt"

            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("COURSE SCHEDULER SUMMARY REPORT\n")
                f.write("=" * 60 + "\n\n")

                # Overall statistics
                f.write("OVERALL STATISTICS\n")
                f.write("-" * 30 + "\n")
                f.write(f"Total schedules generated: {len(schedules)}\n")
                f.write(f"Total courses available: {len(all_courses)}\n")

                if schedules:
                    avg_ects = sum(s.total_ects for s in schedules) / len(schedules)
                    avg_courses = sum(len(s.courses) for s in schedules) / len(schedules)
                    conflict_free = sum(1 for s in schedules if s.conflict_cost == 0)

                    f.write(f"Average ECTS per schedule: {avg_ects:.1f}\n")
                    f.write(f"Average courses per schedule: {avg_courses:.1f}\n")
                    f.write(f"Conflict-free schedules: {conflict_free}/{len(schedules)}\n")

                f.write("\n")

                # Individual schedule details
                f.write("INDIVIDUAL SCHEDULE DETAILS\n")
                f.write("-" * 40 + "\n")

                for i, schedule in enumerate(schedules, 1):
                    f.write(f"\nSchedule {i}:\n")
                    f.write(f"  ECTS: {schedule.total_ects}\n")
                    f.write(f"  Courses: {len(schedule.courses)}\n")
                    f.write(f"  Conflicts: {schedule.conflict_cost}\n")
                    f.write(f"  Course codes: {', '.join(c.code for c in schedule.courses)}\n")

                # Course frequency analysis
                f.write("\n\nCOURSE FREQUENCY ANALYSIS\n")
                f.write("-" * 35 + "\n")

                course_frequency = {}
                for schedule in schedules:
                    for course in schedule.courses:
                        course_frequency[course.code] = course_frequency.get(course.code, 0) + 1

                sorted_freq = sorted(course_frequency.items(), key=lambda x: x[1], reverse=True)

                f.write("Most frequently selected courses:\n")
                for code, freq in sorted_freq[:10]:
                    percentage = (freq / len(schedules)) * 100
                    f.write(f"  {code}: {freq}/{len(schedules)} ({percentage:.1f}%)\n")

            logger.info(f"Summary report saved as: {report_filename}")

        except Exception as e:
            logger.error(f"Failed to create summary report: {e}")
            raise

    @staticmethod
    def create_conflict_report(schedules: List[Schedule]) -> None:
        """Create a detailed conflict analysis report."""
        try:
            report_filename = "conflict_report.txt"

            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write("=" * 50 + "\n")
                f.write("CONFLICT ANALYSIS REPORT\n")
                f.write("=" * 50 + "\n\n")

                total_conflicts = 0
                conflict_pairs = {}

                for i, schedule in enumerate(schedules, 1):
                    f.write(f"Schedule {i} Conflicts: {schedule.conflict_cost}\n")

                    if schedule.conflict_cost > 0:
                        # Find specific conflicts
                        for j, course1 in enumerate(schedule.courses):
                            for course2 in schedule.courses[j+1:]:
                                if course1.conflicts_with(course2):
                                    pair = tuple(sorted([course1.code, course2.code]))
                                    conflict_pairs[pair] = conflict_pairs.get(pair, 0) + 1

                                    # Find specific time conflicts
                                    common_times = set(course1.schedule) & set(course2.schedule)
                                    f.write(f"  {course1.code} vs {course2.code}: {list(common_times)}\n")

                    total_conflicts += schedule.conflict_cost
                    f.write("\n")

                f.write(f"Total conflicts across all schedules: {total_conflicts}\n\n")

                if conflict_pairs:
                    f.write("Most common conflict pairs:\n")
                    sorted_pairs = sorted(conflict_pairs.items(), key=lambda x: x[1], reverse=True)
                    for (course1, course2), freq in sorted_pairs[:10]:
                        f.write(f"  {course1} vs {course2}: {freq} times\n")

            logger.info(f"Conflict report saved as: {report_filename}")

        except Exception as e:
            logger.error(f"Failed to create conflict report: {e}")
            raise


class AdvancedExporter:
    """Advanced export functionality with enhanced features."""

    @staticmethod
    def export_schedule_comparison(schedules: List[Schedule], filename: str = "schedule_comparison.pdf") -> None:
        """Create a side-by-side comparison of multiple schedules."""
        try:
            with PdfPages(filename) as pdf:
                schedules_per_page = 2
                pages_needed = math.ceil(len(schedules) / schedules_per_page)

                for page in range(pages_needed):
                    fig, axes = plt.subplots(1, schedules_per_page, figsize=(16, 10))
                    if schedules_per_page == 1:
                        axes = [axes]

                    start_idx = page * schedules_per_page
                    end_idx = min(start_idx + schedules_per_page, len(schedules))

                    for i, schedule_idx in enumerate(range(start_idx, end_idx)):
                        schedule = schedules[schedule_idx]
                        ax = axes[i]

                        # Create schedule grid for this schedule
                        grid_data = ScheduleExporter.get_schedule_grid_data(schedule)

                        ax.axis("tight")
                        ax.axis("off")

                        table = ax.table(cellText=grid_data[1:], colLabels=grid_data[0],
                                       loc="center", cellLoc="center")
                        table.auto_set_font_size(False)
                        table.set_fontsize(8)
                        table.scale(1, 1.2)

                        ax.set_title(f"Schedule {schedule_idx + 1}\n"
                                   f"ECTS: {schedule.total_ects}, "
                                   f"Conflicts: {schedule.conflict_cost}",
                                   fontsize=12, fontweight='bold')

                    # Hide unused subplots
                    for i in range(end_idx - start_idx, schedules_per_page):
                        axes[i].set_visible(False)

                    plt.suptitle(f"Schedule Comparison - Page {page + 1}", fontsize=16)
                    plt.tight_layout()
                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close()

            logger.info(f"Schedule comparison saved as: {filename}")

        except Exception as e:
            logger.error(f"Failed to create schedule comparison: {e}")
            raise

    @staticmethod
    def export_analytics_dashboard(schedules: List[Schedule], all_courses: List[Course],
                                 filename: str = "analytics_dashboard.pdf") -> None:
        """Create an analytics dashboard with charts and statistics."""
        try:
            with PdfPages(filename) as pdf:
                # Page 1: Overview statistics
                fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

                # ECTS distribution
                ects_values = [s.total_ects for s in schedules]
                ax1.hist(ects_values, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
                ax1.set_title('ECTS Distribution')
                ax1.set_xlabel('ECTS')
                ax1.set_ylabel('Frequency')

                # Conflict analysis
                conflict_values = [s.conflict_cost for s in schedules]
                conflict_counts = {}
                for val in conflict_values:
                    conflict_counts[val] = conflict_counts.get(val, 0) + 1

                ax2.bar(conflict_counts.keys(), conflict_counts.values(),
                       alpha=0.7, color='lightcoral', edgecolor='black')
                ax2.set_title('Conflict Distribution')
                ax2.set_xlabel('Number of Conflicts')
                ax2.set_ylabel('Number of Schedules')

                # Course count distribution
                course_counts = [len(s.courses) for s in schedules]
                ax3.hist(course_counts, bins=8, alpha=0.7, color='lightgreen', edgecolor='black')
                ax3.set_title('Courses per Schedule')
                ax3.set_xlabel('Number of Courses')
                ax3.set_ylabel('Frequency')

                # Top courses
                course_frequency = {}
                for schedule in schedules:
                    for course in schedule.courses:
                        course_frequency[course.code] = course_frequency.get(course.code, 0) + 1

                top_courses = sorted(course_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
                if top_courses:
                    codes, freqs = zip(*top_courses)
                    ax4.barh(range(len(codes)), freqs, alpha=0.7, color='orange')
                    ax4.set_yticks(range(len(codes)))
                    ax4.set_yticklabels(codes)
                    ax4.set_title('Most Selected Courses')
                    ax4.set_xlabel('Selection Frequency')

                plt.suptitle('Schedule Analytics Dashboard', fontsize=16, fontweight='bold')
                plt.tight_layout()
                pdf.savefig(fig, bbox_inches='tight')
                plt.close()

            logger.info(f"Analytics dashboard saved as: {filename}")

        except Exception as e:
            logger.error(f"Failed to create analytics dashboard: {e}")
            raise
