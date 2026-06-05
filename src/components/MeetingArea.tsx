import React, { useRef, useEffect } from 'react';
import { useMeetingStore } from '../store/meetingStore';
import type { Transcript } from '../types';

interface MeetingAreaProps {
  onStartMeeting: () => void;
  onStopMeeting: () => void;
  isRecording: boolean;
  transcripts: Transcript[];
}

const MeetingArea: React.FC<MeetingAreaProps> = ({
  onStartMeeting,
  onStopMeeting,
  isRecording,
  transcripts,
}) => {
  const transcriptEndRef = useRef<HTMLDivElement>(null);
  const { config, speakers } = useMeetingStore();

  // 自动滚动到底部
  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcripts]);

  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const getSpeakerName = (speakerId: string) => {
    const speaker = speakers.find((s) => s.id === speakerId);
    return speaker?.name || '未知';
  };

  const getSpeakerColor = (speakerId: string) => {
    const speaker = speakers.find((s) => s.id === speakerId);
    return speaker?.color || '#6366f1';
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
    <main className="meeting-area">
      <div className="transcript-area">
        {transcripts.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">🎤</div>
            <h3 className="empty-state-title">准备开始会议</h3>
            <p>点击下方"开始会议"按钮启动实时翻译</p>
          </div>
        ) : (
          <>
            {transcripts.map((item) => (
              <div key={item.id} className="transcript-item">
                <div
                  className="transcript-avatar"
                  style={{ background: getSpeakerColor(item.speakerId) }}
                >
                  {getInitials(getSpeakerName(item.speakerId))}
                </div>

                <div className="transcript-content">
                  <div className="transcript-header">
                    <span className="transcript-speaker">
                      {getSpeakerName(item.speakerId)}
                    </span>
                    <span className="transcript-time">
                      {formatTime(item.timestamp)}
                    </span>
                  </div>

                  <div className="transcript-text">{item.text}</div>

                  {item.translation && (
                    <div className="transcript-translation">{item.translation}</div>
                  )}
                </div>
              </div>
            ))}
            <div ref={transcriptEndRef} />
          </>
        )}
      </div>

      <div className="controls">
        {!isRecording ? (
          <button className="btn btn-success" onClick={onStartMeeting}>
            ▶️ 开始会议
          </button>
        ) : (
          <>
            <button className="btn btn-danger" onClick={onStopMeeting}>
              ⏹️ 结束会议
            </button>
            <button className="btn btn-secondary" disabled>
              🗣️ 说话人: {speakers.length || '-'}
            </button>
          </>
        )}

        <button
          className="btn btn-secondary"
          onClick={() => {
            if (confirm('确定要清除所有记录吗？')) {
              useMeetingStore.getState().clearTranscripts();
            }
          }}
        >
          🗑️ 清除
        </button>
      </div>
    </main>
  );
};

export default MeetingArea;