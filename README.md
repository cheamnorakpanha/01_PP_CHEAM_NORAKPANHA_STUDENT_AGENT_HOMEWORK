# Safe Student Assistant Agent

A simple safe agent built for **AI Engineering — Topic 07: Autonomous Agents & Tool Integration**.

The agent uses a local LLM through Ollama to receive a student request, choose an appropriate tool, execute it through a safety harness, observe the result, and produce a final answer.

The project demonstrates:

- Agent tool calling
- Structured tool inputs
- Permission control
- Input validation
- Error handling
- Bounded agent iterations

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
User
  ↓
main.py
  ↓
agent.py
  ↓
Ollama / Llama 3.2
  ↓
Tool Call
  ↓
harness.py
  ↓
Permission + Validation + Safety Checks
  ↓
tools.py
  ↓
Tool Result
  ↓
Agent
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

Registers a student for a course.

Example:

```python
register_course(student_id=1001, course_id=1)
```

> **Note:** This tool requires `admin` permission.

---

## 3. Agent Loop

The agent follows a tool-using loop:

```text
User Request
     ↓
Agent / LLM
     ↓
Tool Call
     ↓
Harness
     ↓
Tool Execution
     ↓
Tool Result
     ↓
Agent Observes Result
     ↓
Final Answer
```

After receiving a tool result, the agent can decide whether another step is required.

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
Iteration: 1/5
Tool call: search_course
Arguments: {'keyword': 'python'}
Tool result: {'success': True, 'courses': [{'id': 1, 'name': 'Python Programming', 'teacher': 'Mr. Dara', 'schedule': 'Monday 6:00 PM - 8:00 PM'}]}
Iteration: 2/5
Agent: You can register for the Python Programming course, which is taught by Mr. Dara and scheduled on Mondays from 6:00 PM to 8:00 PM.
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

The agent requests `register_course`, but the harness rejects the tool call because students do not have permission to register courses.

```text
Tool result:
{
    'success': False,
    'error': "Permission denied: role 'student' cannot use 'register_course'."
}
```

The agent then observes the error and provides a final response.

---

## 7. Project Structure

```text
safe-student-agent-homework/
│
├── README.md
├── main.py
├── agent.py
├── tools.py
├── schemas.py
├── harness.py
├── requirements.txt
└── .gitignore
```

### File Responsibilities

| File               | Purpose                                            |
| ------------------ | -------------------------------------------------- |
| `main.py`          | Application entry point and user input             |
| `agent.py`         | Agent loop and LLM tool calling                    |
| `tools.py`         | Tool implementations                               |
| `schemas.py`       | Pydantic input schemas                             |
| `harness.py`       | Permission, validation, and tool execution control |
| `requirements.txt` | Python dependencies                                |
| `.gitignore`       | Files excluded from Git                            |

---

## 8. Installation

Install the required Python dependencies:

```powershell
pip install -r requirements.txt
```

Make sure Ollama is installed and the `llama3.2` model is available.

Check installed models:

```powershell
ollama list
```

If necessary, download the model:

```powershell
ollama pull llama3.2
```

---

## 9. Run the Agent

Start the application:

```powershell
python main.py
```

Enter a role:

```text
student
```

Then enter a request, for example:

```text
I want python course
```

The agent will:

1. Send the request to the LLM.
2. Select an appropriate tool.
3. Validate and authorize the tool call.
4. Execute the tool.
5. Observe the tool result.
6. Continue if another step is needed.
7. Return the final answer.
