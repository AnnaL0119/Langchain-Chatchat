@echo off
chcp 65001 >nul
cd /d "E:\dasishang\grogrem\Langchain-Chatchat\libs\chatchat-server"
echo ================================================
echo  Langchain-Chatchat 启动中...
echo  API 服务:   http://127.0.0.1:7861  (接口文档 /docs)
echo  WebUI 界面: http://127.0.0.1:8501
echo  模型服务:   Ollama http://127.0.0.1:11434 (需先启动)
echo  按 Ctrl+C 停止服务
echo ================================================
"E:\dasishang\grogrem\Langchain-Chatchat\venv\Scripts\chatchat.exe" start -a
pause
