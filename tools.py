COURSES = [
    {
        "id": 1,
        "name": "Python Programming",
        "teacher": "Mr. Dara",
        "schedule": "Monday 6:00 PM - 8:00 PM",
    },
    {
        "id": 2,
        "name": "Artificial Intelligence",
        "teacher": "Ms. Srey",
        "schedule": "Tuesday 6:00 PM - 8:00 PM",
    },
    {
        "id": 3,
        "name": "Data Analytics",
        "teacher": "Mr. Vannak",
        "schedule": "Wednesday 6:00 PM - 8:00 PM",
    },
    {
        "id": 4,
        "name": "Korean Language",
        "teacher": "Ms. Mina",
        "schedule": "Friday 6:00 PM - 8:00 PM",
    },
]


STUDENT_SCHEDULES = {
    1001: [2, 4],
    1002: [1, 3],
}


def search_course(keyword: str):
    """Search for courses by name."""

    keyword = keyword.strip().lower()

    if not keyword:
        return {
            "success": False,
            "error": "Search keyword cannot be empty."
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
    """Check the courses registered by a student."""

    if student_id <= 0:
        return {
            "success": False,
            "error": "Student ID must be positive."
        }

    course_ids = STUDENT_SCHEDULES.get(student_id)

    if course_ids is None:
        return {
            "success": False,
            "error": f"Student {student_id} was not found."
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


def register_course(student_id: int, course_id: int):
    """Register a student for a course."""

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
            "error": f"Student {student_id} was not found."
        }

    course = next(
        (course for course in COURSES if course["id"] == course_id),
        None
    )

    if course is None:
        return {
            "success": False,
            "error": f"Course {course_id} was not found."
        }

    if course_id in STUDENT_SCHEDULES[student_id]:
        return {
            "success": False,
            "error": "Student is already registered for this course."
        }

    STUDENT_SCHEDULES[student_id].append(course_id)

    return {
        "success": True,
        "message": (
            f"Student {student_id} successfully registered "
            f"for {course['name']}."
        ),
        "course": course
    }
