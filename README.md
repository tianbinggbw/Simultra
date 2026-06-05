# Simultra - AI 同声传译软件

实时会议转录与翻译工具，支持说话人分离、多语言翻译、会议纪要生成。

## 功能特性

- 🎤 **实时语音识别** - 基于 FunASR 的高精度中英文识别
- 🔊 **说话人分离** - 自动区分不同发言人
- 🌐 **实时翻译** - 中英文双向翻译
- 📝 **会议纪要** - 自动生成会议摘要
- 📄 **文档导出** - 支持 PDF/Word 格式
- 🔧 **本地部署** - 保护隐私，无需联网

## 系统要求

- macOS 12.0+ (Apple Silicon M1/M2/M3 优先)
- Python 3.10+
- Ollama (本地大模型)

## 安装

### 1. 安装 Ollama

```bash
# macOS
brew install ollama

# 启动 Ollama
ollama serve

# 下载翻译模型
ollama pull llama3.2:3b
```

### 2. 安装 Python 依赖

```bash
cd python
pip install -r requirements.txt
```

### 3. 运行服务

```bash
cd python
python -m uvicorn main:app --reload --port 7860
```

## API 接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/config` | POST | 配置翻译参数 |
| `/api/meeting/start` | POST | 开始会议 |
| `/api/meeting/stop` | POST | 结束会议 |
| `/api/audio/process` | POST | 处理音频 |
| `/api/translate` | POST | 翻译文本 |
| `/api/export/pdf` | POST | 导出 PDF |
| `/api/export/word` | POST | 导出 Word |

## 推荐模型

| 用途 | 模型 | 说明 |
|------|------|------|
| 翻译 | `llama3.2:3b` | 轻量快速 |
| 翻译 | `qwen2.5:7b` | 中文优化 |
| 摘要 | `llama3.2:3b` | 可复用 |

## 项目结构

```
simultrans/
├── python/               # Python 后端
│   ├── main.py          # FastAPI 服务入口
│   ├── asr/             # 语音识别 (FunASR)
│   ├── translate/       # 翻译 (Ollama)
│   ├── export/          # 文档导出
│   └── speaker/         # 说话人管理
├── src/                  # 前端源码
└── scripts/             # 构建脚本
```

## 开发

```bash
# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
python -m uvicorn main:app --reload --port 7860

# 运行测试
pytest tests/
```

## 打包发布

```bash
# 生成 macOS dmg 安装包
python scripts/package_macos.py
```

## 许可证

MIT License