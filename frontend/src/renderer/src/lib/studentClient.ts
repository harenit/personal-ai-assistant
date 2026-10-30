const BACKEND_URL = "http://127.0.0.1:8756";

async function request(path: string, init?: RequestInit): Promise<any> {
  const res = await fetch(`${BACKEND_URL}${path}`, init);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `request failed: ${res.status}`);
  }
  return res.json();
}

export function getLmsCredentialStatus(): Promise<{ configured: boolean; username: string }> {
  return request("/api/student/lms/credentials");
}

export function saveLmsCredentials(username: string, password: string): Promise<{ configured: boolean; username: string }> {
  return request("/api/student/lms/credentials", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
}

export function clearLmsCredentials(): Promise<{ configured: boolean }> {
  return request("/api/student/lms/credentials", { method: "DELETE" });
}

export function checkLms(): Promise<{ result: string }> {
  return request("/api/student/lms/check", { method: "POST" });
}

export interface StudentProfile {
  name: string;
  college: string;
  department: string;
  degree: string;
  academic_year: string;
  semester: string;
  subjects: string[];
  academic_goals: string[];
  preferred_learning_style: string;
  preferred_language: string;
  exam_schedule: Array<{ subject: string; date: string; session: string }>;
  deadlines: Array<{ title: string; subject: string; due: string }>;
}

export function getStudentProfile(): Promise<{ profile: StudentProfile }> {
  return request("/api/academic/profile");
}

export function updateStudentProfile(data: Partial<StudentProfile>): Promise<{ profile: StudentProfile }> {
  return request("/api/academic/profile", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function getAcademicMemory(): Promise<{ academic: any; preferences: any; episodes: any[] }> {
  return request("/api/academic/memory");
}

export function getAcademicPreferences(): Promise<{ preferences: Record<string, string> }> {
  return request("/api/academic/preferences");
}

export function setAcademicPreference(key: string, value: string): Promise<{ saved: boolean }> {
  return request("/api/academic/preferences", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key, value }),
  });
}

export function generateAttendanceTracker(subjects?: string[], targetPct: number = 75): Promise<{ status: string; file_path: string }> {
  return request("/api/academic/deliverables/attendance", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ subjects, target_pct: targetPct }),
  });
}

export function generateAssignmentTracker(assignments?: any[]): Promise<{ status: string; file_path: string }> {
  return request("/api/academic/deliverables/assignments", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ assignments }),
  });
}

export function generateReport(params: {
  title: string;
  student_name?: string;
  department?: string;
  college?: string;
  sections?: any[];
}): Promise<{ status: string; file_path: string }> {
  return request("/api/academic/deliverables/report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
}

export function generatePresentation(params: {
  title: string;
  subtitle?: string;
  presenter?: string;
  slides?: any[];
}): Promise<{ status: string; file_path: string }> {
  return request("/api/academic/deliverables/presentation", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
}

export function generateStudyPack(params: {
  subject: string;
  topic: string;
  flashcards?: any[];
  key_formulas?: any[];
  exam_questions?: any[];
}): Promise<{ status: string; file_path: string }> {
  return request("/api/academic/deliverables/study-pack", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
}

export function getReminders(): Promise<{ reminders: any[]; summary: string }> {
  return request("/api/student/reminders");
}

export function sendStudentEmail(to: string, subject: string, body: string): Promise<{ result: string }> {
  return request("/api/student/email/send", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ to, subject, body }),
  });
}
