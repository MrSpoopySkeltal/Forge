import json
from pathlib import Path
from typing import List, Optional

from models import UserProfile, WorkoutEntry


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROFILE_PATH = DATA_DIR / "profile.json"
WORKOUTS_PATH = DATA_DIR / "workouts.json"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(exist_ok=True)


def save_profile(profile: UserProfile) -> None:
    ensure_data_dir()

    with open(PROFILE_PATH, "w", encoding="utf-8") as file:
        json.dump(profile.to_dict(), file, indent=4)


def load_profile() -> Optional[UserProfile]:
    ensure_data_dir()

    if not PROFILE_PATH.exists():
        return None

    with open(PROFILE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    return UserProfile(
        age=int(data["age"]),
        sex=str(data["sex"]),
        height_cm=float(data["height_cm"]),
        weight_lb=float(data["weight_lb"]),
        activity_level=str(data["activity_level"])
    )


def save_workout(entry: WorkoutEntry) -> None:
    ensure_data_dir()

    workouts = load_workouts()
    workouts.append(entry)
    _write_workouts(workouts)


def load_workouts() -> List[WorkoutEntry]:
    ensure_data_dir()

    if not WORKOUTS_PATH.exists():
        return []

    with open(WORKOUTS_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    workouts: List[WorkoutEntry] = []

    for item in data:
        workouts.append(
            WorkoutEntry(
                date=str(item["date"]),
                exercise=str(item["exercise"]),
                sets=int(item["sets"]),
                reps=int(item["reps"]),
                weight=float(item["weight"]),
                rpe=float(item["rpe"])
            )
        )

    return workouts


def get_previous_workout(exercise_name: str) -> Optional[WorkoutEntry]:
    workouts = load_workouts()
    matching_workouts = [
        workout for workout in workouts
        if workout.exercise.strip().lower() == exercise_name.strip().lower()
    ]

    if not matching_workouts:
        return None

    return matching_workouts[-1]


def delete_workout_at_index(index: int) -> None:
    workouts = load_workouts()

    if 0 <= index < len(workouts):
        del workouts[index]
        _write_workouts(workouts)


def clear_workouts() -> None:
    _write_workouts([])


def _write_workouts(workouts: List[WorkoutEntry]) -> None:
    ensure_data_dir()

    with open(WORKOUTS_PATH, "w", encoding="utf-8") as file:
        json.dump([workout.to_dict() for workout in workouts], file, indent=4)
