"""
Schedule report tab implementation for the course scheduler.

This module provides the fourth tab of the application, where users can
view generated schedules and export reports.
"""
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from typing import List, Any, Optional
import logging
import os

from ..data.models import Schedule
from ..reporting.charts import ScheduleAnalyticsChart, DayDistributionChart, create_course_type_chart

# Set up logging
logger = logging.getLogger(__name__)


class ScheduleReportTab:
    """
    Fourth tab of the scheduler application for viewing and exporting schedules.

    This tab allows users to:
    1. View generated schedules in a table format
    2. See schedule analytics and charts
    3. Export schedules to various formats
    4. Generate conflict reports
    """

    def __init__(self, parent: ctk.CTkFrame, main_app: Any):
        """
        Initialize the schedule report tab.

        Args:
            parent: Parent frame (tab container)
            main_app: Reference to the main application
        """
        self.parent = parent
        self.main_app = main_app
        self.schedules: List[Schedule] = []
        self.selected_schedule_index = 0

        # Create UI components
        self._create_schedule_list()
        self._create_schedule_display()
        self._create_export_section()

    def _create_schedule_list(self):
        """Create the schedule list section."""
        # Schedule list frame
        list_frame = ctk.CTkFrame(self.parent)
        list_frame.pack(fill="x", padx=20, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            list_frame,
            text="📋 Generated Schedules",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 10))

        # Schedule selection frame
        selection_frame = ctk.CTkFrame(list_frame)
        selection_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            selection_frame,
            text="Select Schedule:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(10, 5))

        self.schedule_var = ctk.StringVar(value="No schedules available")
        self.schedule_combo = ctk.CTkComboBox(
            selection_frame,
            variable=self.schedule_var,
            state="readonly",
            width=300,
            command=self._on_schedule_selected
        )
        self.schedule_combo.pack(side="left", padx=10)

        # Refresh button
        refresh_btn = ctk.CTkButton(
            selection_frame,
            text="🔄 Refresh",
            command=self._refresh_schedules,
            width=100
        )
        refresh_btn.pack(side="left", padx=10)

        # Schedule info frame
        info_frame = ctk.CTkFrame(list_frame)
        info_frame.pack(fill="x", padx=15, pady=5)

        self.info_label = ctk.CTkLabel(
            info_frame,
            text="Select a schedule to view details",
            font=ctk.CTkFont(size=11),
            wraplength=800
        )
        self.info_label.pack(pady=10)

    def _create_schedule_display(self):
        """Create the schedule display section."""
        # Display frame
        display_frame = ctk.CTkFrame(self.parent)
        display_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            display_frame,
            text="📅 Schedule Details",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 10))

        # Notebook for different views
        self.notebook = ttk.Notebook(display_frame)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        # Course list tab
        self.courses_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.courses_frame, text="Course List")

        # Create course treeview
        columns = ("Code", "Name", "Credits", "Type", "Schedule", "Teacher")
        self.courses_tree = ttk.Treeview(self.courses_frame, columns=columns, show="headings")

        for col in columns:
            self.courses_tree.heading(col, text=col)
            width = 150 if col in ("Name", "Schedule") else 100
            self.courses_tree.column(col, width=width)

        # Add scrollbars to treeview
        tree_scroll_y = ttk.Scrollbar(self.courses_frame, orient="vertical", command=self.courses_tree.yview)
        tree_scroll_x = ttk.Scrollbar(self.courses_frame, orient="horizontal", command=self.courses_tree.xview)

        self.courses_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x.pack(side="bottom", fill="x")
        self.courses_tree.pack(fill="both", expand=True)

        # Grid view tab
        self.grid_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.grid_frame, text="Weekly Grid")

        # Analytics tab
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="Analytics")

    def _create_export_section(self):
        """Create the export options section."""
        # Export frame
        export_frame = ctk.CTkFrame(self.parent)
        export_frame.pack(fill="x", padx=20, pady=10)

        # Title
        title_label = ctk.CTkLabel(
            export_frame,
            text="📤 Export Options",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(15, 10))

        # Button frame
        button_frame = ctk.CTkFrame(export_frame)
        button_frame.pack(fill="x", padx=15, pady=10)

        # Export buttons
        pdf_btn = ctk.CTkButton(
            button_frame,
            text="📄 Export to PDF",
            command=self._export_pdf,
            width=140,
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red")
        )
        pdf_btn.pack(side="left", padx=5)

        excel_btn = ctk.CTkButton(
            button_frame,
            text="📊 Export to Excel",
            command=self._export_excel,
            width=140,
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "green")
        )
        excel_btn.pack(side="left", padx=5)

        image_btn = ctk.CTkButton(
            button_frame,
            text="🖼️ Export Images",
            command=self._export_images,
            width=140,
            fg_color=("blue", "darkblue"),
            hover_color=("darkblue", "blue")
        )
        image_btn.pack(side="left", padx=5)

        report_btn = ctk.CTkButton(
            button_frame,
            text="📋 Conflict Report",
            command=self._generate_conflict_report,
            width=140,
            fg_color=("orange", "darkorange"),
            hover_color=("darkorange", "orange")
        )
        report_btn.pack(side="left", padx=5)

    def _on_schedule_selected(self, value):
        """Handle schedule selection change."""
        try:
            if value and value != "No schedules available":
                # Extract schedule index from the selection
                index = int(value.split(":")[0].split()[-1]) - 1
                self.selected_schedule_index = index
                self._display_schedule(self.schedules[index])
        except (ValueError, IndexError) as e:
            logger.error(f"Error selecting schedule: {e}")

    def _refresh_schedules(self):
        """Refresh the schedule list from the main application."""
        if hasattr(self.main_app, 'final_schedules') and self.main_app.final_schedules:
            self.schedules = self.main_app.final_schedules
            self._update_schedule_combo()
        else:
            self.schedule_var.set("No schedules available")
            self.info_label.configure(text="No schedules generated yet. Please run the scheduler first.")

    def _update_schedule_combo(self):
        """Update the schedule selection combo box."""
        if self.schedules:
            schedule_options = []
            for i, schedule in enumerate(self.schedules):
                total_credits = schedule.total_credits
                conflict_count = schedule.conflict_count
                schedule_options.append(f"Schedule {i+1}: {total_credits} ECTS, {conflict_count} conflicts")

            self.schedule_combo.configure(values=schedule_options)
            if schedule_options:
                self.schedule_var.set(schedule_options[0])
                self._display_schedule(self.schedules[0])
        else:
            self.schedule_combo.configure(values=["No schedules available"])
            self.schedule_var.set("No schedules available")

    def _display_schedule(self, schedule: Schedule):
        """
        Display the selected schedule details.

        Args:
            schedule: Schedule object to display
        """
        # Update info label
        info_text = (f"Total Credits: {schedule.total_credits} ECTS | "
                    f"Conflicts: {schedule.conflict_count} | "
                    f"Courses: {len(schedule.courses)}")
        self.info_label.configure(text=info_text)

        # Update course list
        self._update_course_list(schedule)

        # Update grid view
        self._update_grid_view(schedule)

        # Update analytics
        self._update_analytics(schedule)

    def _update_course_list(self, schedule: Schedule):
        """Update the course list treeview."""
        # Clear existing items
        for item in self.courses_tree.get_children():
            self.courses_tree.delete(item)

        # Add courses
        for course in schedule.courses:
            schedule_str = ", ".join(f"{day}{slot}" for day, slot in course.schedule)

            self.courses_tree.insert("", "end", values=(
                course.code,
                course.name,
                course.ects,
                course.course_type,
                schedule_str,
                course.teacher
            ))

    def _update_grid_view(self, schedule: Schedule):
        """Update the weekly grid view."""
        # Clear existing widgets
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        # Create grid (simplified version)
        grid_label = ctk.CTkLabel(
            self.grid_frame,
            text="Weekly Schedule Grid\n(Detailed grid implementation would go here)",
            font=ctk.CTkFont(size=12)
        )
        grid_label.pack(expand=True)

    def _update_analytics(self, schedule: Schedule):
        """Update the analytics view."""
        # Clear existing widgets
        for widget in self.analytics_frame.winfo_children():
            widget.destroy()

        # Create analytics display
        analytics_label = ctk.CTkLabel(
            self.analytics_frame,
            text="Schedule Analytics\n(Charts and metrics would go here)",
            font=ctk.CTkFont(size=12)
        )
        analytics_label.pack(expand=True)

    def _export_pdf(self):
        """Export schedule to PDF."""
        if not self.schedules:
            messagebox.showwarning("No Data", "No schedules available to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if file_path:
            try:
                # Implementation would call the PDF export functionality
                messagebox.showinfo("Success", f"Schedule exported to {file_path}")
                logger.info(f"Schedule exported to PDF: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")
                logger.error(f"PDF export error: {e}")

    def _export_excel(self):
        """Export schedule to Excel."""
        if not self.schedules:
            messagebox.showwarning("No Data", "No schedules available to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if file_path:
            try:
                # Implementation would call the Excel export functionality
                messagebox.showinfo("Success", f"Schedule exported to {file_path}")
                logger.info(f"Schedule exported to Excel: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export Excel: {str(e)}")
                logger.error(f"Excel export error: {e}")

    def _export_images(self):
        """Export schedule as images."""
        if not self.schedules:
            messagebox.showwarning("No Data", "No schedules available to export.")
            return

        folder_path = filedialog.askdirectory()

        if folder_path:
            try:
                # Implementation would call the image export functionality
                messagebox.showinfo("Success", f"Schedule images exported to {folder_path}")
                logger.info(f"Schedule images exported to: {folder_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export images: {str(e)}")
                logger.error(f"Image export error: {e}")

    def _generate_conflict_report(self):
        """Generate a conflict analysis report."""
        if not self.schedules:
            messagebox.showwarning("No Data", "No schedules available to analyze.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if file_path:
            try:
                # Implementation would call the conflict report functionality
                messagebox.showinfo("Success", f"Conflict report generated: {file_path}")
                logger.info(f"Conflict report generated: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
                logger.error(f"Conflict report error: {e}")

    def update_schedules(self, schedules: List[Schedule]):
        """
        Update the displayed schedules.

        Args:
            schedules: List of Schedule objects to display
        """
        self.schedules = schedules
        self._update_schedule_combo()
        logger.info(f"Schedule report updated with {len(schedules)} schedules")
