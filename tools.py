import json
from pathlib import Path


DATA_FILE = (Path(__file__).parent / "data" / "courses.json")


def load_data():
    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        courses = data.get("courses", [])

        student_schedules = {
            int(student_id): course_ids
            for student_id, course_ids
            in data.get("student_schedules", {}).items()
        }

        return courses, student_schedules

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ) as error:
        raise RuntimeError(
            f"Failed to load course data: {error}"
        )


COURSES, STUDENT_SCHEDULES = load_data()


def search_course(keyword: str):
    keyword = keyword.strip().lower()

    # Empty keyword means "return all available courses"
    if not keyword:
        return {
            "success": True,
            "courses": COURSES
        }

    results = [
        course
        for course in COURSES
        if keyword in course["name"].lower()
    ]

    return {
        "success": True,
        "courses": results
    }


def check_schedule(student_id: int):
    if student_id <= 0:
        return {
            "success": False,
            "error": "Student ID must be positive."
        }

    course_ids = STUDENT_SCHEDULES.get(student_id)

    if course_ids is None:
        return {
            "success": False,
            "error": (
                f"Student {student_id} was not found."
            )
        }

    courses = [
        course
        for course in COURSES
        if course["id"] in course_ids
    ]

    return {
        "success": True,
        "student_id": student_id,
        "courses": courses
    }


def register_course(
    student_id: int,
    course_id: int
):
    if student_id <= 0:
        return {
            "success": False,
            "error": "Student ID must be positive."
        }

    if course_id <= 0:
        return {
            "success": False,
            "error": "Course ID must be positive."
        }

    if student_id not in STUDENT_SCHEDULES:
        return {
            "success": False,
            "error": (
                f"Student {student_id} was not found."
            )
        }

    course = next(
        (
            course
            for course in COURSES
            if course["id"] == course_id
        ),
        None
    )

    if course is None:
        return {
            "success": False,
            "error": (
                f"Course {course_id} was not found."
            )
        }

    if course_id in STUDENT_SCHEDULES[student_id]:
        return {
            "success": False,
            "error": (
                "Student is already registered "
                "for this course."
            )
        }

    STUDENT_SCHEDULES[student_id].append(course_id)

    return {
        "success": True,
        "message": (
            f"Student {student_id} successfully "
            f"registered for {course['name']}."
        ),
        "course": course
    }
