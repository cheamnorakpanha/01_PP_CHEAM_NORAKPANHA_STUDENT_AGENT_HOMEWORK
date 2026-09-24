
import json
# pyrefly: ignore [missing-import]
import ollama

from harness import ToolHarness


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
                "Register a student for a course. "
                "This action requires admin permission."
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
                        "description": "The course ID."
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
"""


class StudentAgent:

    def __init__(self, role="student"):
        self.role = role
        self.harness = ToolHarness(role)

    def run(self, user_request):

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_request
            }
        ]

        print(f"\nUser: {user_request}")
        print(f"Role: {self.role}")
        print("-" * 50)

        for iteration in range(1, MAX_ITERATIONS + 1):

            print(f"Iteration: {iteration}/{MAX_ITERATIONS}")

            response = ollama.chat(
                model=MODEL,
                messages=messages,
                tools=TOOLS
            )

            assistant_message = response["message"]

            messages.append(assistant_message)

            if not assistant_message.get("tool_calls"):
                print(f"Agent: {assistant_message['content']}")
                return assistant_message["content"]

            for tool_call in assistant_message["tool_calls"]:

                tool_name = tool_call["function"]["name"]
                arguments = tool_call["function"]["arguments"]

                print(f"Tool call: {tool_name}")
                print(f"Arguments: {arguments}")

                result = self.harness.execute(
                    tool_name,
                    arguments
                )

                print(f"Tool result: {result}")

                messages.append(
                    {
                        "role": "tool",
                        "content": json.dumps(result)
                    }
                )

        print("Agent stopped: maximum iteration limit reached.")

        return (
            "I could not complete the request within "
            "the allowed number of steps."
        )


if __name__ == "__main__":
    agent = StudentAgent(role="student")

    agent.run(
        "Keep checking my schedule again and again."
    )
