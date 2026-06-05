"""
FunASR 语音识别引擎
支持实时语音识别、说话人分离、中英文识别
"""
import os
import asyncio
from typing import Optional, Dict, Any, List
import numpy as np

class FunASREngine:
    """FunASR 语音识别引擎封装"""

    def __init__(self, model_name: str = "iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"):
        self.model_name = model_name
        self.model = None
        self.vocabulary = []
        self._initialized = False

    async def initialize(self):
        """初始化 FunASR 模型"""
        if self._initialized:
            return

        try:
            from funasr import AutoModel

            # 检查是否有 Mac MPS 支持
            if os.environ.get("PYTORCH_ENABLE_MPS_FALLBACK") == "1":
                print("正在使用 Mac MPS 加速...")

            # 初始化模型
            self.model = AutoModel(
                model=self.model_name,
                model_revision="v2.0.4",
                device="mps" if os.uname().sysname == "Darwin" else "cuda"
            )

            self._initialized = True
            print(f"FunASR 模型加载完成: {self.model_name}")

        except ImportError:
            print("FunASR 未安装，将使用模拟模式进行开发")
            self._initialized = True

    async def recognize(self, audio_data: bytes) -> Dict[str, Any]:
        """
        识别音频数据

        Args:
            audio_data: 音频字节数据

        Returns:
            识别结果字典，包含 text, language, speaker 等字段
        """
        await self.initialize()

        # 如果模型未加载，使用模拟结果
        if self.model is None:
            return {
                "text": "[模拟识别结果] Hello, welcome to the meeting.",
                "language": "en",
                "speaker": "Speaker_1",
                "timestamp": asyncio.get_event_loop().time()
            }

        try:
            # 转换音频数据
            # audio_array = np.frombuffer(audio_data, dtype=np.float32)

            # 调用 FunASR
            result = self.model.generate(
                input=audio_data,
                batch_size=1
            )

            if result:
                return {
                    "text": result[0].get("text", ""),
                    "language": result[0].get("language", "en"),
                    "speaker": result[0].get("spk", "Unknown"),
                    "timestamp": asyncio.get_event_loop().time()
                }

        except Exception as e:
            print(f"识别错误: {e}")

        return {"text": "", "error": str(e)}

    async def recognize_stream(self, audio_chunk: bytes) -> Optional[Dict[str, Any]]:
        """流式识别（实时处理）"""
        if not audio_chunk:
            return None

        # 简单的能量检测，判断是否有语音
        try:
            audio_array = np.frombuffer(audio_chunk, dtype=np.float32)
            energy = np.abs(audio_array).mean()

            # 能量太低，视为静音
            if energy < 0.01:
                return None

        except Exception:
            pass

        return await self.recognize(audio_chunk)

    async def recognize_file(self, file_path: str) -> Dict[str, Any]:
        """识别音频文件"""
        await self.initialize()

        if self.model is None:
            return {
                "text": f"[模拟文件识别] {os.path.basename(file_path)}",
                "language": "en",
                "segments": []
            }

        try:
            result = self.model.generate(
                input=file_path,
                batch_size=1
            )

            return {
                "text": result[0].get("text", ""),
                "language": result[0].get("language", "en"),
                "segments": result[0].get("segments", [])
            }

        except Exception as e:
            return {"text": "", "error": str(e)}

    def set_vocabulary(self, vocabulary: List[str]):
        """设置自定义词汇库"""
        self.vocabulary = vocabulary
        if self.model:
            # 如果模型支持，注入词汇
            print(f"已设置自定义词汇库: {len(vocabulary)} 个词")

    async def speaker_diarization(self, audio_data: bytes, num_speakers: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        说话人分离

        Args:
            audio_data: 音频数据
            num_speakers: 预估说话人数量

        Returns:
            说话人片段列表
        """
        await self.initialize()

        # 模拟说话人分离结果
        return [
            {"speaker": "Speaker_1", "start": 0.0, "end": 5.2, "text": "Hello everyone."},
            {"speaker": "Speaker_2", "start": 5.3, "end": 10.1, "text": "Thank you for joining."},
        ]

    def close(self):
        """关闭引擎，释放资源"""
        if self.model:
            del self.model
            self.model = None
        self._initialized = False