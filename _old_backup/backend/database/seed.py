from datetime import datetime, timedelta
from backend.database.connection import SessionLocal, Base, engine
from backend.database.models import (
    User, Course, Assignment, Exam, Announcement, Document,
    Reminder, CalendarEvent, Email, Task, AuditLog
)

def init_db():
    Base.metadata.create_all(bind=engine)
    seed_demo_data()

def seed_demo_data():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Course).first():
            return
        
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        in_two_days = today + timedelta(days=2)
        in_five_days = today + timedelta(days=5)

        # 1. User
        user = User(
            name="Alex Rivers",
            email="alex.rivers@university.edu",
            student_id="STU-2026-8842",
            major="Computer Science & Artificial Intelligence",
            semester="Fall 2026 / Senior Year"
        )
        db.add(user)

        # 2. Courses
        c_ai = Course(
            code="CS401",
            name="Artificial Intelligence",
            instructor="Dr. Elena Martinez",
            instructor_email="elena.martinez@university.edu",
            room="Hall 304",
            schedule="Mon/Wed 10:00 AM - 11:30 AM",
            description="Foundations of AI, heuristic search, neural networks, machine learning, and knowledge representation."
        )
        c_algo = Course(
            code="CS350",
            name="Advanced Data Structures & Algorithms",
            instructor="Prof. Alan Turing",
            instructor_email="alan.turing@university.edu",
            room="Hall 105",
            schedule="Tue/Thu 1:00 PM - 2:30 PM",
            description="Graph algorithms, dynamic programming, balanced trees, and algorithmic complexity."
        )
        c_db = Course(
            code="CS480",
            name="Database Systems & Cloud Storage",
            instructor="Dr. Brenda Smith",
            instructor_email="bsmith@university.edu",
            room="Lab 201",
            schedule="Mon/Wed 2:00 PM - 3:30 PM",
            description="Relational database design, query optimization, indexing, transactions, and distributed databases."
        )
        c_math = Course(
            code="MATH310",
            name="Linear Algebra & Optimization",
            instructor="Prof. Carl Gauss",
            instructor_email="cgauss@university.edu",
            room="Hall 210",
            schedule="Fri 9:00 AM - 12:00 PM",
            description="Vector spaces, eigenvalues, matrix decompositions, and convex optimization in machine learning."
        )
        db.add_all([c_ai, c_algo, c_db, c_math])
        db.flush()

        # 3. Assignments
        a1 = Assignment(
            course_id=c_ai.id,
            title="AI Assignment 3: Deep Neural Networks & Backprop",
            description="Implement a multi-layer perceptron from scratch with backpropagation on the MNIST dataset.",
            due_date=in_two_days.replace(hour=23, minute=59),
            points=100,
            status="pending"
        )
        a2 = Assignment(
            course_id=c_algo.id,
            title="Binary Search Tree & Red-Black Tree Implementation",
            description="Implement balanced BST insertion, rotation, and deletion in Python/C++.",
            due_date=tomorrow.replace(hour=17, minute=0),
            points=100,
            status="pending"
        )
        a3 = Assignment(
            course_id=c_db.id,
            title="Relational Schema Normalization & BCNF Project",
            description="Design an e-commerce database schema, identify functional dependencies, and normalize to 3NF/BCNF.",
            due_date=in_five_days.replace(hour=23, minute=59),
            points=100,
            status="pending"
        )
        a4 = Assignment(
            course_id=c_ai.id,
            title="AI Assignment 2: A* Search & Heuristics",
            description="Solve 8-puzzle problem using Manhattan distance and custom admissible heuristics.",
            due_date=today - timedelta(days=7),
            points=100,
            status="graded",
            submission_text="Submitted code repository and report.",
            submitted_at=today - timedelta(days=7, hours=2),
            grade=96.0
        )
        db.add_all([a1, a2, a3, a4])

        # 4. Exams
        e1 = Exam(
            course_id=c_ai.id,
            title="Midterm Exam: Artificial Intelligence",
            date=tomorrow,
            start_time="10:00 AM",
            end_time="12:00 PM",
            room="Hall 304",
            topics="Search Algorithms (BFS, DFS, A*, IDA*), Alpha-Beta Pruning, Neural Network Architectures, Backpropagation, Loss Functions",
            weight_percent=30
        )
        e2 = Exam(
            course_id=c_algo.id,
            title="Quiz 3: Balanced Search Trees & Graphs",
            date=today + timedelta(days=4),
            start_time="02:00 PM",
            end_time="03:00 PM",
            room="Hall 105",
            topics="Red-Black Trees, AVL Trees, Dijkstra, Bellman-Ford",
            weight_percent=15
        )
        db.add_all([e1, e2])

        # 5. Announcements
        an1 = Announcement(
            course_id=c_ai.id,
            title="CS401 AI Midterm Exam Format & Review Sheet",
            content="The midterm tomorrow in Hall 304 will have 20 multiple choice questions and 4 problem-solving questions. Formulas for backprop will be provided.",
            author="Dr. Elena Martinez",
            created_at=today - timedelta(hours=6),
            is_urgent=True
        )
        an2 = Announcement(
            course_id=c_algo.id,
            title="CS350 Tree Assignment Office Hours Extension",
            content="TAs will hold extended office hours today from 4:00 PM to 7:00 PM in Lab 102 for the Red-Black tree project.",
            author="Prof. Alan Turing",
            created_at=today - timedelta(hours=14),
            is_urgent=False
        )
        an3 = Announcement(
            course_id=None,
            title="Campus Library 24/7 Hours for Midterm Week",
            content="The main library will be open 24 hours daily with free study rooms and coffee available on Level 2.",
            author="Campus Services",
            created_at=today - timedelta(days=1),
            is_urgent=False
        )
        db.add_all([an1, an2, an3])

        # 6. Emails
        m1 = Email(
            sender="elena.martinez@university.edu",
            sender_name="Dr. Elena Martinez",
            recipient="alex.rivers@university.edu",
            subject="CS401: Midterm Preparation & Study Materials",
            body="Dear Alex,\n\nTomorrow is our Artificial Intelligence Midterm exam at 10:00 AM in Hall 304. Please make sure to review heuristic search, A* admissibility, neural network backprop gradients, and decision trees. Bring a student ID and a non-programmable calculator.\n\nBest regards,\nDr. Martinez",
            received_at=today - timedelta(hours=4),
            is_read=False,
            category="academic"
        )
        m2 = Email(
            sender="alan.turing@university.edu",
            sender_name="Prof. Alan Turing",
            recipient="alex.rivers@university.edu",
            subject="CS350: BST Lab Extension Request",
            body="Hi Alex,\n\nI received your note about the BST lab. The extension until tomorrow 5:00 PM is approved. Make sure your unit tests for tree balancing pass before submitting.\n\nCheers,\nProf. Turing",
            received_at=today - timedelta(hours=8),
            is_read=True,
            category="academic"
        )
        m3 = Email(
            sender="advisor@university.edu",
            sender_name="Academic Advising",
            recipient="alex.rivers@university.edu",
            subject="Senior Year Capstone Project Registration Deadline",
            body="Alex, please confirm your capstone project advisor and proposal topic by Friday so your graduation audit remains clear.\n\nOffice of Academic Advising",
            received_at=today - timedelta(days=1),
            is_read=True,
            category="administrative"
        )
        db.add_all([m1, m2, m3])

        # 7. Calendar Events
        cal1 = CalendarEvent(
            title="CS401 AI Lecture",
            start_datetime=today.replace(hour=10, minute=0),
            end_datetime=today.replace(hour=11, minute=30),
            location="Hall 304",
            event_type="class",
            course_id=c_ai.id,
            description="Regular lecture on Neural Networks"
        )
        cal2 = CalendarEvent(
            title="AI Midterm Study Group",
            start_datetime=today.replace(hour=18, minute=0),
            end_datetime=today.replace(hour=20, minute=0),
            location="Campus Library Room 2B",
            event_type="study",
            description="Review session with classmates on A* and Backprop"
        )
        cal3 = CalendarEvent(
            title="CS401 Midterm Exam",
            start_datetime=tomorrow.replace(hour=10, minute=0),
            end_datetime=tomorrow.replace(hour=12, minute=0),
            location="Hall 304",
            event_type="exam",
            course_id=c_ai.id,
            description="Formal Midterm Exam for Artificial Intelligence"
        )
        cal4 = CalendarEvent(
            title="CS350 Algorithm Lab Session",
            start_datetime=tomorrow.replace(hour=13, minute=0),
            end_datetime=tomorrow.replace(hour=15, minute=0),
            location="Lab 105",
            event_type="class",
            course_id=c_algo.id,
            description="Balanced Tree hands-on coding"
        )
        db.add_all([cal1, cal2, cal3, cal4])

        # 8. Reminders
        r1 = Reminder(
            title="Review AI Midterm Flashcards and Notes",
            description="Focus on Backprop equations and Alpha-Beta search.",
            due_datetime=today.replace(hour=19, minute=0),
            recurrence="none",
            is_completed=False
        )
        r2 = Reminder(
            title="Finish BST Tree Code and submit before 5 PM",
            description="Run pytest suite on balanced tree implementation.",
            due_datetime=tomorrow.replace(hour=16, minute=0),
            recurrence="none",
            is_completed=False
        )
        db.add_all([r1, r2])

        # 9. Audit Log Initial Entry
        log = AuditLog(
            event_type="SYSTEM_INIT",
            tool_name="database.seed",
            details="Demo academic environment initialized with CS401, CS350, CS480, MATH310 data.",
            status="SUCCESS"
        )
        db.add(log)

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("Database seeded successfully.")
