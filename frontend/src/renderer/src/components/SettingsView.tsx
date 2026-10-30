import { useEffect, useState } from "react";
import { getPermissions, setPermission } from "../lib/aiClient";
import { getMemoryEnabled, setMemoryEnabled } from "../lib/memoryClient";
import { getRecentActions, type ActionEntry } from "../lib/historyClient";
import { getWakewordEnabled, setWakewordEnabled } from "../lib/wakewordClient";
import { useBackendStatus } from "../hooks/useBackendStatus";
import {
  getLmsCredentialStatus,
  saveLmsCredentials,
  clearLmsCredentials,
  checkLms,
  getStudentProfile,
  updateStudentProfile,
  generateAttendanceTracker,
  generateAssignmentTracker,
  generateReport,
  generatePresentation,
  generateStudyPack,
  type StudentProfile,
} from "../lib/studentClient";

const LAUNCH_APP_SCOPE = "control.launch_app";
const FS_READ_SCOPE = "fs.read";
const FS_WRITE_SCOPE = "fs.write";
const LMS_SCOPE = "student.lms";
const PPT_SCOPE = "student.create_ppt";

type UpdateStatus =
  | { state: "idle" }
  | { state: "checking" }
  | { state: "available"; version: string }
  | { state: "not-available" }
  | { state: "error"; message: string }
  | { state: "downloading"; percent: number }
  | { state: "downloaded"; version: string };

function isUpdateStatus(value: unknown): value is UpdateStatus {
  return typeof value === "object" && value !== null && "state" in value;
}

