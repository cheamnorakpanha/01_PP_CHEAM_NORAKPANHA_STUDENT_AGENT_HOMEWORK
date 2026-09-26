from schemas import SearchCourseInput, CheckScheduleInput, RegisterCourseInput
from tools import search_course, check_schedule, register_course


MAX_TOOL_CALLS = 5

ALLOWED_TOOLS = {
    "search_course",
    "check_schedule",
    "register_course",
}

TOOL_RISK_LEVELS = {
    "search_course": "LOW",
    "check_schedule": "LOW",
    "register_course": "HIGH",
}

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
    def __init__(self, role: str, approval_callback=None):
        self.role = role
        self.tool_calls = 0
        self.approval_callback = approval_callback

    def execute(self, tool_name: str, arguments: dict):

        if tool_name not in ALLOWED_TOOLS:
            return {
                "success": False,
                "error_code": "TOOL_NOT_ALLOWED",
                "error": f"Tool '{tool_name}' is not allowed."
            }

        risk_level = TOOL_RISK_LEVELS.get(tool_name)

        if risk_level is None:
            return {
                "success": False,
                "error_code": "RISK_NOT_DEFINED",
                "error": (
                    f"Risk level is not defined for tool '{tool_name}'."
                )
            }

        if self.tool_calls >= MAX_TOOL_CALLS:
            return {
                "success": False,
                "error_code": "TOOL_CALL_LIMIT",
                "error": "Maximum tool-call limit reached."
            }

        allowed_tools = PERMISSIONS.get(self.role, set())

        if tool_name not in allowed_tools:
            return {
                "success": False,
                "error_code": "PERMISSION_DENIED",
                "error": (
                    f"Permission denied: role '{self.role}' "
                    f"cannot use '{tool_name}'."
                )
            }

        schema = TOOL_SCHEMAS[tool_name]

        try:
            validated_input = schema(**arguments)

        except Exception:
            if tool_name == "register_course":
                return {
                    "success": False,
                    "error_code": "COURSE_ID_REQUIRED",
                    "error": (
                        "A valid numeric course_id is required for "
                        "registration. If the user provided a course name, "
                        "call search_course first to find the correct "
                        "course_id, then call register_course again."
                    )
                }

            return {
                "success": False,
                "error_code": "INVALID_ARGUMENT",
                "error": "Invalid tool arguments."
            }

        if risk_level == "HIGH":

            if self.approval_callback is None:
                return {
                    "success": False,
                    "error_code": "APPROVAL_REQUIRED",
                    "error": (
                        f"Human approval required for high-risk tool "
                        f"'{tool_name}'."
                    )
                }

            approved = self.approval_callback(
                tool_name,
                validated_input.model_dump(),
                risk_level
            )

            if not approved:
                return {
                    "success": False,
                    "error_code": "APPROVAL_DENIED",
                    "error": (
                        f"Human approval denied for '{tool_name}'."
                    )
                }

        self.tool_calls += 1

        tool_function = TOOL_FUNCTIONS[tool_name]

        try:
            result = tool_function(
                **validated_input.model_dump()
            )

            return result

        except Exception:
            return {
                "success": False,
                "error_code": "TOOL_EXECUTION_FAILED",
                "error": "Tool execution failed."
            }
