from schemas import (
    SearchCourseInput,
    CheckScheduleInput,
    RegisterCourseInput,
)

from tools import (
    search_course,
    check_schedule,
    register_course,
)


MAX_TOOL_CALLS = 5


PERMISSIONS = {
    "student": {
        "search_course",
        "check_schedule",
    },
    "admin": {
        "search_course",
        "check_schedule",
        "register_course",
    },
}


TOOL_SCHEMAS = {
    "search_course": SearchCourseInput,
    "check_schedule": CheckScheduleInput,
    "register_course": RegisterCourseInput,
}


TOOL_FUNCTIONS = {
    "search_course": search_course,
    "check_schedule": check_schedule,
    "register_course": register_course,
}


class ToolHarness:

    def __init__(self, role: str):
        self.role = role
        self.tool_calls = 0

    def execute(self, tool_name: str, arguments: dict):
        if self.tool_calls >= MAX_TOOL_CALLS:
            return {
                "success": False,
                "error": "Maximum tool-call limit reached."
            }

        if tool_name not in TOOL_FUNCTIONS:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }

        allowed_tools = PERMISSIONS.get(self.role, set())

        if tool_name not in allowed_tools:
            return {
                "success": False,
                "error": (
                    f"Permission denied: role '{self.role}' "
                    f"cannot use '{tool_name}'."
                )
            }

        schema = TOOL_SCHEMAS[tool_name]

        try:
            validated_input = schema(**arguments)
        except Exception as error:
            return {
                "success": False,
                "error": f"Invalid tool arguments: {error}"
            }

        self.tool_calls += 1

        tool_function = TOOL_FUNCTIONS[tool_name]

        try:
            result = tool_function(**validated_input.model_dump())
            return result

        except Exception:
            return {
                "success": False,
                "error": "Tool execution failed."
            }
