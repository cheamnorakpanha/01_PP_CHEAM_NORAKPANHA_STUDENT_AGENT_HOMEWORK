# Safe Student Assistant Agent

A simple safe agent built for **AI Engineering — Topic 07: Autonomous Agents & Tool Integration**.

The agent uses a local LLM through Ollama to process student requests, route them to the appropriate workflow, choose and call tools when needed, execute them through a safety harness, observe the results, and produce a final answer.

The project demonstrates:

- Agent tool calling
- Request routing
- Structured tool inputs
- Permission control
- Input validation
- Risk classification
- Human-in-the-loop approval
- Error handling
- Retry and failure boundaries
- Bounded agent iterations

---

## 0. Installation and Run Instructions

Install the required Python dependencies:

```powershell
pip install -r requirements.txt
```

Make sure Ollama is installed and the llama3.2 model is available.

Check installed models:

```powershell
ollama list
```

If necessary, download the model:

```powershell
ollama pull llama3.2
```

Start the application:

```powershell
python main.py
```

Enter a role:

```text
student
```

or:

```text
admin
```

Then enter a request, for example:

```text
I want python course
```

The agent will:

1. Receive the user request.
2. Route the request.
3. Send the request to the local LLM when tool use is required.
4. Select an appropriate tool.
5. Validate and authorize the tool call.
6. Execute the tool.
7. Observe the tool result.
8. Continue if another step is required.
9. Return the final answer.

---

## 1. Project Overview

The **Safe Student Assistant Agent** helps users with course-related tasks.

The agent can:

- Search for available courses
- Check a student's schedule
- Register a student for a course

The application uses **Llama 3.2** through Ollama as the local LLM.

### Architecture

```text
User Request
     ↓
main.py
     ↓
Request Router
     ↓
agent.py
     ↓
Ollama / Llama 3.2
     ↓
Tool Call
     ↓
Safety Harness
     ├── Allowlist
     ├── Permission Check
     ├── Pydantic Validation
     ├── Risk Classification
     ├── HITL Approval
     └── Tool Call Limit
     ↓
tools.py
     ↓
data/courses.json
     ↓
Tool Result
     ↓
Agent / ReAct Loop
     ↓
Final Answer
```

---

## 2. Available Tools

The agent has three tools.

### `search_course(keyword)`

Searches for available courses using a keyword.

Example:

```python
search_course(keyword="Python")
```

Example result:

```text
Python Programming
Teacher: Mr. Dara
Schedule: Monday 6:00 PM - 8:00 PM
```

### `check_schedule(student_id)`

Checks the courses registered by a student.

Example:

```python
check_schedule(student_id=1001)
```

### `register_course(student_id, course_id)`

Registers a student for a course using the course ID.

Example:

```python
register_course(student_id=1001, course_id=1)
```

> **Note:** This tool requires `admin` permission and human approval because it is classified as a high-risk action.

---

## 3. Agent Loop

The agent follows a tool-using ReAct-style loop:

```text
User Request
     ↓
Request Router
     ↓
Agent / LLM
     ↓
Tool Call
     ↓
Safety Harness
     ↓
Tool Execution
     ↓
Tool Result
     ↓
Agent Observes Result
     ↓
Agent Decides Again
     ↓
Final Answer
```

After receiving a tool result, the agent can decide whether another step is required.

For example, a registration request may require:

```text
User Request
     ↓
search_course
     ↓
Course ID found
     ↓
register_course
     ↓
Human Approval
     ↓
Registration Result
     ↓
Final Answer
```

The maximum number of agent iterations is **5**. This prevents the agent from running indefinitely.

---

## 4. Permission Rule

The application supports two roles:

- `student`
- `admin`

### Permission Table

| Tool              | Student | Admin |
| ----------------- | ------- | ----- |
| `search_course`   | Yes     | Yes   |
| `check_schedule`  | Yes     | Yes   |
| `register_course` | No      | Yes   |

