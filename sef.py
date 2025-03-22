import math
import os
import random
import shutil
import threading
import tkinter as tk
from collections import defaultdict
from tkinter import ttk, filedialog, messagebox
import urllib.request
import io
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import matplotlib.pyplot as plt
import pandas as pd
from tabulate import tabulate

# =============================================================================
# Global Defaults and Settings
# =============================================================================

DEFAULT_MAX_ECTS = 31
DEFAULT_ALLOW_CONFLICT = 1
DEFAULT_MAX_RESULTS = 5
DEFAULT_PRIORITY = "lecture,ps,lab"
DEFAULT_REPLACEMENT_TARGET = "sections"  # or "course"

# Global parameters (updated via GUI)
MAX_ECTS = DEFAULT_MAX_ECTS
ALLOW_CONFLICT = DEFAULT_ALLOW_CONFLICT
MAX_RESULTS = DEFAULT_MAX_RESULTS

# Global user preferences
USER_PREFERENCES = {
    "preferred_courses": [],  # Mandatory lecture courses (main codes)
    "include_extra": True,  # Whether extra courses may be added
}
USER_MANDATORY_CODES = set()  # To be set from the course selection window
FREQUENCY_PREFS = {}  # Frequency preferences (0: Never, 1: Rarely, 2: Often, 3: Always)

# =============================================================================
# Static Constraints – Auto-generated from Excel data.
# =============================================================================
CONSTRAINTS = {"DEFAULT": {"must_ps": False, "must_lab": False}}


def auto_generate_constraints(courses):
    groups = defaultdict(list)
    for course in courses:
        groups[course["main_code"]].append(course)
    constraints = {}
    for main_code, group in groups.items():
        constraints[main_code] = {
            "must_ps": any(c["type"] == "ps" for c in group),
            "must_lab": any(c["type"] == "lab" for c in group)
        }
    return constraints


# =============================================================================
# Helper: Effective Credit Calculation
# =============================================================================
def get_effective_credit(course, freq_prefs, count_optional):
    """
    Returns the effective credit of a course based on its frequency.
    If the course’s frequency (from freq_prefs, keyed by its main code) is less than 3
    (i.e. not "always") and count_optional is False, return 0.
    Otherwise, return the course's actual credit.
    """
    freq = freq_prefs.get(course["main_code"], 3)
    if freq < 3 and not count_optional:
        return 0
    return course["ECTS"]


# =============================================================================
# Parsing Functions
# =============================================================================
def foundation_main_code(code):
    code = str(code).strip()
    if "-PS" in code:
        return code.split("-PS")[0]
    elif "-L" in code:
        return code.split("-L")[0]
    elif "." in code:
        return code.split(".")[0]
    else:
        return code


def foundation_tour(code):
    # "Th" stands for Thursday.
    if "-PS" in code:
        return "ps"
    elif "-L" in code:
        return "lab"
    else:
        return "lecture"


def parse_schedule(schedule_str):
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


# =============================================================================
# Excel Data Processing (with Teacher Column)
# =============================================================================
# noinspection PyBroadException
def process_excel(file_path, sheet_name):
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        if "Code" not in df.columns:
            raise ValueError("Expected column 'Code' not found.")
    except Exception:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        if df.shape[1] == 5:
            df.columns = ["Code", "Lecture Name", "Credit", "Hour", "Lecture Instructor"]
        else:
            df.columns = ["Code", "Lecture Name", "Credit", "Hour"]
    teacher_col = "Lecture Instructor" if "Lecture Instructor" in df.columns else None
    courses = []
    for _, row in df.iterrows():
        code = str(row["Code"]).strip()
        course_name = str(row["Lecture Name"]).strip()
        credit = int(row["Credit"])
        schedule_str = row["Hour"]
        main_code = foundation_main_code(code)
        tour = foundation_tour(code)
        schedule_list = parse_schedule(schedule_str)
        has_lecture = True if tour == "lecture" else False
        teacher = str(row[teacher_col]).strip() if teacher_col else "Default"
        courses.append({
            "code": code,
            "main_code": main_code,
            "name": course_name,
            "ECTS": credit,
            "type": tour,
            "schedule": schedule_list,
            "hasLecture": has_lecture,
            "teacher": teacher
        })
    return courses


