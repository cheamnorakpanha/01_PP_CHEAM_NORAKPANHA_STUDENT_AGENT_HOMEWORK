SEARCH = "search"
SCHEDULE = "schedule"
REGISTER = "register"


class RequestRouter:

    def route(self, user_request: str) -> str:
        request = user_request.lower().strip()

        if self._is_registration_request(request):
            return REGISTER

        if self._is_schedule_request(request):
            return SCHEDULE

        if self._is_search_request(request):
            return SEARCH

        return "unknown"

    def _is_registration_request(self, request: str) -> bool:
        keywords = [
            "register student",
            "register for",
            "registration for",
            "enroll student",
            "enroll in",
            "enrollment for",
        ]

        return any(
            keyword in request
            for keyword in keywords
        )

    def _is_schedule_request(self, request: str) -> bool:
        keywords = [
            "schedule",
            "registered courses",
            "registered for",
            "my courses",
            "courses for student",
            "courses student",
        ]

        return any(
            keyword in request
            for keyword in keywords
        )

    def _is_search_request(self, request: str) -> bool:
        search_words = [
            "search",
            "find",
            "look for",
        ]

        course_words = [
            "course",
            "courses",
        ]

        has_search_word = any(
            word in request
            for word in search_words
        )

        has_course_word = any(
            word in request
            for word in course_words
        )

        return (
            has_search_word and has_course_word
        ) or "available" in request
