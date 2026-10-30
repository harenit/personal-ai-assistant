const API_BASE = '';

async function fetchJSON(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorBody.detail || `Request failed with status ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Chat & Agent
  sendMessage: (message, conversation_id, voice_mode = false) =>
    fetchJSON('/chat', {
      method: 'POST',
      body: JSON.stringify({ message, conversation_id, voice_mode }),
    }),

  // Permissions
  getPendingPermissions: () => fetchJSON('/permissions'),
  approvePermission: (id) => fetchJSON(`/permissions/${id}/approve`, { method: 'POST' }),
  denyPermission: (id) => fetchJSON(`/permissions/${id}/deny`, { method: 'POST' }),

  // LMS
  getCourses: () => fetchJSON('/courses'),
  getAssignments: (course_id) => fetchJSON(course_id ? `/assignments?course_id=${course_id}` : '/assignments'),
  getUpcomingAssignments: (days_ahead = 7) => fetchJSON(`/assignments/upcoming?days_ahead=${days_ahead}`),
  submitAssignment: (id, submission_text) =>
    fetchJSON(`/assignments/${id}/submit`, {
      method: 'POST',
      body: JSON.stringify({ submission_text }),
    }),
  getExams: () => fetchJSON('/exams'),
  getAnnouncements: () => fetchJSON('/announcements'),

  // Email
  getEmails: (limit = 15, unread_only = false) =>
    fetchJSON(`/emails?limit=${limit}&unread_only=${unread_only}`),
  searchEmails: (query, limit = 5) =>
    fetchJSON('/emails/search', {
      method: 'POST',
      body: JSON.stringify({ query, limit }),
    }),
  readEmail: (id) => fetchJSON(`/emails/${id}`),
  draftEmail: (email_id, reply_text) =>
    fetchJSON('/emails/draft', {
      method: 'POST',
      body: JSON.stringify({ email_id, reply_text }),
    }),
  sendEmail: (recipient, subject, body) =>
    fetchJSON('/emails/send', {
      method: 'POST',
      body: JSON.stringify({ recipient, subject, body }),
    }),

  // Calendar
  getCalendarEvents: () => fetchJSON('/calendar/events'),
  getUpcomingEvents: (hours_ahead = 48) => fetchJSON(`/calendar/upcoming?hours_ahead=${hours_ahead}`),
  createCalendarEvent: (eventData) =>
    fetchJSON('/calendar/events', {
      method: 'POST',
      body: JSON.stringify(eventData),
    }),
  cancelCalendarEvent: (id) => fetchJSON(`/calendar/events/${id}`, { method: 'DELETE' }),

  // Reminders
  getReminders: (include_completed = false) =>
    fetchJSON(`/reminders?include_completed=${include_completed}`),
  createReminder: (reminderData) =>
    fetchJSON('/reminders', {
      method: 'POST',
      body: JSON.stringify(reminderData),
    }),
  deleteReminder: (id) => fetchJSON(`/reminders/${id}`, { method: 'DELETE' }),

  // Documents & Study RAG
  getDocuments: () => fetchJSON('/documents'),
  uploadDocument: async (formData) => {
    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail);
    }
    return res.json();
  },
  askDocument: (id, question) =>
    fetchJSON(`/documents/${id}/ask`, {
      method: 'POST',
      body: JSON.stringify({ question }),
    }),
  generateQuiz: (id, topic, count = 10) =>
    fetchJSON(`/documents/${id}/quiz`, {
      method: 'POST',
      body: JSON.stringify({ topic, count }),
    }),
  generateFlashcards: (id, topic, count = 8) =>
    fetchJSON(`/documents/${id}/flashcards`, {
      method: 'POST',
      body: JSON.stringify({ topic, count }),
    }),
  deleteDocument: (id) => fetchJSON(`/documents/${id}`, { method: 'DELETE' }),

  // Presentations
  getPresentations: () => fetchJSON('/presentations'),
  generatePresentation: (data) =>
    fetchJSON('/presentations/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  openPresentation: (file_path) =>
    fetchJSON('/presentations/open', {
      method: 'POST',
      body: JSON.stringify({ file_path }),
    }),

  // Activity & Health
  getActivityLogs: (limit = 50) => fetchJSON(`/activity?limit=${limit}`),
  getHealth: () => fetchJSON('/health'),

  // System Control
  openApp: (application_name) =>
    fetchJSON('/system/open/app', {
      method: 'POST',
      body: JSON.stringify({ application_name }),
    }),
  openUrl: (url) =>
    fetchJSON('/system/open/url', {
      method: 'POST',
      body: JSON.stringify({ url }),
    }),
  openFolder: (folder_name) =>
    fetchJSON('/system/open/folder', {
      method: 'POST',
      body: JSON.stringify({ folder_name }),
    }),
  getTelemetry: () => fetchJSON('/system/telemetry'),

  // Voice
  getVoiceStatus: () => fetchJSON('/voice/status'),
  synthesizeVoice: (text, speak_desktop = false) =>
    fetchJSON('/voice/synthesize', {
      method: 'POST',
      body: JSON.stringify({ text, speak_desktop }),
    }),
};