# =============================================================================
# Grouping and Option Generation
# =============================================================================
def build_course_groups(courses):
    groups = defaultdict(list)
    for course in courses:
        groups[course["main_code"]].append(course)
    return groups


def generate_valid_group_selections(course_group):
    lectures = [c for c in course_group if c["hasLecture"]]
    if not lectures:
        return []
    ps_sections = [c for c in course_group if c["type"] == "ps"]
    lab_sections = [c for c in course_group if c["type"] == "lab"]
    valid_selections = []
    for lec in lectures:
        base_selection = [lec]
        constraint = CONSTRAINTS.get(lec["main_code"], {"must_ps": False, "must_lab": False})
        must_ps = constraint.get("must_ps", False)
        must_lab = constraint.get("must_lab", False)
        ps_options = ps_sections if must_ps else [None] + ps_sections
        lab_options = lab_sections if must_lab else [None] + lab_sections
        if must_ps and not ps_sections:
            continue
        if must_lab and not lab_sections:
            continue
        for ps in ps_options:
            for lab in lab_options:
                sel = base_selection.copy()
                if ps is not None:
                    sel.append(ps)
                if lab is not None:
                    sel.append(lab)
                valid_selections.append(sel)
    return valid_selections


def build_group_options(course_groups, replacement_target):
    group_valid_selections = {}
    group_options = {}
    for main_code, group in course_groups.items():
        selections = generate_valid_group_selections(group)
        group_valid_selections[main_code] = selections
        if main_code in USER_MANDATORY_CODES:
            group_options[main_code] = selections
        else:
            group_options[main_code] = [None] + (selections if selections else [])
        # If replacement target is "course", restrict to the first valid option.
        if replacement_target == "course":
            if group_options[main_code] and group_options[main_code][0] is not None:
                group_options[main_code] = [group_options[main_code][0]]
    return group_valid_selections, group_options


# =============================================================================
# Conflict Calculation
# =============================================================================
def conflict_cost(schedule):
    slot_counts = {}
    for course in schedule:
        for slot in course["schedule"]:
            slot_counts[slot] = slot_counts.get(slot, 0) + 1
    return sum(max(0, count - 1) for count in slot_counts.values())


def no_conflict(existing_schedule, new_courses):
    occupied = set()
    for course in existing_schedule:
        for slot in course["schedule"]:
            occupied.add(slot)
    for course in new_courses:
        for slot in course["schedule"]:
            if slot in occupied:
                return False
    return True


# =============================================================================
# DFS Scheduling Functions (with frequency parameters)
# =============================================================================
def dfs_strict(keys, index, current_schedule, current_total, group_options, max_remaining, mandatory_set, freq_prefs,
               count_optional):
    if index == len(keys):
        if all(m in {c["main_code"] for c in current_schedule} for m in mandatory_set):
            return [(current_total, list(current_schedule))]
        return []
    results = []
    current_key = keys[index]
    for option in group_options[current_key]:
        if option is None:
            if current_key not in mandatory_set:
                results.extend(
                    dfs_strict(keys, index + 1, current_schedule, current_total, group_options, max_remaining,
                               mandatory_set, freq_prefs, count_optional))
            continue
        if not no_conflict(current_schedule, option):
            continue
        option_total = sum(get_effective_credit(course, freq_prefs, count_optional) for course in option)
        new_total = current_total + option_total
        if new_total > MAX_ECTS:
            continue
        results.extend(dfs_strict(keys, index + 1, current_schedule + option, new_total, group_options, max_remaining,
                                  mandatory_set, freq_prefs, count_optional))
    return results


