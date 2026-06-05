import React from 'react';
import { useMeetingStore } from '../store/meetingStore';

interface HeaderProps {
  onOpenConfig: () => void;
  isRecording: boolean;
}

const Header: React.FC<HeaderProps> = ({ onOpenConfig, isRecording }) => {
  const { transcripts, speakers } = useMeetingStore();

  return (
    <header className="header">
      <h1>🎙️ Simultra</h1>

      <div className="header-actions">
        <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          {speakers.length} 人发言 | {transcripts.length} 条记录
        </span>

        <span className={`status-badge ${isRecording ? 'recording' : 'idle'}`}>
          {isRecording ? '● 录音中' : '○ 待机'}
        </span>

        <button className="btn btn-secondary" onClick={onOpenConfig}>
          ⚙️ 设置
        </button>
      </div>
    </header>
  );
};

export default Header;