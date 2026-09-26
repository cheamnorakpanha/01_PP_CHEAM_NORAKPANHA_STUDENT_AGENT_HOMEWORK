import json
import re

# pyrefly: ignore [missing-import]
import ollama

from harness import MAX_RETRIES, ToolHarness
from router import RequestRouter
from tools import COURSES

MODEL = "llama3.2:latest"
MAX_ITERATIONS = 5

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_course",
            "description": "Search for courses by keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Course name or keyword to search for."
                    }
                },
                "required": ["keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_schedule",
            "description": "Check the courses registered by a student.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "integer",
                        "description": "The student's ID."
                    }
                },
                "required": ["student_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "register_course",
            "description": (
                "Register a student for a course using a numeric course_id. "
                "The course_id must come from search_course. "
                "Never use a course name as course_id. "
                "This action requires admin permission and human approval."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "integer",
                        "description": "The student's ID."
                    },
                    "course_id": {
                        "type": "integer",
                        "description": (
                            "The numeric course ID returned by search_course. "
                            "Do not use the course name here."
                        )
                    }
                },
                "required": ["student_id", "course_id"]
            }
        }
    }
]

SYSTEM_PROMPT = """
You are a simple Student Assistant Agent.

Your job is to help users with course-related requests.

Available capabilities:
- Search for courses.
- Check a student's schedule.
- Register a student for a course.

Rules:
1. Use a tool when the user's request requires information from the application.
2. Use the tool result to decide what to do next.
3. Do not invent tool results.
4. If a tool returns an error, explain the error to the user.
5. Do not try to bypass permission restrictions.
6. Give a concise final answer when the task is complete.
7. Before calling register_course, make sure you have a numeric course_id.
8. If the user provides a course name instead of a course ID, call search_course first.
9. Never use a course name as the course_id.
10. Do not call register_course if the course_id is unknown.
11. Never claim that a student was registered unless register_course
    was actually called and returned success: true.
12. After search_course returns the correct course ID for a registration
    request, call register_course using that course ID.
13. For a registration request, do not give a final answer immediately
    after search_course.
"""


