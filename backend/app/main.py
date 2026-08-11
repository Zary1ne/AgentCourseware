from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import HOST, PORT, OUTPUT_DIR
from app.routers import chat, knowledge, generate, admin, auth, community, notifications, feedback

app = FastAPI(
    title="AI教学智能体 API",
    description="多模态AI互动式教学智能体 - 后端服务",
    version="1.0.0",
)

# CORS 中间件（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(generate.router)
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(community.router)
app.include_router(notifications.router)
app.include_router(feedback.router)

# 静态文件服务（生成的文件下载）
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")


@app.get("/")
async def root():
    return {
        "name": "AI教学智能体",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "AI教学智能体"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
