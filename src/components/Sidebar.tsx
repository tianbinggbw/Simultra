import React from 'react';
import { useMeetingStore } from '../store/meetingStore';
import type { Speaker } from '../types';

const Sidebar: React.FC = () => {
  const { speakers, currentSpeakerId, setCurrentSpeaker, updateSpeakerName } = useMeetingStore();
  const [editingId, setEditingId] = React.useState<string | null>(null);
  const [editName, setEditName] = React.useState('');

  const handleNameEdit = (speaker: Speaker) => {
    setEditingId(speaker.id);
    setEditName(speaker.name);
  };

  const handleNameSave = (id: string) => {
    if (editName.trim()) {
      updateSpeakerName(id, editName.trim());
    }
    setEditingId(null);
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <h3 className="sidebar-title">👥 参会人员</h3>

        {speakers.length === 0 ? (
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            暂无参会人员
          </div>
        ) : (
          <div className="speaker-list">
            {speakers.map((speaker) => (
              <div
                key={speaker.id}
                className={`speaker-item ${currentSpeakerId === speaker.id ? 'active' : ''}`}
                onClick={() => setCurrentSpeaker(speaker.id)}
                onDoubleClick={() => handleNameEdit(speaker)}
              >
                <div
                  className="speaker-avatar"
                  style={{ background: speaker.color }}
                >
                  {getInitials(speaker.name)}
                </div>

                <div className="speaker-info">
                  {editingId === speaker.id ? (
                    <input
                      type="text"
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      onBlur={() => handleNameSave(speaker.id)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleNameSave(speaker.id);
                        if (e.key === 'Escape') setEditingId(null);
                      }}
                      autoFocus
                      style={{
                        background: 'var(--bg-dark)',
                        border: '1px solid var(--primary)',
                        borderRadius: '4px',
                        padding: '2px 6px',
                        color: 'var(--text-primary)',
                        width: '100%',
                      }}
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <div className="speaker-name">{speaker.name}</div>
                  )}
                  <div className="speaker-status">
                    {currentSpeakerId === speaker.id ? '发言中' : '在线'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="sidebar-section">
        <h3 className="sidebar-title">💡 使用提示</h3>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          <p>• 点击开始会议，软件将自动识别语音</p>
          <p>• 双击参会人员可修改姓名</p>
          <p>• 在设置中配置 Ollama 地址</p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;