from openai import OpenAI, AsyncOpenAI
from app.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from typing import List, Dict, AsyncGenerator
import json
import asyncio

# 同步客户端（用于 chat_sync、extract_intent 等同步调用）
sync_client = OpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL,
)

# 异步客户端（用于 chat_stream 流式传输，不阻塞事件循环）
client = AsyncOpenAI(
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
- 每次提问控制在1-2个关键问题，不要一次性问太多。

交互输出格式（非提问阶段）：
- 当你向教师提问时，必须使用以下结构化标记格式，让教师可以直接点击或输入：

1. **选择题**（提供可选选项，教师点击即可）：
   格式：请选择XX？{{CHOICE:选项A|选项B|选项C}}
   示例：请选择年级？{{CHOICE:高一|高二|高三}}

2. **数字输入题**（需要教师输入数字的场景）：
   格式：请输入XX？{{INPUT:请输入数字|默认值}}
   示例：请输入课时长度（分钟）？{{INPUT:请输入分钟数|45}}

- 除了以上结构化标记外，其他内容用自然语言描述，不要使用任何特殊标记或JSON。
- 每次提问只使用1-2个结构化标记，其余用自然语言引导。
- 标记的选项要精炼准确，不要超过4个选项。

最终意图输出：
- 当需求确认完毕后，在回复末尾添加 [INTENT_READY] 标记
- 然后输出结构化的教学意图JSON（仅在最终确认时输出，平时不要输出JSON）：
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


# ===== 专用 Prompt（来自 AITEACH(对话) app.py 原型） =====
ANALYSIS_PROMPT = """你是资深教学解析专家。当用户请求教学解析时，请按以下结构回答：

1. 【教学定位】这个知识点在课程体系中的位置和作用
2. 【重点分析】必须掌握的核心内容和关键概念
3. 【难点突破】学生容易卡住的地方，以及突破方法
4. 【教学建议】教学顺序、教学方法建议
5. 【常见误区】学生常犯的错误和纠正方法
6. 【拓展延伸】相关知识点关联和拓展方向

要求：
- 结合具体学科特点
- 语言通俗易懂
- 禁止使用 * 字符做格式标记"""

SUGGESTIONS_PROMPT = """你是个性化学习顾问。当用户请求学习建议时，请按以下结构回答：

1. 【学习诊断】分析学生的学习现状和可能的薄弱点
2. 【学习目标】制定明确、可衡量的学习目标
3. 【学习计划】分阶段的学习计划（周计划/月计划）
4. 【学习方法】适合该学科的高效学习方法和技巧
5. 【练习推荐】针对性的练习题和学习资源
6. 【进度追踪】如何检验学习效果、调整计划

要求：
- 方案具体可行
- 方法科学有效
- 禁止使用 * 字符做格式标记"""

EXPLAIN_PROMPT = """你是知识讲解专家。当用户请求知识讲解时，请按以下结构回答：

1. 【概念定义】用最简洁的语言定义这个知识点
2. 【通俗解释】用生活中的例子或比喻来解释
3. 【原理分析】深入讲解背后的原理和逻辑
4. 【示例演示】给出典型的例题或应用场景
5. 【注意事项】使用时的注意点和常见陷阱
6. 【举一反三】相关知识点的关联和延伸

要求：
- 由浅入深，循序渐进
- 多用直观的例子
- 禁止使用 * 字符做格式标记"""

ENGLISH_PROMPT = """你是高中英语专家，专注于高一英语教学。请根据高一英语教学大纲，提供以下内容：

1. 【词汇学习】重点词汇、短语辨析、用法举例
2. 【语法讲解】高一核心语法点（时态、从句、非谓语动词等）
3. 【阅读理解】阅读技巧、常见题型分析
4. 【写作指导】写作框架、常用句型、范文赏析
5. 【听力训练】听力技巧、常见场景词汇
6. 【口语表达】日常交际用语、情景对话

要求：
- 内容贴合高一水平
- 例句实用地道
- 中英双语解释
- 禁止使用 * 字符做格式标记"""


# ===== Prompt 路由表（来自 AITEACH(对话) app.py PROMPT_MAP 原型） =====
PROMPT_MAP = {
    "general": SYSTEM_PROMPT,
    "teaching": TEACHING_PLAN_PROMPT,
    "analysis": ANALYSIS_PROMPT,
    "suggestions": SUGGESTIONS_PROMPT,
    "explain": EXPLAIN_PROMPT,
    "english": ENGLISH_PROMPT,
}


def select_system_prompt(history: List[Dict], prompt_type: str = "") -> str:
    """根据 prompt_type 或关键词选择系统提示词。

    优先级：显式 prompt_type > 关键词检测（is_teaching_request）> 默认 SYSTEM_PROMPT。
    """
    if prompt_type and prompt_type in PROMPT_MAP:
        return PROMPT_MAP[prompt_type]
    user_msgs = [m for m in history if m["role"] == "user"]
    last_user_text = user_msgs[-1]["content"] if user_msgs else ""
    if is_teaching_request(last_user_text):
        return TEACHING_PLAN_PROMPT
    return SYSTEM_PROMPT


# ===== 工具函数（来自 AITEACH(对话) 原型） =====
def clean_response(text: str) -> str:
    """保留原始回复内容

    前端已改为 Markdown 渲染（marked + KaTeX + highlight.js），
    星号等格式标记是合法语法，不再移除。
    """
    return text


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
    # 物理/公式类问题：输出 LaTeX 公式 + 示例代码，用于验证公式渲染与代码高亮
    if any(g in t for g in ["物理", "公式", "牛顿", "力学", "F=ma", "f=ma", "加速度"]):
        return ("好的，我们以**牛顿第二定律**为例进行讲解：\n\n"
                "## 核心公式\n\n物体所受合外力与加速度成正比：$F = ma$\n\n"
                "动能定理的微分形式：$dW = \\vec{F} \\cdot d\\vec{s}$\n\n"
                "## Python 演示代码\n\n"
                "```python\n"
                "def compute_force(mass, accel):\n"
                "    \"\"\"根据牛顿第二定律 F = ma 计算合外力\"\"\"\n"
                "    return mass * accel\n"
                "\n"
                "print(compute_force(2.0, 3.5))  # 输出: 7.0\n"
                "```\n\n"
                "**教学要点**：\n"
                "1. 强调 $F$ 是*合外力*，不是单个力\n"
                "2. 单位统一使用国际单位制（N、kg、m/s²）\n"
                "3. 通过实验让学生直观感受 $a \\propto F$ 的关系\n\n"
                "[当前 AI 服务暂时不可用，以上为示例教学回复]")
    # 编程类问题：输出示例代码块
    if any(g in t for g in ["代码", "python", "编程", "程序", "算法"]):
        return ("好的，这里给出一个**Python 示例**：\n\n"
                "```python\n"
                "def fibonacci(n):\n"
                "    \"\"\"生成斐波那契数列前 n 项\"\"\"\n"
                "    seq = [0, 1]\n"
                "    while len(seq) < n:\n"
                "        seq.append(seq[-1] + seq[-2])\n"
                "    return seq[:n]\n"
                "\n"
                "print(fibonacci(10))  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]\n"
                "```\n\n"
                "**说明**：时间复杂度为 $O(n)$，空间复杂度为 $O(n)$。\n\n"
                "[当前 AI 服务暂时不可用，以上为示例教学回复]")
    return ("这是一个很好的教学主题。建议从以下方面入手：\n\n"
            "1. **明确教学目标**：让学生知道学完能做什么\n"
            "2. **梳理重难点**：围绕核心知识点设计突破策略\n"
            "3. **课堂活动**：准备实验或互动，帮助理解抽象概念\n"
            "4. **分层练习**：设计不同难度的题目检验学习效果\n\n"
            "[当前 AI 服务暂时不可用，以上为基础建议]")


def build_messages(history: List[Dict], system_prompt: str = SYSTEM_PROMPT) -> List[Dict]:
    """构建消息列表"""
    return [{"role": "system", "content": system_prompt}] + history


def _stream_text_chunks(text: str):
    """把文本切成流式块，但不要把 LaTeX 命令（\\command）从中间断开"""
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "\\" and i + 1 < n and text[i + 1].isalpha():
            j = i + 1
            while j < n and text[j].isalpha():
                j += 1
            yield text[i:j]
            i = j
        else:
            yield text[i]
            i += 1


async def chat_stream(history: List[Dict], prompt_type: str = "") -> AsyncGenerator[str, None]:
    """流式聊天（含 prompt_type 路由 + 三层降级）"""
    # 检测最后一条用户消息是否为教学方案请求
    user_msgs = [m for m in history if m["role"] == "user"]
    last_user_text = user_msgs[-1]["content"] if user_msgs else ""

    system_prompt = select_system_prompt(history, prompt_type)
    messages = build_messages(history, system_prompt)

    # 第一层：异步流式调用 OpenAI
    try:
        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            stream=True,
            temperature=0.7,
            max_tokens=4096,
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield clean_response(chunk.choices[0].delta.content)
        return
    except Exception as e:
        pass  # 降级到下一层

    # 第二层：异步重试（不带 stream，分块输出模拟流式）
    try:
        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
        )
        content = response.choices[0].message.content
        cleaned = clean_response(content)
        for chunk in _stream_text_chunks(cleaned):
            yield chunk
            await asyncio.sleep(0.01)
        return
    except Exception as e:
        pass  # 降级到下一层

    # 第三层：硬编码兜底，分块输出
    fallback = clean_response(fallback_response(last_user_text))
    for chunk in _stream_text_chunks(fallback):
        yield chunk
        await asyncio.sleep(0.01)


def chat_sync(history: List[Dict], prompt_type: str = "") -> str:
    """同步聊天（含 prompt_type 路由 + 降级）"""
    user_msgs = [m for m in history if m["role"] == "user"]
    last_user_text = user_msgs[-1]["content"] if user_msgs else ""

    system_prompt = select_system_prompt(history, prompt_type)
    messages = build_messages(history, system_prompt)

    try:
        response = sync_client.chat.completions.create(
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
    response = sync_client.chat.completions.create(
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
    response = sync_client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=8192,
    )
    return response.choices[0].message.content
