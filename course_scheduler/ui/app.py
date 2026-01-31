"""
Main application window and controller for the course scheduler.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import List, Optional
import threading
import sys
import os

# Add the parent directory to Python path for relative imports
if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from ..core.models import Course, Schedule, SchedulerConfig, UserPreferences, FilterProfile
    from ..core.parser import process_excel_robust, validate_course_data
    from ..core.planner import CourseScheduler
    from ..core.export import ScheduleExporter
    from ..utils.snapshot import SnapshotManager
    from .preview import CoursePreviewTab
    from .dialogs import CourseSelectionDialog, SnapshotLoadDialog
    from .charts import ScheduleAnalyticsChart
    from .report import DetailedScheduleReport
except ImportError:
    # Fallback for direct execution
    from course_scheduler.core.models import Course, Schedule, SchedulerConfig, UserPreferences, FilterProfile
    from course_scheduler.core.parser import process_excel_robust, validate_course_data
    from course_scheduler.core.planner import CourseScheduler
    from course_scheduler.core.export import ScheduleExporter
    from course_scheduler.utils.snapshot import SnapshotManager
    from course_scheduler.ui.preview import CoursePreviewTab
    from course_scheduler.ui.dialogs import CourseSelectionDialog, SnapshotLoadDialog
    from course_scheduler.ui.charts import ScheduleAnalyticsChart
    from course_scheduler.ui.report import DetailedScheduleReport

logger = logging.getLogger(__name__)


class SchedulerApplication:
    """Main application class for the course scheduler."""

    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("Course Scheduler - Enhanced")
        self.master.geometry("1200x800")

        # Configuration and state
        self.config = SchedulerConfig()
        self.preferences = UserPreferences()
        self.snapshot_manager = SnapshotManager("course_snapshots.sqlite")

        # Data state
        self.courses: List[Course] = []
        self.filtered_courses: Optional[List[Course]] = None
        self.last_filter_profile: Optional[FilterProfile] = None
        self.final_schedules: List[Schedule] = []

        # UI components
        self.setup_ui()

        # Configure logging
        self.setup_logging()

        logger.info("Course Scheduler application initialized")

    def setup_ui(self):
        """Setup the main UI components."""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Tab 1: File & Settings
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="1. File & Settings")
        self.setup_settings_tab()

        # Tab 2: Course Preview with Filters
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="2. Course Preview")
        self.course_preview = CoursePreviewTab(self.tab2, self)

        # Tab 3: Weekly Schedule View (NEW)
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="3. Weekly Schedule")
        self.setup_weekly_schedule_tab()

        # Tab 4: Course Selection & Planning
        self.tab4 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab4, text="4. Planning")
        self.setup_planning_tab()

        # Tab 5: Analytics & Reports
        self.tab5 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab5, text="5. Analytics")
        self.setup_analytics_tab()

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.master, textvariable=self.status_var,
                                   relief="sunken", anchor="w")
        self.status_bar.pack(side="bottom", fill="x")

    def setup_settings_tab(self):
        """Setup the file and settings tab."""
        main_frame = ttk.Frame(self.tab1)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="Excel File", padding=10)
        file_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(file_frame, text="Excel File:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_var, width=50)
        self.file_entry.grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=(5, 0))

        ttk.Label(file_frame, text="Sheet Name:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(5, 0))
        self.sheet_var = tk.StringVar(value="Sheet1")
        self.sheet_entry = ttk.Entry(file_frame, textvariable=self.sheet_var, width=20)
        self.sheet_entry.grid(row=1, column=1, sticky="w", padx=5, pady=(5, 0))

        # Scheduler settings
        settings_frame = ttk.LabelFrame(main_frame, text="Scheduler Settings", padding=10)
        settings_frame.pack(fill="x", pady=(0, 10))

        # Max ECTS
        ttk.Label(settings_frame, text="Max ECTS:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.max_ects_var = tk.IntVar(value=self.config.max_ects)
        self.max_ects_spin = ttk.Spinbox(settings_frame, from_=20, to=50,
                                        textvariable=self.max_ects_var, width=10)
        self.max_ects_spin.grid(row=0, column=1, sticky="w", padx=5)

        # Allow conflicts
        ttk.Label(settings_frame, text="Allow Conflicts:").grid(row=0, column=2, sticky="w", padx=(20, 5))
        self.allow_conflict_var = tk.IntVar(value=self.config.allow_conflict)
        self.conflict_spin = ttk.Spinbox(settings_frame, from_=0, to=5,
                                        textvariable=self.allow_conflict_var, width=10)
        self.conflict_spin.grid(row=0, column=3, sticky="w", padx=5)

        # Max results
        ttk.Label(settings_frame, text="Max Results:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(5, 0))
        self.max_results_var = tk.IntVar(value=self.config.max_results)
        self.results_spin = ttk.Spinbox(settings_frame, from_=1, to=20,
                                       textvariable=self.max_results_var, width=10)
        self.results_spin.grid(row=1, column=1, sticky="w", padx=5, pady=(5, 0))

        # Replacement target
        ttk.Label(settings_frame, text="Replacement Target:").grid(row=1, column=2, sticky="w", padx=(20, 5), pady=(5, 0))
        self.target_var = tk.StringVar(value=self.config.replacement_target)
        target_frame = ttk.Frame(settings_frame)
        target_frame.grid(row=1, column=3, sticky="w", padx=5, pady=(5, 0))
        ttk.Radiobutton(target_frame, text="Sections", variable=self.target_var, value="sections").pack(side="left")
        ttk.Radiobutton(target_frame, text="Course", variable=self.target_var, value="course").pack(side="left", padx=(10, 0))

        # Advanced options
        advanced_frame = ttk.LabelFrame(main_frame, text="Advanced Options", padding=10)
        advanced_frame.pack(fill="x", pady=(0, 10))

        self.sa_var = tk.BooleanVar(value=self.config.use_simulated_annealing)
        ttk.Checkbutton(advanced_frame, text="Use Simulated Annealing",
                       variable=self.sa_var).pack(anchor="w")

        self.count_optional_var = tk.BooleanVar(value=self.config.count_optional)
        ttk.Checkbutton(advanced_frame, text="Count Optional Courses in Credit Calculation",
                       variable=self.count_optional_var).pack(anchor="w")

        # New optimization toggles
        self.require_all_sections_var = tk.BooleanVar(value=self.config.require_all_sections)
        ttk.Checkbutton(advanced_frame, text="Require PS/Lab When Available",
                        variable=self.require_all_sections_var).pack(anchor="w")

        self.optimize_diversity_var = tk.BooleanVar(value=self.config.optimize_diversity)
        ttk.Checkbutton(advanced_frame, text="Optimize Diversity",
                        variable=self.optimize_diversity_var).pack(anchor="w")

        self.balance_workload_var = tk.BooleanVar(value=self.config.balance_workload)
        ttk.Checkbutton(advanced_frame, text="Balance Workload",
                        variable=self.balance_workload_var).pack(anchor="w")

        self.weekend_bias_var = tk.BooleanVar(value=self.config.auto_limit_weekend_bias)
        ttk.Checkbutton(advanced_frame, text="Penalize Weekend Load",
                        variable=self.weekend_bias_var).pack(anchor="w")

        # Load button
        ttk.Button(main_frame, text="Load Courses",
                  command=self.load_courses, style="Accent.TButton").pack(pady=10)

    def setup_selection_tab(self):
        """Setup the course selection tab."""
        label = ttk.Label(self.tab3, text="Course selection will appear here after loading courses.",
                         font=("Arial", 12))
        label.pack(expand=True)

    def setup_weekly_schedule_tab(self):
        """Setup the weekly schedule view tab."""
        try:
            from .enhanced_dashboard import InteractiveDashboard
            # Create the enhanced dashboard
            self.dashboard = InteractiveDashboard(self.tab3)
        except ImportError:
            # Fallback UI if enhanced dashboard is not available
            fallback_label = ttk.Label(self.tab3, 
                                     text="Enhanced Dashboard not available.\nWeekly schedule view will be implemented here.",
                                     font=("Arial", 12),
                                     justify="center")
            fallback_label.pack(expand=True)
            
            # Create a simple placeholder dashboard
            class SimpleDashboard:
                def __init__(self, parent):
                    self.parent = parent
                
                def set_courses(self, courses):
                    pass
                    
                def set_filtered_courses(self, courses):
                    pass
                    
                def set_schedules(self, schedules):
                    pass
                    
                def clear_data(self):
                    pass
                    
                def update_dashboard(self):
                    pass
                    
                def export_dashboard(self, filename):
                    raise NotImplementedError("Enhanced dashboard not available")
            
            self.dashboard = SimpleDashboard(self.tab3)

        # Add control buttons
        control_frame = ttk.Frame(self.tab3)
        control_frame.pack(side="bottom", fill="x", padx=10, pady=5)

        ttk.Button(control_frame, text="📊 Export Dashboard",
                  command=self.export_dashboard).pack(side="left", padx=5)
        ttk.Button(control_frame, text="🔄 Refresh Analytics",
                  command=self.refresh_dashboard).pack(side="left", padx=5)

    def setup_planning_tab(self):
        """Setup the course selection and planning tab."""
        try:
            from .smart_optimizer import SmartSchedulingAssistant
            # Create the smart scheduling assistant
            self.smart_assistant = SmartSchedulingAssistant(self.tab4)
        except ImportError:
            # Fallback UI if smart optimizer is not available
            fallback_label = ttk.Label(self.tab4,
                                     text="Smart Scheduling Assistant not available.\nCourse planning features will be implemented here.",
                                     font=("Arial", 12),
                                     justify="center")
            fallback_label.pack(expand=True)

            # Create a simple placeholder assistant
            class SimpleAssistant:
                def __init__(self, parent):
                    self.parent = parent

                def set_courses(self, courses):
                    pass

                def clear_data(self):
                    pass

            self.smart_assistant = SimpleAssistant(self.tab4)

    def setup_analytics_tab(self):
        """Setup the analytics and reports tab."""
        main_frame = ttk.Frame(self.tab5)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="Process Log", padding=10)
        log_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.log_text = tk.Text(log_frame, height=15, wrap="word")
        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        log_scroll.pack(side="right", fill="y")

        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")

        ttk.Button(button_frame, text="📊 Live Analytics",
                  command=self.show_analytics).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="📋 Detailed Report",
                  command=self.show_detailed_report).pack(side="left", padx=5)
        ttk.Button(button_frame, text="🗑️ Clear Cache",
                  command=self.clear_cache).pack(side="left", padx=5)

    def setup_logging(self):
        """Setup logging to display in the UI."""
        class UILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget

            def emit(self, record):
                msg = self.format(record)
                self.text_widget.insert(tk.END, msg + "\n")
                self.text_widget.see(tk.END)
                self.text_widget.update()

        handler = UILogHandler(self.log_text)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    def browse_file(self):
        """Browse for Excel file."""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        if file_path:
            self.file_var.set(file_path)

    def export_dashboard(self):
        """Export dashboard as image."""
        from tkinter import filedialog

        filename = filedialog.asksaveasfilename(
            title="Export Dashboard",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if filename:
            try:
                self.dashboard.export_dashboard(filename)
                messagebox.showinfo("Success", f"Dashboard exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export dashboard: {e}")

    def refresh_dashboard(self):
        """Refresh dashboard data."""
        if hasattr(self, 'dashboard'):
            self.dashboard.update_dashboard()
            self.status_var.set("Dashboard refreshed")

    def load_courses(self):
        """Load courses from Excel file."""
        file_path = self.file_var.get().strip()
        if not file_path:
            messagebox.showerror("Error", "Please select an Excel file first.")
            return

        sheet_name = self.sheet_var.get().strip() or "Sheet1"

        try:
            self.status_var.set("Loading courses...")
            logger.info(f"Loading courses from {file_path}, sheet: {sheet_name}")

            # Parse courses using robust parser
            self.courses = process_excel_robust(file_path, sheet_name)

            # Validate courses
            issues = validate_course_data(self.courses)
            if issues:
                logger.warning(f"Data validation issues found: {len(issues)}")
                for issue in issues[:5]:  # Show first 5 issues
                    logger.warning(f"  - {issue}")

            # Reset filter state
            self.filtered_courses = None
            self.last_filter_profile = None

            # Update all components with new data
            self.course_preview.load_courses(self.courses)

            # Update dashboard if exists
            if hasattr(self, 'dashboard'):
                self.dashboard.set_courses(self.courses)

            # Update smart assistant if exists
            if hasattr(self, 'smart_assistant'):
                self.smart_assistant.set_courses(self.courses)

            # Switch to preview tab
            self.notebook.select(self.tab2)

            self.status_var.set(f"Loaded {len(self.courses)} courses successfully")
            logger.info(f"Successfully loaded {len(self.courses)} courses")

        except Exception as e:
            error_msg = f"Failed to load courses: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Load Error", error_msg)
            self.status_var.set("Failed to load courses")

    def update_config(self):
        """Update configuration from UI values."""
        self.config.max_ects = self.max_ects_var.get()
        self.config.allow_conflict = self.allow_conflict_var.get()
        self.config.max_results = self.max_results_var.get()
        self.config.replacement_target = self.target_var.get()
        self.config.use_simulated_annealing = self.sa_var.get()
        self.config.count_optional = self.count_optional_var.get()
        self.config.require_all_sections = self.require_all_sections_var.get()
        self.config.optimize_diversity = self.optimize_diversity_var.get()
        self.config.balance_workload = self.balance_workload_var.get()
        self.config.auto_limit_weekend_bias = self.weekend_bias_var.get()

    def set_filtered_courses(self, courses: List[Course], profile: FilterProfile):
        """Set filtered courses from course preview."""
        self.filtered_courses = courses
        self.last_filter_profile = profile

        # Update dashboard with filtered data
        if hasattr(self, 'dashboard'):
            self.dashboard.set_filtered_courses(courses)

        logger.info(f"Filtered courses set: {len(courses)} courses")

    def proceed_to_selection(self, courses: List[Course]):
        """Proceed to course selection with given courses."""
        # Auto-save snapshot if using filtered courses
        if self.filtered_courses and self.last_filter_profile:
            try:
                snapshot_id = self.snapshot_manager.save_snapshot(
                    self.filtered_courses, self.last_filter_profile
                )
                logger.info(f"Auto-saved snapshot {snapshot_id} before selection")
            except Exception as e:
                logger.warning(f"Failed to auto-save snapshot: {e}")

        # Open course selection dialog
        dialog = CourseSelectionDialog(self.master, courses, self.on_course_selection)
        self.notebook.select(self.tab4)

    def on_course_selection(self, preferences: UserPreferences):
        """Handle course selection completion."""
        self.preferences = preferences
        logger.info(f"Course selection completed: {len(preferences.mandatory_courses)} mandatory courses")

        # Start scheduling
        self.run_scheduler()
        self.notebook.select(self.tab5)

    def run_scheduler(self):
        """Run the course scheduler with automatic section selection support."""
        if not self.courses:
            messagebox.showerror("Error", "No courses loaded. Please load courses first.")
            return

        self.update_config()

        # Determine source courses
        source_courses = self.filtered_courses if self.filtered_courses else self.courses
        source_type = "FILTERED" if self.filtered_courses else "ALL"

        logger.info(f"Starting scheduler with {source_type} courses: {len(source_courses)}")

        def scheduler_worker():
            try:
                scheduler = CourseScheduler(self.config, self.preferences)

                # Use automatic section selection if enabled
                if self.preferences.should_auto_select_sections():
                    logger.info("Using automatic section selection")
                    schedules = scheduler.generate_schedules_with_auto_sections(source_courses)
                else:
                    logger.info("Using traditional scheduling approach")
                    schedules = scheduler.generate_schedules(source_courses)

                if schedules:
                    # Export schedules
                    self.master.after(0, lambda: self._on_schedules_complete(schedules, source_courses))
                else:
                    self.master.after(0, lambda: self._on_scheduling_failed())

            except Exception as e:
                error_msg = f"Scheduling failed: {str(e)}"
                self.master.after(0, lambda: self._on_scheduling_error(error_msg))

        self.status_var.set("Generating optimal schedule with automatic section selection...")
        threading.Thread(target=scheduler_worker, daemon=True).start()

    def _on_schedules_complete(self, schedules: List[Schedule], source_courses: List[Course]):
        """Handle successful schedule generation."""
        self.final_schedules = schedules

        def exporter():
            try:
                # Update dashboard with schedule data (main thread via after)
                if hasattr(self, 'dashboard'):
                    self.master.after(0, lambda: self.dashboard.set_schedules(schedules))

                # Export all schedules (CPU/IO heavy)
                ScheduleExporter.export_all_schedules(schedules, source_courses)

                # After export finish
                auto_selected = all(hasattr(s, 'metadata') and s.metadata.get('auto_selected', False) for s in schedules)
                method_text = "with automatic section selection" if auto_selected else "using traditional method"

                self.master.after(0, lambda: self.status_var.set(f"Generated {len(schedules)} schedules successfully {method_text}"))
                self.master.after(0, lambda: logger.info(f"Successfully generated {len(schedules)} schedules {method_text}"))
                self.master.after(0, lambda: messagebox.showinfo("Success",
                              f"Generated {len(schedules)} optimal schedules {method_text}!\n"
                              f"The system automatically selected the best lecture, lab, and PS sections.\n"
                              f"Check the exported files for details."))
            except Exception as e:
                error_msg = f"Export failed: {str(e)}"
                self.master.after(0, lambda: self._on_scheduling_error(error_msg))

        threading.Thread(target=exporter, daemon=True).start()

    def _on_scheduling_failed(self):
        """Handle scheduling failure."""
        self.status_var.set("Scheduling failed - no valid schedules found")
        logger.warning("No valid schedules could be generated")

        auto_selection_enabled = self.preferences.should_auto_select_sections() if self.preferences else False

        if auto_selection_enabled:
            messagebox.showwarning("Scheduling Failed",
                                 "No valid schedules could be generated with automatic section selection.\n\n"
                                 "Possible solutions:\n"
                                 "• Try selecting fewer courses\n"
                                 "• Relax your time preferences\n"
                                 "• Increase the maximum ECTS limit\n"
                                 "• Allow more conflicts in settings")
        else:
            messagebox.showwarning("Scheduling Failed",
                                 "No valid schedules could be generated.\n"
                                 "Try adjusting your course selection or configuration.")

    def _on_scheduling_error(self, error_msg: str):
        """Handle scheduling errors."""
        logger.error(error_msg)
        messagebox.showerror("Scheduling Error", error_msg)
        self.status_var.set("Scheduling failed")

    def show_analytics(self):
        """Show live analytics dashboard."""
        if not self.final_schedules:
            messagebox.showwarning("No Data", "No schedules available for analytics.")
            return

        try:
            analytics_window = tk.Toplevel(self.master)
            analytics_window.title("Live Analytics Dashboard")
            analytics_window.geometry("1000x700")

            # Create analytics chart
            chart = ScheduleAnalyticsChart(analytics_window, self.final_schedules)
            chart.pack(fill="both", expand=True, padx=10, pady=10)

            logger.info("Analytics dashboard opened")

        except Exception as e:
            error_msg = f"Failed to show analytics: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Analytics Error", error_msg)

    def show_detailed_report(self):
        """Show detailed schedule report."""
        if not self.final_schedules:
            messagebox.showwarning("No Data", "No schedules available for reporting.")
            return

        try:
            report_window = tk.Toplevel(self.master)
            report_window.title("Detailed Schedule Report")
            report_window.geometry("1200x800")

            # Create detailed report
            report = DetailedScheduleReport(report_window, self.final_schedules, self.courses)
            report.pack(fill="both", expand=True, padx=10, pady=10)

            logger.info("Detailed report opened")

        except Exception as e:
            error_msg = f"Failed to show report: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Report Error", error_msg)

    def clear_cache(self):
        """Clear application cache and reset state."""
        try:
            # Clear data state
            self.courses.clear()
            self.filtered_courses = None
            self.last_filter_profile = None
            self.final_schedules.clear()

            # Clear UI components
            if hasattr(self, 'course_preview'):
                self.course_preview.clear_data()

            if hasattr(self, 'dashboard'):
                self.dashboard.clear_data()

            if hasattr(self, 'smart_assistant'):
                self.smart_assistant.clear_data()

            # Clear log
            self.log_text.delete(1.0, tk.END)

            # Reset status
            self.status_var.set("Cache cleared - Ready")
            logger.info("Application cache cleared successfully")

            messagebox.showinfo("Success", "Application cache cleared successfully.")

        except Exception as e:
            error_msg = f"Failed to clear cache: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Cache Error", error_msg)

    def load_snapshot(self):
        """Load a previously saved snapshot."""
        try:
            dialog = SnapshotLoadDialog(self.master, self.snapshot_manager)
            if dialog.result:
                courses, profile = dialog.result
                self.filtered_courses = courses
                self.last_filter_profile = profile

                # Update course preview
                self.course_preview.load_filtered_courses(courses, profile)

                # Switch to preview tab
                self.notebook.select(self.tab2)

                self.status_var.set(f"Loaded snapshot with {len(courses)} courses")
                logger.info(f"Loaded snapshot with {len(courses)} courses")

        except Exception as e:
            error_msg = f"Failed to load snapshot: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("Snapshot Error", error_msg)

    def export_current_state(self):
        """Export current application state."""
        from tkinter import filedialog
        import json

        if not self.courses:
            messagebox.showwarning("No Data", "No data to export.")
            return

        filename = filedialog.asksaveasfilename(
            title="Export Application State",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                state_data = {
                    "config": {
                        "max_ects": self.config.max_ects,
                        "allow_conflict": self.config.allow_conflict,
                        "max_results": self.config.max_results,
                        "replacement_target": self.config.replacement_target,
                        "use_simulated_annealing": self.config.use_simulated_annealing,
                        "count_optional": self.config.count_optional
                    },
                    "courses_count": len(self.courses),
                    "filtered_courses_count": len(self.filtered_courses) if self.filtered_courses else 0,
                    "schedules_count": len(self.final_schedules),
                    "export_timestamp": str(threading.current_thread().ident)
                }

                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(state_data, f, indent=2, ensure_ascii=False)

                messagebox.showinfo("Success", f"Application state exported to {filename}")
                logger.info(f"Application state exported to {filename}")

            except Exception as e:
                error_msg = f"Failed to export state: {str(e)}"
                logger.error(error_msg)
                messagebox.showerror("Export Error", error_msg)

    def on_closing(self):
        """Handle application closing."""
        try:
            # Save any pending data
            if hasattr(self, 'snapshot_manager'):
                self.snapshot_manager.close()

            logger.info("Course Scheduler application closing")
            self.master.destroy()

        except Exception as e:
            logger.error(f"Error during application shutdown: {e}")
            self.master.destroy()


def main():
    """Main entry point for the application."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('course_scheduler.log'),
            logging.StreamHandler()
        ]
    )

    # Create and run application
    root = tk.Tk()
    app = SchedulerApplication(root)

    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected application error: {e}")
    finally:
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    main()
