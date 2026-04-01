from dataclasses import dataclass, asdict


@dataclass
class UserProfile:
    age: int
    sex: str
    height_cm: float
    weight_lb: float
    activity_level: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WorkoutEntry:
    date: str
    exercise: str
    sets: int
    reps: int
    weight: float
    rpe: float

    def to_dict(self) -> dict:
        return asdict(self)