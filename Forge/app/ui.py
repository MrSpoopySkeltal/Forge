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
    get_progression_recommendation,
    estimate_cardio_calories,
)
from models import CardioEntry, UserProfile, WorkoutEntry
from storage import (
    load_profile,
    save_profile,
    save_workout,
    load_workouts,
    get_previous_workout,
    delete_workout_at_index,
    clear_workouts,
    save_cardio_entry,
    load_cardio_entries,
    delete_cardio_at_index,
    clear_cardio_entries,
)


class RoundedButton(tk.Canvas):
    """A soft-cornered, hover-aware button built with standard Tkinter only."""

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        command,
        width: int,
        bg_color: str,
        hover_color: str,
        text_color: str,
        parent_bg: str,
    ) -> None:
        self.button_width = width
        self.button_height = 46
        self.radius = 16
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.command = command

        super().__init__(
            parent,
            width=self.button_width,
            height=self.button_height,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )

        self.shape_id = self._create_rounded_rectangle(
            1,
            1,
            self.button_width - 1,
            self.button_height - 1,
            self.radius,
            fill=self.bg_color,
            outline="",
        )
        self.text_id = self.create_text(
            self.button_width / 2,
            self.button_height / 2,
            text=text,
            fill=self.text_color,
            font=("Segoe UI", 11, "bold"),
        )

        for item in (self, self.shape_id, self.text_id):
            self.tag_bind(item, "<Enter>", self._on_enter) if item != self else None
            self.tag_bind(item, "<Leave>", self._on_leave) if item != self else None
            self.tag_bind(item, "<Button-1>", self._on_click) if item != self else None

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _create_rounded_rectangle(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        radius: int,
        **kwargs,
    ) -> int:
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_enter(self, _event=None) -> None:
        self.itemconfigure(self.shape_id, fill=self.hover_color)

    def _on_leave(self, _event=None) -> None:
        self.itemconfigure(self.shape_id, fill=self.bg_color)

    def _on_click(self, _event=None) -> None:
        self.command()


class ForgeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Forge")
        self.root.geometry("950x700")
        self.root.minsize(850, 620)

        self.BG_COLOR = "#10151d"
        self.PANEL_COLOR = "#3a71be"
        self.BORDER_COLOR = "#135ab8"
        self.BUTTON_COLOR = "#0f3da1"
        self.BUTTON_HOVER = "#102446"
        self.BUTTON_TEXT = "#ffffff"
        self.ENTRY_BG = "#243142"
        self.TEXT_COLOR = "#eef3fb"
        self.MUTED_TEXT = "#9aaabe"

        self.root.configure(bg=self.BG_COLOR)
        self.root.option_add("*Font", ("Segoe UI", 11))

        self.current_frame: Optional[tk.Frame] = None

        self.age_entry: Optional[tk.Entry] = None
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

        self.cardio_date_entry: Optional[tk.Entry] = None
        self.cardio_activity_combo: Optional[ttk.Combobox] = None
        self.cardio_duration_entry: Optional[tk.Entry] = None
        self.cardio_intensity_combo: Optional[ttk.Combobox] = None

        self.macro_results_frame: Optional[tk.Frame] = None

        self.workout_history_listbox: Optional[tk.Listbox] = None
        self.history_display_map = []

        self.cardio_history_listbox: Optional[tk.Listbox] = None
        self.cardio_history_display_map = []

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
            arrowcolor=self.BUTTON_COLOR,
            bordercolor=self.BORDER_COLOR,
            lightcolor=self.BORDER_COLOR,
            darkcolor=self.BORDER_COLOR,
            padding=8,
            relief="flat",
            font=("Segoe UI", 11),
        )
        style.map(
            "Forge.TCombobox",
            fieldbackground=[("readonly", self.ENTRY_BG)],
            selectbackground=[("readonly", self.ENTRY_BG)],
            selectforeground=[("readonly", self.TEXT_COLOR)],
            background=[("active", "#e7effa"), ("readonly", self.ENTRY_BG)],
            bordercolor=[("focus", self.BUTTON_COLOR)],
        )

    def clear_frame(self) -> None:
        if self.current_frame is not None:
            self.current_frame.destroy()

    def create_screen(
        self,
        title_text: str,
        show_back: bool = False,
        back_command=None,
    ) -> tk.Frame:
        self.clear_frame()

        outer = tk.Frame(
            self.root,
            bg=self.BORDER_COLOR,
            padx=1,
            pady=1,
        )
        outer.pack(fill="both", expand=True, padx=24, pady=24)
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
                font=("Segoe UI", 28, "bold"),
                bg=self.BG_COLOR,
                fg=self.TEXT_COLOR,
                cursor="hand2",
            )
            back_label.pack(side="left", padx=10, pady=10)
            back_label.bind("<Button-1>", lambda event: back_command())

        title = tk.Label(
            header,
            text=title_text,
            font=("Segoe UI", 22, "bold"),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR,
        )
        title.pack(expand=True)

        divider = tk.Frame(content, bg=self.BORDER_COLOR, height=2)
        divider.pack(fill="x")

        body = tk.Frame(content, bg=self.BG_COLOR)
        body.pack(fill="both", expand=True)

        return body

    def create_section(self, parent: tk.Widget) -> tk.Frame:
        section = tk.Frame(
            parent,
            bg=self.BORDER_COLOR,
            padx=1,
            pady=1,
        )
        section.pack(fill="x", padx=24, pady=12)

        inner = tk.Frame(section, bg=self.PANEL_COLOR, padx=24, pady=22)
        inner.pack(fill="x")

        return inner

    def make_button(
        self,
        parent: tk.Widget,
        text: str,
        command,
        width: int = 18,
    ) -> RoundedButton:
        return RoundedButton(
            parent=parent,
            text=text,
            command=command,
            width=(width * 10) + 34,
            bg_color=self.BUTTON_COLOR,
            hover_color=self.BUTTON_HOVER,
            text_color=self.BUTTON_TEXT,
            parent_bg=parent.cget("bg"),
        )

    def make_entry(self, parent: tk.Widget, width: int = 18) -> tk.Entry:
        return tk.Entry(
            parent,
            width=width,
            font=("Segoe UI", 11),
            bg=self.ENTRY_BG,
            fg=self.TEXT_COLOR,
            insertbackground=self.TEXT_COLOR,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.BORDER_COLOR,
            highlightcolor=self.BUTTON_COLOR,
            justify="center",
        )

    def show_dashboard(self) -> None:
        body = self.create_screen("FORGE")

        subtitle = tk.Label(
            body,
            text="Fitness Metrics & Workout Tracker",
            font=("Segoe UI", 16, "bold"),
            bg=self.BG_COLOR,
            fg=self.TEXT_COLOR,
        )
        subtitle.pack(pady=(25, 5))

        button_section = self.create_section(body)

        button_rows = [
            ("🏋", "Workout Tracker", self.show_log_workout),
            ("🚲", "Cardio Tracker", self.show_log_cardio),
            ("📊", "Metrics & Macros", self.show_metrics_and_macros),
            ("☻", "Profile Setup", self.show_profile_setup),
            ("📋", "Workout History", self.show_workout_history),
        ]

        for icon, text, command in button_rows:
            row = tk.Frame(button_section, bg=self.PANEL_COLOR)
            row.pack(pady=8)

            icon_label = tk.Label(
                row,
                text=icon,
                font=("Segoe UI", 22),
                bg=self.PANEL_COLOR,
            )
            icon_label.pack(side="left", padx=(0, 20))

            self.make_button(row, text, command, width=20).pack(side="left")

    def show_metrics_and_macros(self) -> None:
        profile = load_profile()

        if profile is None:
            messagebox.showerror(
                "No Profile Found",
                "Please create and save a profile before viewing metrics and macros.",
            )
            return

        try:
            bmi = calculate_bmi(profile.weight_lb, profile.height_cm)
            bmr = calculate_bmr(
                profile.age,
                profile.sex,
                profile.weight_lb,
                profile.height_cm,
            )
            tdee = calculate_tdee(bmr, profile.activity_level)
        except ValueError as error:
            messagebox.showerror("Calculation Error", str(error))
            return

        body = self.create_screen(
            "Metrics & Macros",
            show_back=True,
            back_command=self.show_dashboard,
        )

        metrics_section = self.create_section(body)

        metric_labels = [
            ("BMI:", f"{bmi:.1f}"),
            ("BMR:", f"{bmr:.0f} kcal"),
            ("TDEE:", f"{tdee:.0f} kcal"),
        ]

        for label_text, value_text in metric_labels:
            row = tk.Frame(metrics_section, bg=self.PANEL_COLOR)
            row.pack(anchor="w", pady=8)

            tk.Label(
                row,
                text=label_text,
                font=("Segoe UI", 13, "bold"),
                bg=self.PANEL_COLOR,
            ).pack(side="left", padx=(40, 40))

            value_box = tk.Label(
                row,
                text=value_text,
                font=("Segoe UI", 12),
                width=12,
                bg=self.ENTRY_BG,
                relief="solid",
                bd=1,
            )
            value_box.pack(side="left")

        macro_section = self.create_section(body)

        goal_row = tk.Frame(macro_section, bg=self.PANEL_COLOR)
        goal_row.pack(anchor="w", pady=(0, 15))

        tk.Label(
            goal_row,
            text="Goal:",
            font=("Segoe UI", 12, "bold"),
            bg=self.PANEL_COLOR,
        ).pack(side="left", padx=(0, 15))

        self.goal_combo = ttk.Combobox(
            goal_row,
            values=["Cut", "Bulk", "Maintenance", "Recomp"],
            state="readonly",
            width=15,
            style="Forge.TCombobox",
        )
        self.goal_combo.pack(side="left")
        self.goal_combo.set("Maintenance")

        self.macro_results_frame = tk.Frame(macro_section, bg=self.PANEL_COLOR)
        self.macro_results_frame.pack(fill="x", pady=10)

        button_row = tk.Frame(body, bg=self.BG_COLOR)
        button_row.pack(pady=15)

        self.make_button(
            button_row,
            "Recalculate",
            self.display_macro_results,
            width=16,
        ).pack()

        self.display_macro_results()

    def display_macro_results(self) -> None:
        profile = load_profile()

        if (
            profile is None
            or self.goal_combo is None
            or self.macro_results_frame is None
        ):
            messagebox.showerror("Error", "Profile or goal selection is unavailable.")
            return

        goal = self.goal_combo.get().strip()

        try:
            bmr = calculate_bmr(
                profile.age,
                profile.sex,
                profile.weight_lb,
                profile.height_cm,
            )
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

            tk.Label(
                row,
                text=label_text,
                font=("Segoe UI", 12, "bold"),
                bg=self.PANEL_COLOR,
            ).pack(side="left", padx=(0, 12))

            tk.Label(
                row,
                text=value_text,
                font=("Segoe UI", 12),
                bg=self.PANEL_COLOR,
            ).pack(side="left")

        row = tk.Frame(right, bg=self.PANEL_COLOR)
        row.pack(anchor="w", pady=6)

        tk.Label(
            row,
            text="Caloric Goal:",
            font=("Segoe UI", 12, "bold"),
            bg=self.PANEL_COLOR,
        ).pack(side="left", padx=(0, 12))

        tk.Label(
            row,
            text=f"{macros['calories']} kcal",
            font=("Segoe UI", 12),
            bg=self.PANEL_COLOR,
        ).pack(side="left")

    def show_profile_setup(self) -> None:
        body = self.create_screen(
            "Profile Setup",
            show_back=True,
            back_command=self.show_dashboard,
        )

        section = self.create_section(body)
        form = tk.Frame(section, bg=self.PANEL_COLOR)
        form.pack()

        row_pad = 10

        tk.Label(
            form,
            text="Age:",
            font=("Segoe UI", 13, "bold"),
            bg=self.PANEL_COLOR,
        ).grid(row=0, column=0, sticky="e", padx=20, pady=row_pad)

        self.age_entry = self.make_entry(form)
        self.age_entry.grid(row=0, column=1, padx=20, pady=row_pad)

        tk.Label(
            form,
            text="Weight (lbs):",
            font=("Segoe UI", 13, "bold"),
            bg=self.PANEL_COLOR,
        ).grid(row=1, column=0, sticky="e", padx=20, pady=row_pad)

        self.weight_entry = self.make_entry(form)
        self.weight_entry.grid(row=1, column=1, padx=20, pady=row_pad)

        tk.Label(
            form,
            text="Height (cm):",
            font=("Segoe UI", 13, "bold"),
            bg=self.PANEL_COLOR,
        ).grid(row=2, column=0, sticky="e", padx=20, pady=row_pad)

        self.height_entry = self.make_entry(form)
        self.height_entry.grid(row=2, column=1, padx=20, pady=row_pad)

        tk.Label(
            form,
            text="Sex:",
            font=("Segoe UI", 13, "bold"),
            bg=self.PANEL_COLOR,
        ).grid(row=3, column=0, sticky="e", padx=20, pady=row_pad)

        sex_frame = tk.Frame(form, bg=self.PANEL_COLOR)
        sex_frame.grid(row=3, column=1, padx=20, pady=row_pad)

        self.sex_var = tk.StringVar()

        tk.Radiobutton(
            sex_frame,
            text="Male",
            variable=self.sex_var,
            value="Male",
            bg=self.PANEL_COLOR,
            font=("Segoe UI", 11),
        ).pack(side="left", padx=8)

        tk.Radiobutton(
            sex_frame,
            text="Female",
            variable=self.sex_var,
            value="Female",
            bg=self.PANEL_COLOR,
            font=("Segoe UI", 11),
        ).pack(side="left", padx=8)

        tk.Label(
            form,
            text="Activity:",
            font=("Segoe UI", 13, "bold"),
            bg=self.PANEL_COLOR,
        ).grid(row=4, column=0, sticky="e", padx=20, pady=row_pad)

        self.activity_combo = ttk.Combobox(
            form,
            values=[
                "Sedentary",
                "Lightly Active",
                "Moderately Active",
                "Very Active",
                "Extra Active",
            ],
            state="readonly",
            width=16,
            style="Forge.TCombobox",
        )
        self.activity_combo.grid(row=4, column=1, padx=20, pady=row_pad)

        self.load_profile_into_form()

        button_section = self.create_section(body)
        button_row = tk.Frame(button_section, bg=self.PANEL_COLOR)
        button_row.pack()

        self.make_button(
            button_row,
            "Save Profile",
            self.save_profile_form,
            width=14,
        ).pack(side="left", padx=20)

        self.make_button(
            button_row,
            "Back",
            self.show_dashboard,
            width=14,
        ).pack(side="left", padx=20)

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
            self.activity_combo,
        ]):
            messagebox.showerror(
                "Form Error",
                "Profile form is not initialized correctly.",
            )
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
                activity_level=activity,
            )
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Age must be a whole number, and height/weight must be numeric.",
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
        body = self.create_screen(
            "Add New Workout",
            show_back=True,
            back_command=self.show_dashboard,
        )

        top_section = self.create_section(body)
        top_form = tk.Frame(top_section, bg=self.PANEL_COLOR)
        top_form.pack()

        tk.Label(
            top_form,
            text="Date:",
            font=("Segoe UI", 12, "bold"),
            bg=self.PANEL_COLOR,
        ).grid(row=0, column=0, sticky="e", padx=20, pady=10)

        self.workout_date_entry = self.make_entry(top_form)
        self.workout_date_entry.grid(row=0, column=1, padx=20, pady=10)
        self.workout_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(
            top_form,
            text="Exercise:",
            font=("Segoe UI", 12, "bold"),
            bg=self.PANEL_COLOR,
        ).grid(row=1, column=0, sticky="e", padx=20, pady=10)

        self.exercise_entry = self.make_entry(top_form)
        self.exercise_entry.grid(row=1, column=1, padx=20, pady=10)

        bottom_section = self.create_section(body)
        form = tk.Frame(bottom_section, bg=self.PANEL_COLOR)
        form.pack()

        tk.Label(
            form,
            text="Sets:",
            font=("Segoe UI", 12, "bold"),
            bg=self.PANEL_COLOR,
        ).grid(row=0, column=0, sticky="e", padx=20, pady=10)

        self.sets_entry = self.make_entry(form)
        self.sets_entry.grid(row=0, column=1, padx=20, pady=10)

        tk.Label(
            form,
            text="Reps:",
            font=("Segoe UI", 12, "bold"),
            bg=self.PANEL_COLOR,
        ).grid(row=1, column=0, sticky="e", padx=20, pady=10)

        self.reps_entry = self.make_entry(form)
        self.reps_entry.grid(row=1, column=1, padx=20, pady=10)

        tk.Label(
            form,
            text="Weight (lbs):",
            font=("Segoe UI", 12, "bold"),
            bg=self.PANEL_COLOR,
        ).grid(row=2, column=0, sticky="e", padx=20, pady=10)

        self.workout_weight_entry = self.make_entry(form)
        self.workout_weight_entry.grid(row=2, column=1, padx=20, pady=10)

        tk.Label(
            form,
            text="RPE:",
            font=("Segoe UI", 12, "bold"),
            bg=self.PANEL_COLOR,
        ).grid(row=3, column=0, sticky="e", padx=20, pady=10)

        self.rpe_entry = self.make_entry(form)
        self.rpe_entry.grid(row=3, column=1, padx=20, pady=10)

        button_section = self.create_section(body)
        button_row = tk.Frame(button_section, bg=self.PANEL_COLOR)
        button_row.pack()

        self.make_button(
            button_row,
            "Save Workout",
            self.save_workout_form,
            width=14,
        ).pack(side="left", padx=20)

        self.make_button(
            button_row,
            "Back",
            self.show_dashboard,
            width=14,
        ).pack(side="left", padx=20)

    def save_workout_form(self) -> None:
        if not all([
            self.workout_date_entry,
            self.exercise_entry,
            self.sets_entry,
            self.reps_entry,
            self.workout_weight_entry,
            self.rpe_entry,
        ]):
            messagebox.showerror(
                "Form Error",
                "Workout form is not initialized correctly.",
            )
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
                rpe=float(rpe),
            )
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Enter a valid date (YYYY-MM-DD).\n"
                "Sets/reps must be whole numbers.\n"
                "Weight/RPE must be numeric.",
            )
            return

        save_workout(workout)

        feedback = evaluate_progressive_overload(previous_workout, workout)
        recommendation = get_progression_recommendation(previous_workout, workout)

        messagebox.showinfo(
            "Workout Saved",
            f"Workout saved successfully.\n\n"
            f"Progress Feedback:\n{feedback}\n\n"
            f"Next Session Recommendation:\n{recommendation}",
        )

        self.show_dashboard()

    def show_log_cardio(self) -> None:
        body = self.create_screen(
            "Log Cardio",
            show_back=True,
            back_command=self.show_dashboard,
        )

        profile = load_profile()

        if profile is None:
            warning_section = self.create_section(body)
            tk.Label(
                warning_section,
                text="A saved profile is required to estimate calories burned.",
                font=("Segoe UI", 12, "bold"),
                bg=self.PANEL_COLOR,
                fg=self.TEXT_COLOR,
            ).pack(pady=5)

        form_section = self.create_section(body)
        form = tk.Frame(form_section, bg=self.PANEL_COLOR)
        form.pack()

        tk.Label(
            form,
            text="Date:",
            font=("Segoe UI", 12, "bold"),
            bg=self.PANEL_COLOR,
        ).grid(row=0, column=0, sticky="e", padx=20, pady=10)

        self.cardio_date_entry = self.make_entry(form)
        self.cardio_date_entry.grid(row=0, column=1, padx=20, pady=10)
        self.cardio_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(
            form,
            text="Exercise Type:",
            font=("Segoe UI", 12, "bold"),
            bg=self.PANEL_COLOR,
        ).grid(row=1, column=0, sticky="e", padx=20, pady=10)

        self.cardio_activity_combo = ttk.Combobox(
            form,
            values=[
                "Biking",
                "Running",
                "Walking",
                "Jogging",
                "Rowing",
                "Elliptical",
                "Boxing",
            ],
            state="readonly",
            width=16,
            style="Forge.TCombobox",
        )
        self.cardio_activity_combo.grid(row=1, column=1, padx=20, pady=10)
        self.cardio_activity_combo.set("Walking")

        tk.Label(
            form,
            text="Duration (minutes):",
            font=("Segoe UI", 12, "bold"),
            bg=self.PANEL_COLOR,
        ).grid(row=2, column=0, sticky="e", padx=20, pady=10)

        self.cardio_duration_entry = self.make_entry(form)
        self.cardio_duration_entry.grid(row=2, column=1, padx=20, pady=10)

        tk.Label(
            form,
            text="Intensity:",
            font=("Segoe UI", 12, "bold"),
            bg=self.PANEL_COLOR,
        ).grid(row=3, column=0, sticky="e", padx=20, pady=10)

        self.cardio_intensity_combo = ttk.Combobox(
            form,
            values=["Low", "Moderate", "High"],
            state="readonly",
            width=16,
            style="Forge.TCombobox",
        )
        self.cardio_intensity_combo.grid(row=3, column=1, padx=20, pady=10)
        self.cardio_intensity_combo.set("Moderate")

        button_section = self.create_section(body)
        button_row = tk.Frame(button_section, bg=self.PANEL_COLOR)
        button_row.pack()

        self.make_button(
            button_row,
            "Save Cardio",
            self.save_cardio_form,
            width=14,
        ).pack(side="left", padx=10)

        self.make_button(
            button_row,
            "View History",
            self.show_cardio_history,
            width=14,
        ).pack(side="left", padx=10)

        self.make_button(
            button_row,
            "Back",
            self.show_dashboard,
            width=14,
        ).pack(side="left", padx=10)

    def save_cardio_form(self) -> None:
        if not all([
            self.cardio_date_entry,
            self.cardio_activity_combo,
            self.cardio_duration_entry,
            self.cardio_intensity_combo,
        ]):
            messagebox.showerror(
                "Form Error",
                "Cardio form is not initialized correctly.",
            )
            return

        profile = load_profile()

        if profile is None:
            messagebox.showerror(
                "No Profile Found",
                "Please create and save a profile before logging cardio.",
            )
            return

        date = self.cardio_date_entry.get().strip()
        activity_type = self.cardio_activity_combo.get().strip()
        duration = self.cardio_duration_entry.get().strip()
        intensity = self.cardio_intensity_combo.get().strip()

        if not all([date, activity_type, duration, intensity]):
            messagebox.showerror("Missing Information", "Please fill out all cardio fields.")
            return

        try:
            datetime.strptime(date, "%Y-%m-%d")
            duration_minutes = int(duration)

            if duration_minutes <= 0:
                raise ValueError

            estimated_calories = estimate_cardio_calories(
                profile.weight_lb,
                activity_type,
                duration_minutes,
                intensity,
            )

            cardio_entry = CardioEntry(
                date=date,
                activity_type=activity_type,
                duration_minutes=duration_minutes,
                intensity=intensity,
                estimated_calories=estimated_calories,
            )
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Enter a valid date (YYYY-MM-DD).\n"
                "Duration must be a whole number greater than zero.",
            )
            return

        save_cardio_entry(cardio_entry)

        messagebox.showinfo(
            "Cardio Saved",
            f"Cardio session saved successfully.\n\n"
            f"Estimated Calories Burned: {estimated_calories} kcal",
        )

        self.show_cardio_history()

    def show_cardio_history(self) -> None:
        cardio_entries = load_cardio_entries()

        body = self.create_screen(
            "Cardio History",
            show_back=True,
            back_command=self.show_dashboard,
        )

        top_section = self.create_section(body)
        top_row = tk.Frame(top_section, bg=self.PANEL_COLOR)
        top_row.pack()

        self.make_button(
            top_row,
            "Add Cardio",
            self.show_log_cardio,
            width=16,
        ).pack(side="left", padx=10)

        self.make_button(
            top_row,
            "Delete Selected",
            self.delete_selected_cardio,
            width=16,
        ).pack(side="left", padx=10)

        self.make_button(
            top_row,
            "Clear All Cardio",
            self.clear_all_cardio_confirmed,
            width=16,
        ).pack(side="left", padx=10)

        history_section = self.create_section(body)

        tk.Label(
            history_section,
            text="Cardio History:",
            font=("Segoe UI", 12, "bold"),
            bg=self.PANEL_COLOR,
        ).pack(anchor="w", pady=(0, 10))

        if not cardio_entries:
            tk.Label(
                history_section,
                text="No cardio sessions logged yet.",
                font=("Segoe UI", 12),
                bg=self.PANEL_COLOR,
            ).pack(anchor="w")

            self.cardio_history_listbox = None
            self.cardio_history_display_map = []
            return

        list_frame = tk.Frame(history_section, bg=self.PANEL_COLOR)
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.cardio_history_listbox = tk.Listbox(
            list_frame,
            width=120,
            height=14,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            bg=self.ENTRY_BG,
            fg=self.TEXT_COLOR,
            selectbackground=self.BUTTON_COLOR,
            selectforeground=self.BUTTON_TEXT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.BORDER_COLOR,
        )
        self.cardio_history_listbox.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=self.cardio_history_listbox.yview)

        self.cardio_history_display_map = []

        for current_index in range(len(cardio_entries) - 1, -1, -1):
            entry = cardio_entries[current_index]

            cardio_text = (
                f"{entry.date} | "
                f"{entry.activity_type} | "
                f"{entry.duration_minutes} min | "
                f"{entry.intensity} intensity | "
                f"Est. Calories Burned: {entry.estimated_calories} kcal"
            )

            self.cardio_history_listbox.insert(tk.END, cardio_text)
            self.cardio_history_display_map.append(current_index)

    def delete_selected_cardio(self) -> None:
        if self.cardio_history_listbox is None or not self.cardio_history_display_map:
            messagebox.showwarning(
                "No Cardio Sessions",
                "There are no cardio sessions to delete.",
            )
            return

        selection = self.cardio_history_listbox.curselection()

        if not selection:
            messagebox.showwarning(
                "No Selection",
                "Please select a cardio session to delete.",
            )
            return

        selected_display_index = selection[0]
        original_index = self.cardio_history_display_map[selected_display_index]

        confirm = messagebox.askyesno(
            "Delete Cardio Session",
            "Are you sure you want to delete the selected cardio session?",
        )

        if not confirm:
            return

        delete_cardio_at_index(original_index)

        messagebox.showinfo(
            "Cardio Session Deleted",
            "The selected cardio session was deleted.",
        )

        self.show_cardio_history()

    def clear_all_cardio_confirmed(self) -> None:
        cardio_entries = load_cardio_entries()

        if not cardio_entries:
            messagebox.showwarning(
                "No Cardio Sessions",
                "There are no cardio sessions to clear.",
            )
            return

        confirm = messagebox.askyesno(
            "Clear All Cardio Sessions",
            "Are you sure you want to permanently delete all cardio history?",
        )

        if not confirm:
            return

        clear_cardio_entries()

        messagebox.showinfo(
            "Cardio History Cleared",
            "All cardio history has been removed.",
        )

        self.show_cardio_history()

    def show_workout_history(self) -> None:
        workouts = load_workouts()

        body = self.create_screen(
            "Workout Tracker",
            show_back=True,
            back_command=self.show_dashboard,
        )

        top_section = self.create_section(body)
        top_row = tk.Frame(top_section, bg=self.PANEL_COLOR)
        top_row.pack()

        self.make_button(
            top_row,
            "Add New Workout",
            self.show_log_workout,
            width=18,
        ).pack(side="left", padx=10)

        self.make_button(
            top_row,
            "Delete Selected",
            self.delete_selected_workout,
            width=18,
        ).pack(side="left", padx=10)

        self.make_button(
            top_row,
            "Clear All Workouts",
            self.clear_all_workouts_confirmed,
            width=18,
        ).pack(side="left", padx=10)

        history_section = self.create_section(body)

        tk.Label(
            history_section,
            text="Workout History:",
            font=("Segoe UI", 12, "bold"),
            bg=self.PANEL_COLOR,
        ).pack(anchor="w", pady=(0, 10))

        if not workouts:
            tk.Label(
                history_section,
                text="No workouts logged yet.",
                font=("Segoe UI", 12),
                bg=self.PANEL_COLOR,
            ).pack(anchor="w")

            self.workout_history_listbox = None
            self.history_display_map = []
            return

        list_frame = tk.Frame(history_section, bg=self.PANEL_COLOR)
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.workout_history_listbox = tk.Listbox(
            list_frame,
            width=150,
            height=14,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            bg=self.ENTRY_BG,
            fg=self.TEXT_COLOR,
            selectbackground=self.BUTTON_COLOR,
            selectforeground=self.BUTTON_TEXT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.BORDER_COLOR,
        )
        self.workout_history_listbox.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=self.workout_history_listbox.yview)

        self.history_display_map = []

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

            self.workout_history_listbox.insert(tk.END, workout_text)
            self.history_display_map.append(current_index)

    def delete_selected_workout(self) -> None:
        if self.workout_history_listbox is None or not self.history_display_map:
            messagebox.showwarning("No Workouts", "There are no workouts to delete.")
            return

        selection = self.workout_history_listbox.curselection()

        if not selection:
            messagebox.showwarning("No Selection", "Please select a workout to delete.")
            return

        selected_display_index = selection[0]
        original_index = self.history_display_map[selected_display_index]

        confirm = messagebox.askyesno(
            "Delete Workout",
            "Are you sure you want to delete the selected workout?",
        )

        if not confirm:
            return

        delete_workout_at_index(original_index)

        messagebox.showinfo("Workout Deleted", "The selected workout was deleted.")

        self.show_workout_history()

    def clear_all_workouts_confirmed(self) -> None:
        workouts = load_workouts()

        if not workouts:
            messagebox.showwarning("No Workouts", "There are no workouts to clear.")
            return

        confirm = messagebox.askyesno(
            "Clear All Workouts",
            "Are you sure you want to permanently delete all workout history?",
        )

        if not confirm:
            return

        clear_workouts()

        messagebox.showinfo(
            "Workout History Cleared",
            "All workout history has been removed.",
        )

        self.show_workout_history()

    def not_implemented(self) -> None:
        messagebox.showinfo("Coming Soon", "This feature is not built yet.")
