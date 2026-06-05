# Simultra - AI 同声传译软件

🎙️ 实时会议转录与翻译工具，支持说话人分离、中英文互译、会议纪要生成。

## 安装方式

### 方式一：DMG 安装包（推荐）

1. 从 [Releases](https://github.com/tianbinggbw/Simultra/releases) 下载最新版的 `Simultra-x.x.x.dmg`
2. 双击安装
3. 在 Mac 上安装 Ollama:
   ```bash
   brew install ollama
   ollama pull llama3.2:3b
   ```
4. 启动 Simultra 应用

### 方式二：从源码安装

```bash
# 1. 克隆项目
git clone https://github.com/tianbinggbw/Simultra.git
cd Simultra

# 2. 运行安装脚本
chmod +x install.sh
./install.sh

# 3. 启动
chmod +x start.sh
./start.sh
```

## Ollama 模型安装

**你必须先在 Mac 上安装 Ollama**，软件本身不包含 Ollama：

```bash
# 安装 Ollama
brew install ollama

# 下载翻译模型（必须）
ollama pull llama3.2:3b

# 下载中文优化模型（可选）
ollama pull qwen2.5:7b

# 启动 Ollama 服务
ollama serve
```

## 功能特性

| 功能 | 说明 |
|------|------|
| 🎤 **实时语音识别** | 基于 FunASR 的中英文识别，支持 M1/M2 MPS 加速 |
| 🔊 **说话人分离** | 自动区分不同发言人，可手动命名 |
| 🌐 **实时翻译** | 中英文双向翻译（英文→中文，中文→英文） |
| 📝 **会议纪要** | 自动生成会议摘要 |
| 📄 **文档导出** | 支持 PDF / Word 格式 |
| 💡 **口音优化** | 特别优化印度、日本、韩国英语口音 |

## 使用流程

1. **启动 Ollama** (如果未运行):
   ```bash
   ollama serve
   ```

2. **启动 Simultra**:
   ```bash
   ./start.sh
   # 或双击 DMG 中的应用
   ```

3. **开始会议**:
   - 点击 "开始会议" 按钮
   - 选择音频源（麦克风/系统音频）
   - 说话内容会自动识别并翻译

4. **结束会议**:
   - 点击 "结束会议"
   - 可导出 PDF 或 Word 格式的会议纪要

## 系统要求

- macOS 12.0+ (Apple Silicon M1/M2/M3 优先)
- Ollama (必须安装)
- Python 3.10+ (仅源码安装需要)

## 项目结构

```
simultrans/
├── src/                    # React 前端
│   ├── components/         # UI 组件
│   ├── store/              # 状态管理
│   └── styles/            # 样式
├── src-tauri/             # Tauri 桌面配置
├── python/                 # Python 后端
│   ├── main.py            # FastAPI 服务
│   ├── asr/               # FunASR 语音识别
│   ├── audio/             # 音频捕获
│   ├── translate/         # Ollama 翻译
│   ├── export/            # 文档生成
│   └── speaker/           # 说话人管理
├── start.sh               # 启动脚本
├── install.sh             # 安装脚本
└── .github/workflows/      # CI/CD 构建
```

## 常见问题

### Q: Ollama 连接失败
确保 Ollama 服务正在运行：
```bash
ollama serve
```

### Q: FunASR 模型下载慢
FunASR 模型会在首次运行时自动下载。可手动下载加速：
```python
from funasr import AutoModel
model = AutoModel(model='iic/speech_paraformer-large')
```

### Q: 如何捕获腾讯会议/Zoom 的声音？
需要安装 BlackHole 虚拟音频设备：
```bash
brew install blackhole-2ch
```
然后在系统音频设置中将输出改为 BlackHole。

## 开发

```bash
# 安装依赖
cd python && pip install -r requirements.txt
cd ../src && npm install

# 运行后端
cd python && python -m uvicorn main:app --port 7860

# 运行前端
cd src && npm run dev
```

## 许可证

MIT License