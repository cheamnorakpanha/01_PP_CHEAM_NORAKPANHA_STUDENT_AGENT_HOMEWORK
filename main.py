from agent import StudentAgent


def main():
    print("=" * 50)
    print("       SAFE STUDENT ASSISTANT AGENT")
    print("=" * 50)

    role = input("\nEnter your role (student/admin): ").strip().lower()

    if role not in {"student", "admin"}:
        print("Invalid role. Please use 'student' or 'admin'.")
        return

    user_request = input("Enter the request: ").strip()

    if not user_request:
        print("request cannot be empty.")
        return

    agent = StudentAgent(role=role)

    print("\n" + "=" * 50)
    print("             AI RESPONSE")
    print("=" * 50)

    agent.run(user_request)


if __name__ == "__main__":
    main()