def dfs_relaxed(keys, index, current_schedule, current_total, group_options, max_remaining, mandatory_set, freq_prefs,
                count_optional):
    if current_total + max_remaining[index] < MAX_ECTS:
        return []
    if index == len(keys):
        if all(m in {c["main_code"] for c in current_schedule} for m in mandatory_set):
            return [(current_total, list(current_schedule))]
        return []
    results = []
    current_key = keys[index]
    for option in group_options[current_key]:
        if option is None:
            results.extend(dfs_relaxed(keys, index + 1, current_schedule, current_total, group_options, max_remaining,
                                       mandatory_set, freq_prefs, count_optional))
        else:
            option_total = sum(get_effective_credit(course, freq_prefs, count_optional) for course in option)
            new_total = current_total + option_total
            if new_total > MAX_ECTS:
                continue
            if conflict_cost(current_schedule + option) > ALLOW_CONFLICT:
                continue
            results.extend(
                dfs_relaxed(keys, index + 1, current_schedule + option, new_total, group_options, max_remaining,
                            mandatory_set, freq_prefs, count_optional))
    return results


# =============================================================================
# Deduplication
# =============================================================================
def deduplicate_schedules(schedule_tuples):
    unique = []
    seen = set()
    for total, sched in schedule_tuples:
        codes_tuple = tuple(sorted(c["code"] for c in sched))
        if codes_tuple not in seen:
            seen.add(codes_tuple)
            unique.append((total, sched))
    unique.sort(key=lambda x: x[0], reverse=True)
    return unique


# =============================================================================
# Repair Functions
# =============================================================================
def repair_schedule_with_priority(schedule, group_valid_selections, priority_order):
    current = {}
    for course in schedule:
        current.setdefault(course["main_code"], []).append(course)
    best_schedule = schedule
    best_cost = conflict_cost(schedule)
    improved = True
    iteration = 0
    max_iter = 10
    while improved and iteration < max_iter:
        improved = False
        for p_type in priority_order:
            for group in list(current.keys()):
                current_selection = current[group]
                if not any(course["type"] == p_type for course in current_selection):
                    continue
                alternatives = group_valid_selections.get(group, [])
                for alternative in alternatives:
                    alt_has_priority = any(course["type"] == p_type for course in alternative)
                    cur_has_priority = any(course["type"] == p_type for course in current_selection)
                    if alt_has_priority == cur_has_priority:
                        continue
                    new_schedule = []
                    for g in current:
                        if g == group:
                            new_schedule.extend(alternative)
                        else:
                            new_schedule.extend(current[g])
                    new_cost = conflict_cost(new_schedule)
                    if new_cost < best_cost:
                        best_cost = new_cost
                        best_schedule = new_schedule
                        current[group] = alternative
                        improved = True
        iteration += 1
    return best_schedule


def global_repair_schedule(schedule, courses):
    best_schedule = schedule
    best_cost = conflict_cost(schedule)
    for i in range(len(schedule)):
        candidate_removed = schedule[:i] + schedule[i + 1:]
        for course in courses:
            if course["code"] in [c["code"] for c in candidate_removed]:
                continue
            if no_conflict(candidate_removed, [course]):
                new_schedule = candidate_removed + [course]
                new_cost = conflict_cost(new_schedule)
                if new_cost < best_cost:
                    best_cost = new_cost
                    best_schedule = new_schedule
    return best_schedule


# =============================================================================
# Detailed Schedule Failure Analysis
# =============================================================================
def analyze_schedule_failure(group_valid_selections, mandatory_set):
    reasons = []
    for code in mandatory_set:
        if not group_valid_selections.get(code):
            reasons.append(f"{code}: No valid sections available (missing lecture, PS, or lab).")
        else:
            reasons.append(f"{code}: Check for conflicts in available sections.")
    return reasons


# =============================================================================
# Schedule Grid Generation and JPEG Output
# =============================================================================
def get_schedule_grid_data(schedule):
    days = ["M", "T", "W", "Th", "F", "Sa", "Su"]
    period_times = {
        1: "08:30-09:20",
        2: "09:30-10:20",
        3: "10:30-11:20",
        4: "11:30-12:20",
        5: "12:30-13:20",
        6: "13:30-14:20",
        7: "14:30-15:20",
        8: "15:30-16:20",
        9: "16:30-17:20",
        10: "17:30-18:20",
        11: "18:30-19:20",
        12: "19:30-20:20"
    }
    grid = []
    header = ["Time"] + days
    grid.append(header)
    for period in range(1, 13):
        row = [period_times.get(period, str(period))]
        row.extend([""] * len(days))
        grid.append(row)
    for course in schedule:
        display_str = course["code"]
        for (day, period) in course["schedule"]:
            if day in days and 1 <= period <= 12:
                row_index = period
                col_index = header.index(day)
                if grid[row_index][col_index]:
                    grid[row_index][col_index] += "\n" + display_str
                else:
                    grid[row_index][col_index] = display_str
    return grid


