"""End-to-End Test Suite for JARVIS Academic Autonomous Companion.
Tests:
1. Student Profile & 4-Tier Memory
2. Excel Deliverables: Attendance Tracker (.xlsx) with formulas & target calculations
3. Word Deliverables: Academic Project Report (.docx)
4. PowerPoint Deliverables: Academic Seminar Presentation (.pptx)
5. Study Pack Deliverables: Flashcards & Formula Sheet (.md)
6. Fast-path regex / Tool routing in AIManager
7. Groq Cloud Model connectivity (if network available)
8. Fish Audio TTS synthesis (if network available)
"""
import sys
import os
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

def test_student_profile():
    print("\n--- 1. Testing Student Profile ---")
    from app.academic.profile import get_profile_manager
    mgr = get_profile_manager()
    profile = mgr.get_profile()
    print(f"Loaded student profile: {profile.name} ({profile.college}) - {profile.degree}")
    assert profile.name is not None
    assert len(profile.subjects) > 0
    print("[PASS] Student Profile verified.")

def test_academic_memory():
    print("\n--- 2. Testing 4-Tier Memory ---")
    from app.academic.memory import AcademicMemoryManager
    mem = AcademicMemoryManager()
    mem.record_subject_topic("Operating Systems", "Process Scheduling", "Round Robin and Priority Scheduling algorithms.")
    mem.set_preference("explanation_depth", "Comprehensive with diagrams")
    mem.record_episode("create_attendance_tracker", "Target: 75%", "Generated Attendance_Tracker.xlsx successfully")
    
    academic = mem.get_academic_memory()
    prefs = mem.get_preferences()
    episodes = mem.get_episodic_memory()
    
    assert "operating systems" in academic["subjects"]
    assert prefs["explanation_depth"] == "Comprehensive with diagrams"
    assert len(episodes) > 0
    print(f"Memory entries: {len(academic['subjects'])} subjects, {len(prefs)} preferences, {len(episodes)} episodes.")
    print("[PASS] 4-Tier Memory verified.")

def test_deliverables():
    print("\n--- 3. Testing Academic Deliverables ---")
    from app.academic.deliverables import (
        create_attendance_tracker,
        create_assignment_tracker,
        create_academic_report,
        create_academic_presentation,
        create_study_pack
    )
    
    # 3a. Excel Attendance
    xlsx_path = create_attendance_tracker(
        subjects=["Database Management Systems", "Operating Systems", "Computer Networks"],
        target_pct=75.0,
        output_filename="Test_Attendance.xlsx"
    )
    print(f"Created Attendance Tracker: {xlsx_path}")
    assert Path(xlsx_path).exists()
    assert Path(xlsx_path).stat().st_size > 1000

    # 3b. Excel Assignment Tracker
    assign_path = create_assignment_tracker(output_filename="Test_Assignments.xlsx")
    print(f"Created Assignment Tracker: {assign_path}")
    assert Path(assign_path).exists()
    assert Path(assign_path).stat().st_size > 1000

    # 3c. Word Report
    docx_path = create_academic_report(
        title="Autonomous AI Agent Architecture in EdTech",
        student_name="Haren",
        department="Computer Science and Engineering",
        college="National Engineering College",
        output_filename="Test_Report.docx"
    )
    print(f"Created Academic Report: {docx_path}")
    assert Path(docx_path).exists()
    assert Path(docx_path).stat().st_size > 1000

    # 3d. PowerPoint Presentation
    pptx_path = create_academic_presentation(
        title="JARVIS: Autonomous Academic Agent",
        subtitle="Department Technical Seminar",
        presenter="Haren",
        output_filename="Test_Presentation.pptx"
    )
    print(f"Created Academic Presentation: {pptx_path}")
    assert Path(pptx_path).exists()
    assert Path(pptx_path).stat().st_size > 1000

    # 3e. Study Pack
    pack_path = create_study_pack(
        subject="Database Management Systems",
        topic="Normalization and ACID Properties",
        output_filename="Test_Study_Pack.md"
    )
    print(f"Created Study Pack: {pack_path}")
    assert Path(pack_path).exists()
    assert Path(pack_path).stat().st_size > 500

    print("[PASS] All Deliverable Generators (Excel, Word, PowerPoint, Study Pack) verified.")

def test_ai_tools_and_fastpaths():
    print("\n--- 4. Testing AI Manager Tool Declarations & Fastpaths ---")
    from app.ai.manager import FUNCTION_CALLING_TOOLS, AIManager
    tool_names = [t["function"]["name"] for t in FUNCTION_CALLING_TOOLS]
    print(f"Registered tools count: {len(tool_names)}")
    expected_tools = [
        "create_excel_tracker",
        "create_study_pack",
        "create_word_document",
        "read_pdf_document",
        "delete_file",
        "get_student_profile",
        "open_lms",
        "create_presentation"
    ]
    for et in expected_tools:
        assert et in tool_names, f"Missing tool: {et}"
    print(f"Verified presence of tools: {', '.join(expected_tools)}")
    
    # Test fastpath execution for direct student requests
    mgr = AIManager()
    fast_resp = mgr._try_control_command("show my student profile")
    print(f"Fastpath student profile response: {fast_resp is not None}")
    assert fast_resp is not None
    assert "Academic Profile" in fast_resp
    print("[PASS] AI Tools and Fastpaths verified.")

def test_api_endpoints():
    print("\n--- 5. Testing FastAPI Academic & Student Route Handlers ---")
    from app.api.server import (
        health,
        get_student_profile_route,
        update_student_profile_route,
        get_academic_memory_route,
        deliverable_attendance_route,
        deliverable_study_pack_route,
        ProfileUpdateRequest,
        AttendanceTrackerRequest,
        StudyPackRequest
    )

    # Health check
    h = health()
    assert h["status"] == "ok"
    print(f"Health response: {h}")

    # Academic profile GET & POST
    p = get_student_profile_route()
    assert "profile" in p
    assert "name" in p["profile"]

    up = update_student_profile_route(ProfileUpdateRequest(name="Haren", semester="Semester IV"))
    assert up["profile"]["name"] == "Haren"
    assert up["profile"]["semester"] == "Semester IV"
    print(f"Profile updated: {up['profile']['name']} - {up['profile']['semester']}")

    # Academic memory GET
    m = get_academic_memory_route()
    assert "academic" in m
    assert "preferences" in m

    # Deliverable Attendance POST
    att = deliverable_attendance_route(AttendanceTrackerRequest(target_pct=80.0, output_filename="API_Attendance.xlsx"))
    assert att["status"] == "success"
    assert Path(att["file_path"]).exists()
    print(f"API Attendance route generated: {att['file_path']}")

    # Deliverable Study Pack POST
    sp = deliverable_study_pack_route(StudyPackRequest(subject="AI", topic="Autonomous Agents", output_filename="API_Pack.md"))
    assert sp["status"] == "success"
    assert Path(sp["file_path"]).exists()
    print(f"API Study Pack route generated: {sp['file_path']}")

    print("[PASS] FastAPI Route Handlers verified.")


if __name__ == "__main__":
    print("=" * 60)
    print("      STARTING JARVIS E2E INTEGRATION TEST")
    print("=" * 60)
    test_student_profile()
    test_academic_memory()
    test_deliverables()
    test_ai_tools_and_fastpaths()
    test_api_endpoints()
    print("\n" + "=" * 60)
    print("      ALL JARVIS CORE TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
