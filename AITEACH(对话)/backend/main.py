"""
AI 教学助手 - 对话模块后端 (陈雅朵负责)
技术栈: Python + FastAPI + SSE 流式输出

API 接口:
    POST /api/v1/chat  - SSE 流式对话

运行方式:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

import asyncio
import json
import os
import re
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import openai
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ============================================
# DeepSeek 大模型客户端初始化
# ============================================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

if not DEEPSEEK_API_KEY:
    raise ValueError("未找到 DEEPSEEK_API_KEY，请在 .env 文件中配置")

deepseek_client = openai.AsyncOpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)

# ============================================
# FastAPI 应用初始化
# ============================================
app = FastAPI(
    title="AI 教学助手 - 对话服务",
    version="1.0.0",
)

# CORS: 允许前端页面跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# 数据模型
# ============================================
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    subject: str = ""
    grade: str = ""
    lesson_type: str = ""
    duration: str = ""
    style: str = ""


# ============================================
# 意图识别 (模拟 Prompt Engineering)
# ============================================
SUBJECT_KEYWORDS = {
    "物理": ["物理", "力学", "电学", "牛顿", "运动", "能量", "光的", "磁"],
    "数学": ["数学", "函数", "几何", "代数", "方程", "概率", "微积分", "三角"],
    "化学": ["化学", "元素", "反应", "分子", "原子", "酸碱", "氧化", "有机"],
    "生物": ["生物", "细胞", "基因", "光合", "生态", "遗传", "进化", "DNA"],
    "语文": ["语文", "古诗", "文言文", "阅读", "作文", "修辞", "诗歌", "散文"],
    "英语": ["英语", "语法", "词汇", "阅读理解", "完形填空", "听力"],
    "历史": ["历史", "朝代", "战争", "革命", "古代", "近代", "文明"],
    "地理": ["地理", "气候", "地形", "河流", "板块", "人口", "城市"],
}

GRADE_KEYWORDS = {
    "高一": ["高一", "高中一年级"],
    "高二": ["高二", "高中二年级"],
    "高三": ["高三", "高中三年级"],
    "初一": ["初一", "七年级"],
    "初二": ["初二", "八年级"],
    "初三": ["初三", "九年级"],
}

TYPE_KEYWORDS = {
    "新课": ["新课", "新授课", "讲授"],
    "复习课": ["复习", "回顾", "总结课"],
    "实验课": ["实验", "动手", "操作"],
    "习题课": ["习题", "练习", "题", "做题"],
}


def recognize_intent(text: str) -> dict:
    """从用户输入中识别教学意图参数"""
    intents = {}

    for subject, keywords in SUBJECT_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            intents["subject"] = subject
            break

    for grade, keywords in GRADE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            intents["grade"] = grade
            break

    for lesson_type, keywords in TYPE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            intents["type"] = lesson_type
            break

    duration_match = re.search(r"(\d+)\s*分钟", text)
    if duration_match:
        intents["duration"] = duration_match.group(1) + "分钟"

    if "严谨" in text or "学术" in text:
        intents["style"] = "学术严谨"
    elif "活泼" in text or "互动" in text or "有趣" in text:
        intents["style"] = "活泼互动"
    elif "简洁" in text or "商务" in text or "极简" in text:
        intents["style"] = "极简商务"

    return intents


# ============================================
# AI 回复生成 (模拟大模型，后续替换为真实 API 调用)
# ============================================
def generate_ai_response(text: str, params: dict) -> str:
    """
    模拟大模型生成教学方案回复。

    TODO: 接入真实大模型 API (通义千问 / DeepSeek)
    接入方式参考:
        import openai
        client = openai.OpenAI(api_key="your-key", base_url="...")
        for chunk in client.chat.completions.create(..., stream=True):
            yield chunk.choices[0].delta.content
    """
    subject = params.get("subject", "该学科")
    grade = params.get("grade", "相应年级")
    duration = params.get("duration", "45分钟")
    lesson_type = params.get("type", "新课")

    if "牛顿" in text or "物理" in text:
        return (
            f"好的！我来帮你设计一节{grade}{subject}——牛顿第一定律的{lesson_type}教学方案，课时{duration}。\n\n"
            "以下是结构化的教学大纲：\n\n"
            "【教学目标】\n"
            "• 知识与技能：理解牛顿第一定律的内容，知道惯性的概念\n"
            "• 过程与方法：通过理想实验法，培养科学推理能力\n"
            "• 情感态度价值观：体会科学探索精神，认识物理与生活的联系\n\n"
            "【教学重难点】\n"
            "• 重点：牛顿第一定律的内容及理解\n"
            "• 难点：惯性的概念及其与质量的关系\n\n"
            "【教学过程】\n"
            "1. 引入（5分钟）：通过生活实例（公交车急刹车）引出问题\n"
            "2. 讲解（15分钟）：伽利略理想斜面实验 → 笛卡尔补充 → 牛顿总结\n"
            "3. 实验（10分钟）：惯性演示实验（小车+木块突然运动）\n"
            "4. 练习（10分钟）：典型例题分析，判断物体运动状态\n"
            "5. 总结（5分钟）：知识梳理，布置课后思考题\n\n"
            "【所需教具】斜面、小车、木块、多媒体课件\n\n"
            "需要我调整哪个部分，或者直接生成课件吗？"
        )

    if "实验" in text:
        return (
            "收到！我注意到你提到了实验环节，这很重要。以下是包含实验设计的建议：\n\n"
            "【实验设计建议】\n"
            f"• 实验类型：演示实验 + 分组探究\n"
            f"• 建议时长：{duration}中安排15-20分钟实验时间\n"
            "• 安全提示：提前检查器材，强调操作规范\n\n"
            "【实验流程】\n"
            "1. 提出问题（2分钟）\n"
            "2. 学生猜想（3分钟）\n"
            "3. 动手实验（10分钟）\n"
            "4. 数据记录与分析（3分钟）\n"
            "5. 结论汇报（2分钟）\n\n"
            "你可以告诉我具体学科和知识点，我来生成完整的教学方案。"
        )

    if "复习" in text:
        return (
            "好的！复习课的设计需要注重知识梳理和查漏补缺。\n\n"
            "【复习课教学框架】\n"
            "1. 知识回顾（10分钟）：思维导图梳理本章核心概念\n"
            "2. 易错点辨析（10分钟）：典型错误案例分析\n"
            "3. 综合练习（15分钟）：分层练习题，从基础到提高\n"
            "4. 方法总结（5分钟）：解题技巧与思路归纳\n"
            "5. 课后任务（5分钟）：针对性练习布置\n\n"
            "请告诉我具体的学科和知识点，我可以生成更详细的复习方案。"
        )

    return (
        f"好的！我已经识别到你的教学需求：\n\n"
        f"• 学科：{subject}\n"
        f"• 年级：{grade}\n"
        f"• 课型：{lesson_type}\n"
        f"• 课时：{duration}\n\n"
        "接下来我会基于以上信息为你生成教学方案。你可以进一步补充：\n"
        "1. 具体的知识点或章节\n"
        "2. 是否需要实验环节\n"
        "3. 学生的学习基础情况\n"
        "4. 特别的教学偏好\n\n"
        "请补充以上信息，我将为你生成详细的教学大纲。"
    )


# ============================================
# SSE 流式生成器 (对接 DeepSeek 大模型)
# ============================================
async def stream_response(text: str) -> AsyncGenerator[str, None]:
    """
    SSE 流式响应生成器。
    1. 先本地识别意图并推送给前端
    2. 调用 DeepSeek API 流式生成教学方案
    3. 逐字转发给前端
    4. 发送结束标记
    """
    # 1. 本地识别意图
    intents = recognize_intent(text)

    # 2. 推送意图识别结果
    intent_data = json.dumps({"type": "intents", "data": intents}, ensure_ascii=False)
    yield f"data: {intent_data}\n\n"
    await asyncio.sleep(0.1)

    # 3. 构建系统提示词
    subject = intents.get("subject", "未指定")
    grade = intents.get("grade", "未指定")
    duration = intents.get("duration", "45分钟")
    lesson_type = intents.get("type", "未指定")
    style = intents.get("style", "未指定")

    system_prompt = f"""你是一位资深的 AI 教学设计专家，擅长为中小学教师生成结构化的教学方案。

