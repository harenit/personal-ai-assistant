import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { PermissionModal } from './components/PermissionModal';
import { useVoice } from './hooks/useVoice';
import { api } from './services/api';

// Pages
import { Dashboard } from './pages/Dashboard';
import { Chat } from './pages/Chat';
import { Assignments } from './pages/Assignments';
import { Exams } from './pages/Exams';
import { Announcements } from './pages/Announcements';
import { StudyMaterials } from './pages/StudyMaterials';
import { Presentations } from './pages/Presentations';
import { Reminders } from './pages/Reminders';
import { Email } from './pages/Email';
import { Calendar } from './pages/Calendar';
import { Activity } from './pages/Activity';
import { Settings } from './pages/Settings';

export default function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [chatInitialPrompt, setChatInitialPrompt] = useState('');
  const [pendingPermissions, setPendingPermissions] = useState([]);
  const [activeModalPermission, setActiveModalPermission] = useState(null);

  const voice = useVoice({
    onTranscript: (spokenText) => {
      if (spokenText.trim()) {
        setCurrentTab('chat');
        setChatInitialPrompt(spokenText.trim());
      }
    }
  });

  useEffect(() => {
    checkPermissions();
    const interval = setInterval(checkPermissions, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkPermissions = async () => {
    try {
      const data = await api.getPendingPermissions();
      setPendingPermissions(data || []);
      if (data && data.length > 0 && !activeModalPermission) {
        setActiveModalPermission(data[0]);
      }
    } catch {
      // ignore background poll errors
    }
  };

  const handleApprove = async (id) => {
    try {
      await api.approvePermission(id);
      setActiveModalPermission(null);
      await checkPermissions();
    } catch (e) {
      alert(`Approval error: ${e.message}`);
    }
  };

  const handleDeny = async (id) => {
    try {
      await api.denyPermission(id);
      setActiveModalPermission(null);
      await checkPermissions();
    } catch (e) {
      alert(`Denial error: ${e.message}`);
    }
  };

  const handleAskJarvis = (promptText) => {
    setChatInitialPrompt(promptText);
    setCurrentTab('chat');
  };

  const renderContent = () => {
    switch (currentTab) {
      case 'dashboard':
        return (
          <Dashboard
            onNavigateToTab={(tab) => setCurrentTab(tab)}
            onQuickAsk={handleAskJarvis}
            voice={voice}
          />
        );
      case 'chat':
        return (
          <Chat
            initialMessage={chatInitialPrompt}
            isListening={voice.isListening}
            isSpeaking={voice.isSpeaking}
            onToggleVoice={() => {
              if (voice.isListening) voice.stopListening();
              else voice.startListening();
            }}
            speakText={voice.speakText}
            stopSpeaking={voice.stopSpeaking}
            onOpenPermission={(req) => setActiveModalPermission(req)}
          />
        );
      case 'assignments':
        return <Assignments onAskJarvis={handleAskJarvis} />;
      case 'exams':
        return <Exams onAskJarvis={handleAskJarvis} />;
      case 'announcements':
        return <Announcements />;
      case 'study':
        return <StudyMaterials onAskJarvis={handleAskJarvis} />;
      case 'presentations':
        return <Presentations />;
      case 'reminders':
        return <Reminders />;
      case 'email':
        return <Email onAskJarvis={handleAskJarvis} />;
      case 'calendar':
        return <Calendar />;
      case 'activity':
        return <Activity />;
      case 'settings':
        return <Settings />;
      default:
        return <Dashboard onNavigateToTab={setCurrentTab} onQuickAsk={handleAskJarvis} />;
    }
  };

  const getTabTitle = () => {
    switch (currentTab) {
      case 'dashboard': return 'Student Productivity Dashboard';
      case 'chat': return 'JARVIS Autonomous AI Assistant';
      case 'assignments': return 'Course Assignments & Submissions';
      case 'exams': return 'Examination Timetable & Prep';
      case 'announcements': return 'Faculty Bulletins & Announcements';
      case 'study': return 'Study Materials & Vector RAG';
      case 'presentations': return 'AI PowerPoint Presentation Generator';
      case 'reminders': return 'Reminders & Scheduled Tasks';
      case 'email': return 'Student Email Inbox';
      case 'calendar': return 'Academic Schedule & Calendar';
      case 'activity': return 'Agent Security Audit Log';
      case 'settings': return 'System Settings & Diagnostics';
      default: return 'JARVIS AI';
    }
  };

  return (
    <div className="flex h-screen bg-[#0A0D14] overflow-hidden text-slate-100">
      {/* Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={(tab) => {
          setChatInitialPrompt('');
          setCurrentTab(tab);
        }}
        pendingPermissionsCount={pendingPermissions.length}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header
          title={getTabTitle()}
          isListening={voice.isListening}
          isSpeaking={voice.isSpeaking}
          onToggleVoice={() => {
            if (voice.isListening) voice.stopListening();
            else voice.startListening();
          }}
          pendingPermissionsCount={pendingPermissions.length}
          onOpenPermissions={() => {
            if (pendingPermissions.length > 0) {
              setActiveModalPermission(pendingPermissions[0]);
            }
          }}
        />

        <main className="flex-1 overflow-y-auto">
          {renderContent()}
        </main>
      </div>

      {/* Global Permission Modal if sensitive action requires approval */}
      {activeModalPermission && (
        <PermissionModal
          permissionRequest={activeModalPermission}
          onApprove={handleApprove}
          onDeny={handleDeny}
        />
      )}
    </div>
  );
}
