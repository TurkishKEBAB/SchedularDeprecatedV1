"""
Advanced Schedule Analysis and Filtering GUI.

This module provides a comprehensive interface for analyzing and filtering
generated schedules with advanced criteria and export capabilities.
"""
import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict
import logging
import os
from datetime import datetime

from ..data.schedule_database import ScheduleDatabase
from ..data.models import Schedule
from ..reporting.pdf import save_schedules_as_pdf
from ..reporting.jpeg import save_schedules_as_jpegs
from ..reporting.excel import export_schedules_to_excel

logger = logging.getLogger(__name__)


class AdvancedScheduleAnalysisWindow:
    """
    Advanced schedule analysis and filtering window.

    Features:
    - Database-powered schedule storage and retrieval
    - Advanced filtering by multiple criteria
    - Statistical analysis and visualization
    - Export to PDF, Excel, and JPEG formats
    - Schedule comparison and ranking
    """

    def __init__(self, parent: ctk.CTk, schedule_db: ScheduleDatabase):
        """
        Initialize the advanced analysis window.

        Args:
            parent: Parent window
            schedule_db: Schedule database instance
        """
        self.parent = parent
        self.schedule_db = schedule_db
        self.filtered_schedules = []

        # Create the window
        self.window = ctk.CTkToplevel(parent)
        self.window.title("🔬 Advanced Schedule Analysis")
        self.window.geometry("1400x900")
        self.window.transient(parent)
        self.window.grab_set()

        # Create main layout
        self._create_layout()
        self._load_initial_data()

    def _create_layout(self):
        """Create the main layout of the analysis window."""
        # Create main container with tabs
        self.tab_view = ctk.CTkTabview(self.window)
        self.tab_view.pack(fill="both", expand=True, padx=20, pady=20)

        # Create tabs
        self.filter_tab = self.tab_view.add("🔍 Advanced Filters")
        self.analysis_tab = self.tab_view.add("📊 Statistical Analysis")
        self.export_tab = self.tab_view.add("📤 Export & Reports")

        # Setup each tab
        self._setup_filter_tab()
        self._setup_analysis_tab()
        self._setup_export_tab()

    def _setup_filter_tab(self):
        """Setup the advanced filtering tab."""
        # Main container with scroll
        main_frame = ctk.CTkScrollableFrame(self.filter_tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Filter Controls Section
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            controls_frame,
            text="🎛️ Filter Controls",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))

        # Credits Filter
        credits_frame = ctk.CTkFrame(controls_frame)
        credits_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            credits_frame,
            text="Credits Range:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=10)

        self.min_credits_var = ctk.IntVar(value=0)
        self.max_credits_var = ctk.IntVar(value=50)

        ctk.CTkLabel(credits_frame, text="Min:").pack(side="left", padx=(20, 5))
        self.min_credits_slider = ctk.CTkSlider(
            credits_frame, from_=0, to=50, variable=self.min_credits_var,
            command=self._on_filter_change, width=150
        )
        self.min_credits_slider.pack(side="left", padx=5)

        self.min_credits_label = ctk.CTkLabel(credits_frame, text="0")
        self.min_credits_label.pack(side="left", padx=(5, 20))

        ctk.CTkLabel(credits_frame, text="Max:").pack(side="left", padx=5)
        self.max_credits_slider = ctk.CTkSlider(
            credits_frame, from_=0, to=50, variable=self.max_credits_var,
            command=self._on_filter_change, width=150
        )
        self.max_credits_slider.pack(side="left", padx=5)

        self.max_credits_label = ctk.CTkLabel(credits_frame, text="50")
        self.max_credits_label.pack(side="left", padx=5)

        # Conflicts Filter
        conflicts_frame = ctk.CTkFrame(controls_frame)
        conflicts_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            conflicts_frame,
            text="Maximum Conflicts:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=10)

        self.max_conflicts_var = ctk.IntVar(value=10)
        self.max_conflicts_slider = ctk.CTkSlider(
            conflicts_frame, from_=0, to=10, variable=self.max_conflicts_var,
            command=self._on_filter_change, width=200
        )
        self.max_conflicts_slider.pack(side="left", padx=20)

        self.max_conflicts_label = ctk.CTkLabel(conflicts_frame, text="10")
        self.max_conflicts_label.pack(side="left", padx=10)

        # Free Days Filter
        free_days_frame = ctk.CTkFrame(controls_frame)
        free_days_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            free_days_frame,
            text="Required Free Days:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=10)

        self.free_day_vars = {}
        days = ["M", "T", "W", "Th", "F", "Sa", "Su"]
        for day in days:
            var = ctk.BooleanVar()
            self.free_day_vars[day] = var
            check = ctk.CTkCheckBox(
                free_days_frame, text=day, variable=var,
                command=self._on_filter_change
            )
            check.pack(side="left", padx=5)

        # Days Used Filter
        days_used_frame = ctk.CTkFrame(controls_frame)
        days_used_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            days_used_frame,
            text="Maximum Days Used:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=10)

        self.max_days_var = ctk.IntVar(value=7)
        self.max_days_slider = ctk.CTkSlider(
            days_used_frame, from_=1, to=7, variable=self.max_days_var,
            command=self._on_filter_change, width=200
        )
        self.max_days_slider.pack(side="left", padx=20)

        self.max_days_label = ctk.CTkLabel(days_used_frame, text="7")
        self.max_days_label.pack(side="left", padx=10)

        # Course Filter
        course_filter_frame = ctk.CTkFrame(controls_frame)
        course_filter_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            course_filter_frame,
            text="Must Include Courses:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=10)

        self.course_filter_entry = ctk.CTkEntry(
            course_filter_frame,
            placeholder_text="Enter course codes separated by commas (e.g., COMP101, MATH201)",
            width=400
        )
        self.course_filter_entry.pack(side="left", padx=10)
        self.course_filter_entry.bind("<Return>", lambda e: self._on_filter_change())

        # Filter Buttons
        button_frame = ctk.CTkFrame(controls_frame)
        button_frame.pack(fill="x", padx=15, pady=15)

        ctk.CTkButton(
            button_frame,
            text="🔍 Apply Filters",
            command=self._apply_filters,
            width=150,
            fg_color=("blue", "darkblue")
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="🗑️ Clear All",
            command=self._clear_filters,
            width=150,
            fg_color=("gray60", "gray40")
        ).pack(side="left", padx=10)

        # Results Section
        results_frame = ctk.CTkFrame(main_frame)
        results_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            results_frame,
            text="📋 Filtered Results",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # Results summary
        self.results_summary = ctk.CTkLabel(
            results_frame,
            text="Ready to filter schedules",
            font=ctk.CTkFont(size=11)
        )
        self.results_summary.pack(pady=5)

        # Results treeview
        tree_container = ctk.CTkFrame(results_frame)
        tree_container.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("ID", "Credits", "Conflicts", "Days", "Gaps", "Free Days", "Courses", "Created")
        self.results_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15)

        for col in columns:
            self.results_tree.heading(col, text=col)
            width = 120 if col in ("Free Days", "Courses") else 80
            self.results_tree.column(col, width=width)

        # Scrollbars for results
        v_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=self.results_tree.yview)
        v_scroll.pack(side="right", fill="y")
        h_scroll = ttk.Scrollbar(tree_container, orient="horizontal", command=self.results_tree.xview)
        h_scroll.pack(side="bottom", fill="x")

        self.results_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self.results_tree.pack(fill="both", expand=True)

    def _setup_analysis_tab(self):
        """Setup the statistical analysis tab."""
        # Create scrollable frame
        analysis_frame = ctk.CTkScrollableFrame(self.analysis_tab)
        analysis_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Database Statistics Section
        stats_frame = ctk.CTkFrame(analysis_frame)
        stats_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            stats_frame,
            text="📈 Database Statistics",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 10))

        # Stats container
        self.stats_container = ctk.CTkFrame(stats_frame)
        self.stats_container.pack(fill="x", padx=15, pady=10)

        # Pattern Analysis Section
        pattern_frame = ctk.CTkFrame(analysis_frame)
        pattern_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            pattern_frame,
            text="🔍 Pattern Analysis",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))

        # Popular courses
        popular_frame = ctk.CTkFrame(pattern_frame)
        popular_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            popular_frame,
            text="Most Popular Courses:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=5)

        self.popular_courses_text = ctk.CTkTextbox(popular_frame, height=150)
        self.popular_courses_text.pack(fill="x", padx=10, pady=5)

        # Refresh button
        ctk.CTkButton(
            analysis_frame,
            text="🔄 Refresh Analysis",
            command=self._refresh_analysis,
            width=200
        ).pack(pady=20)

    def _setup_export_tab(self):
        """Setup the export and reports tab."""
        export_frame = ctk.CTkFrame(self.export_tab)
        export_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            export_frame,
            text="📤 Export Options",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 20))

        # Export format selection
        format_frame = ctk.CTkFrame(export_frame)
        format_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            format_frame,
            text="Select Export Format:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)

        self.export_format = ctk.StringVar(value="PDF")
        formats = ["PDF", "Excel", "JPEG"]

        for fmt in formats:
            radio = ctk.CTkRadioButton(
                format_frame,
                text=fmt,
                variable=self.export_format,
                value=fmt
            )
            radio.pack(side="left", padx=20)

        # Export options
        options_frame = ctk.CTkFrame(export_frame)
        options_frame.pack(fill="x", padx=20, pady=10)

        self.export_filtered_only = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="Export only filtered schedules",
            variable=self.export_filtered_only
        ).pack(pady=5)

        self.include_analysis = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="Include statistical analysis",
            variable=self.include_analysis
        ).pack(pady=5)

        # Export buttons
        button_frame = ctk.CTkFrame(export_frame)
        button_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            button_frame,
            text="📁 Choose Output Folder",
            command=self._choose_export_folder,
            width=200
        ).pack(pady=10)

        self.export_path_label = ctk.CTkLabel(
            button_frame,
            text="No folder selected",
            font=ctk.CTkFont(size=11)
        )
        self.export_path_label.pack(pady=5)

        ctk.CTkButton(
            button_frame,
            text="🚀 Export Schedules",
            command=self._export_schedules,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("green", "darkgreen")
        ).pack(pady=15)

        # Export status
        self.export_status = ctk.CTkLabel(
            export_frame,
            text="Ready to export",
            font=ctk.CTkFont(size=11)
        )
        self.export_status.pack(pady=10)

    def _load_initial_data(self):
        """Load initial data into the analysis window."""
        try:
            # Load recent schedules
            recent_schedules = self.schedule_db.get_schedules_with_filters({"limit": 100})
            self.filtered_schedules = recent_schedules
            self._update_results_display()

            # Load database statistics
            self._refresh_analysis()

        except Exception as e:
            logger.error(f"Error loading initial data: {e}")
            messagebox.showerror("Error", f"Failed to load data: {e}")

    def _on_filter_change(self, value=None):
        """Handle filter control changes."""
        # Update labels
        self.min_credits_label.configure(text=str(self.min_credits_var.get()))
        self.max_credits_label.configure(text=str(self.max_credits_var.get()))
        self.max_conflicts_label.configure(text=str(self.max_conflicts_var.get()))
        self.max_days_label.configure(text=str(self.max_days_var.get()))

    def _apply_filters(self):
        """Apply the current filter settings."""
        try:
            # Build filter dictionary
            filters = {
                "min_credits": self.min_credits_var.get(),
                "max_credits": self.max_credits_var.get(),
                "max_conflicts": self.max_conflicts_var.get(),
                "max_days_used": self.max_days_var.get()
            }

            # Add free days filter
            required_free_days = [day for day, var in self.free_day_vars.items() if var.get()]
            if required_free_days:
                filters["required_free_days"] = required_free_days

            # Add course filter
            course_filter = self.course_filter_entry.get().strip()
            if course_filter:
                course_codes = [code.strip().upper() for code in course_filter.split(",")]
                filters["course_codes"] = course_codes

            # Apply filters
            self.filtered_schedules = self.schedule_db.get_schedules_with_filters(filters)
            self._update_results_display()

            logger.info(f"Applied filters, found {len(self.filtered_schedules)} matching schedules")

        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            messagebox.showerror("Filter Error", f"Failed to apply filters: {e}")

    def _clear_filters(self):
        """Clear all filter settings."""
        # Reset sliders
        self.min_credits_var.set(0)
        self.max_credits_var.set(50)
        self.max_conflicts_var.set(10)
        self.max_days_var.set(7)

        # Reset checkboxes
        for var in self.free_day_vars.values():
            var.set(False)

        # Clear entry
        self.course_filter_entry.delete(0, "end")

        # Update labels
        self._on_filter_change()

        # Load all schedules
        self.filtered_schedules = self.schedule_db.get_schedules_with_filters({"limit": 100})
        self._update_results_display()

    def _update_results_display(self):
        """Update the results treeview with filtered schedules."""
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Add filtered schedules
        for schedule in self.filtered_schedules:
            free_days_str = ", ".join(schedule["free_days"]) if schedule["free_days"] else "None"
            courses_str = f"{len(schedule['course_codes'])} courses"
            created_str = schedule["created_at"][:16]  # Show date and time

            self.results_tree.insert("", "end", values=(
                schedule["id"],
                schedule["total_credits"],
                schedule["conflict_count"],
                schedule["days_used"],
                schedule["total_gaps"],
                free_days_str,
                courses_str,
                created_str
            ))

        # Update summary
        self.results_summary.configure(
            text=f"Showing {len(self.filtered_schedules)} schedules"
        )

    def _refresh_analysis(self):
        """Refresh the statistical analysis."""
        try:
            stats = self.schedule_db.get_database_stats()

            # Clear existing stats
            for widget in self.stats_container.winfo_children():
                widget.destroy()

            # Display statistics
            if stats:
                stats_text = f"""
                📊 Total Schedules: {stats.get('total_schedules', 0)}
                📚 Unique Courses: {stats.get('unique_courses', 0)}
                📈 Average Credits: {stats.get('avg_credits', 0)}
                ⚖️ Credit Range: {stats.get('credit_range', (0, 0))[0]} - {stats.get('credit_range', (0, 0))[1]}
                ⚠️ Average Conflicts: {stats.get('avg_conflicts', 0)}
                📅 Average Days Used: {stats.get('avg_days_used', 0)}
                ✅ Conflict-Free Schedules: {stats.get('conflict_free_schedules', 0)}
                """

                stats_label = ctk.CTkLabel(
                    self.stats_container,
                    text=stats_text,
                    font=ctk.CTkFont(size=12),
                    justify="left"
                )
                stats_label.pack(padx=20, pady=10)

                # Display popular courses
                popular_text = "Most Popular Courses:\\n\\n"
                for course in stats.get('popular_courses', [])[:10]:
                    popular_text += f"• {course['code']}: {course['name']} ({course['usage']} times)\\n"

                self.popular_courses_text.delete(1.0, "end")
                self.popular_courses_text.insert(1.0, popular_text)

        except Exception as e:
            logger.error(f"Error refreshing analysis: {e}")

    def _choose_export_folder(self):
        """Choose the export output folder."""
        folder = filedialog.askdirectory(title="Choose Export Folder")
        if folder:
            self.export_folder = folder
            self.export_path_label.configure(text=f"Export to: {folder}")

    def _export_schedules(self):
        """Export the schedules in the selected format."""
        if not hasattr(self, 'export_folder'):
            messagebox.showerror("Error", "Please choose an export folder first.")
            return

        try:
            # Determine which schedules to export
            schedules_to_export = self.filtered_schedules if self.export_filtered_only.get() else None

            if not schedules_to_export:
                schedules_to_export = self.schedule_db.get_schedules_with_filters({})

            if not schedules_to_export:
                messagebox.showwarning("Warning", "No schedules to export.")
                return

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            format_type = self.export_format.get().lower()

            if format_type == "pdf":
                filename = f"schedule_analysis_{timestamp}.pdf"
                filepath = os.path.join(self.export_folder, filename)
                success = self._export_to_pdf(schedules_to_export, filepath)

            elif format_type == "excel":
                filename = f"schedule_analysis_{timestamp}.xlsx"
                filepath = os.path.join(self.export_folder, filename)
                success = self.schedule_db.export_schedules_analysis(filepath, {})

            elif format_type == "jpeg":
                folder_name = f"schedule_images_{timestamp}"
                export_path = os.path.join(self.export_folder, folder_name)
                os.makedirs(export_path, exist_ok=True)
                success = self._export_to_jpeg(schedules_to_export, export_path)

            if success:
                self.export_status.configure(text=f"✅ Successfully exported to {format_type.upper()}")
                messagebox.showinfo("Success", f"Schedules exported successfully to {filepath if format_type != 'jpeg' else export_path}")
            else:
                self.export_status.configure(text="❌ Export failed")

        except Exception as e:
            logger.error(f"Export error: {e}")
            messagebox.showerror("Export Error", f"Failed to export: {e}")
            self.export_status.configure(text="❌ Export failed")

    def _export_to_pdf(self, schedules_data: List[Dict], filepath: str) -> bool:
        """Export schedules to PDF format."""
        try:
            # Convert database format to Schedule objects
            schedules = []
            for schedule_data in schedules_data:
                schedule = self.schedule_db.get_schedule_by_id(schedule_data['id'])
                if schedule:
                    schedules.append(schedule)

            if schedules:
                save_schedules_as_pdf(schedules, filepath)
                return True
            return False

        except Exception as e:
            logger.error(f"PDF export error: {e}")
            return False

    def _export_to_jpeg(self, schedules_data: List[Dict], export_path: str) -> bool:
        """Export schedules to JPEG format."""
        try:
            # Convert database format to Schedule objects
            schedules = []
            for schedule_data in schedules_data:
                schedule = self.schedule_db.get_schedule_by_id(schedule_data['id'])
                if schedule:
                    schedules.append(schedule)

            if schedules:
                save_schedules_as_jpegs(schedules, export_path)
                return True
            return False

        except Exception as e:
            logger.error(f"JPEG export error: {e}")
            return False
