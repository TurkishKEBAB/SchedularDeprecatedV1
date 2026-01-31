"""
PDF reporting utilities for schedule export.

This module provides functions for exporting schedules to PDF format
with professional formatting and layout.
"""
import logging
from typing import List, Dict
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import os

from ..data.models import Schedule

logger = logging.getLogger(__name__)


def save_schedules_as_pdf(schedules: List[Schedule], output_path: str) -> bool:
    """
    Save multiple schedules to a PDF file.

    Args:
        schedules: List of Schedule objects to export
        output_path: Path where PDF will be saved

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create the PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []

        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )

        # Add title
        title = Paragraph("Course Schedule Report", title_style)
        story.append(title)
        story.append(Spacer(1, 20))

        # Add each schedule
        for i, schedule in enumerate(schedules, 1):
            # Schedule header
            header = Paragraph(f"Schedule {i}", styles['Heading2'])
            story.append(header)

            # Schedule summary
            summary_data = [
                ["Total Credits:", str(schedule.total_credits)],
                ["Number of Courses:", str(len(schedule.courses))],
                ["Conflicts:", str(schedule.conflict_count)]
            ]

            summary_table = Table(summary_data, colWidths=[2*inch, 1*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(summary_table)
            story.append(Spacer(1, 15))

            # Course details table
            course_data = [["Course Code", "Course Name", "Credits", "Schedule", "Instructor"]]

            for course in schedule.courses:
                schedule_str = ", ".join(f"{day}{slot}" for day, slot in course.schedule)
                course_data.append([
                    course.code,
                    course.name[:30] + "..." if len(course.name) > 30 else course.name,
                    str(course.ects),
                    schedule_str,
                    course.teacher[:20] + "..." if len(course.teacher) > 20 else course.teacher
                ])

            course_table = Table(course_data, colWidths=[1.2*inch, 2*inch, 0.6*inch, 1.2*inch, 1.5*inch])
            course_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(course_table)

            # Add page break between schedules (except for last one)
            if i < len(schedules):
                story.append(Spacer(1, 30))

        # Build PDF
        doc.build(story)
        logger.info(f"Successfully exported {len(schedules)} schedules to PDF: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error exporting schedules to PDF: {e}")
        return False


def save_schedule_as_pdf(schedule: Schedule, output_path: str) -> bool:
    """
    Save a single schedule to PDF.

    Args:
        schedule: Schedule object to export
        output_path: Path where PDF will be saved

    Returns:
        True if successful, False otherwise
    """
    return save_schedules_as_pdf([schedule], output_path)


def create_conflict_report(schedules: List[Schedule], output_path: str) -> bool:
    """
    Create a detailed conflict report for schedules.

    Args:
        schedules: List of Schedule objects to analyze for conflicts
        output_path: Path where conflict report PDF will be saved

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create the PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []

        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )

        # Add title
        title = Paragraph("Schedule Conflict Analysis Report", title_style)
        story.append(title)
        story.append(Spacer(1, 20))

        # Overall statistics
        total_schedules = len(schedules)
        conflict_schedules = [s for s in schedules if s.conflict_count > 0]
        conflict_free_schedules = total_schedules - len(conflict_schedules)

        summary_data = [
            ["Total Schedules Analyzed:", str(total_schedules)],
            ["Conflict-Free Schedules:", str(conflict_free_schedules)],
            ["Schedules with Conflicts:", str(len(conflict_schedules))],
            ["Conflict-Free Percentage:", f"{(conflict_free_schedules/total_schedules)*100:.1f}%" if total_schedules > 0 else "0%"]
        ]

        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 30))

        # Detailed conflict analysis for schedules with conflicts
        if conflict_schedules:
            conflict_header = Paragraph("Detailed Conflict Analysis", styles['Heading2'])
            story.append(conflict_header)
            story.append(Spacer(1, 15))

            for i, schedule in enumerate(conflict_schedules, 1):
                # Schedule conflict details
                conflict_detail_header = Paragraph(f"Schedule {i} - {schedule.conflict_count} Conflicts", styles['Heading3'])
                story.append(conflict_detail_header)

                # Find specific conflicts
                conflicts = _find_schedule_conflicts(schedule)

                if conflicts:
                    conflict_data = [["Course 1", "Course 2", "Conflicting Time Slots"]]

                    for conflict in conflicts:
                        conflict_slots = ", ".join(f"{day}{slot}" for day, slot in conflict['time_slots'])
                        conflict_data.append([
                            conflict['course1'],
                            conflict['course2'],
                            conflict_slots
                        ])

                    conflict_table = Table(conflict_data, colWidths=[2*inch, 2*inch, 2*inch])
                    conflict_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))

                    story.append(conflict_table)
                    story.append(Spacer(1, 20))

        # Build PDF
        doc.build(story)
        logger.info(f"Successfully created conflict report: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error creating conflict report: {e}")
        return False