export default function SettingsView(): JSX.Element {
  const [autostart, setAutostartState] = useState<boolean | null>(null);
  const [savingAutostart, setSavingAutostart] = useState(false);

  const [micEnabled, setMicEnabledState] = useState<boolean | null>(null);
  const [savingMic, setSavingMic] = useState(false);

  const [wakewordEnabled, setWakewordEnabledState] = useState<boolean | null>(null);
  const [savingWakeword, setSavingWakeword] = useState(false);
  const [wakewordError, setWakewordError] = useState<string | null>(null);

  const [launchAppGranted, setLaunchAppGranted] = useState<boolean | null>(null);
  const [savingPermission, setSavingPermission] = useState(false);

  const [fsReadGranted, setFsReadGranted] = useState<boolean | null>(null);
  const [savingFsRead, setSavingFsRead] = useState(false);

  const [fsWriteGranted, setFsWriteGranted] = useState<boolean | null>(null);
  const [lmsGranted, setLmsGranted] = useState<boolean | null>(null);
  const [pptGranted, setPptGranted] = useState<boolean | null>(null);
  const [savingFsWrite, setSavingFsWrite] = useState(false);
  const [lmsUsername, setLmsUsername] = useState("24104005@nec.edu.in");
  const [lmsPassword, setLmsPassword] = useState("");
  const [lmsConfigured, setLmsConfigured] = useState(false);
  const [lmsMessage, setLmsMessage] = useState("");
  const [savingLms, setSavingLms] = useState(false);

  const [memoryEnabled, setMemoryEnabledState] = useState<boolean | null>(null);
  const [savingMemory, setSavingMemory] = useState(false);

  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [profName, setProfName] = useState("");
  const [profCollege, setProfCollege] = useState("");
  const [profDept, setProfDept] = useState("");
  const [profSemester, setProfSemester] = useState("");
  const [deliverableMsg, setDeliverableMsg] = useState("");
  const [generatingDoc, setGeneratingDoc] = useState(false);

  const [recentActions, setRecentActions] = useState<ActionEntry[] | null>(null);
  const backendStatus = useBackendStatus();

  const [appVersion, setAppVersion] = useState<string | null>(null);
  const [updateStatus, setUpdateStatus] = useState<UpdateStatus>({ state: "idle" });

  function loadBackendState(): void {
    getPermissions()
      .then((perms) => {
        setLaunchAppGranted(Boolean(perms[LAUNCH_APP_SCOPE]));
        setFsReadGranted(Boolean(perms[FS_READ_SCOPE]));
        setFsWriteGranted(Boolean(perms[FS_WRITE_SCOPE]));
        setLmsGranted(Boolean(perms[LMS_SCOPE]));
        setPptGranted(Boolean(perms[PPT_SCOPE]));
      })
      .catch(() => {
        setLaunchAppGranted(null);
        setFsReadGranted(null);
        setFsWriteGranted(null);
        setLmsGranted(null);
        setPptGranted(null);
      });
    getMemoryEnabled()
      .then((status) => setMemoryEnabledState(status.enabled))
      .catch(() => setMemoryEnabledState(null));
    getRecentActions(10)
      .then((data) => setRecentActions(data.actions))
      .catch(() => setRecentActions(null));
    getWakewordEnabled()
      .then((status) => setWakewordEnabledState(status.enabled))
      .catch(() => setWakewordEnabledState(null));
    getLmsCredentialStatus()
      .then((status) => { setLmsConfigured(status.configured); if (status.username) setLmsUsername(status.username); })
      .catch(() => setLmsConfigured(false));
    getStudentProfile()
      .then((res) => {
        if (res && res.profile) {
          setProfile(res.profile);
          setProfName(res.profile.name || "Student");
          setProfCollege(res.profile.college || "National Engineering College");
          setProfDept(res.profile.department || "Computer Science and Engineering");
          setProfSemester(res.profile.semester || "Semester IV");
        }
      })
      .catch(() => {});
  }

  const auraApi = window.aura || window.jarvis;

  useEffect(() => {
    auraApi.settings.getAutostart().then(setAutostartState);
    auraApi.settings.getMicrophone().then(setMicEnabledState);
    loadBackendState();
    auraApi.updates.getVersion().then(setAppVersion);
    return auraApi.updates.onStatus((status) => {
      if (isUpdateStatus(status)) setUpdateStatus(status);
    });
  }, []);

  // Retry the backend-derived cards automatically once it's back online —
  // catches both "was down when this page first loaded" and "crashed while
  // this page was already open."
  useEffect(() => {
    if (backendStatus === "online") loadBackendState();
  }, [backendStatus]);

  function formatActionTime(iso: string): string {
    try {
      return new Date(iso).toLocaleString(undefined, {
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
      });
    } catch {
      return iso;
    }
  }

  async function toggleAutostart(): Promise<void> {
    if (autostart === null || savingAutostart) return;
    setSavingAutostart(true);
    const next = await auraApi.settings.setAutostart(!autostart);
    setAutostartState(next);
    setSavingAutostart(false);
  }

  async function toggleMic(): Promise<void> {
    if (micEnabled === null || savingMic) return;
    setSavingMic(true);
    const next = await auraApi.settings.setMicrophone(!micEnabled);
    setMicEnabledState(next);
    setSavingMic(false);
  }

  async function toggleWakeword(): Promise<void> {
    if (wakewordEnabled === null || savingWakeword) return;
    setSavingWakeword(true);
    setWakewordError(null);
    try {
      const result = await setWakewordEnabled(!wakewordEnabled);
      setWakewordEnabledState(result.enabled);
      if (result.enabled && !result.running) {
        setWakewordError("Enabled, but the listener didn't start — check that a microphone is connected.");
      }
    } catch (err) {
      setWakewordError(err instanceof Error ? err.message : "Couldn't change wake-word listening.");
    } finally {
      setSavingWakeword(false);
    }
  }

  async function toggleLaunchAppPermission(): Promise<void> {
    if (launchAppGranted === null || savingPermission) return;
    setSavingPermission(true);
    try {
      const result = await setPermission(LAUNCH_APP_SCOPE, !launchAppGranted);
      setLaunchAppGranted(result.granted);
    } finally {
      setSavingPermission(false);
    }
  }

  async function toggleFsRead(): Promise<void> {
    if (fsReadGranted === null || savingFsRead) return;
    setSavingFsRead(true);
    try {
      const result = await setPermission(FS_READ_SCOPE, !fsReadGranted);
      setFsReadGranted(result.granted);
    } finally {
      setSavingFsRead(false);
    }
  }

  async function toggleFsWrite(): Promise<void> {
    if (fsWriteGranted === null || savingFsWrite) return;
    setSavingFsWrite(true);
    try {
      const result = await setPermission(FS_WRITE_SCOPE, !fsWriteGranted);
      setFsWriteGranted(result.granted);
    } finally {
      setSavingFsWrite(false);
    }
  }

  async function toggleStudentPermission(scope: string, granted: boolean | null, setter: (v: boolean) => void): Promise<void> {
    if (granted === null || savingPermission) return;
    setSavingPermission(true);
    try {
      const result = await setPermission(scope, !granted);
      setter(result.granted);
    } finally { setSavingPermission(false); }
  }

  function checkForUpdates(): void {
    auraApi.updates.check();
  }

  function downloadUpdate(): void {
    auraApi.updates.download();
  }

  function installUpdate(): void {
    auraApi.updates.install();
  }

  async function toggleMemory(): Promise<void> {
    if (memoryEnabled === null || savingMemory) return;
    setSavingMemory(true);
    try {
      const result = await setMemoryEnabled(!memoryEnabled);
      setMemoryEnabledState(result.enabled);
    } finally {
      setSavingMemory(false);
    }
  }

  return (
    <div className="settings-view">
      <div className="settings-card glass-panel">
        <h2>Startup</h2>

        <div className="settings-row">
          <div>
            <p className="settings-row-title">Start AURA with Windows</p>
            <p className="settings-row-desc">
              Launches AURA automatically when you sign in to Windows, minimized to
              the system tray — no window pops up.
            </p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={autostart ?? false}
            className={`toggle-switch${autostart ? " on" : ""}`}
            onClick={toggleAutostart}
            disabled={autostart === null || savingAutostart}
          >
            <span className="toggle-knob" />
          </button>
        </div>

        {autostart && (
          <p className="settings-note">
            Background mode is active for startup launches: while minimized to the
            tray, AURA keeps CPU and RAM usage minimal and just waits for your next
            command. Right-click the tray icon to reopen, activate, or quit at any
            time.
          </p>
        )}
      </div>

      <div className="settings-card glass-panel">
        <h2>Microphone</h2>

        <div className="settings-row">
          <div>
            <p className="settings-row-title">Allow microphone access</p>
            <p className="settings-row-desc">
              Off by default. Controls both the mic button here and "Activate
              Assistant" from the tray — no audio is captured while disabled.
            </p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={micEnabled ?? false}
            className={`toggle-switch${micEnabled ? " on" : ""}`}
            onClick={toggleMic}
            disabled={micEnabled === null || savingMic}
          >
            <span className="toggle-knob" />
          </button>
        </div>

        <div className="settings-row">
          <div>
            <p className="settings-row-title">Wake word ("Hey Aura")</p>
            <p className="settings-row-desc">
              Off by default. When on, AURA listens continuously in the
              background for "Hey Aura" or just "Aura" and starts
              listening for your command automatically — no button press
              needed. Detection runs fully offline, on your own PC; audio is
              never sent anywhere unless it actually triggers a command.
            </p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={wakewordEnabled ?? false}
            className={`toggle-switch${wakewordEnabled ? " on" : ""}`}
            onClick={toggleWakeword}
            disabled={wakewordEnabled === null || savingWakeword}
          >
            <span className="toggle-knob" />
          </button>
        </div>
        {wakewordError && <p className="automation-error">{wakewordError}</p>}
      </div>

      <div className="settings-card glass-panel">
        <h2>Permissions</h2>

        <div className="settings-row">
          <div>
            <p className="settings-row-title">Allow AURA to control applications</p>
            <p className="settings-row-desc">
              Off by default. Lets the assistant open, switch to, or close any
              application actually installed on this PC, open common websites
              (YouTube, Netflix, Gmail, and more) or any web address, and open
              Windows Settings. Closing an app always asks you to confirm
              first, even with this on — nothing closes silently. Deleting
              files and changing system settings are never available.
            </p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={launchAppGranted ?? false}
            className={`toggle-switch${launchAppGranted ? " on" : ""}`}
            onClick={toggleLaunchAppPermission}
            disabled={launchAppGranted === null || savingPermission}
          >
            <span className="toggle-knob" />
          </button>
        </div>
      </div>

      <div className="settings-card glass-panel">
        <h2>Files</h2>

        <div className="settings-row">
          <div>
            <p className="settings-row-title">Search files and folders</p>
            <p className="settings-row-desc">
              Off by default. Lets the assistant look for files and folders by
              name — your Desktop, Documents, Downloads, Pictures, Music, and
              Videos folders by default, or anywhere else on any drive if you
              name it (e.g. a drive letter or folder path). Read-only —
              nothing is moved, renamed, or created.
            </p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={fsReadGranted ?? false}
            className={`toggle-switch${fsReadGranted ? " on" : ""}`}
            onClick={toggleFsRead}
            disabled={fsReadGranted === null || savingFsRead}
          >
            <span className="toggle-knob" />
          </button>
        </div>

        <div className="settings-row">
          <div>
            <p className="settings-row-title">Create, rename, and organize files</p>
            <p className="settings-row-desc">
              Off by default. Lets the assistant create folders, rename files,
              and sort a folder's loose files into type-based subfolders —
              anywhere on any drive, not just your personal folders.
              Organizing always previews the plan and asks you to confirm
              before moving anything. Deleting files is never available, with
              or without this on.
            </p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={fsWriteGranted ?? false}
            className={`toggle-switch${fsWriteGranted ? " on" : ""}`}
            onClick={toggleFsWrite}
            disabled={fsWriteGranted === null || savingFsWrite}
          >
            <span className="toggle-knob" />
          </button>
        </div>
      </div>

      <div className="settings-card glass-panel">
        <h2>Student LMS</h2>
        <p className="settings-row-desc">
          NEC LMS uses Google sign-in. AURA stores the LMS username and password in the Windows Credential Manager, not in the project or a JSON file. Google MFA/security checks are still completed by you in the visible AURA browser window.
        </p>
        <div className="settings-row" style={{ display: "block" }}>
          <label className="settings-row-title">NEC Google account</label>
          <input value={lmsUsername} onChange={(e) => setLmsUsername(e.target.value)} placeholder="24104005@nec.edu.in" style={{ width: "100%", marginTop: 8 }} />
          <label className="settings-row-title" style={{ display: "block", marginTop: 14 }}>LMS password</label>
          <input type="password" value={lmsPassword} onChange={(e) => setLmsPassword(e.target.value)} placeholder={lmsConfigured ? "Saved in Windows Credential Manager" : "Enter password here"} style={{ width: "100%", marginTop: 8 }} />
          <div style={{ display: "flex", gap: 10, marginTop: 14 }}>
            <button type="button" onClick={async () => {
              if (!lmsUsername.trim() || !lmsPassword) { setLmsMessage("Enter both username and password."); return; }
              setSavingLms(true); setLmsMessage("");
              try { await saveLmsCredentials(lmsUsername, lmsPassword); setLmsConfigured(true); setLmsPassword(""); setLmsMessage("Credentials saved securely in Windows Credential Manager."); }
              catch (err) { setLmsMessage(err instanceof Error ? err.message : "Could not save credentials."); }
              finally { setSavingLms(false); }
            }} disabled={savingLms}>Save securely</button>
            <button type="button" onClick={async () => { await clearLmsCredentials(); setLmsConfigured(false); setLmsPassword(""); setLmsMessage("Saved LMS credentials removed."); }}>Remove saved password</button>
            <button type="button" onClick={async () => { try { const r = await checkLms(); setLmsMessage(r.result); } catch (err) { setLmsMessage(err instanceof Error ? err.message : "LMS check failed."); } }}>Check LMS</button>
          </div>
          {lmsMessage && <p className="settings-note" style={{ whiteSpace: "pre-wrap" }}>{lmsMessage}</p>}
        </div>
      </div>

      <div className="settings-card glass-panel">
        <h2>Academic Profile & Deliverables</h2>
        <p className="settings-row-desc">
          JARVIS personalizes academic tasks, LMS sync, and deliverables using your profile. You can also generate verified files instantly.
        </p>
        <div className="settings-row" style={{ display: "block" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginTop: 8 }}>
            <div>
              <label className="settings-row-title">Student Name</label>
              <input value={profName} onChange={(e) => setProfName(e.target.value)} placeholder="Student Name" style={{ width: "100%", marginTop: 4 }} />
            </div>
            <div>
              <label className="settings-row-title">College / University</label>
              <input value={profCollege} onChange={(e) => setProfCollege(e.target.value)} placeholder="College Name" style={{ width: "100%", marginTop: 4 }} />
            </div>
            <div>
              <label className="settings-row-title">Department</label>
              <input value={profDept} onChange={(e) => setProfDept(e.target.value)} placeholder="Department" style={{ width: "100%", marginTop: 4 }} />
            </div>
            <div>
              <label className="settings-row-title">Semester</label>
              <input value={profSemester} onChange={(e) => setProfSemester(e.target.value)} placeholder="Semester" style={{ width: "100%", marginTop: 4 }} />
            </div>
          </div>
          <div style={{ marginTop: 12, display: "flex", gap: 10 }}>
            <button
              type="button"
              onClick={async () => {
                try {
                  const res = await updateStudentProfile({
                    name: profName,
                    college: profCollege,
                    department: profDept,
                    semester: profSemester,
                  });
                  setProfile(res.profile);
                  setDeliverableMsg("Academic Profile updated successfully!");
                } catch (e: any) {
                  setDeliverableMsg(e.message || "Could not update profile.");
                }
              }}
            >
              Save Profile
            </button>
          </div>

          <div style={{ marginTop: 18, borderTop: "1px solid rgba(255, 255, 255, 0.1)", paddingTop: 14 }}>
            <p className="settings-row-title" style={{ marginBottom: 8 }}>Instant Academic Deliverables</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              <button
                type="button"
                disabled={generatingDoc}
                onClick={async () => {
                  setGeneratingDoc(true);
                  setDeliverableMsg("Generating Attendance Tracker Excel...");
                  try {
                    const res = await generateAttendanceTracker(profile?.subjects, 75);
                    setDeliverableMsg(`Attendance Tracker created: ${res.file_path}`);
                  } catch (e: any) {
                    setDeliverableMsg(e.message || "Failed to generate attendance sheet.");
                  } finally {
                    setGeneratingDoc(false);
                  }
                }}
              >
                📊 Attendance Sheet (.xlsx)
              </button>
              <button
                type="button"
                disabled={generatingDoc}
                onClick={async () => {
                  setGeneratingDoc(true);
                  setDeliverableMsg("Generating Assignment Marks Tracker Excel...");
                  try {
                    const res = await generateAssignmentTracker();
                    setDeliverableMsg(`Assignment Tracker created: ${res.file_path}`);
                  } catch (e: any) {
                    setDeliverableMsg(e.message || "Failed to generate assignment sheet.");
                  } finally {
                    setGeneratingDoc(false);
                  }
                }}
              >
                📝 Assignment Marks (.xlsx)
              </button>
              <button
                type="button"
                disabled={generatingDoc}
                onClick={async () => {
                  setGeneratingDoc(true);
                  setDeliverableMsg("Generating Academic Project Report DOCX...");
                  try {
                    const res = await generateReport({
                      title: "Autonomous Student Companion Report",
                      student_name: profName || "Student",
                      department: profDept || "Computer Science and Engineering",
                      college: profCollege || "National Engineering College",
                    });
                    setDeliverableMsg(`Academic Report created: ${res.file_path}`);
                  } catch (e: any) {
                    setDeliverableMsg(e.message || "Failed to generate academic report.");
                  } finally {
                    setGeneratingDoc(false);
                  }
                }}
              >
                📄 Lab/Project Report (.docx)
              </button>
              <button
                type="button"
                disabled={generatingDoc}
                onClick={async () => {
                  setGeneratingDoc(true);
                  setDeliverableMsg("Generating Presentation Slides PPTX...");
                  try {
                    const res = await generatePresentation({
                      title: "Artificial Intelligence Seminar",
                      presenter: profName || "Student",
                    });
                    setDeliverableMsg(`Presentation created: ${res.file_path}`);
                  } catch (e: any) {
                    setDeliverableMsg(e.message || "Failed to generate slides.");
                  } finally {
                    setGeneratingDoc(false);
                  }
                }}
              >
                📽️ Seminar Slides (.pptx)
              </button>
              <button
                type="button"
                disabled={generatingDoc}
                onClick={async () => {
                  setGeneratingDoc(true);
                  setDeliverableMsg("Generating Study Pack & Flashcards...");
                  try {
                    const res = await generateStudyPack({
                      subject: "Computer Science",
                      topic: "Operating Systems & Networking",
                    });
                    setDeliverableMsg(`Study Pack created: ${res.file_path}`);
                  } catch (e: any) {
                    setDeliverableMsg(e.message || "Failed to generate study pack.");
                  } finally {
                    setGeneratingDoc(false);
                  }
                }}
              >
                🗂️ Study Pack (.md)
              </button>
            </div>
            {deliverableMsg && (
              <p className="settings-note" style={{ whiteSpace: "pre-wrap", marginTop: 10, wordBreak: "break-all" }}>
                {deliverableMsg}
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="settings-card glass-panel">
        <h2>Memory</h2>

        <div className="settings-row">
          <div>
            <p className="settings-row-title">Remember things I tell you</p>
            <p className="settings-row-desc">
              On by default. When you say "Remember I use VS Code," AURA
              stores that and can use it later, e.g. "Open my editor." Turning
              this off stops new preferences and conversation history from
              being recorded, and stops existing ones from being used — it
              doesn't erase what's already remembered. View or delete what's
              remembered from the Memory page in the sidebar.
            </p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={memoryEnabled ?? false}
            className={`toggle-switch${memoryEnabled ? " on" : ""}`}
            onClick={toggleMemory}
            disabled={memoryEnabled === null || savingMemory}
          >
            <span className="toggle-knob" />
          </button>
        </div>
      </div>

      <div className="settings-card glass-panel">
        <h2>Updates</h2>
        <div className="settings-row">
          <div>
            <p className="settings-row-title">AURA version {appVersion ?? "…"}</p>
            <p className="settings-row-desc">
              {updateStatus.state === "idle" && "Check for a newer version of AURA."}
              {updateStatus.state === "checking" && "Checking for updates…"}
              {updateStatus.state === "not-available" && "You're on the latest version."}
              {updateStatus.state === "available" && `Version ${updateStatus.version} is available.`}
              {updateStatus.state === "downloading" && `Downloading update… ${updateStatus.percent}%`}
              {updateStatus.state === "downloaded" &&
                `Version ${updateStatus.version} is ready — restart to finish installing.`}
              {updateStatus.state === "error" && updateStatus.message}
            </p>
          </div>
          {updateStatus.state === "downloaded" ? (
            <button type="button" className="automation-save" onClick={installUpdate}>
              Restart to update
            </button>
          ) : updateStatus.state === "available" ? (
            <button type="button" className="automation-save" onClick={downloadUpdate}>
              Download
            </button>
          ) : (
            <button
              type="button"
              className="automation-new-button"
              onClick={checkForUpdates}
              disabled={updateStatus.state === "checking" || updateStatus.state === "downloading"}
            >
              Check for updates
            </button>
          )}
        </div>
        {updateStatus.state === "downloading" && (
          <div className="meter-track">
            <div className="meter-fill" style={{ width: `${updateStatus.percent}%` }} />
          </div>
        )}
      </div>

      <div className="settings-card glass-panel">
        <h2>Recent activity</h2>
        <p className="settings-row-desc">
          A local record of actions AURA has actually taken — not requests or
          denials — so you can see exactly what it's done on your computer.
        </p>
        {recentActions === null ? (
          <p className="settings-row-desc">Nothing to show yet.</p>
        ) : recentActions.length === 0 ? (
          <p className="settings-row-desc">No actions recorded yet.</p>
        ) : (
          <ul className="memory-list">
            {recentActions.map((entry) => (
              <li key={entry.id} className="memory-item activity-item">
                <div className="memory-item-text activity-item-text">
                  <span className="memory-key">{entry.action.replace(/_/g, " ")}</span>
                  <span className="memory-value">{entry.result}</span>
                </div>
                <span className="activity-time">{formatActionTime(entry.timestamp)}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="settings-card glass-panel muted">
        <h2>More settings</h2>
        <p className="settings-row-desc">
          Voice engine choice and appearance options will live here later.
        </p>
      </div>
    </div>
  );
}