def save_schedule_grid_as_jpeg(schedule, filename="schedule.jpg", note_text=""):
    grid_data = get_schedule_grid_data(schedule)
    col_labels = grid_data[0]
    data_rows = grid_data[1:]
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis("tight")
    ax.axis("off")
    table = ax.table(cellText=data_rows, colLabels=col_labels, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    plt.title("Program Schedule", fontsize=14)
    if note_text:
        plt.figtext(0.5, 0.01, note_text, wrap=True, horizontalalignment="center", fontsize=10)
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Schedule JPEG saved as: {filename}")


def display_schedule_grid_terminal(schedule):
    grid_data = get_schedule_grid_data(schedule)
    headers = grid_data[0]
    data_rows = grid_data[1:]
    table_str = tabulate(data_rows, headers=headers, tablefmt="fancy_grid")
    print("Search:")
    print(table_str)


# =============================================================================
# NEW: Selection Matrix Generation and JPEG Output (for each schedule)
# =============================================================================

from matplotlib.backends.backend_pdf import PdfPages


def save_all_selection_matrices_to_pdf(final_schedules, all_courses, pdf_filename="final_selection_matrices.pdf"):
    """
    Generates a PDF file where each page shows:
      1. A selection matrix of all available lecture courses (ignoring PS/lab),
         with those included in the final schedule highlighted in light green.
      2. Below that, the corresponding course schedule grid.
    """
    # If the PDF file already exists, try to remove it.
    if os.path.exists(pdf_filename):
        try:
            os.remove(pdf_filename)
        except Exception as e:
            messagebox.showerror("File Error", f"Unable to remove existing file '{pdf_filename}': {e}\n"
                                               "Please close the file or choose a different file name.")
            return

    # Build a dictionary of all unique lecture courses from all_courses.
    lecture_courses = {}
    for course in all_courses:
        if course["type"] == "lecture":
            lecture_courses[course["main_code"]] = f"{course['code']} {course['name']} ({course['ECTS']})"
    sorted_courses = sorted(lecture_courses.items(), key=lambda x: x[0])
    num_courses = len(sorted_courses)
    # Set fixed number of columns for the selection matrix.
    cols = 5
    rows = math.ceil(num_courses / cols)

    # Create a PDF file with one page per final schedule.
    with PdfPages(pdf_filename) as pdf:
        for idx, final_schedule in enumerate(final_schedules, start=1):
            # Create a figure with two subplots (vertical layout)
            fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(12, 12))
            fig.subplots_adjust(hspace=0.5)

            # --- Top subplot: Selection Matrix ---
            # Build the cell-text for the selection matrix.
            cell_text_sel = []
            for i in range(rows):
                row_text = []
                for j in range(cols):
                    cell_index = i * cols + j
                    if cell_index < num_courses:
                        row_text.append(sorted_courses[cell_index][1])
                    else:
                        row_text.append("")
                cell_text_sel.append(row_text)
            # Determine which lecture course groups are selected in this schedule.
            selected_courses = {course["main_code"] for course in final_schedule if course["type"] == "lecture"}

            ax_sel = axs[0]
            ax_sel.axis("tight")
            ax_sel.axis("off")
            table_sel = ax_sel.table(cellText=cell_text_sel, loc="center", cellLoc="center")
            # Highlight cells corresponding to selected courses.
            for i in range(rows):
                for j in range(cols):
                    cell_index = i * cols + j
                    if cell_index < num_courses:
                        course_code = sorted_courses[cell_index][0]
                        cell = table_sel[(i, j)]
                        if course_code in selected_courses:
                            cell.set_facecolor("lightgreen")
            ax_sel.set_title(f"Selection Matrix for Program {idx}", fontsize=14)

            # --- Bottom subplot: Course Schedule Grid ---
            grid_data = get_schedule_grid_data(final_schedule)
            # grid_data[0] is the header; grid_data[1:] are the data rows.
            ax_sched = axs[1]
            ax_sched.axis("tight")
            ax_sched.axis("off")
            table_sched = ax_sched.table(cellText=grid_data[1:], colLabels=grid_data[0],
                                         loc="center", cellLoc="center")
            ax_sched.set_title(f"Course Schedule for Program {idx}", fontsize=14)

            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    print(f"Selection matrices and schedules saved to PDF: {pdf_filename}")


