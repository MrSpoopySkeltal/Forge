def calculate_bmi(weight_lb: float, height_cm: float) -> float:
    weight_kg = weight_lb * 0.45359237
    height_m = height_cm / 100

    if height_m <= 0:
        raise ValueError("Height must be greater than zero.")

    return weight_kg / (height_m ** 2)


def calculate_bmr(age: int, sex: str, weight_lb: float, height_cm: float) -> float:
    weight_kg = weight_lb * 0.45359237
    sex_lower = sex.strip().lower()

    if sex_lower == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    if sex_lower == "female":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    raise ValueError("Sex must be 'Male' or 'Female'.")


def calculate_tdee(bmr: float, activity_level: str) -> float:
    activity_map = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725,
        "Extra Active": 1.9
    }

    if activity_level not in activity_map:
        raise ValueError("Invalid activity level.")

    return bmr * activity_map[activity_level]


def calculate_macro_targets(weight_lb: float, tdee: float, goal: str) -> dict:
    goal_key = goal.strip().lower()

    if goal_key == "cut":
        calories = tdee - 500
        protein = weight_lb * 1.0
        fats = weight_lb * 0.30
    elif goal_key == "maintenance":
        calories = tdee
        protein = weight_lb * 0.90
        fats = weight_lb * 0.35
    elif goal_key == "bulk":
        calories = tdee + 300
        protein = weight_lb * 1.0
        fats = weight_lb * 0.35
    elif goal_key == "recomp":
        calories = tdee - 200
        protein = weight_lb * 1.0
        fats = weight_lb * 0.30
    else:
        raise ValueError("Goal must be Cut, Maintenance, Bulk, or Recomp.")

    protein_calories = protein * 4
    fat_calories = fats * 9
    carbs = (calories - protein_calories - fat_calories) / 4

    if carbs < 0:
        raise ValueError("Calculated carbs cannot be negative. Check calorie and macro settings.")

    return {
        "goal": goal.title(),
        "calories": round(calories),
        "protein_g": round(protein),
        "carbs_g": round(carbs),
        "fats_g": round(fats)
    }


def evaluate_progressive_overload(previous_workout, current_workout) -> str:
    if previous_workout is None:
        return "First logged workout for this exercise. Build a baseline and repeat next session."

    if (
        current_workout.weight > previous_workout.weight
        and current_workout.reps >= previous_workout.reps
    ):
        return "Progress detected: increase achieved. Keep pushing."

    if (
        current_workout.weight == previous_workout.weight
        and current_workout.reps > previous_workout.reps
    ):
        return "Progress detected: more reps completed at the same weight."

    if (
        current_workout.weight == previous_workout.weight
        and current_workout.reps == previous_workout.reps
    ):
        return "Performance matched the last session. Hold steady or aim for one more rep next time."

    return "Performance was below the last session. Repeat this weight or reduce fatigue before increasing."


def get_progression_recommendation(previous_workout, current_workout) -> str:
    if previous_workout is None:
        return "Baseline established. Repeat this weight next session and aim to add 1 rep."

    exercise_name = current_workout.exercise.strip().lower()
    lower_body_keywords = [
        "squat",
        "deadlift",
        "leg press",
        "lunge",
        "rdl",
        "hip thrust",
        "leg curl",
        "leg extension"
    ]

    is_lower_body = any(keyword in exercise_name for keyword in lower_body_keywords)
    weight_increase = 10 if is_lower_body else 5

    if current_workout.rpe >= 9.5:
        return "RPE was very high. Hold this weight steady next session and focus on cleaner reps."

    if (
        current_workout.weight > previous_workout.weight
        and current_workout.reps >= previous_workout.reps
    ):
        return "You increased the load successfully. Stay here and try to add 1 more rep next session."

    if (
        current_workout.weight == previous_workout.weight
        and current_workout.reps > previous_workout.reps
    ):
        if current_workout.reps >= 12 and current_workout.rpe <= 8.0:
            return f"Top of rep range reached. Increase weight by {weight_increase} lb next session."
        return "Progress detected. Keep the same weight and try to add 1 more rep next session."

    if (
        current_workout.weight == previous_workout.weight
        and current_workout.reps == previous_workout.reps
    ):
        return "Matched last session. Repeat this weight and try to add 1 rep next time."

    return "Performance dropped. Repeat this weight until reps recover, or reduce fatigue before increasing."