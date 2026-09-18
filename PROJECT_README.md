# Langchain-Chatchat 个性化定制版

> 本项目基于 [chatchat-space/Langchain-Chatchat](https://github.com/chatchat-space/Langchain-Chatchat) v0.3.1.3 进行二次开发与定制修改。

## 项目简介

本项目是在开源项目 Langchain-Chatchat 基础上，针对以下方面进行了个性化改造：

- **界面汉化与主题定制**：WebUI 界面全面中文化，新增粉色主题样式
- **Ollama 模型管理面板**：新增 Ollama 本机模型列表展示、详情查看、一键切换功能
- **上传校验优化**：文件上传前增加中文格式说明、空文件/超限/扩展名伪装等前端校验
- **聊天记录导出**：支持将对话记录导出为 Markdown 文件
- **一键启停脚本**：提供 `start_chatchat.bat` 和 `stop_chatchat.bat` 便捷启动脚本

## 技术栈

| 组件 | 技术 |
|------|------|
| 前端 | Streamlit + streamlit-chatbox |
| 后端 | FastAPI + Langchain |
| 模型服务 | Ollama（qwen2:1.5b + bge-large-zh-v1.5） |
| 向量数据库 | FAISS |
| 运行环境 | Python 3.10+ |

## 快速开始

### 环境要求

- Python 3.10 ~ 3.11
- Ollama（已安装并拉取模型）

### 安装与启动

```bash
# 1. 克隆仓库
git clone <你的仓库地址>
cd Langchain-Chatchat

# 2. 创建虚拟环境
python -m venv venv
.\venv\Scripts\Activate.ps1  # PowerShell
# 或 .\venv\Scripts\activate.bat  # CMD

# 3. 安装依赖
pip install -e libs\chatchat-server

# 4. 初始化配置
cd libs\chatchat-server
chatchat init
chatchat kb -r  # 初始化知识库（可选）

# 5. 启动服务
chatchat start -a
```

或直接双击项目根目录的 `start_chatchat.bat`。

### 服务地址

| 服务 | 地址 |
|------|------|
| WebUI | http://127.0.0.1:8501 |
| API Server | http://127.0.0.1:7861 |

## 相对于原项目的改动

| 改动项 | 说明 |
|--------|------|
| `webui.py` | 新增粉色主题 CSS 注入、页面导航样式 |
| `dialogue.py` | 界面汉化、会话重命名中文校验、聊天记录导出 Markdown |
| `kb_chat.py` | 文件上传前中文格式说明、前端校验 |
| `knowledge_base.py` | 知识库管理页汉化与提示优化 |
| `ollama_panel.py` | 新增 Ollama 模型管理面板（202行） |
| `upload_utils.py` | 新增上传前端校验工具（113行） |
| `startup.py` | 启动流程适配 |
| `utils.py` | 工具函数适配 |

## 致谢

本项目基于以下开源项目修改，特此感谢：

- [Langchain-Chatchat](https://github.com/chatchat-space/Langchain-Chatchat) - Apache 2.0 License
- [LangChain](https://github.com/langchain-ai/langchain)
- [Ollama](https://github.com/ollama/ollama)
- [Streamlit](https://github.com/streamlit/streamlit)

## 许可证

本项目遵循 [Apache License 2.0](LICENSE) 协议。使用本项目时请遵守原项目的许可条款。