已识别的教学参数：
- 学科：{subject}
- 年级：{grade}
- 课型：{lesson_type}
- 课时：{duration}
- 风格：{style}

输出要求：
1. 使用 Markdown 风格的中文教学方案格式
2. 包含【教学目标】【教学重难点】【教学过程】【所需教具】等模块
3. 教学过程需标注每个环节的时间分配
4. 语气专业、条理清晰
5. 如果某些信息不足，请合理假设并给出建议

请直接输出教学方案内容，不要复述参数。"""

    # 4. 调用 DeepSeek 流式生成
    try:
        stream = await deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            stream=True,
            temperature=0.7,
            max_tokens=2048,
        )

        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                # DeepSeek 按 token 返回，可能包含多个字符
                # 我们将其拆分为单个字符，保持打字机效果
                for char in content:
                    chunk_data = json.dumps({"type": "content", "data": char}, ensure_ascii=False)
                    yield f"data: {chunk_data}\n\n"
                    # 控制前端显示节奏（避免一次性刷完）
                    await asyncio.sleep(0.02)

    except Exception as e:
        # DeepSeek 调用失败时，回退到本地模拟回复
        fallback = generate_ai_response(text, intents)
        for char in fallback:
            chunk_data = json.dumps({"type": "content", "data": char}, ensure_ascii=False)
            yield f"data: {chunk_data}\n\n"
            await asyncio.sleep(0.02)

    # 5. 发送结束标记
    done_data = json.dumps({"type": "done"}, ensure_ascii=False)
    yield f"data: {done_data}\n\n"


# ============================================
# API 路由
# ============================================
@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    """
    SSE 流式对话接口。

    请求体:
        {
            "message": "帮我设计一节高一物理课...",
            "session_id": "可选，会话标识",
            "subject": "",   // 前端已识别的学科
            "grade": "",     // 前端已识别的年级
            ...
        }

    返回: text/event-stream
        流式推送三种事件:
        - type=intents   : 意图识别结果 {subject, grade, type, duration, style}
        - type=content   : 单个字符
        - type=done      : 回复结束标记
    """
    return StreamingResponse(
        stream_response(request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
        },
    )


@app.get("/api/v1/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": "chat"}


# ============================================
# 启动入口
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
