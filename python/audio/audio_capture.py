"""
音频捕获模块
支持麦克风输入和系统音频捕获（macOS）
"""
import asyncio
import queue
import threading
from typing import Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
import numpy as np

class AudioSource(Enum):
    """音频源类型"""
    MICROPHONE = "microphone"
    SYSTEM_AUDIO = "system_audio"
    SCREEN_SHARE = "screen_share"  # 腾讯会议/Zoom 等

class AudioFormat:
    """音频格式配置"""
    SAMPLE_RATE = 16000
    CHANNELS = 1
    CHUNK_SIZE = 1024
    DTYPE = np.float32

@dataclass
class AudioChunk:
    """音频数据块"""
    data: np.ndarray
    sample_rate: int
    timestamp: float
    source: AudioSource

class AudioCapture:
    """
    音频捕获器
    支持麦克风输入和系统音频录制
    """

    def __init__(
        self,
        source: AudioSource = AudioSource.MICROPHONE,
        sample_rate: int = AudioFormat.SAMPLE_RATE,
        channels: int = AudioFormat.CHANNELS,
        chunk_size: int = AudioFormat.CHUNK_SIZE
    ):
        self.source = source
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size

        self._stream = None
        self._is_recording = False
        self._audio_queue: queue.Queue = queue.Queue()
        self._callback: Optional[Callable] = None
        self._thread: Optional[threading.Thread] = None

        # 能量阈值（用于语音活动检测）
        self.energy_threshold = 0.01

    def set_callback(self, callback: Callable[[AudioChunk], None]):
        """设置音频数据回调"""
        self._callback = callback

    def _get_device_info(self):
        """获取音频设备信息"""
        try:
            import sounddevice as sd
            return sd.query_devices()
        except ImportError:
            return None

    def _list_microphones(self) -> List[dict]:
        """列出可用的麦克风设备"""
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            microphones = []

            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    microphones.append({
                        'id': i,
                        'name': dev['name'],
                        'channels': dev['max_input_channels'],
                        'sample_rate': dev['default_samplerate']
                    })

            return microphones
        except ImportError:
            return []

    def _audio_callback(self, indata, frames, time, status):
        """音频流回调函数"""
        if status:
            print(f"音频状态警告: {status}")

        # 转换为 numpy 数组
        audio_data = indata[:, 0].copy()  # 取第一个声道

        # 计算能量（用于语音检测）
        energy = np.abs(audio_data).mean()

        # 如果能量太低，跳过（静音）
        if energy < self.energy_threshold:
            return

        # 创建音频块
        chunk = AudioChunk(
            data=audio_data,
            sample_rate=self.sample_rate,
            timestamp=time.currentTime,
            source=self.source
        )

        # 放入队列
        try:
            self._audio_queue.put_nowait(chunk)
        except queue.Full:
            pass  # 队列满，丢弃数据

        # 调用回调
        if self._callback:
            self._callback(chunk)

    def _recording_loop(self):
        """录音线程主循环"""
        import sounddevice as sd

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=AudioFormat.DTYPE,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
                device=self._get_default_input_device()
            ):
                while self._is_recording:
                    sd.sleep(100)  # 100ms 间隔
        except Exception as e:
            print(f"录音线程错误: {e}")

    def _get_default_input_device(self) -> Optional[int]:
        """获取默认输入设备"""
        try:
            import sounddevice as sd
            return sd.query_devices(kind='input')
        except:
            return None

    def start(self):
        """开始录音"""
        if self._is_recording:
            return

        self._is_recording = True
        self._thread = threading.Thread(target=self._recording_loop, daemon=True)
        self._thread.start()
        print(f"✓ 音频捕获已开始: {self.source.value}")

    def stop(self):
        """停止录音"""
        if not self._is_recording:
            return

        self._is_recording = False
        if self._thread:
            self._thread.join(timeout=1)
        print(f"✓ 音频捕获已停止: {self.source.value}")

    def get_audio_chunk(self, timeout: float = 1.0) -> Optional[AudioChunk]:
        """获取一个音频块（阻塞）"""
        try:
            return self._audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_audio_chunks(self, max_chunks: int = 10) -> List[AudioChunk]:
        """获取多个音频块（非阻塞）"""
        chunks = []
        for _ in range(max_chunks):
            try:
                chunk = self._audio_queue.get_nowait()
                chunks.append(chunk)
            except queue.Empty:
                break
        return chunks

    def clear_queue(self):
        """清空音频队列"""
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except queue.Empty:
                break

    def is_recording(self) -> bool:
        """检查是否正在录音"""
        return self._is_recording


class SystemAudioCapture(AudioCapture):
    """
    系统音频捕获（ macOS）
    用于捕获腾讯会议、Zoom 等应用的声音
    """

    # macOS 上可用的音频源
    # 注意：系统音频录制需要特殊权限
    MACOS_AUDIO_SOURCES = {
        "zoom": "zoom.us",
        "teams": "Microsoft Teams",
        "tencent": "Tencent Meeting",
        "discord": "Discord",
        "system": "Built-in Output"
    }

    def __init__(self, app_name: str = "system"):
        super().__init__(source=AudioSource.SYSTEM_AUDIO)
        self.app_name = app_name

    def _recording_loop(self):
        """
        macOS 系统音频录制循环

        注意：macOS 需要使用 BlackHole 或类似虚拟音频设备
        来捕获系统音频流
        """
        try:
            import sounddevice as sd

            # BlackHole 虚拟设备 ID（通常为 1 或 2）
            # 用户需要安装 BlackHole: https://github.com/ExistentialAudio/BlackHole
            device = self._find_blackhole_device()

            if device is None:
                print("警告: 未找到 BlackHole 虚拟音频设备")
                print("  请安装 BlackHole: https://github.com/ExistentialAudio/BlackHole")
                print("  并在音频设置中将 BlackHole 设置为系统音频输出")
                # 使用备用方案
                device = self._get_default_input_device()

            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=2,  # 系统音频通常是立体声
                dtype=AudioFormat.DTYPE,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
                device=device
            ):
                while self._is_recording:
                    sd.sleep(100)

        except Exception as e:
            print(f"系统音频捕获错误: {e}")

    def _find_blackhole_device(self) -> Optional[int]:
        """查找 BlackHole 虚拟设备"""
        try:
            import sounddevice as sd
            devices = sd.query_devices()

            for i, dev in enumerate(devices):
                if 'BlackHole' in dev.get('name', ''):
                    return i
        except:
            pass
        return None

    def list_system_audio_apps(self) -> List[str]:
        """列出可用的系统音频应用"""
        return list(self.MACOS_AUDIO_SOURCES.keys())


class AudioCaptureManager:
    """
    音频捕获管理器
    统一管理多个音频源
    """

    def __init__(self):
        self._captures: dict[AudioSource, AudioCapture] = {}
        self._active_source: Optional[AudioSource] = None

    def add_capture(self, source: AudioSource, capture: AudioCapture):
        """添加音频捕获器"""
        self._captures[source] = capture

    def set_active_source(self, source: AudioSource):
        """设置活跃的音频源"""
        # 停止当前的
        if self._active_source and self._active_source in self._captures:
            self._captures[self._active_source].stop()

        # 启动新的
        self._active_source = source
        if source in self._captures:
            self._captures[source].start()

    def start_all(self):
        """启动所有捕获"""
        for capture in self._captures.values():
            capture.start()

    def stop_all(self):
        """停止所有捕获"""
        for capture in self._captures.values():
            capture.stop()

    def get_capture(self, source: AudioSource) -> Optional[AudioCapture]:
        """获取指定音频源"""
        return self._captures.get(source)