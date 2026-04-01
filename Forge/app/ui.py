import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional
from datetime import datetime

from calculations import (
    calculate_bmi,
    calculate_bmr,
    calculate_tdee,
    calculate_macro_targets,
    evaluate_progressive_overload,
    get_progression_recommendation
)
from models import UserProfile, WorkoutEntry
from storage import (
    load_profile,
    save_profile,
    save_workout,
    load_workouts,
    get_previous_workout
)


class ForgeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Forge")
        self.root.geometry("950x700")
        self.root.minsize(850, 620)

        self.BG_COLOR = "#dbe5f1"
        self.PANEL_COLOR = "#dbe5f1"
        self.BORDER_COLOR = "#6f8fbf"
        self.BUTTON_COLOR = "#0b63e5"
        self.BUTTON_TEXT = "#ffffff"
        self.ENTRY_BG = "#f4f4f4"
        self.TEXT_COLOR = "#000000"

        self.root.configure(bg=self.BG_COLOR)

        self.current_frame: Optional[tk.Frame] = None

        self.age_entry: Optional[tk.Entry] = None
        self.sex_combo: Optional[ttk.Combobox] = None
        self.height_entry: Optional[tk.Entry] = None
        self.weight_entry: Optional[tk.Entry] = None
        self.activity_combo: Optional[ttk.Combobox] = None
        self.goal_combo: Optional[ttk.Combobox] = None

        self.workout_date_entry: Optional[tk.Entry] = None
        self.exercise_entry: Optional[tk.Entry] = None
        self.sets_entry: Optional[tk.Entry] = None
        self.reps_entry: Optional[tk.Entry] = None
        self.workout_weight_entry: Optional[tk.Entry] = None
        self.rpe_entry: Optional[tk.Entry] = None

        self.macro_results_frame: Optional[tk.Frame] = None

        self.setup_styles()
        self.show_dashboard()

    def setup_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Forge.TCombobox",
            fieldbackground=self.ENTRY_BG,
            background=self.ENTRY_BG,
            foreground=self.TEXT_COLOR,
            padding=6
        )

    def clear_frame(self) -> None:
        if self.current_frame is not None:
            self.current_frame.destroy()

    def create_screen(self, title_text: str, show_back: bool = False, back_command=None) -> tk.Frame:
        self.clear_frame()

        outer = tk.Frame(
            self.root,
            bg=self.BORDER_COLOR,
            padx=4,
            pady=4
        )
        outer.pack(fill="both", expand=True, padx=20, pady=20)
        self.current_frame = outer

        content = tk.Frame(outer, bg=self.BG_COLOR)
        content.pack(fill="both", expand=True)

        header = tk.Frame(content, bg=self.BG_COLOR, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        if show_back and back_command is not None:
            back_label = tk.Label(
                header,
                text="←",
                font=("Arial", 28, "bold"),
                bg=self.BG_COLOR,
                fg=self.TEXT_COLOR,
                cursor="hand2"
            )
            back_label.pack(side="left", padx=10, pady=10)
            back_label.bind("<Button-1>", lambda event: back_command())

        title = tk.Label(
            header,
            text=title_text,
            font=("Arial", 22, "bold"),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR
        )
        title.pack(expand=True)

        divider = tk.Frame(content, bg=self.BORDER_COLOR, height=4)
        divider.pack(fill="x")

        body = tk.Frame(content, bg=self.BG_COLOR)
        body.pack(fill="both", expand=True)

        return body

    def create_section(self, parent: tk.Widget) -> tk.Frame:
        section = tk.Frame(
            parent,
            bg=self.BORDER_COLOR,
            padx=3,
            pady=3
        )
        section.pack(fill="x", padx=20, pady=15)

        inner = tk.Frame(section, bg=self.PANEL_COLOR, padx=20, pady=20)
        inner.pack(fill="x")
        return inner

    def make_button(
        self,
        parent: tk.Widget,
        text: str,
        command,
        width: int = 18
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            font=("Arial", 12, "bold"),
            bg=self.BUTTON_COLOR,
            fg=self.BUTTON_TEXT,
            activebackground="#0952be",
            activeforeground=self.BUTTON_TEXT,
            relief="raised",
            bd=0,
            padx=8,
            pady=8,
            cursor="hand2"
        )

    def make_entry(self, parent: tk.Widget, width: int = 18) -> tk.Entry:
        return tk.Entry(
            parent,
            width=width,
            font=("Arial", 12),
            bg=self.ENTRY_BG,
            fg=self.TEXT_COLOR,
            relief="solid",
            bd=1,
            justify="center"
        )

    def make_label(self, parent: tk.Widget, text: str, font_size: int = 12, bold: bool = False) -> tk.Label:
        weight = "bold" if bold else "normal"
        return tk.Label(
            parent,
            text=text,
            font=("Arial", font_size, weight),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR
        )

    def show_dashboard(self) -> None:
        body = self.create_screen("FORGE")

        subtitle = tk.Label(
            body,
            text="Fitness Metrics & Workout Tracker",
            font=("Arial", 16, "bold"),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR
        )
        subtitle.pack(pady=(25, 5))

        button_section = self.create_section(body)

        button_rows = [
            ("🏋", "Workout Tracker", self.show_log_workout),
            ("🍽", "Metrics & Macros", self.show_metrics_and_macros),
            ("☻", "Profile Setup", self.show_profile_setup),
            ("📜", "Workout History", self.show_workout_history),
        ]

        for icon, text, command in button_rows:
            row = tk.Frame(button_section, bg=self.PANEL_COLOR)
            row.pack(pady=10)

            icon_label = tk.Label(
                row,
                text=icon,
                font=("Arial", 22),
                bg=self.PANEL_COLOR
            )
            icon_label.pack(side="left", padx=(0, 20))

            self.make_button(row, text, command, width=20).pack(side="left")

    def show_metrics_and_macros(self) -> None:
        profile = load_profile()

        if profile is None:
            messagebox.showerror(
                "No Profile Found",
                "Please create and save a profile before viewing metrics and macros."
            )
            return

        try:
            bmi = calculate_bmi(profile.weight_lb, profile.height_cm)
            bmr = calculate_bmr(profile.age, profile.sex, profile.weight_lb, profile.height_cm)
            tdee = calculate_tdee(bmr, profile.activity_level)
        except ValueError as error:
            messagebox.showerror("Calculation Error", str(error))
            return

        body = self.create_screen("Metrics & Macros", show_back=True, back_command=self.show_dashboard)

        metrics_section = self.create_section(body)

        left_col = tk.Frame(metrics_section, bg=self.PANEL_COLOR)
        left_col.pack(side="left", padx=(20, 30))

        right_col = tk.Frame(metrics_section, bg=self.PANEL_COLOR)
        right_col.pack(side="left", padx=20)

        metric_labels = [
            ("BMI:", f"{bmi:.1f}"),
            ("BMR:", f"{bmr:.0f} kcal"),
            ("TDEE:", f"{tdee:.0f} kcal")
        ]

        for label_text, value_text in metric_labels:
            row = tk.Frame(metrics_section, bg=self.PANEL_COLOR)
            row.pack(anchor="w", pady=8)

            tk.Label(
                row,
                text=label_text,
                font=("Arial", 13, "bold"),
                bg=self.PANEL_COLOR
            ).pack(side="left", padx=(40, 40))

            value_box = tk.Label(
                row,
                text=value_text,
                font=("Arial", 12),
                width=12,
                bg=self.ENTRY_BG,
                relief="solid",
                bd=1
            )
            value_box.pack(side="left")

        macro_section = self.create_section(body)

        goal_row = tk.Frame(macro_section, bg=self.PANEL_COLOR)
        goal_row.pack(anchor="w", pady=(0, 15))

        tk.Label(
            goal_row,
            text="Goal:",
            font=("Arial", 12, "bold"),
            bg=self.PANEL_COLOR
        ).pack(side="left", padx=(0, 15))

        self.goal_combo = ttk.Combobox(
            goal_row,
            values=["Cut", "Bulk", "Maintenance", "Recomp"],
            state="readonly",
            width=15,
            style="Forge.TCombobox"
        )
        self.goal_combo.pack(side="left")
        self.goal_combo.set("Maintenance")

        self.macro_results_frame = tk.Frame(macro_section, bg=self.PANEL_COLOR)
        self.macro_results_frame.pack(fill="x", pady=10)

        button_row = tk.Frame(body, bg=self.BG_COLOR)
        button_row.pack(pady=15)

        self.make_button(button_row, "Recalculate", self.display_macro_results, width=16).pack()

        self.display_macro_results()

    def display_macro_results(self) -> None:
        profile = load_profile()

        if profile is None or self.goal_combo is None or self.macro_results_frame is None:
            messagebox.showerror("Error", "Profile or goal selection is unavailable.")
            return

        goal = self.goal_combo.get().strip()

        try:
            bmr = calculate_bmr(profile.age, profile.sex, profile.weight_lb, profile.height_cm)
            tdee = calculate_tdee(bmr, profile.activity_level)
            macros = calculate_macro_targets(profile.weight_lb, tdee, goal)
        except ValueError as error:
            messagebox.showerror("Calculation Error", str(error))
            return

        for widget in self.macro_results_frame.winfo_children():
            widget.destroy()

        left = tk.Frame(self.macro_results_frame, bg=self.PANEL_COLOR)
        left.pack(side="left", padx=(20, 40), anchor="n")

        right = tk.Frame(self.macro_results_frame, bg=self.PANEL_COLOR)
        right.pack(side="left", padx=20, anchor="n")

        rows_left = [
            ("Protein:", f"{macros['protein_g']}g"),
            ("Carbs:", f"{macros['carbs_g']}g"),
            ("Fats:", f"{macros['fats_g']}g"),
        ]

        for label_text, value_text in rows_left:
            row = tk.Frame(left, bg=self.PANEL_COLOR)
            row.pack(anchor="w", pady=6)
            tk.Label(row, text=label_text, font=("Arial", 12, "bold"), bg=self.PANEL_COLOR).pack(side="left", padx=(0, 12))
            tk.Label(row, text=value_text, font=("Arial", 12), bg=self.PANEL_COLOR).pack(side="left")

        row = tk.Frame(right, bg=self.PANEL_COLOR)
        row.pack(anchor="w", pady=6)
        tk.Label(row, text="Caloric Goal:", font=("Arial", 12, "bold"), bg=self.PANEL_COLOR).pack(side="left", padx=(0, 12))
        tk.Label(row, text=f"{macros['calories']} kcal", font=("Arial", 12), bg=self.PANEL_COLOR).pack(side="left")

    def show_profile_setup(self) -> None:
        body = self.create_screen("Profile Setup", show_back=True, back_command=self.show_dashboard)

        section = self.create_section(body)
        form = tk.Frame(section, bg=self.PANEL_COLOR)
        form.pack()

        row_pad = 10

        tk.Label(form, text="Age:", font=("Arial", 13, "bold"), bg=self.PANEL_COLOR).grid(row=0, column=0, sticky="e", padx=20, pady=row_pad)
        self.age_entry = self.make_entry(form)
        self.age_entry.grid(row=0, column=1, padx=20, pady=row_pad)

        tk.Label(form, text="Weight (lbs):", font=("Arial", 13, "bold"), bg=self.PANEL_COLOR).grid(row=1, column=0, sticky="e", padx=20, pady=row_pad)
        self.weight_entry = self.make_entry(form)
        self.weight_entry.grid(row=1, column=1, padx=20, pady=row_pad)

        tk.Label(form, text="Height (cm):", font=("Arial", 13, "bold"), bg=self.PANEL_COLOR).grid(row=2, column=0, sticky="e", padx=20, pady=row_pad)
        self.height_entry = self.make_entry(form)
        self.height_entry.grid(row=2, column=1, padx=20, pady=row_pad)

        tk.Label(form, text="Sex:", font=("Arial", 13, "bold"), bg=self.PANEL_COLOR).grid(row=3, column=0, sticky="e", padx=20, pady=row_pad)

        sex_frame = tk.Frame(form, bg=self.PANEL_COLOR)
        sex_frame.grid(row=3, column=1, padx=20, pady=row_pad)

        self.sex_var = tk.StringVar()

        tk.Radiobutton(
            sex_frame,
            text="Male",
            variable=self.sex_var,
            value="Male",
            bg=self.PANEL_COLOR,
            font=("Arial", 11)
        ).pack(side="left", padx=8)

        tk.Radiobutton(
            sex_frame,
            text="Female",
            variable=self.sex_var,
            value="Female",
            bg=self.PANEL_COLOR,
            font=("Arial", 11)
        ).pack(side="left", padx=8)

        tk.Label(form, text="Activity:", font=("Arial", 13, "bold"), bg=self.PANEL_COLOR).grid(row=4, column=0, sticky="e", padx=20, pady=row_pad)

        self.activity_combo = ttk.Combobox(
            form,
            values=[
                "Sedentary",
                "Lightly Active",
                "Moderately Active",
                "Very Active",
                "Extra Active"
            ],
            state="readonly",
            width=16,
            style="Forge.TCombobox"
        )
        self.activity_combo.grid(row=4, column=1, padx=20, pady=row_pad)

        self.load_profile_into_form()

        button_section = self.create_section(body)
        button_row = tk.Frame(button_section, bg=self.PANEL_COLOR)
        button_row.pack()

        self.make_button(button_row, "Save Profile", self.save_profile_form, width=14).pack(side="left", padx=20)
        self.make_button(button_row, "Back", self.show_dashboard, width=14).pack(side="left", padx=20)

    def load_profile_into_form(self) -> None:
        profile = load_profile()

        if profile is None:
            return

        if self.age_entry is not None:
            self.age_entry.delete(0, tk.END)
            self.age_entry.insert(0, str(profile.age))
        if self.weight_entry is not None:
            self.weight_entry.delete(0, tk.END)
            self.weight_entry.insert(0, str(profile.weight_lb))
        if self.height_entry is not None:
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(profile.height_cm))
        if hasattr(self, "sex_var"):
            self.sex_var.set(profile.sex)
        if self.activity_combo is not None:
            self.activity_combo.set(profile.activity_level)

    def save_profile_form(self) -> None:
        if not all([
            self.age_entry,
            self.weight_entry,
            self.height_entry,
            self.activity_combo
        ]):
            messagebox.showerror("Form Error", "Profile form is not initialized correctly.")
            return

        age = self.age_entry.get().strip()
        sex = self.sex_var.get().strip() if hasattr(self, "sex_var") else ""
        height = self.height_entry.get().strip()
        weight = self.weight_entry.get().strip()
        activity = self.activity_combo.get().strip()

        if not all([age, sex, height, weight, activity]):
            messagebox.showerror("Missing Information", "Please fill out all profile fields.")
            return

        try:
            profile = UserProfile(
                age=int(age),
                sex=sex,
                height_cm=float(height),
                weight_lb=float(weight),
                activity_level=activity
            )
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Age must be a whole number, and height/weight must be numeric."
            )
            return

        save_profile(profile)
        messagebox.showinfo("Profile Saved", "Profile saved successfully.")
        self.show_dashboard()

    def show_metrics(self) -> None:
        self.show_metrics_and_macros()

    def show_macros(self) -> None:
        self.show_metrics_and_macros()

    def show_log_workout(self) -> None:
        body = self.create_screen("Add New Workout", show_back=True, back_command=self.show_dashboard)

        top_section = self.create_section(body)

        top_form = tk.Frame(top_section, bg=self.PANEL_COLOR)
        top_form.pack()

        tk.Label(top_form, text="Date:", font=("Arial", 12, "bold"), bg=self.PANEL_COLOR).grid(row=0, column=0, sticky="e", padx=20, pady=10)
        self.workout_date_entry = self.make_entry(top_form)
        self.workout_date_entry.grid(row=0, column=1, padx=20, pady=10)
        self.workout_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(top_form, text="Exercise:", font=("Arial", 12, "bold"), bg=self.PANEL_COLOR).grid(row=1, column=0, sticky="e", padx=20, pady=10)
        self.exercise_entry = self.make_entry(top_form)
        self.exercise_entry.grid(row=1, column=1, padx=20, pady=10)

        bottom_section = self.create_section(body)

        form = tk.Frame(bottom_section, bg=self.PANEL_COLOR)
        form.pack()

        tk.Label(form, text="Sets:", font=("Arial", 12, "bold"), bg=self.PANEL_COLOR).grid(row=0, column=0, sticky="e", padx=20, pady=10)
        self.sets_entry = self.make_entry(form)
        self.sets_entry.grid(row=0, column=1, padx=20, pady=10)

        tk.Label(form, text="Reps:", font=("Arial", 12, "bold"), bg=self.PANEL_COLOR).grid(row=1, column=0, sticky="e", padx=20, pady=10)
        self.reps_entry = self.make_entry(form)
        self.reps_entry.grid(row=1, column=1, padx=20, pady=10)

        tk.Label(form, text="Weight (lbs):", font=("Arial", 12, "bold"), bg=self.PANEL_COLOR).grid(row=2, column=0, sticky="e", padx=20, pady=10)
        self.workout_weight_entry = self.make_entry(form)
        self.workout_weight_entry.grid(row=2, column=1, padx=20, pady=10)

        tk.Label(form, text="RPE:", font=("Arial", 12, "bold"), bg=self.PANEL_COLOR).grid(row=3, column=0, sticky="e", padx=20, pady=10)
        self.rpe_entry = self.make_entry(form)
        self.rpe_entry.grid(row=3, column=1, padx=20, pady=10)

        button_section = self.create_section(body)
        button_row = tk.Frame(button_section, bg=self.PANEL_COLOR)
        button_row.pack()

        self.make_button(button_row, "Save Workout", self.save_workout_form, width=14).pack(side="left", padx=20)
        self.make_button(button_row, "Back", self.show_dashboard, width=14).pack(side="left", padx=20)

    def save_workout_form(self) -> None:
        if not all([
            self.workout_date_entry,
            self.exercise_entry,
            self.sets_entry,
            self.reps_entry,
            self.workout_weight_entry,
            self.rpe_entry
        ]):
            messagebox.showerror("Form Error", "Workout form is not initialized correctly.")
            return

        date = self.workout_date_entry.get().strip()
        exercise = self.exercise_entry.get().strip()
        sets = self.sets_entry.get().strip()
        reps = self.reps_entry.get().strip()
        weight = self.workout_weight_entry.get().strip()
        rpe = self.rpe_entry.get().strip()

        if not all([date, exercise, sets, reps, weight, rpe]):
            messagebox.showerror("Missing Information", "Please fill out all workout fields.")
            return

        try:
            datetime.strptime(date, "%Y-%m-%d")
            previous_workout = get_previous_workout(exercise)

            workout = WorkoutEntry(
                date=date,
                exercise=exercise,
                sets=int(sets),
                reps=int(reps),
                weight=float(weight),
                rpe=float(rpe)
            )
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Enter a valid date (YYYY-MM-DD). Sets/reps must be whole numbers. Weight/RPE must be numeric."
            )
            return

        save_workout(workout)

        feedback = evaluate_progressive_overload(previous_workout, workout)
        recommendation = get_progression_recommendation(previous_workout, workout)

        messagebox.showinfo(
            "Workout Saved",
            f"Workout saved successfully.\n\n"
            f"Progress Feedback:\n{feedback}\n\n"
            f"Next Session Recommendation:\n{recommendation}"
        )
        self.show_dashboard()

    def show_workout_history(self) -> None:
        workouts = load_workouts()

        body = self.create_screen("Workout Tracker", show_back=True, back_command=self.show_dashboard)

        top_section = self.create_section(body)
        top_row = tk.Frame(top_section, bg=self.PANEL_COLOR)
        top_row.pack()

        self.make_button(top_row, "Add New Workout", self.show_log_workout, width=18).pack()

        history_section = self.create_section(body)

        tk.Label(
            history_section,
            text="Workout History:",
            font=("Arial", 12, "bold"),
            bg=self.PANEL_COLOR
        ).pack(anchor="w", pady=(0, 10))

        if not workouts:
            tk.Label(
                history_section,
                text="No workouts logged yet.",
                font=("Arial", 12),
                bg=self.PANEL_COLOR
            ).pack(anchor="w")
            return

        list_frame = tk.Frame(history_section, bg=self.PANEL_COLOR)
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        workout_listbox = tk.Listbox(
            list_frame,
            width=150,
            height=14,
            yscrollcommand=scrollbar.set,
            font=("Courier New", 10),
            bg="#ffffff",
            fg=self.TEXT_COLOR,
            relief="solid",
            bd=1
        )
        workout_listbox.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=workout_listbox.yview)

        for current_index in range(len(workouts) - 1, -1, -1):
            workout = workouts[current_index]
            previous_workout = None

            for previous_index in range(current_index - 1, -1, -1):
                candidate = workouts[previous_index]
                if candidate.exercise.strip().lower() == workout.exercise.strip().lower():
                    previous_workout = candidate
                    break

            feedback = evaluate_progressive_overload(previous_workout, workout)
            recommendation = get_progression_recommendation(previous_workout, workout)

            workout_text = (
                f"{workout.date} | {workout.exercise} | "
                f"{workout.sets}x{workout.reps} @ {workout.weight:.1f} lbs | "
                f"{feedback} | Next: {recommendation}"
            )
            workout_listbox.insert(tk.END, workout_text)

    def not_implemented(self) -> None:
        messagebox.showinfo("Coming Soon", "This feature is not built yet.")