def save_all_selection_matrices_to_pdf(schedules: List[Schedule], output_path: str) -> bool:
    """
    Save selection matrices for all schedules to a single PDF.

    Args:
        schedules: List of Schedule objects
        output_path: Path where PDF will be saved

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create the PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []

        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )

        # Add title
        title = Paragraph("Course Selection Matrices Report", title_style)
        story.append(title)
        story.append(Spacer(1, 20))

        # Add summary
        summary = Paragraph(f"This report contains {len(schedules)} course selection matrices.", styles['Normal'])
        story.append(summary)
        story.append(Spacer(1, 30))

        # Add each schedule's selection matrix
        for i, schedule in enumerate(schedules, 1):
            # Schedule header
            header = Paragraph(f"Schedule {i} Selection Matrix", styles['Heading2'])
            story.append(header)

            # Create time slot matrix
            days = ["Time", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            time_slots = [
                "08:30-09:20", "09:30-10:20", "10:30-11:20", "11:30-12:20",
                "12:30-13:20", "13:30-14:20", "14:30-15:20", "15:30-16:20",
                "16:30-17:20", "17:30-18:20", "18:30-19:20", "19:30-20:20"
            ]

            # Create matrix data
            matrix_data = [days]  # Header row

            for slot_idx, time_slot in enumerate(time_slots):
                row = [time_slot]  # Time column

                for day_idx, day in enumerate(["M", "T", "W", "Th", "F", "Sa", "Su"]):
                    cell_content = ""
                    # Find courses that occupy this time slot
                    for course in schedule.courses:
                        if (day, slot_idx + 1) in course.schedule:
                            if cell_content:
                                cell_content += "\n"
                            cell_content += course.code[:8]  # Truncate long course codes

                    row.append(cell_content if cell_content else "")

                matrix_data.append(row)

            # Create table
            matrix_table = Table(matrix_data, colWidths=[1.2*inch] + [0.8*inch]*7)
            matrix_table.setStyle(TableStyle([
                # Header row styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),

                # Time column styling
                ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 1), (0, -1), 7),

                # Data cells styling
                ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (1, 1), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

                # Grid
                ('GRID', (0, 0), (-1, -1), 1, colors.black),

                # Alternate row colors for better readability
                ('BACKGROUND', (1, 1), (-1, -1), colors.white),
            ]))

            # Add some color coding for occupied cells
            for row_idx in range(1, len(matrix_data)):
                for col_idx in range(1, len(matrix_data[row_idx])):
                    if matrix_data[row_idx][col_idx]:  # If cell has content
                        matrix_table.setStyle(TableStyle([
                            ('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), colors.lightgreen)
                        ]))

            story.append(matrix_table)

            # Course list for this schedule
            story.append(Spacer(1, 15))
            course_list_header = Paragraph(f"Courses in Schedule {i}:", styles['Heading3'])
            story.append(course_list_header)

            course_list = []
            for course in schedule.courses:
                schedule_str = ", ".join(f"{day}{slot}" for day, slot in course.schedule)
                course_info = f"{course.code}: {course.name} ({course.ects} ECTS) - {schedule_str}"
                course_list.append(course_info)

            course_text = Paragraph("<br/>".join(course_list), styles['Normal'])
            story.append(course_text)

            # Add page break between schedules (except for last one)
            if i < len(schedules):
                story.append(Spacer(1, 30))

        # Build PDF
        doc.build(story)
        logger.info(f"Successfully created selection matrices PDF: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error creating selection matrices PDF: {e}")
        return False


def _find_schedule_conflicts(schedule: Schedule) -> List[Dict]:
    """
    Find specific conflicts in a schedule.

    Args:
        schedule: Schedule to analyze

    Returns:
        List of conflict dictionaries with details
    """
    conflicts = []
    courses = schedule.courses

    for i, course1 in enumerate(courses):
        for j, course2 in enumerate(courses[i+1:], i+1):
            # Find overlapping time slots
            overlapping_slots = []
            for slot1 in course1.schedule:
                if slot1 in course2.schedule:
                    overlapping_slots.append(slot1)

            if overlapping_slots:
                conflicts.append({
                    'course1': course1.code,
                    'course2': course2.code,
                    'time_slots': overlapping_slots
                })

    return conflicts

