from harness import ToolHarness


def approve(tool_name, arguments, risk_level):
    print("\n--- HUMAN APPROVAL ---")
    print(f"Tool: {tool_name}")
    print(f"Risk: {risk_level}")
    print(f"Arguments: {arguments}")
    return True


def reject(tool_name, arguments, risk_level):
    print("\n--- HUMAN APPROVAL ---")
    print(f"Tool: {tool_name}")
    print(f"Risk: {risk_level}")
    print(f"Arguments: {arguments}")
    return False


print("=" * 60)
print("HARNESS TESTS")
print("=" * 60)


# --------------------------------------------------
# Test 1: LOW-risk tool
# --------------------------------------------------

print("\n[TEST 1] Student searches for a course")

student = ToolHarness("student")

result = student.execute(
    "search_course",
    {"keyword": "Python"}
)

print("Result:", result)


# --------------------------------------------------
# Test 2: Permission control
# --------------------------------------------------

print("\n[TEST 2] Student tries to register a course")

result = student.execute(
    "register_course",
    {"student_id": 1001, "course_id": 1}
)

print("Result:", result)


# --------------------------------------------------
# Test 3: Allowlist
# --------------------------------------------------

print("\n[TEST 3] Student requests an unapproved tool")

result = student.execute(
    "delete_student",
    {"student_id": 1001}
)

print("Result:", result)


# --------------------------------------------------
# Test 4: HIGH-risk without HITL callback
# --------------------------------------------------

print("\n[TEST 4] Admin tries HIGH-risk tool without approval")

admin = ToolHarness("admin")

result = admin.execute(
    "register_course",
    {"student_id": 1002, "course_id": 1}
)

print("Result:", result)


# --------------------------------------------------
# Test 5: HIGH-risk with approval
# --------------------------------------------------

print("\n[TEST 5] Admin approves HIGH-risk tool")

admin_approve = ToolHarness(
    "admin",
    approval_callback=approve
)

result = admin_approve.execute(
    "register_course",
    {"student_id": 1002, "course_id": 1}
)

print("Result:", result)


# --------------------------------------------------
# Test 6: HIGH-risk rejected
# --------------------------------------------------

print("\n[TEST 6] Admin rejects HIGH-risk tool")

admin_reject = ToolHarness(
    "admin",
    approval_callback=reject
)

result = admin_reject.execute(
    "register_course",
    {"student_id": 1001, "course_id": 1}
)

print("Result:", result)
