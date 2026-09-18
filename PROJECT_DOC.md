# 项目文档

## 1. 项目结构

```
Langchain-Chatchat/
├── libs/chatchat-server/        # 核心代码
│   └── chatchat/
│       ├── webui.py             # WebUI 入口（粉色主题）
│       ├── webui_pages/
│       │   ├── dialogue/        # 对话页面
│       │   ├── knowledge_base/  # 知识库管理
│       │   ├── ollama_panel.py  # [新增] Ollama 模型面板
│       │   └── upload_utils.py  # [新增] 上传校验工具
│       ├── server/              # 后端 API
│       └── startup.py           # 启动流程
├── .streamlit/
│   └── config.toml              # Streamlit 配置（粉色主题、端口8501）
├── docker/                      # Docker 部署文件
├── docs/                        # 原项目文档
├── start_chatchat.bat           # 一键启动脚本
├── stop_chatchat.bat            # 一键停止脚本
└── PROJECT_README.md            # 项目简介（本次生成）
```

## 2. 新增功能说明

### 2.1 Ollama 模型管理面板

位置：`libs/chatchat-server/chatchat/webui_pages/ollama_panel.py`

功能：
- 读取本机 Ollama 模型列表（`/api/tags`）
- 展示模型详情（参数量、量化等级）
- 一键应用为当前对话模型
- 刷新模型列表

### 2.2 上传前端校验

位置：`libs/chatchat-server/chatchat/webui_pages/upload_utils.py`

功能：
- 空文件拦截（中文提示）
- 200MB 文件大小超限检测
- 扩展名伪装检测（如 .txt 实为 .exe）
- 后端不可达时的中文错误提示

### 2.3 聊天记录导出

位置：`libs/chatchat-server/chatchat/webui_pages/dialogue/dialogue.py`

功能：
- 支持导出当前会话或全部会话
- 导出为 Markdown 格式
- 纯前端实现，无需后端参与

## 3. 配置文件说明

### 3.1 模型配置 (`libs/chatchat-server/model_settings.yaml`)

```yaml
DEFAULT_LLM_MODEL: qwen2:1.5b
DEFAULT_EMBEDDING_MODEL: quentinz/bge-large-zh-v1.5

MODEL_PLATFORMS:
  - platform_name: ollama
    platform_type: ollama
    api_base_url: http://127.0.0.1:11434/v1
    api_key: EMPTY
    llm_models:
      - qwen2:1.5b
    embed_models:
      - quentinz/bge-large-zh-v1.5
```

### 3.2 基础配置 (`libs/chatchat-server/basic_settings.yaml`)

```yaml
KB_ROOT_PATH: <知识库存储路径>
DB_ROOT_PATH: <数据库存储路径>
```

### 3.3 Streamlit 配置 (`.streamlit/config.toml`)

```toml
[theme]
primaryColor = "#FF69B4"  # 粉色主题

[server]
port = 8501
maxUploadSize = 200
```

## 4. 常见问题

### Q1: WebUI 打不开
- 确认使用 `chatchat start -a` 启动
- 检查 8501 端口是否被占用
- 确认在 `libs/chatchat-server` 目录下启动

### Q2: 对话报"无法连接API服务器"
- 确认 7861 端口服务正常
- 检查防火墙是否拦截

### Q3: 模型报错
- 确认 Ollama 已启动（http://127.0.0.1:11434）
- 确认模型已拉取：`ollama list`

### Q4: 上传文件失败
- 检查文件大小是否超过 200MB
- 确认后端服务正常运行

## 5. 开发指南

### 5.1 添加新页面

1. 在 `libs/chatchat-server/chatchat/webui_pages/` 下创建新文件
2. 在 `webui.py` 中注册新页面

### 5.2 添加新工具

1. 在 `libs/chatchat-server/chatchat/server/agent/tools_factory/` 下创建工具
2. 在 WebUI 工具设置中启用

### 5.3 修改主题

编辑 `.streamlit/config.toml` 中的 `[theme]` 部分。

## 6. 更新日志

### 2026-09-15
- 完成 WebUI 界面汉化
- 新增 Ollama 模型管理面板
- 新增上传前端校验
- 新增聊天记录导出功能
- 新增一键启停脚本
- 完成 GUI 测试验证

---

*本文档基于 Langchain-Chatchat v0.3.1.3 改造版本*
