"""
Ollama 翻译引擎
支持本地大模型翻译，兼容 OpenAI API 格式
"""
import json
import asyncio
from typing import Optional, List, Dict, Any

class OllamaTranslator:
    """Ollama 翻译引擎封装"""

    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama3.2:3b"):
        self.base_url = base_url
        self.model_name = model_name
        self._client = None

    def configure(self, base_url: str, model_name: str):
        """配置翻译器参数"""
        self.base_url = base_url
        self.model_name = model_name
        self._client = None  # 重置客户端

    async def _get_client(self):
        """获取 HTTP 客户端"""
        if self._client is None:
            import aiohttp
            self._client = aiohttp.ClientSession()
        return self._client

    async def list_models(self, base_url: str) -> List[str]:
        """获取可用的模型列表"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{base_url}/api/tags") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return [m["name"] for m in data.get("models", [])]
        except Exception as e:
            print(f"获取模型列表失败: {e}")

        # 返回默认列表
        return ["llama3.2:3b", "qwen2.5:7b", "llama3.1:8b"]

    async def translate(self, text: str, source_lang: str = "en", target_lang: str = "zh") -> str:
        """
        翻译文本

        Args:
            text: 待翻译文本
            source_lang: 源语言
            target_lang: 目标语言

        Returns:
            翻译结果
        """
        if not text.strip():
            return ""

        # 构建提示词
        prompt = self._build_translation_prompt(text, source_lang, target_lang)

        try:
            result = await self._call_llm(prompt)
            return result
        except Exception as e:
            print(f"翻译失败: {e}")
            return f"[翻译失败: {text[:20]}...]"

    def _build_translation_prompt(self, text: str, source_lang: str, target_lang: str) -> str:
        """构建翻译提示词"""
        lang_map = {
            "en": "English",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean"
        }

        source = lang_map.get(source_lang, source_lang)
        target = lang_map.get(target_lang, target_lang)

        return f"""You are a professional translator. Translate the following {source} text to {target}.

Only output the translation, nothing else.

Text: {text}

Translation:"""

    async def _call_llm(self, prompt: str) -> str:
        """调用 LLM 进行推理"""
        import aiohttp

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 512
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("response", "").strip()
                else:
                    error = await resp.text()
                    raise Exception(f"LLM 调用失败: {error}")

    async def generate_summary(self, transcripts: List[Dict[str, Any]]) -> str:
        """
        生成会议摘要

        Args:
            transcripts: 会议记录列表

        Returns:
            摘要文本
        """
        if not transcripts:
            return "暂无内容"

        # 拼接所有文本
        all_text = "\n".join([
            f"[{t.get('speaker', 'Unknown')}] {t.get('text', '')}"
            for t in transcripts if t.get('text')
        ])

        prompt = f"""You are a professional meeting summarizer. Create a concise summary of the following meeting transcript in Chinese.

Include:
1. Meeting main topics
2. Key points discussed
3. Action items or conclusions

Transcript:
{all_text}

Summary:"""

        try:
            return await self._call_llm(prompt)
        except Exception as e:
            print(f"摘要生成失败: {e}")
            return f"[摘要生成失败，请检查 Ollama 服务是否运行在 {self.base_url}]"

    async def translate_batch(self, texts: List[str], source_lang: str = "en", target_lang: str = "zh") -> List[str]:
        """批量翻译"""
        tasks = [
            self.translate(text, source_lang, target_lang)
            for text in texts
        ]
        return await asyncio.gather(*tasks)