# =============================================================================
# Simulated Annealing Optimization (Optional Improvement)
# =============================================================================
def simulated_annealing_schedule_sa(sorted_group_keys, group_options, initial_schedule, initial_total,
                                    temp0=100.0, alpha=0.95, iterations=1000):
    current_schedule = initial_schedule
    current_total = initial_total

    def fitness(schedule, total):
        return (MAX_ECTS - total) ** 2 + conflict_cost(schedule) * 100

    current_fitness = fitness(current_schedule, current_total)
    best_schedule = current_schedule
    best_fitness = current_fitness
    T = temp0
    for _ in range(iterations):
        group = random.choice(sorted_group_keys)
        valid_options = group_options[group]
        if len(valid_options) <= 1:
            continue
        new_schedule = [c for c in current_schedule if c["main_code"] != group]
        new_option = random.choice([opt for opt in valid_options if opt is not None])
        new_schedule.extend(new_option)
        new_total = sum(c["ECTS"] for c in new_schedule)
        new_fitness = fitness(new_schedule, new_total)
        delta = new_fitness - current_fitness
        if delta < 0 or random.random() < math.exp(-delta / T):
            current_schedule = new_schedule
            current_total = new_total
            current_fitness = new_fitness
            if current_fitness < best_fitness:
                best_schedule = current_schedule
                best_fitness = current_fitness
        T *= alpha
        if T < 1e-3:
            break
    return best_schedule, sum(c["ECTS"] for c in best_schedule), conflict_cost(best_schedule)


# =============================================================================
# Unique Courses Annotation
# =============================================================================
def compute_unique_courses(schedule, all_schedules):
    all_sets = [set(c["code"] for c in sched) for sched in all_schedules]
    if not all_sets:
        return set()
    common = set.intersection(*all_sets)
    current = set(c["code"] for c in schedule)
    return current - common


# =============================================================================
# Cache Clearing Function
# =============================================================================
def clear_jpg_cache(cache_dir="."):
    response = messagebox.askyesno("Clear Cache", "Move JPG files to Desktop before clearing?")
    if response:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        for file in os.listdir(cache_dir):
            if file.lower().endswith(".jpg"):
                shutil.move(os.path.join(cache_dir, file), os.path.join(desktop, file))
        messagebox.showinfo("Cache Cleared", "JPG files moved to Desktop.")
    else:
        for file in os.listdir(cache_dir):
            if file.lower().endswith(".jpg"):
                os.remove(os.path.join(cache_dir, file))
        messagebox.showinfo("Cache Cleared", "JPG files deleted.")


