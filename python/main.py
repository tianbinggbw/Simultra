"""
Simultra - AI 同声传译软件后端服务
FastAPI 服务器，提供语音识别、翻译、会议纪要生成等接口
"""
import os
import asyncio
import json
import base64
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 导入各功能模块
from asr.funasr_engine import FunASREngine
from translate.ollama_translator import OllamaTranslator
from export.document_generator import DocumentGenerator
from speaker.speaker_manager import SpeakerManager
from audio.audio_capture import AudioCapture, SystemAudioCapture, AudioSource, AudioCaptureManager

# 全局变量
asr_engine: Optional[FunASREngine] = None
translator: Optional[OllamaTranslator] = None
document_gen: Optional[DocumentGenerator] = None
speaker_manager: Optional[SpeakerManager] = None
audio_manager: Optional[AudioCaptureManager] = None

# 会议状态
current_meeting = {
    "id": None,
    "start_time": None,
    "speaker_segments": [],
    "transcripts": [],
    "translations": []
}

class MeetingConfig(BaseModel):
    ollama_url: str = "http://localhost:11434"
    model_name: str = "llama3.2:3b"
    source_lang: str = "en"
    target_lang: str = "zh"
    audio_source: str = "microphone"  # microphone or system
    custom_vocabulary: Optional[List[str]] = None

class SpeakerName(BaseModel):
    speaker_id: str
    name: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global asr_engine, translator, document_gen, speaker_manager

    # 初始化各模块
    print("正在初始化 Simultra 后端服务...")

    # 设置 MPS 加速（Mac M1/M2）
    os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

    # 初始化翻译器
    translator = OllamaTranslator()
    print("翻译模块初始化完成")

    # 初始化文档生成器
    document_gen = DocumentGenerator()
    print("文档生成模块初始化完成")

    # 初始化说话人管理器
    speaker_manager = SpeakerManager()
    print("说话人管理模块初始化完成")

    yield

    # 清理
    if asr_engine:
        asr_engine.close()

# 创建 FastAPI 应用
app = FastAPI(
    title="Simultra API",
    description="AI 同声传译软件后端 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== 健康检查 ==============

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# ============== 配置接口 ==============

@app.post("/api/config")
async def configure(config: MeetingConfig):
    """配置翻译参数"""
    global translator, asr_engine

    # 配置翻译器
    translator.configure(
        base_url=config.ollama_url,
        model_name=config.model_name
    )

    # 配置语音识别（如果需要）
    if asr_engine is None:
        asr_engine = FunASREngine()

    # 设置自定义词汇
    if config.custom_vocabulary:
        asr_engine.set_vocabulary(config.custom_vocabulary)

    return {"status": "configured", "config": config.dict()}

@app.get("/api/config/models")
async def list_models(ollama_url: str = "http://localhost:11434"):
    """获取可用的 Ollama 模型列表"""
    try:
        models = await translator.list_models(ollama_url)
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============== 会议管理 ==============

@app.post("/api/meeting/start")
async def start_meeting():
    """开始新会议"""
    global current_meeting

    current_meeting = {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "start_time": datetime.now().isoformat(),
        "speaker_segments": [],
        "transcripts": [],
        "translations": []
    }

    return {"meeting_id": current_meeting["id"], "status": "started"}

@app.post("/api/meeting/stop")
async def stop_meeting():
    """结束当前会议"""
    global current_meeting

    meeting_id = current_meeting["id"]
    current_meeting["end_time"] = datetime.now().isoformat()

    return {"meeting_id": meeting_id, "status": "stopped"}

@app.get("/api/meeting/status")
async def get_meeting_status():
    """获取当前会议状态"""
    return current_meeting

# ============== 音频处理 ==============

@app.post("/api/audio/process")
async def process_audio(audio: UploadFile = File(...)):
    """处理上传的音频文件"""
    if asr_engine is None:
        asr_engine = FunASREngine()

    # 读取音频数据
    audio_data = await audio.read()

    # 语音识别
    result = await asr_engine.recognize(audio_data)

    # 翻译
    if translator and result.get("text"):
        translation = await translator.translate(
            result["text"],
            source_lang=result.get("language", "en"),
            target_lang="zh"
        )
        result["translation"] = translation

    return result

@app.websocket("/ws/audio")
async def audio_websocket(websocket: WebSocket):
    """WebSocket 实时音频处理"""
    await websocket.accept()

    if asr_engine is None:
        asr_engine = FunASREngine()

    try:
        while True:
            # 接收音频数据
            data = await websocket.receive_bytes()

            # 语音识别
            result = await asr_engine.recognize_stream(data)

            if result:
                # 翻译
                if translator and result.get("text"):
                    translation = await translator.translate(
                        result["text"],
                        source_lang=result.get("language", "en"),
                        target_lang="zh"
                    )
                    result["translation"] = translation

                    # 记录到会议
                    current_meeting["transcripts"].append(result)

                # 发送结果
                await websocket.send_json(result)

    except WebSocketDisconnect:
        print("WebSocket 连接断开")

# ============== 说话人管理 ==============

@app.get("/api/speakers")
async def get_speakers():
    """获取当前会议的说话人列表"""
    speakers = speaker_manager.get_speakers()
    return {"speakers": speakers}

@app.post("/api/speakers/name")
async def set_speaker_name(speaker: SpeakerName):
    """设置说话人名称"""
    speaker_manager.set_name(speaker.speaker_id, speaker.name)
    return {"speaker_id": speaker.speaker_id, "name": speaker.name}

@app.get("/api/speakers/assignments")
async def get_speaker_assignments():
    """获取用户-发言人的分配关系"""
    return speaker_manager.get_user_assignments()

# ============== 翻译接口 ==============

@app.post("/api/translate")
async def translate_text(text: str, source_lang: str = "en", target_lang: str = "zh"):
    """翻译文本"""
    if translator is None:
        raise HTTPException(status_code=500, detail="翻译器未初始化")

    result = await translator.translate(text, source_lang, target_lang)
    return {"original": text, "translation": result}

# ============== 会议纪要 ==============

@app.get("/api/meeting/summary")
async def get_meeting_summary():
    """获取会议摘要"""
    if not current_meeting["transcripts"]:
        return {"summary": "暂无内容"}

    # 生成摘要
    summary = await translator.generate_summary(
        current_meeting["transcripts"]
    )

    return {
        "meeting_id": current_meeting["id"],
        "duration": len(current_meeting["transcripts"]),
        "speaker_count": len(speaker_manager.get_speakers()),
        "summary": summary
    }

@app.get("/api/meeting/transcripts")
async def get_transcripts():
    """获取完整会议记录"""
    return {
        "transcripts": current_meeting["transcripts"],
        "translations": current_meeting["translations"]
    }

# ============== 文档导出 ==============

@app.post("/api/export/pdf")
async def export_pdf(filename: Optional[str] = None):
    """导出为 PDF"""
    if document_gen is None:
        raise HTTPException(status_code=500, detail="文档生成器未初始化")

    if not filename:
        filename = f"meeting_{current_meeting['id']}.pdf"

    # 收集会议数据
    meeting_data = {
        "title": f"会议纪要 - {current_meeting['id']}",
        "date": current_meeting.get("start_time", datetime.now().isoformat()),
        "speakers": speaker_manager.get_speakers(),
        "transcripts": current_meeting["transcripts"]
    }

    # 生成 PDF
    pdf_path = await document_gen.generate_pdf(meeting_data, filename)
    return {"file_path": pdf_path, "filename": filename}

@app.post("/api/export/word")
async def export_word(filename: Optional[str] = None):
    """导出为 Word 文档"""
    if document_gen is None:
        raise HTTPException(status_code=500, detail="文档生成器未初始化")

    if not filename:
        filename = f"meeting_{current_meeting['id']}.docx"

    # 收集会议数据
    meeting_data = {
        "title": f"会议纪要 - {current_meeting['id']}",
        "date": current_meeting.get("start_time", datetime.now().isoformat()),
        "speakers": speaker_manager.get_speakers(),
        "transcripts": current_meeting["transcripts"]
    }

    # 生成 Word
    docx_path = await document_gen.generate_docx(meeting_data, filename)
    return {"file_path": docx_path, "filename": filename}

@app.post("/api/feedback")
async def submit_feedback(feedback: Dict[str, Any]):
    """提交用户反馈"""
    # 保存反馈到文件
    feedback_file = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(feedback_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "meeting_id": current_meeting["id"],
            "feedback": feedback
        }, f, ensure_ascii=False, indent=2)

    return {"status": "saved", "file": feedback_file}