Permission is enforced in `harness.py` before a tool is executed.

The LLM cannot bypass this application-level permission check.

### Example

If a student requests:

```text
Register student 1001 for course 1.
```

The agent may request `register_course`, but the harness checks the user's role before executing the tool.

For a student, the tool call is rejected:

```text
Permission denied: role 'student' cannot use 'register_course'.
```

The application therefore prevents the restricted action regardless of what the LLM requests.

---

## 5. Safety

The project includes several safety controls.

### Input Validation

Tool arguments are validated using **Pydantic** schemas before execution.

For example:

```python
student_id: int = Field(..., gt=0)
```

Student IDs and course IDs must be positive integers.

Invalid arguments are rejected before the tool executes.

### Tool Allowlist

Only explicitly allowed tools can be executed:

```python
ALLOWED_TOOLS = {
    "search_course",
    "check_schedule",
    "register_course"
}
```

Unknown or unauthorized tools are rejected by the harness.

### Risk Classification

Tools are assigned risk levels.

```python
TOOL_RISK_LEVELS = {
    "search_course": "LOW",
    "check_schedule": "LOW",
    "register_course": "HIGH"
}
```

High-risk actions require human approval before execution.

### Human-in-the-Loop

Before executing `register_course`, the application asks for human approval.

Example:

```text
==================================================
HUMAN APPROVAL REQUIRED
==================================================
Action: Register student 1001 for Data Analytics
Risk Level: HIGH
==================================================

Do you want to approve this action? [y/N]:
```

If the user enters `y`, the action proceeds.
If the user enters `n`, the action is rejected.

### Error Handling

Tool execution errors are returned as controlled results instead of exposing application failures.

Example:

```json
{
  "success": false,
  "error": "Student 9999 was not found."
}
```

The agent can observe the error and provide an appropriate response.

### Retry and Failure Boundaries

Tool execution failures can be retried up to **2 times** when the error is retryable.

After the retry limit is reached, the harness stops retrying and returns a controlled failure.

### Maximum Limits

The agent has a maximum of **5 iterations**.

The tool harness also limits the total number of tool calls to **5**.

These limits help prevent uncontrolled execution loops.

---

## 6. Example Run

### Example 1 — Searching for a Course

User request:

```text
I want python course
```

Agent execution:

```text
User: I want python course
Role: student
--------------------------------------------------

Route: search

ReAct Step: 1/5

Action: search_course
Arguments: {'keyword': 'python'}

Observation: {'success': True, 'courses': [{'id': 1, 'name': 'Python Programming', 'teacher': 'Mr. Dara', 'schedule': 'Monday 6:00 PM - 8:00 PM'}]}

ReAct Step: 2/5

Final Answer:
You can register for the Python Programming course,
which is taught by Mr. Dara and scheduled on Mondays
from 6:00 PM to 8:00 PM.
```

### Example 2 — Permission Control

User request:

```text
Register student 1001 for course 1.
```

Role:

```text
student
```

The application rejects the registration because students do not have permission to use `register_course`.

```text
Observation: {
    'success': False,
    'error_code': 'PERMISSION_DENIED',
    'error': "Permission denied: role 'student' cannot use 'register_course'."
}

Final Answer:
I could not register the student because registration
requires admin permission.
```

The agent then observes the error and provides a final response.

### Example 3 — Human-in-the-Loop

User request:

```text
Register student 1002 for Korean Language
```

Role:

```text
admin
```

The agent first searches for the course:

```text
Action: search_course
Arguments: {'keyword': 'Korean Language'}
```

The course is found:

```text
Course found: Korean Language (ID: 4)
```

The agent then requests approval before registration:

```text
==================================================
HUMAN APPROVAL REQUIRED
==================================================
Action: Register student 1002 for Korean Language
Risk Level: HIGH
==================================================

Do you want to approve this action? [y/N]:
```

If approved:

```text
Student 1002 successfully registered for Korean Language.
```
