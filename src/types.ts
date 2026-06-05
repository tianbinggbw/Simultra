export interface Speaker {
  id: string;
  name: string;
  color: string;
  isActive?: boolean;
}

export interface Transcript {
  id: string;
  speakerId: string;
  speakerName: string;
  text: string;
  translation: string;
  timestamp: Date;
}

export interface MeetingState {
  isRecording: boolean;
  meetingId: string | null;
  startTime: Date | null;
  speakers: Speaker[];
  transcripts: Transcript[];
}

export interface AppConfig {
  ollamaUrl: string;
  modelName: string;
  sourceLang: string;
  targetLang: string;
  audioSource: 'microphone' | 'system';
  customVocabulary: string[];
}