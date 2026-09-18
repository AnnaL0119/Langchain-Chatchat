@echo off
chcp 65001 >nul
echo 正在停止 Langchain-Chatchat (端口 7861 / 8501)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr "LISTENING" ^| findstr ":7861 :8501"') do (
    echo 结束进程 PID %%a
    taskkill /F /T /PID %%a 2>nul
)
echo 完成。
pause
