import { useEffect } from 'react';
import { useMeetingStore } from './store/meetingStore';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import MeetingArea from './components/MeetingArea';
import ConfigModal from './components/ConfigModal';
import { useState } from 'react';

function App() {
  const [showConfig, setShowConfig] = useState(false);
  const { startMeeting, stopMeeting, isRecording, transcripts } = useMeetingStore();

  // 模拟开始会议（实际应该调用后端API）
  const handleStartMeeting = async () => {
    try {
      // 调用后端 API 开始会议
      const response = await fetch('http://localhost:7860/api/meeting/start', {
        method: 'POST',
      });
      if (response.ok) {
        startMeeting();
      }
    } catch (error) {
      // 后端未运行，使用本地状态
      startMeeting();
    }
  };

  const handleStopMeeting = async () => {
    try {
      await fetch('http://localhost:7860/api/meeting/stop', {
        method: 'POST',
      });
    } catch (error) {
      // 忽略错误
    }
    stopMeeting();
  };

  return (
    <div className="app">
      <Header
        onOpenConfig={() => setShowConfig(true)}
        isRecording={isRecording}
      />

      <div className="main-content">
        <Sidebar />
        <MeetingArea
          onStartMeeting={handleStartMeeting}
          onStopMeeting={handleStopMeeting}
          isRecording={isRecording}
          transcripts={transcripts}
        />
      </div>

      {showConfig && (
        <ConfigModal onClose={() => setShowConfig(false)} />
      )}
    </div>
  );
}

export default App;