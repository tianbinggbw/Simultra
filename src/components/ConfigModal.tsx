import React, { useState } from 'react';
import { useMeetingStore } from '../store/meetingStore';

interface ConfigModalProps {
  onClose: () => void;
}

const ConfigModal: React.FC<ConfigModalProps> = ({ onClose }) => {
  const { config, updateConfig } = useMeetingStore();
  const [formData, setFormData] = useState(config);
  const [models, setModels] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${formData.ollamaUrl}/api/tags`);
      if (response.ok) {
        const data = await response.json();
        setModels(data.models?.map((m: any) => m.name) || []);
      }
    } catch (error) {
      console.error('Failed to fetch models:', error);
    }
    setLoading(false);
  };

  const handleSave = () => {
    updateConfig(formData);
    onClose();
  };

  const testConnection = async () => {
    setTesting(true);
    try {
      const response = await fetch(`${formData.ollamaUrl}/api/tags`);
      if (response.ok) {
        alert('✅ Ollama 连接成功！');
      } else {
        alert('❌ 连接失败');
      }
    } catch (error) {
      alert('❌ 无法连接到 Ollama 服务');
    }
    setTesting(false);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">⚙️ 设置</h2>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="modal-body">
          <div className="form-group">
            <label className="form-label">Ollama 服务地址</label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="text"
                className="form-input"
                value={formData.ollamaUrl}
                onChange={(e) =>
                  setFormData({ ...formData, ollamaUrl: e.target.value })
                }
                placeholder="http://localhost:11434"
              />
              <button
                className="btn btn-secondary"
                onClick={testConnection}
                disabled={testing}
              >
                {testing ? '测试中...' : '测试'}
              </button>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">翻译模型</label>
            <select
              className="form-select"
              value={formData.modelName}
              onChange={(e) =>
                setFormData({ ...formData, modelName: e.target.value })
              }
            >
              {loading ? (
                <option>加载中...</option>
              ) : models.length > 0 ? (
                models.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))
              ) : (
                <>
                  <option value="llama3.2:3b">llama3.2:3b (推荐)</option>
                  <option value="qwen2.5:7b">qwen2.5:7b</option>
                  <option value="llama3.1:8b">llama3.1:8b</option>
                </>
              )}
            </select>
            <small style={{ color: 'var(--text-secondary)', marginTop: '0.25rem', display: 'block' }}>
              推荐使用 llama3.2:3b（轻量快速）
            </small>
          </div>

          <div className="form-group">
            <label className="form-label">音频源</label>
            <select
              className="form-select"
              value={formData.audioSource}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  audioSource: e.target.value as 'microphone' | 'system',
                })
              }
            >
              <option value="microphone">🎤 麦克风</option>
              <option value="system">🔊 系统音频 (需安装 BlackHole)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">翻译方向</label>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <select
                className="form-select"
                style={{ flex: 1 }}
                value={formData.sourceLang}
                onChange={(e) =>
                  setFormData({ ...formData, sourceLang: e.target.value })
                }
              >
                <option value="en">🇺🇸 英语</option>
                <option value="zh">🇨🇳 中文</option>
                <option value="ja">🇯🇵 日语</option>
                <option value="ko">🇰🇷 韩语</option>
              </select>

              <span style={{ lineHeight: '2.5rem' }}>→</span>

              <select
                className="form-select"
                style={{ flex: 1 }}
                value={formData.targetLang}
                onChange={(e) =>
                  setFormData({ ...formData, targetLang: e.target.value })
                }
              >
                <option value="zh">🇨🇳 中文</option>
                <option value="en">🇺🇸 英语</option>
                <option value="ja">🇯🇵 日语</option>
                <option value="ko">🇰🇷 韩语</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">自定义词汇 (每行一个)</label>
            <textarea
              className="form-input"
              rows={4}
              value={formData.customVocabulary.join('\n')}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  customVocabulary: e.target.value.split('\n').filter(Boolean),
                })
              }
              placeholder="输入专业术语，每行一个&#10;例如: Kubernetes&#10;Docker"
            />
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            取消
          </button>
          <button className="btn btn-primary" onClick={handleSave}>
            保存设置
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfigModal;