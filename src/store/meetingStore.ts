import { create } from 'zustand';
import type { Speaker, Transcript, AppConfig } from '../types';

interface MeetingStore {
  // State
  isRecording: boolean;
  meetingId: string | null;
  startTime: Date | null;
  speakers: Speaker[];
  transcripts: Transcript[];
  currentSpeakerId: string | null;

  // Config
  config: AppConfig;

  // Actions
  startMeeting: () => void;
  stopMeeting: () => void;
  addSpeaker: (speaker: Speaker) => void;
  updateSpeakerName: (id: string, name: string) => void;
  setCurrentSpeaker: (id: string | null) => void;
  addTranscript: (transcript: Omit<Transcript, 'id'>) => void;
  clearTranscripts: () => void;
  updateConfig: (config: Partial<AppConfig>) => void;
  reset: () => void;
}

// 生成随机颜色
const generateColor = () => {
  const colors = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
  return colors[Math.floor(Math.random() * colors.length)];
};

// 生成简短ID
const generateId = () => Math.random().toString(36).substring(2, 9);

export const useMeetingStore = create<MeetingStore>((set, get) => ({
  // Initial State
  isRecording: false,
  meetingId: null,
  startTime: null,
  speakers: [],
  transcripts: [],
  currentSpeakerId: null,

  config: {
    ollamaUrl: 'http://localhost:11434',
    modelName: 'llama3.2:3b',
    sourceLang: 'en',
    targetLang: 'zh',
    audioSource: 'microphone',
    customVocabulary: [],
  },

  // Actions
  startMeeting: () => {
    const meetingId = `meeting_${Date.now()}`;
    set({
      isRecording: true,
      meetingId,
      startTime: new Date(),
      transcripts: [],
      speakers: [],
      currentSpeakerId: null,
    });
  },

  stopMeeting: () => {
    set({
      isRecording: false,
    });
  },

  addSpeaker: (speaker) => {
    set((state) => ({
      speakers: [...state.speakers, { ...speaker, color: speaker.color || generateColor() }],
    }));
  },

  updateSpeakerName: (id, name) => {
    set((state) => ({
      speakers: state.speakers.map((s) =>
        s.id === id ? { ...s, name } : s
      ),
    }));
  },

  setCurrentSpeaker: (id) => {
    set({ currentSpeakerId: id });
  },

  addTranscript: (transcript) => {
    const id = generateId();
    const speaker = get().speakers.find((s) => s.id === transcript.speakerId);

    // 如果没有这个发言人，自动添加
    if (!speaker) {
      const newSpeaker: Speaker = {
        id: transcript.speakerId,
        name: `Speaker ${get().speakers.length + 1}`,
        color: generateColor(),
      };
      get().addSpeaker(newSpeaker);
    }

    set((state) => ({
      transcripts: [...state.transcripts, { ...transcript, id }],
      currentSpeakerId: transcript.speakerId,
    }));
  },

  clearTranscripts: () => {
    set({ transcripts: [], currentSpeakerId: null });
  },

  updateConfig: (newConfig) => {
    set((state) => ({
      config: { ...state.config, ...newConfig },
    }));
  },

  reset: () => {
    set({
      isRecording: false,
      meetingId: null,
      startTime: null,
      speakers: [],
      transcripts: [],
      currentSpeakerId: null,
    });
  },
}));