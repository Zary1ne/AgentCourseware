@echo off
chcp 65001 >nul
echo ========================================
echo   AI教学智能体 - 启动脚本
echo ========================================
echo.

echo [1/2] 启动后端服务...
start "AI教学智能体-后端" cmd /c "cd /d "d:\Zary1ne\项目组\ai-teaching-agent\backend" && D:\66920\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo 后端服务已启动 (http://localhost:8000)
echo API文档: http://localhost:8000/docs
echo.

echo [2/2] 启动前端开发服务器...
start "AI教学智能体-前端" cmd /c "cd /d "d:\Zary1ne\项目组\ai-teaching-agent\frontend" && npm run dev"
echo 前端服务已启动 (http://localhost:5173)
echo.

echo ========================================
echo   启动完成! 请在浏览器访问:
echo   http://localhost:5173
echo ========================================
pause
