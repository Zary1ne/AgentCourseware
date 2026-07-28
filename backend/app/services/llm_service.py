from openai import OpenAI
from app.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from typing import List, Dict, AsyncGenerator
import json
import asyncio

# 初始化 OpenAI 兼容客户端
client = OpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL,
)

SYSTEM_PROMPT = """你是一个专业的教学智能体助手，帮助教师完成课件设计和教案撰写。

你的核心能力：
1. **需求澄清**：通过多轮对话，主动询问教师的教学目标、知识要点、授课时长、学生水平、教学风格等关键信息，直到完整理解教学需求。
2. **知识融合**：结合教师提供的参考资料内容和本地知识库检索结果，丰富教学内容。
3. **课件生成**：基于确认的需求，生成结构化的课件指令集。

对话策略：
- 如果教师的需求模糊（如只说"帮我做个物理课件"），你要主动询问：年级/学段、具体知识点、课时长度、学生已有知识基础和学习水平、教学风格偏好等。
- 特别关注学情信息：学生所在年级、整体学习水平（基础薄弱/中等/优秀）、已掌握的前置知识、学习风格偏好（视觉型/动手型/听觉型等）、是否有特殊需求（如需要更多基础铺垫或延伸拓展）。
- 每次提问控制在2-3个关键问题，不要一次性问太多。
- 当信息足够完整时，主动总结确认："根据您的需求，我理解为：...，是否准确？"

输出格式要求：
- 当需求确认完毕后，在回复末尾添加 [INTENT_READY] 标记
- 然后输出结构化的教学意图JSON：
```json
{
  "subject": "学科",
  "topic": "课题",
  "grade": "年级/学段",
  "duration": "课时(分钟)",
  "objectives": ["教学目标1", "教学目标2"],
  "knowledge_points": ["知识点1", "知识点2"],
  "key_points": ["重点1"],
  "difficult_points": ["难点1"],
  "teaching_methods": ["讲授法", "案例法"],
  "activities": ["课堂活动1"],
  "style": "professional/interesting/minimal",
  "student_profile": {
    "level": "基础薄弱/中等/优秀",
    "prior_knowledge": ["已掌握的前置知识"],
    "learning_style": "视觉型/动手型/听觉型/混合型",
    "special_needs": "特殊需求说明或留空"
  },
  "references": [{"source": "文件名", "used_content": "引用的内容摘要"}]
}
```
"""


# ===== 四段式教学方案 Prompt（来自 AITEACH(对话) 原型） =====
TEACHING_PLAN_PROMPT = '''你是 AI 教学设计专家。请根据教师的需求，生成一份完整的教学方案。

必须包含以下四个部分，用【】标注标题：

【教学目标】
- 学生学完能做什么（具体的、可验证的目标）
- 涉及的核心概念有哪些

【教学重难点】
- 重点：必须掌握的核心内容
- 难点：容易卡住的地方及突破方法

【实验设计】
- 实验名称
- 实验目标：这个小实验要验证什么
- 实验步骤（分步写清楚，每步附代码或操作说明）
- 预期结果
- 实验总结

【课后练习】
- 基础题（2道，能独立完成即可）
- 提高题（1道，稍微拓展思维）
- 思考题（1道，帮助理解原理）

要求：
1. 内容紧扣教师提出的学科和知识点
2. 语言简单直白，适合学生理解
3. 代码用 ```python ``` 包裹
4. 禁止使用 * 字符做任何格式标记
5. 始终用中文回复'''


# ===== 工具函数（来自 AITEACH(对话) 原型） =====
def clean_response(text: str) -> str:
    """移除星号格式标记"""
    return text.replace("*", "")


def is_teaching_request(text: str) -> bool:
    """判断用户是否在请求完整教学方案（关键词检测）"""
    keywords = [
        "教学目标", "教学设计", "教案", "备课", "教学方案",
        "重难点", "实验设计", "课堂练习", "完整方案", "教学大纲"
    ]
    return any(k in text for k in keywords)


def fallback_response(text: str) -> str:
    """API调用失败时的硬编码兜底回复"""
    t = text.strip()
    if any(g in t for g in ["你好", "hello", "hi", "喂", "在吗", "在不在"]) or len(t) < 3:
        return "你好！我是 AI 教学助手，请告诉我您想准备的学科和知识点，我来帮您设计教学方案～"
    return ("这是一个很好的教学主题。建议从以下方面入手：\n\n"
            "1. 明确本课时的教学目标，让学生知道学完能做什么\n"
            "2. 梳理核心知识点和重难点，设计突破策略\n"
            "3. 准备课堂活动或实验，帮助学生理解抽象概念\n"
            "4. 设计分层练习，检验学习效果\n\n"
            "[当前 AI 服务暂时不可用，以上为基础建议]")


def build_messages(history: List[Dict], system_prompt: str = SYSTEM_PROMPT) -> List[Dict]:
    """构建消息列表"""
    return [{"role": "system", "content": system_prompt}] + history


async def chat_stream(history: List[Dict]) -> AsyncGenerator[str, None]:
    """流式聊天（含教学方案检测 + 三层降级）"""
    # 检测最后一条用户消息是否为教学方案请求
    user_msgs = [m for m in history if m["role"] == "user"]
    last_user_text = user_msgs[-1]["content"] if user_msgs else ""
    use_teaching_prompt = is_teaching_request(last_user_text)

    system_prompt = TEACHING_PLAN_PROMPT if use_teaching_prompt else SYSTEM_PROMPT
    messages = build_messages(history, system_prompt)

    # 第一层：直接调用 OpenAI
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            stream=True,
            temperature=0.7,
            max_tokens=4096,
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield clean_response(chunk.choices[0].delta.content)
        return
    except Exception as e:
        pass  # 降级到下一层

    # 第二层：重试一次（不带 stream）
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
        )
        content = response.choices[0].message.content
        for ch in clean_response(content):
            yield ch
            await asyncio.sleep(0.015)
        return
    except Exception as e:
        pass  # 降级到最后层

    # 第三层：硬编码兜底
    fallback = clean_response(fallback_response(last_user_text))
    for ch in fallback:
        yield ch
        await asyncio.sleep(0.015)


def chat_sync(history: List[Dict]) -> str:
    """同步聊天（含教学方案检测 + 降级）"""
    user_msgs = [m for m in history if m["role"] == "user"]
    last_user_text = user_msgs[-1]["content"] if user_msgs else ""
    use_teaching_prompt = is_teaching_request(last_user_text)

    system_prompt = TEACHING_PLAN_PROMPT if use_teaching_prompt else SYSTEM_PROMPT
    messages = build_messages(history, system_prompt)

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
        )
        return clean_response(response.choices[0].message.content)
    except Exception:
        return clean_response(fallback_response(last_user_text))


def extract_intent(history: List[Dict]) -> dict:
    """从对话历史中提取结构化教学意图"""
    prompt = """请基于以上对话历史，提取结构化的教学意图信息。
如果某些信息还不明确，请根据上下文合理推断。

返回严格的JSON格式（不要包含markdown代码块标记）：
{
  "subject": "学科名称",
  "topic": "课题名称",
  "grade": "年级/学段",
  "duration": "课时(分钟)",
  "objectives": ["教学目标列表"],
  "knowledge_points": ["知识点列表"],
  "key_points": ["重点列表"],
  "difficult_points": ["难点列表"],
  "teaching_methods": ["教学方法列表"],
  "activities": ["课堂活动列表"],
  "style": "professional/interesting/minimal",
  "student_profile": {
    "level": "学生整体水平（基础薄弱/中等/优秀）",
    "prior_knowledge": ["已掌握的前置知识"],
    "learning_style": "学习风格（视觉型/动手型/听觉型）",
    "special_needs": "特殊需求（无则留空字符串）"
  },
  "summary": "教学需求摘要"
}"""

    messages = history + [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=2048,
    )
    content = response.choices[0].message.content.strip()
    # 清理可能的 markdown 标记
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return json.loads(content.strip())


def generate_content(prompt: str, context: str = "", student_profile: dict = None) -> str:
    """通用内容生成，支持学情自适应"""
    system_content = "你是一个专业的教学内容生成助手，请根据要求生成高质量的教学内容。"
    
    # 注入学情信息到 system prompt
    if student_profile:
        level = student_profile.get("level", "")
        prior = student_profile.get("prior_knowledge", [])
        style = student_profile.get("learning_style", "")
        needs = student_profile.get("special_needs", "")
        
        profile_parts = []
        if level:
            profile_parts.append(f"学生水平：{level}")
        if prior:
            profile_parts.append(f"已有知识基础：{'、'.join(prior)}")
        if style:
            profile_parts.append(f"学习风格偏好：{style}")
        if needs:
            profile_parts.append(f"特殊需求：{needs}")
        
        if profile_parts:
            system_content += f"\n\n【学情信息】\n" + "\n".join(profile_parts)
            system_content += "\n\n请根据以上学情信息调整内容的难度、讲解方式和深度："
            system_content += "\n- 基础薄弱：多用生活化类比，放慢节奏，增加基础铺垫和回顾环节"
            system_content += "\n- 中等水平：在基础讲解之余加入适当延伸，注重理解和应用"
            system_content += "\n- 优秀水平：增加深度分析和拓展内容，引入高阶思维训练"
    
    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": f"参考资料：\n{context}\n\n生成要求：\n{prompt}"} if context else {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=8192,
    )
    return response.choices[0].message.content
