# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**Simultra** - AI 同声传译软件，实时会议转录与翻译工具。

### 核心功能
- 基于 FunASR 的实时语音识别
- 说话人分离与自动识别
- 中英文双向翻译（Ollama 本地大模型）
- 会议纪要生成与 PDF/Word 导出

## 技术栈

- **后端**: Python 3.10+ / FastAPI
- **语音识别**: FunASR (阿里达摩院)
- **翻译引擎**: Ollama (本地 LLM)
- **文档生成**: reportlab, python-docx
- **macOS 打包**: DMG 格式

## 常用命令

```bash
# 安装依赖
cd python
pip install -r requirements.txt

# 启动后端服务
cd python
python -m uvicorn main:app --reload --port 7860

# 运行测试
cd python
python -m pytest tests/

# 生成 macOS 安装包
python scripts/package_macos.py
```

## 架构说明

```
python/
├── main.py              # FastAPI 服务入口
├── asr/
│   └── funasr_engine.py # FunASR 语音识别封装
├── translate/
│   └── ollama_translator.py # Ollama 翻译引擎
├── export/
│   └── document_generator.py # PDF/Word 生成
└── speaker/
    └── speaker_manager.py     # 说话人管理
```

### API 设计

| 接口 | 方法 | 描述 |
|------|------|------|
| `POST /api/meeting/start` | 开始会议 | 初始化会议状态 |
| `POST /api/meeting/stop` | 结束会议 | 停止并保存 |
| `POST /api/audio/process` | 处理音频 | 上传音频文件识别 |
| `WS /ws/audio` | 实时音频 | WebSocket 流式处理 |
| `POST /api/translate` | 翻译文本 | 调用 Ollama 翻译 |
| `GET /api/speakers` | 获取说话人 | 列表所有发言人 |
| `POST /api/export/pdf` | 导出 PDF | 生成会议纪要 PDF |
| `POST /api/export/word` | 导出 Word | 生成会议纪要 DocX |

## Ollama 模型配置

推荐模型（用于翻译和摘要）:
- `llama3.2:3b` - 轻量快速
- `qwen2.5:7b` - 中文优化

Ollama 服务地址: `http://localhost:11434`

## 说话人识别流程

1. FunASR 进行语音识别
2. `SpeakerManager` 管理发言人 ID 和名称映射
3. 用户可通过 `/api/speakers/name` 设置发言人名称
4. UI 层根据用户选择的参会人推荐发言人

## macOS GPU 加速

M1/M2/M3 芯片使用 MPS 加速:
```python
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
```

## 依赖包说明

- `funasr>=1.0.0` - 阿里达摩院语音识别
- `openai>=1.12.0` - OpenAI 兼容客户端
- `python-docx>=1.1.0` - Word 文档生成
- `reportlab>=4.0.9` - PDF 生成

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OLLAMA_BASE_URL` | Ollama 服务地址 | http://localhost:11434 |
| `PYTORCH_ENABLE_MPS_FALLBACK` | 启用 Mac MPS | 1 |
| `FUNASR_MODEL` | FunASR 模型名 | speech_paraformer-large |