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
                "error": f"Tool '{tool_name}' is not allowed."
            }

        risk_level = TOOL_RISK_LEVELS.get(tool_name)

        if risk_level is None:
            return {
                "success": False,
                "error": f"Risk level is not defined for tool '{tool_name}'."
            }

        if self.tool_calls >= MAX_TOOL_CALLS:
            return {
                "success": False,
                "error": "Maximum tool-call limit reached."
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

        if risk_level == "HIGH":
            if self.approval_callback is None:
                return {
                    "success": False,
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
                    "error": f"Human approval denied for '{tool_name}'."
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