class StudentAgent:
    def __init__(self, role="student"):
        self.role = role
        self.router = RequestRouter()

        self.harness = ToolHarness(
            role,
            approval_callback=self.request_approval
        )

    def request_approval(self, tool_name, arguments, risk_level):
        print("\n" + "=" * 50)
        print("HUMAN APPROVAL REQUIRED")
        print("=" * 50)

        if tool_name == "register_course":
            student_id = arguments["student_id"]
            course_id = arguments["course_id"]

            course = next(
                (
                    course
                    for course in COURSES
                    if course["id"] == course_id
                ),
                None
            )

            if course:
                print(
                    f"Action: Register student {student_id} "
                    f"for {course['name']}"
                )
            else:
                print(
                    f"Action: Register student {student_id} "
                    f"for course {course_id}"
                )

            print(f"Risk Level: {risk_level}")

        else:
            print(f"Action: Execute {tool_name}")
            print(f"Risk Level: {risk_level}")

        print("=" * 50)

        response = input(
            "\nDo you want to approve this action? [y/N]: "
        ).strip().lower()

        return response == "y"

    def extract_registration_request(self, user_request):
        """
        Detect a simple registration request.

        Example:
        'register student 1001 for Python'

        Returns:
        {
            "student_id": 1001,
            "course_keyword": "Python"
        }

        or None if the request is not a registration request.
        """

        pattern = r"register\s+student\s+(\d+)\s+for\s+(.+)"

        match = re.search(
            pattern,
            user_request,
            re.IGNORECASE
        )

        if not match:
            return None

        student_id = int(match.group(1))
        course_keyword = match.group(2).strip()

        return {
            "student_id": student_id,
            "course_keyword": course_keyword
        }

    def handle_search(self, user_request):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_request}
        ]

        return self.run_tool_workflow(messages)

    def handle_schedule(self, user_request):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_request}
        ]

        return self.run_tool_workflow(messages)

    def handle_registration(self, user_request):
        """
        Handle a registration request using a deterministic
        search -> register workflow.

        Both tools still go through the safety harness.
        """

        registration = self.extract_registration_request(user_request)

        if registration is None:
            return None

        if self.role != "admin":
            result = self.harness.execute(
                "register_course",
                {
                    "student_id": registration["student_id"],
                    "course_id": 0
                }
            )

            print("Action: register_course")
            print(f"Arguments: {registration}")
            print(f"Observation: {result}")

            return (
                "I could not register the student because "
                "registration requires admin permission."
            )

        student_id = registration["student_id"]
        course_keyword = registration["course_keyword"]

        print("Registration workflow detected.")

        # Step 1: Search for the course
        print("Action: search_course")
        print(
            f"Arguments: {{'keyword': '{course_keyword}'}}"
        )

        search_result = self.harness.execute(
            "search_course",
            {
                "keyword": course_keyword
            }
        )

        print(f"Observation: {search_result}")

        if not search_result.get("success"):
            return (
                "I could not find the requested course. "
                f"{search_result.get('error', '')}"
            )

        courses = search_result.get("courses", [])

        if not courses:
            return (
                f"No course was found for '{course_keyword}'."
            )

        if len(courses) > 1:
            return (
                "Multiple courses were found. "
                "Please provide a more specific course name."
            )

        course = courses[0]
        course_id = course["id"]

        print()
        print(
            f"Course found: {course['name']} "
            f"(ID: {course_id})"
        )

        # Step 2: Register the student
        print("Action: register_course")

        register_arguments = {
            "student_id": student_id,
            "course_id": course_id
        }

        print(f"Arguments: {register_arguments}")

        register_result = self.harness.execute(
            "register_course",
            register_arguments
        )

        print(f"Observation: {register_result}")

        if not register_result.get("success"):
            return (
                register_result.get(
                    "error",
                    "The registration could not be completed."
                )
            )

        return register_result.get(
            "message",
            "The student was successfully registered."
        )

    def handle_routed_request(self, route, user_request):
        if route == "register":
            return self.handle_registration(user_request)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_request}
        ]

        if route == "search":
            return self.run_tool_workflow(messages)

        if route == "schedule":
            return self.run_tool_workflow(messages)

        return None

    def run_tool_workflow(self, messages):
        for iteration in range(1, MAX_ITERATIONS + 1):
            print(f"\nReAct Step: {iteration}/{MAX_ITERATIONS}")

            response = ollama.chat(
                model=MODEL,
                messages=messages,
                tools=TOOLS
            )

            assistant_message = response["message"]
            messages.append(assistant_message)

            # No tool call = final answer
            if not assistant_message.get("tool_calls"):
                print("Final Answer:")
                print(assistant_message["content"])
                return assistant_message["content"]

            # Tool action
            for tool_call in assistant_message["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                arguments = tool_call["function"]["arguments"]

                print(f"Action: {tool_name}")
                print(f"Arguments: {arguments}")

                # Execute tool through safety harness
                result = self.execute_with_retry(
                    tool_name,
                    arguments
                )

                # Tool observation
                print(f"Observation: {result}")

                messages.append({
                    "role": "tool",
                    "content": json.dumps(result)
                })

        print("Agent stopped: maximum iteration limit reached.")

        return (
            "I could not complete the request "
            "within the allowed number of steps."
        )

    def execute_with_retry(self, tool_name, arguments):
        for attempt in range(MAX_RETRIES + 1):
            result = self.harness.execute(
                tool_name,
                arguments
            )

            if result.get("success"):
                return result

            if not result.get("retryable"):
                return result

            print(
                f"Retrying {tool_name} "
                f"(attempt {attempt + 2}/{MAX_RETRIES + 1})..."
            )

        return result

    def run(self, user_request):
        print(f"\nUser: {user_request}")
        print(f"Role: {self.role}")
        print("-" * 50)

        route = self.router.route(user_request)

        print(f"Route: {route}")

        routed_result = self.handle_routed_request(
            route,
            user_request
        )

        if routed_result is not None:
            return routed_result

        print(
            "Agent: I could not determine how to handle "
            "that request."
        )

        return (
            "I could not determine how to handle "
            "that request."
        )