# =============================================================================
# Course Selection Window (Tri-State for Each Course)
# =============================================================================
class CourseSelectionWindow:
    # noinspection PyTypeChecker
    def __init__(self, master, courses, callback):
        self.top = tk.Toplevel(master)
        self.top.title("Select Mandatory Courses")
        self.callback = callback
        self.state_vars = {}
        self.fixed_sections = {}

        self.course_groups = build_course_groups(courses)
        self.valid_counts = {}
        for code, group in self.course_groups.items():
            if any(c["hasLecture"] for c in group):
                self.valid_counts[code] = len(group)
            else:
                self.valid_counts[code] = 0

        lecture_courses = {}
        for course in courses:
            if course["type"] == "lecture":
                lecture_courses[course["main_code"]] = f"{course['code']} {course['name']} ({course['ECTS']})"

        teacher_options = defaultdict(set)
        for course in courses:
            if course["type"] == "lecture":
                teacher_options[course["main_code"]].add(course["teacher"])
        for code in teacher_options:
            teacher_options[code] = sorted(list(teacher_options[code]))

        self.teacher_vars = {}

        tk.Label(self.top,
                 text="Select lecture courses to include (click to toggle: Neutral → Include → Exclude):").pack(
            anchor="w")
        self.comb_label = tk.Label(self.top, text="Total possible combinations: 0")
        self.comb_label.pack(anchor="w", pady=2)

        # Create a frame to hold the canvas and scrollbar
        container = tk.Frame(self.top)
        container.pack(fill="both", expand=True)

        # Create a canvas widget
        canvas = tk.Canvas(container)
        canvas.pack(side="left", fill="both", expand=True)

        # Add a scrollbar to the canvas
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the canvas to use the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create a frame inside the canvas
        self.selection_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.selection_frame, anchor="nw")

        for code, info in sorted(lecture_courses.items()):
            frame = tk.Frame(self.selection_frame)
            frame.pack(fill="x", anchor="w", pady=2)
            state_var = tk.IntVar(value=0)
            self.state_vars[code] = state_var
            btn = tk.Button(frame, text=f"{code} - {info}", width=40,
                            command=lambda c=code, b=frame: self.cycle_state(c, b))
            btn.pack(side="left")
            frame.button = btn

            tk.Label(frame, text="Teacher:").pack(side="left", padx=5)
            teacher_var = tk.StringVar()
            self.teacher_vars[code] = teacher_var
            opts = teacher_options.get(code, ["Default"])
            cb = ttk.Combobox(frame, textvariable=teacher_var, values=opts, state="readonly", width=10)
            cb.set(opts[0])
            cb.pack(side="left", padx=5)

            freq_frame = tk.Frame(frame)
            freq_frame.pack(side="left", padx=5)
            tk.Label(freq_frame, text="Frequency:").pack(side="left")
            freq_var = tk.IntVar(value=2)
            freq_frame.freq_var = freq_var
            for val, text in [(0, "Never"), (1, "Rarely"), (2, "Often"), (3, "Always")]:
                tk.Radiobutton(freq_frame, text=text, variable=freq_var, value=val).pack(side="left")
            frame.freq_var = freq_var

            fix_btn = ttk.Button(frame, text="Fix Section", command=lambda c=code: self.fix_section(c))
            fix_btn.pack(side="left", padx=5)

        clear_btn = ttk.Button(self.top, text="Clear Selections", command=self.clear_selections)
        clear_btn.pack(anchor="w", pady=5)
        self.extra_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.top, text="Include extra courses", variable=self.extra_var).pack(anchor="w", pady=5)

        # Adjust the OK button to be at the bottom and always visible
        self.ok_button = tk.Button(self.top, text="OK", command=self.on_ok)
        self.ok_button.pack(side="bottom", pady=5)

    def cycle_state(self, code, frame):
        current = self.state_vars[code].get()
        new_state = (current + 1) % 3
        self.state_vars[code].set(new_state)
        if new_state == 0:
            frame.button.config(bg="SystemButtonFace")
        elif new_state == 1:
            frame.button.config(bg="lightgreen")
        elif new_state == 2:
            frame.button.config(bg="tomato")
        self.update_combination_count()

    def update_combination_count(self):
        comb = 1
        for code, state_var in self.state_vars.items():
            state = state_var.get()
            if state == 1:
                comb *= self.valid_counts.get(code, 1)
        self.comb_label.config(text=f"Total possible combinations: {comb}")

    @staticmethod
    def fix_section(code):
        messagebox.showinfo("Fix Section", f"Section for {code} fixed (stub).")

    def clear_selections(self):
        for code, state_var in self.state_vars.items():
            state_var.set(0)
        self.update_combination_count()

    def on_ok(self):
        selected = []
        freq_prefs = {}
        for code, state_var in self.state_vars.items():
            state = state_var.get()
            if state == 1:
                selected.append(code)
            elif state == 2:
                freq_prefs[code] = 0
        total_credits = 0
        for code in selected:
            group = self.course_groups.get(code, [])
            lecture = next((c for c in group if c["type"] == "lecture"), None)
            if lecture:
                total_credits += lecture["ECTS"]
        if total_credits > DEFAULT_MAX_ECTS:
            messagebox.showerror("Credit Error",
                                 f"Total selected credits ({total_credits}) exceed the maximum allowed ({DEFAULT_MAX_ECTS}).\nPlease reselect courses.")
            return
        self.top.destroy()
        self.callback(selected, self.extra_var.get(), freq_prefs)


