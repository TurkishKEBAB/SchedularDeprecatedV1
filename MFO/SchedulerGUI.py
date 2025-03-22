from sef import *


class SchedulerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Schedule Optimizer")

        self.sa_var = tk.BooleanVar(value=False)
        self.count_optional_var = tk.BooleanVar(value=False)
        self.target_var = tk.StringVar(value=DEFAULT_REPLACEMENT_TARGET)

        # Create Notebook and Tabs first
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill="both", expand=True)

        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Step 1: File & Settings")
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Step 2: Preview Courses")
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="Step 3: Select Courses")
        self.tab4 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab4, text="Step 4: Live Schedule Chart & Report")

        # Initialize tab1 widgets
        self.setup_tab1()

        # Output and control widgets in tab4
        self.output_text = tk.Text(self.tab4, height=10, width=100)
        self.output_text.pack(pady=10)

        self.clear_cache_button = ttk.Button(
            self.tab4,
            text="Clear Cached Schedules",
            command=lambda: clear_jpg_cache(".")
        )
        self.clear_cache_button.pack(pady=5)

        self.live_chart_button = ttk.Button(
            self.tab4, text="Live Schedule Chart", command=self.show_live_chart)
        self.live_chart_button.pack(pady=5)
        self.detailed_report_button = ttk.Button(
            self.tab4, text="Detailed Schedule Report", command=self.show_detailed_report)
        self.detailed_report_button.pack(pady=5)

        # Additional attributes
        self.courses = []
        self.final_schedules = None
        self.user_mandatory = None
        self.frequency_prefs = {}
        self.include_extra = True

    def setup_tab1(self):
        # Create widgets with self.tab1 as parent
        ttk.Label(self.tab1, text="Excel File:").grid(row=0, column=0, sticky="e")
        self.file_entry = ttk.Entry(self.tab1, width=50)
        self.file_entry.grid(row=0, column=1)
        ttk.Button(self.tab1, text="Browse", command=self.browse_file).grid(row=0, column=2)

        ttk.Label(self.tab1, text="Sheet Name:").grid(row=0, column=3, sticky="e")
        self.sheet_entry = ttk.Entry(self.tab1, width=20)
        self.sheet_entry.insert(0, "Sheet2")
        self.sheet_entry.grid(row=0, column=4)

        ttk.Label(self.tab1, text="MAX_ECTS:").grid(row=1, column=0, sticky="e")
        self.max_ECTS_entry = ttk.Entry(self.tab1, width=10)
        self.max_ECTS_entry.insert(0, str(DEFAULT_MAX_ECTS))
        self.max_ECTS_entry.grid(row=1, column=1, sticky="w")

        ttk.Label(self.tab1, text="ALLOW_CONFLICT:").grid(row=2, column=0, sticky="e")
        self.allow_conflict_entry = ttk.Entry(self.tab1, width=10)
        self.allow_conflict_entry.insert(0, str(DEFAULT_ALLOW_CONFLICT))
        self.allow_conflict_entry.grid(row=2, column=1, sticky="w")

        ttk.Label(self.tab1, text="MAX_RESULTS:").grid(row=3, column=0, sticky="e")
        self.max_results_entry = ttk.Entry(self.tab1, width=10)
        self.max_results_entry.insert(0, str(DEFAULT_MAX_RESULTS))
        self.max_results_entry.grid(row=3, column=1, sticky="w")

        ttk.Label(self.tab1, text="Replacement Priority (e.g., lecture,ps,lab):").grid(row=4, column=0, sticky="e")
        self.priority_entry = ttk.Entry(self.tab1, width=30)
        self.priority_entry.insert(0, DEFAULT_PRIORITY)
        self.priority_entry.grid(row=4, column=1, sticky="w")

        ttk.Label(self.tab1, text="Replacement Target:").grid(row=5, column=0, sticky="e")
        ttk.Radiobutton(self.tab1, text="Sections", variable=self.target_var, value="sections").grid(row=5, column=1,
                                                                                                     sticky="w")
        ttk.Radiobutton(self.tab1, text="Course", variable=self.target_var, value="course").grid(row=5, column=1,
                                                                                                 padx=100, sticky="w")

        ttk.Checkbutton(self.tab1, text="Use simulated annealing improvement", variable=self.sa_var).grid(row=6,
                                                                                                          column=1,
                                                                                                          pady=5)
        ttk.Checkbutton(self.tab1, text="Count optional courses in credit calculation",
                        variable=self.count_optional_var).grid(row=7, column=1, pady=5)

        ttk.Button(self.tab1, text="Load Courses", command=self.load_courses).grid(row=8, column=1, pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, file_path)

    def load_courses(self):
        excel_file = self.file_entry.get()
        sheet_name = self.sheet_entry.get().strip() or "Sheet2"
        try:
            self.courses = process_excel(excel_file, sheet_name)
        except Exception as e:
            messagebox.showerror("File Error", f"Error reading Excel file: {e}")
            return
        global CONSTRAINTS
        CONSTRAINTS = auto_generate_constraints(self.courses)
        messagebox.showinfo("Success", f"{len(self.courses)} courses loaded successfully.")
        self.setup_course_preview()
        self.notebook.select(self.tab2)

    def setup_course_preview(self):
        for widget in self.tab2.winfo_children():
            widget.destroy()
        columns = ("Code", "Lecture Name", "Credit", "Hour", "Lecture Instructor")
        tree = ttk.Treeview(self.tab2, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        for course in self.courses:
            teacher = course.get("teacher", "Default")
            schedule_str = ", ".join(f"{d}{h}" for d, h in course["schedule"])
            tree.insert("", tk.END, values=(course["code"], course["name"], course["ECTS"], schedule_str, teacher))
        tree.pack(fill="both", expand=True)
        ttk.Button(self.tab2, text="Proceed to Course Selection", command=self.open_course_selection).pack(pady=5)

    def open_course_selection(self):
        CourseSelectionWindow(self.master, self.courses, self.on_course_selection)
        self.notebook.select(self.tab3)

    def on_course_selection(self, selected_courses, include_extra, freq_prefs):
        self.user_mandatory = set(selected_courses)
        self.include_extra = include_extra
        self.frequency_prefs = freq_prefs
        self.log(f"User selected mandatory courses: {', '.join(self.user_mandatory)}")
        self.log(f"Frequency preferences: {self.frequency_prefs}")
        self.log(f"Include extra courses: {self.include_extra}")
        self.run_scheduler()
        self.notebook.select(self.tab4)

    def run_scheduler(self):
        global MAX_ECTS, ALLOW_CONFLICT, MAX_RESULTS
        self.log("Starting scheduling process...")
        try:
            max_ECTS = int(self.max_ECTS_entry.get())
            allow_conflict = int(self.allow_conflict_entry.get())
            max_results = int(self.max_results_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values.")
            return
        MAX_ECTS = max_ECTS
        ALLOW_CONFLICT = allow_conflict
        MAX_RESULTS = max_results

        priority_input = self.priority_entry.get().strip()
        priority_order = [p.strip().lower() for p in priority_input.split(",") if p.strip()] or ["lecture", "ps", "lab"]
        self.log(f"Replacement priority order: {priority_order}")

        replacement_target = self.target_var.get().lower()
        self.log(f"Replacement target set to: {replacement_target}")

        self.log("Reading Excel data...")
        try:
            courses = process_excel(self.file_entry.get(), self.sheet_entry.get().strip() or "Sheet2")
        except Exception as e:
            messagebox.showerror("File Error", f"Error reading Excel file: {e}")
            return
        self.log(f"{len(courses)} courses read from file.")
        course_groups = build_course_groups(courses)
        global USER_MANDATORY_CODES
        USER_MANDATORY_CODES = self.user_mandatory
        group_valid_selections, group_options = build_group_options(course_groups, replacement_target)

        missing = [code for code in USER_MANDATORY_CODES if not group_valid_selections.get(code)]
        if missing:
            details = "\n".join(analyze_schedule_failure(group_valid_selections, USER_MANDATORY_CODES))
            messagebox.showerror("Mandatory Course Error", f"Problems found:\n{details}")
            return

        mandatory_keys = sorted([k for k in group_options.keys() if k in USER_MANDATORY_CODES],
                                key=lambda k: self.frequency_prefs.get(k, 3), reverse=True)
        optional_keys = sorted([k for k in group_options.keys() if k not in USER_MANDATORY_CODES],
                               key=lambda k: len(group_options[k]))
        sorted_group_keys = mandatory_keys + optional_keys

        max_credit_per_group = {}
        for key in group_options:
            max_credit = 0
            for option in group_options[key]:
                if option:
                    opt_total = sum(
                        get_effective_credit(course, self.frequency_prefs, self.count_optional_var.get()) for course in
                        option)
                    max_credit = max(max_credit, opt_total)
            max_credit_per_group[key] = max_credit
        max_remaining = [0] * (len(sorted_group_keys) + 1)
        for i in range(len(sorted_group_keys) - 1, -1, -1):
            key = sorted_group_keys[i]
            max_remaining[i] = max_credit_per_group[key] + max_remaining[i + 1]

        if not self.include_extra:
            total_mandatory = 0
            seen = set()
            for course in courses:
                if course["type"] == "lecture" and course["main_code"] in self.user_mandatory and course[
                    "main_code"] not in seen:
                    total_mandatory += course["ECTS"]
                    seen.add(course["main_code"])
            self.log(f"Extra courses not included; setting MAX_ECTS to {total_mandatory}")
            MAX_ECTS = total_mandatory

        self.log("Running DFS scheduling in background...")
        progress_win = tk.Toplevel(self.master)
        progress_win.title("Scheduling in Progress")
        pb = ttk.Progressbar(progress_win, mode="indeterminate", length=300)
        pb.pack(padx=20, pady=20)
        pb.start(10)

        def run_dfs():
            dfs_results = []
            strict_results = dfs_strict(sorted_group_keys, 0, [], 0, group_options, max_remaining, self.user_mandatory,
                                        self.frequency_prefs, self.count_optional_var.get())
            strict_results = [(ct, sched) for ct, sched in strict_results if ct == MAX_ECTS]
            if strict_results:
                chosen_schedule = strict_results[0][1]
            else:
                dfs_results = dfs_relaxed(sorted_group_keys, 0, [], 0, group_options, max_remaining,
                                          self.user_mandatory, self.frequency_prefs, self.count_optional_var.get())
                if dfs_results and any(ct == MAX_ECTS for ct, sched in dfs_results):
                    relaxed_results = [(ct, sched) for ct, sched in dfs_results if ct == MAX_ECTS]
                else:
                    max_total = max((ct for ct, sched in dfs_results), default=0)
                    relaxed_results = [(ct, sched) for ct, sched in dfs_results if ct == max_total]
                chosen_schedule = (relaxed_results[0][1] if relaxed_results else [])
            all_results = strict_results + dfs_results
            unique_results = deduplicate_schedules(all_results)
            final_schedules = [sched for ct, sched in unique_results][:MAX_RESULTS]

            if not final_schedules:
                self.log("No valid schedule found.")
                pb.stop()
                progress_win.destroy()
                return

            self.log(f"Final schedules generated: {len(final_schedules)} found.")
            sample = final_schedules[0]
            self.log(
                f"Example: Total credits: {sum(c['ECTS'] for c in sample)}, Conflict Cost: {conflict_cost(sample)}")

            if replacement_target == "sections":
                self.log("Applying local repair (sections)...")
                for idx, sched in enumerate(final_schedules):
                    repaired = repair_schedule_with_priority(sched, group_valid_selections, priority_order)
                    final_schedules[idx] = repaired
            elif replacement_target == "course":
                self.log("Applying global repair (course replacement)...")
                for idx, sched in enumerate(final_schedules):
                    repaired = global_repair_schedule(sched, courses)
                    final_schedules[idx] = repaired

            if self.sa_var.get():
                self.log("Applying simulated annealing improvement on the best schedule...")
                best_schedule = final_schedules[0]
                best_total = sum(c["ECTS"] for c in best_schedule)
                sa_schedule, sa_total, sa_conflict = simulated_annealing_schedule_sa(
                    sorted_group_keys, group_options, best_schedule, best_total
                )
                final_schedules[0] = sa_schedule
                self.log(f"Simulated annealing improved schedule: Credits {sa_total}, Conflict Cost {sa_conflict}")

            report_lines = []
            for sched in final_schedules:
                cost = conflict_cost(sched)
                report_lines.append(f"Schedule with {sum(c['ECTS'] for c in sched)} credits: Conflict Cost = {cost}")
            report_text = "\n".join(report_lines)
            with open("conflict_report.txt", "w", encoding="utf-8") as f:
                f.write(report_text)
            self.log("Conflict report saved as conflict_report.txt.")

            for idx, sched in enumerate(final_schedules, start=1):
                sel_courses = sorted(set(c["code"] for c in sched))
                unique_courses = compute_unique_courses(sched, final_schedules)
                note = "Selected courses: " + ", ".join(sel_courses) + "\n"
                note += "Unique courses: " + (", ".join(sorted(unique_courses)) if unique_courses else "None")
                save_schedule_grid_as_jpeg(sched, filename=f"program{idx}.jpg", note_text=note)
            save_all_selection_matrices_to_pdf(final_schedules, self.courses)
            self.final_schedules = final_schedules
            pb.stop()
            progress_win.destroy()
            self.log("All schedule JPEG files have been created.")
            messagebox.showinfo("Success", "Scheduling completed successfully!")
            self.log("You can now click 'Show Summary Chart' to view an interactive chart of the schedules.")

        t = threading.Thread(target=run_dfs)
        t.start()

    # Legacy function maintained but not used elsewhere
    def show_chart(self):
        # This legacy method is now replaced by live schedule chart functionality.
        self.show_live_chart()

    def log(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)

    def show_live_chart(self):
        live_chart_win = tk.Toplevel(self.master)
        live_chart_win.title("Live Schedule Chart")
        # Pass self so LiveChart can access final_schedules
        ScheduleAnalyticsChart(live_chart_win, self)

    def show_detailed_report(self):
        if not self.final_schedules:
            messagebox.showwarning("Report Warning", "No schedules available. Please run the scheduler first.")
            return
        DetailedScheduleReport(self.master, self.final_schedules)


# =============================================================================
# Additional: Show Summary Chart (Interactive)
# =============================================================================
def show_summary_chart(final_schedules):
    schedule_nums = list(range(1, len(final_schedules) + 1))
    total_list = [sum(c["ECTS"] for c in sched) for sched in final_schedules]
    conflicts = [conflict_cost(sched) for sched in final_schedules]
    width = 0.35
    fig, ax = plt.subplots()
    ax.bar([x - width / 2 for x in schedule_nums], total_list, width, label="Total Credits")
    ax.bar([x + width / 2 for x in schedule_nums], conflicts, width, label="Conflict Cost")
    ax.set_xlabel("Schedule Number")
    ax.set_ylabel("Value")
    ax.set_title("Schedule Summary")
    ax.set_xticks(schedule_nums)
    ax.legend()
    plt.show()


# =============================================================================
# Class Live Chart
# =============================================================================
class ScheduleAnalyticsChart:
    """Displays real-time analytics of course schedules using matplotlib."""

    CHART_UPDATE_INTERVAL_MS = 2000
    CHART_DIMENSIONS = (6, 4)
    BAR_WIDTH = 0.35

    def __init__(self, master_window, scheduler_gui):
        """Initialize the analytics chart.

        Args:
            master_window: Parent tkinter window
            scheduler_gui: Reference to main scheduler GUI
        """
        self.master_window = master_window
        self.scheduler_gui = scheduler_gui

        # Initialize matplotlib figure and canvas
        self.figure, self.axes = plt.subplots(figsize=self.CHART_DIMENSIONS)
        self.canvas = FigureCanvasTkAgg(self.figure, master=master_window)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Start real-time updates
        self.refresh_chart()

    def refresh_chart(self):
        """Update chart with latest schedule data."""
        self.axes.clear()
        self._plot_schedule_data()
        self.canvas.draw()
        self.master_window.after(self.CHART_UPDATE_INTERVAL_MS, self.refresh_chart)

    def _plot_schedule_data(self):
        """Plot schedule analytics if data is available."""
        schedules = self.scheduler_gui.final_schedules
        if not schedules:
            return

        schedule_indices = list(range(1, len(schedules) + 1))
        credit_totals = [self._calculate_total_credits(schedule) for schedule in schedules]
        conflict_counts = [conflict_cost(schedule) for schedule in schedules]

        # Plot credit totals and conflicts as grouped bars
        self._create_grouped_bars(schedule_indices, credit_totals, conflict_counts)
        self._set_chart_labels()

    def _calculate_total_credits(self, schedule):
        """Calculate total ECTS credits for a schedule."""
        return sum(course["ECTS"] for course in schedule)

    def _create_grouped_bars(self, indices, credits, conflicts):
        """Create grouped bar chart showing credits and conflicts."""
        offset = self.BAR_WIDTH / 2
        self.axes.bar([x - offset for x in indices], credits,
                      self.BAR_WIDTH, label="Total Credits")
        self.axes.bar([x + offset for x in indices], conflicts,
                      self.BAR_WIDTH, label="Conflict Count")

    def _set_chart_labels(self):
        """Set chart title, labels and legend."""
        self.axes.set_xlabel("Schedule Number")
        self.axes.set_ylabel("Value")
        self.axes.legend()