# ============== 音频捕获接口 ==============

@app.get("/api/audio/devices")
async def list_audio_devices():
    """获取可用的音频设备"""
    try:
        mic_capture = AudioCapture(source=AudioSource.MICROPHONE)
        microphones = mic_capture._list_microphones()
        return {"microphones": microphones}
    except Exception as e:
        return {"microphones": [], "error": str(e)}

@app.post("/api/audio/start")
async def start_audio_capture(source: str = "microphone"):
    """开始音频捕获"""
    global audio_manager, asr_engine

    if audio_manager is None:
        audio_manager = AudioCaptureManager()

    try:
        if source == "system":
            capture = SystemAudioCapture()
        else:
            capture = AudioCapture(source=AudioSource.MICROPHONE)

        if asr_engine is None:
            asr_engine = FunASREngine()

        # 设置音频数据回调
        async def audio_callback(chunk):
            # 语音识别
            result = await asr_engine.recognize_stream(chunk.data.tobytes())

            if result and result.get("text"):
                # 翻译
                translation = await translator.translate(
                    result["text"],
                    source_lang=result.get("language", "en"),
                    target_lang="zh"
                )
                result["translation"] = translation

                # 记录到会议
                current_meeting["transcripts"].append(result)

                # 广播到 WebSocket
                for connection in active_connections:
                    try:
                        await connection.send_json(result)
                    except:
                        pass

        capture.set_callback(audio_callback)
        capture.start()

        source_type = AudioSource.SYSTEM_AUDIO if source == "system" else AudioSource.MICROPHONE
        audio_manager.add_capture(source_type, capture)
        audio_manager.set_active_source(source_type)

        return {"status": "started", "source": source}

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/audio/stop")
async def stop_audio_capture():
    """停止音频捕获"""
    global audio_manager

    if audio_manager:
        audio_manager.stop_all()

    return {"status": "stopped"}

# WebSocket 连接管理
active_connections: List[WebSocket] = []

@app.websocket("/ws/live")
async def live_transcription(websocket: WebSocket):
    """实时转录 WebSocket 连接"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            # 保持连接
            data = await websocket.receive_text()
            # 可以处理客户端消息
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        active_connections.remove(websocket)

# ============== 入口点 ==============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)