# noinspection PyTypeChecker
def show_splash(splash_root, duration=4000):
    icon_url = "https://www.isikun.edu.tr/themes/custom/isikun/img/default.jpg"
    try:
        with urllib.request.urlopen(icon_url) as u:
            raw_data = u.read()
        image = Image.open(io.BytesIO(raw_data))
    except Exception as e:
        print("Splash ekranı için ikon yüklenemedi:", e)
        return

    splash_image = ImageTk.PhotoImage(image)
    # Splash ekranı için yeni bir pencere oluşturuyoruz
    splash = tk.Toplevel(splash_root)
    splash.overrideredirect(True)  # Pencere kenarlıklarını kaldırır
    splash.attributes("-topmost", True)  # Her zaman en üstte olsun

    # İkonu bir label içerisine yerleştiriyoruz
    label = tk.Label(splash, image=splash_image)
    label.image = splash_image  # Garbage collector'dan korunması için referansı saklıyoruz
    label.pack()

    # Splash ekranını ekranın ortasına yerleştirme
    splash.update_idletasks()
    width = splash.winfo_width()
    height = splash.winfo_height()
    x = (splash.winfo_screenwidth() // 2) - (width // 2)
    y = (splash.winfo_screenheight() // 2) - (height // 2)
    splash.geometry(f"{width}x{height}+{x}+{y}")

    # Belirtilen süre sonra splash ekranını kapatıp ana pencereyi açacak fonksiyon
    def close_splash():
        splash.destroy()
        splash_root.deiconify()  # Ana pencereyi görünür yap

    # duration (milisaniye) sonra splash ekranını kapat
    splash.after(duration, close_splash)


# =============================================================================
# Main GUI – SchedulerGUI
# =============================================================================

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


# =============================================================================
class DetailedScheduleReport:
    """Displays a detailed visual report of course schedules with navigation and interaction."""

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    HOURS = range(1, 13)  # 8:30 AM to 8:20 PM
    CELL_DIMENSIONS = {"width": 100, "height": 50}
    COURSE_COLORS = {
        "lecture": "#FFE5E5",  # Light red
        "ps": "#E5FFE5",  # Light green
        "lab": "#E5E5FF"  # Light blue
    }

    def __init__(self, master, schedules):
        """Initialize the detailed schedule report window."""
        self.schedules = schedules
        self.current_index = 0
        self.setup_window(master)
        self.create_navigation()
        self.create_grid_container()
        self.info_panel = CourseInfoPanel(self.main_container)
        self.render_schedule()

    def setup_window(self, master):
        """Set up the main window and container."""
        self.window = tk.Toplevel(master)
        self.window.title("Detailed Schedule Report")
        self.main_container = ttk.Frame(self.window)
        self.main_container.pack(fill="both", expand=True)

    def create_navigation(self):
        """Create navigation controls for schedule browsing."""
        nav_container = ttk.Frame(self.main_container)
        nav_container.pack(fill="x")

        ttk.Button(nav_container, text="Previous",
                   command=self.show_previous).pack(side="left")

        self.schedule_indicator = ttk.Label(nav_container, text="Schedule 1")
        self.schedule_indicator.pack(side="left", padx=10)

        ttk.Button(nav_container, text="Next",
                   command=self.show_next).pack(side="left")

    def create_grid_container(self):
        """Create the container for the schedule grid."""
        self.grid_container = ttk.Frame(self.main_container)
        self.grid_container.pack(fill="both", expand=True)

    def show_previous(self):
        """Display the previous schedule if available."""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()

    def show_next(self):
        """Display the next schedule if available."""
        if self.current_index < len(self.schedules) - 1:
            self.current_index += 1
            self.update_display()

    def update_display(self):
        """Update the schedule display and indicator."""
        self.schedule_indicator.config(text=f"Schedule {self.current_index + 1}")
        self.render_schedule()

    def render_schedule(self):
        """Render the current schedule grid."""
        self.clear_grid()
        current_schedule = self.schedules[self.current_index]

        for hour_idx, hour in enumerate(self.HOURS):
            for day_idx, day in enumerate(self.DAYS):
                cell = self.create_grid_cell(hour_idx, day_idx)
                self.populate_cell(cell, day, hour, current_schedule)

    def clear_grid(self):
        """Remove all widgets from the grid container."""
        for widget in self.grid_container.winfo_children():
            widget.destroy()

    def create_grid_cell(self, row, col):
        """Create and return a grid cell at specified position."""
        cell = tk.Frame(
            self.grid_container,
            width=self.CELL_DIMENSIONS["width"],
            height=self.CELL_DIMENSIONS["height"],
            relief="solid",
            borderwidth=1
        )
        cell.grid(row=row, column=col, sticky="nsew")
        cell.grid_propagate(False)
        return cell

    def populate_cell(self, cell, day, hour, schedule):
        """Populate a cell with course information."""
        day_code = "Th" if day.startswith("T") else day[0]

        for course in schedule:
            if (day_code, hour) in course["schedule"]:
                self.add_course_label(cell, course)

    def add_course_label(self, cell, course):
        """Add a course label to a cell with proper styling and binding."""
        label = tk.Label(
            cell,
            text=course["code"],
            bg=self.get_course_color(course["type"])
        )
        label.pack(fill="both", expand=True)
        label.bind("<Button-1>", lambda e, c=course: self.handle_course_click(c))

    def handle_course_click(self, course):
        """Handle course selection and highlighting."""
        related_courses = self.find_related_courses(course)
        self.info_panel.update_info(course)
        self.highlight_selected_course(course["code"])

    def find_related_courses(self, course):
        """Find all related sections for a given course."""
        current_schedule = self.schedules[self.current_index]
        return [c for c in current_schedule if c["main_code"] == course["main_code"]]

    def highlight_selected_course(self, course_code):
        """Highlight the selected course and dim others."""
        for cell in self.grid_container.winfo_children():
            for label in cell.winfo_children():
                label.configure(fg="gray" if course_code not in label["text"] else "black")

    @staticmethod
    def get_course_color(course_type):
        """Return the color for a given course type."""
        return DetailedScheduleReport.COURSE_COLORS.get(course_type, "white")


class CourseInfoPanel:
    def __init__(self, master):
        """Initialize the course information panel."""
        self.panel = ttk.Frame(master)
        self.panel.pack(fill="x", pady=10)

        # Header for course code
        self.code_header = ttk.Label(
            self.panel,
            font=("Arial", 12, "bold"),
            anchor="center"
        )
        self.code_header.pack(fill="x", pady=(0, 5))

        # Details section
        self.details_view = tk.Text(
            self.panel,
            height=6,
            width=50,
            wrap="word",
            state="normal",
            font=("Arial", 10)
        )
        self.details_view.pack(fill="x", padx=5)

    def update_info(self, course_data):
        """Update the panel with course information.
    "
    "    Args:
    "        course_data (dict): Dictionary containing course details
        """
        # Update course code header
        self.code_header["text"] = course_data["code"]

        # Build formatted details string
        details = (
            f"Course Name: {course_data['name']}\n"
            f"Credit Hours: {course_data['ECTS']}\n"
            f"Instructor: {course_data['teacher']}\n"
            f"Section Type: {course_data['type'].upper()}\n"
            f"Time Slots: {self._format_schedule(course_data['schedule'])}"
        )

        # Update details view
        self.details_view.delete("1.0", tk.END)
        self.details_view.insert("1.0", details)

    @staticmethod
    def _format_schedule(schedule):
        """Format schedule list into readable string."""
        return ", ".join(f"{day}-{period}" for day, period in schedule)


# =============================================================================
# Main GUI – Start the Application
# =============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Ana pencereyi başlangıçta gizle
    show_splash(root, duration=4000)  # Splash ekranını göster (4 saniye)

    # Splash ekranı kapandıktan sonra ana uygulama penceresi oluşturulacak
    app = SchedulerGUI(root)
    root.mainloop()
