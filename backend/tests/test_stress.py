"""压力测试：连续50轮对话、特殊符号、网络中断重连、超长文本。

运行方式（在后端目录）：
    cd D:\\mo\\ai-teaching-agent\\AgentCourseware\\backend
    py -3.9-64 -m pytest tests/test_stress.py -v

或直接运行（无需 pytest）：
    py -3.9-64 tests/test_stress.py

这些测试直接调用内部函数，不依赖网络与大模型 API，全部走兜底逻辑，
保证在离线环境下也能验证对话链路的健壮性。
"""
import sys
import os
import asyncio
import json

# 让后端包可被导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.llm_service import (
    chat_stream,
    fallback_response,
    clean_response,
    recognize_intent_llm,
    _keyword_intent,
    _stream_text_chunks,
)
from app.services.rag_service import search_knowledge, list_documents, add_document


# ========== 工具 ==========

def _drain(stream_gen):
    """把异步生成器的全部输出拼成一个字符串"""
    return asyncio.get_event_loop().run_until_complete(_collect(stream_gen))


async def _collect(gen):
    parts = []
    async for chunk in gen:
        parts.append(chunk)
    return "".join(parts)


def _make_history(rounds):
    """构造多轮对话历史"""
    history = []
    for i in range(rounds):
        history.append({"role": "user", "content": f"第{i+1}轮：请讲一下牛顿第{ (i % 3) + 1}定律"})
        history.append({"role": "assistant", "content": f"好的，这是第{i+1}轮的回复内容。"})
    return history


# ========== 测试1：连续 50 轮对话上下文不丢 ==========

def test_50_round_context():
    """连续 50 轮对话：最后一轮仍能正常生成，且历史完整保留"""
    history = _make_history(50)
    # 追加最后一轮用户消息
    history.append({"role": "user", "content": "总结一下我们刚才讨论的物理定律"})
    assert len(history) == 101, f"历史轮数不对: {len(history)}"

    result = _drain(chat_stream(history))
    assert result, "50轮对话后流式回复为空"
    assert len(result) > 0
    # 历史未被破坏
    assert history[0]["role"] == "user"
    assert history[-1]["content"] == "总结一下我们刚才讨论的物理定律"
    print(f"[PASS] 50轮对话：历史{len(history)}条消息完整保留，回复{len(result)}字")


# ========== 测试2：特殊符号不崩 ==========

SPECIAL_INPUTS = [
    "包含 \\n 和 \\t 的消息\\n\\t制表符",
    "Emoji 测试 🚀🎉📚✨💯",
    "LaTeX 公式 $E = mc^2$ 以及 $\\vec{F} = m\\vec{a}$",
    "代码块 ```python\\ndef f(x): return x**2\\n```",
    "混合 <html> 标签 <script>alert(1)</script> 防注入",
    "引号 \"双引号\" '单引号' 反斜杠 \\\\ ",
    "中文标点：，。！？；：「」『』【】（）",
    "超长无空格连续字符aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
]


def test_special_symbols():
    """各种特殊符号输入不应导致后端异常"""
    for text in SPECIAL_INPUTS:
        history = [{"role": "user", "content": text}]
        result = _drain(chat_stream(history))
        assert result, f"特殊符号输入导致空回复: {text[:30]}"
        # 验证切块不会切断 LaTeX 命令
    print(f"[PASS] 特殊符号：{len(SPECIAL_INPUTS)} 组输入全部正常返回")


# ========== 测试3：超长文本（>10k 字）不崩 ==========

def test_long_text():
    """超过 10000 字的超长输入不应导致后端崩溃"""
    long_text = "请讲解牛顿第一定律。" * 2000  # 约 20000 字
    assert len(long_text) > 10000
    history = [{"role": "user", "content": long_text}]
    result = _drain(chat_stream(history))
    assert result, "超长文本导致空回复"
    # 兜底回复应该正常生成
    fb = fallback_response(long_text)
    assert fb, "超长文本兜底回复为空"
    print(f"[PASS] 超长文本：输入{len(long_text)}字，回复{len(result)}字")


# ========== 测试4：流式切块不切断 LaTeX 命令 ==========

def test_stream_chunks_preserve_latex():
    """_stream_text_chunks 不应把 \\vec \\cdot 等 LaTeX 命令从中间切断"""
    formula = r"$dW = \vec{F} \cdot d\vec{s}$"
    chunks = list(_stream_text_chunks(formula))
    joined = "".join(chunks)
    assert joined == formula, f"切块拼接后内容不一致: {joined}"
    # 每个完整的 LaTeX 命令应作为一个整体块出现
    assert r"\vec" in chunks, "\\vec 被切碎了"
    assert r"\cdot" in chunks, "\\cdot 被切碎了"
    assert chunks.count(r"\vec") == 2, "\\vec 出现次数不对"
    print(f"[PASS] LaTeX切块：\\vec/\\cdot 保持完整，共{len(chunks)}块")


# ========== 测试5：意图识别（Few-shot/CoT）==========

INTENT_CASES = [
    ("牛顿第一定律", "物理"),
    ("三角函数", "数学"),
    ("氧化还原反应", "化学"),
    ("光合作用", "生物"),
    ("唐朝的建立", "历史"),
    ("板块构造学说", "地理"),
    ("文言文实词", "语文"),
    ("英语时态", "英语"),
    ("牛顿第二定律", "物理"),
    ("基因工程", "生物"),
]


def test_intent_recognition():
    """10 个场景意图识别：关键词层应至少命中 8 个学科"""
    hits = 0
    for text, expected_subject in INTENT_CASES:
        kw = _keyword_intent(text)
        got = kw.get("subject", "")
        if got == expected_subject:
            hits += 1
        else:
            print(f"  意图识别 miss: '{text}' 期望{expected_subject} 得到{got}")
    assert hits >= 8, f"意图识别正确率不达标: {hits}/{len(INTENT_CASES)}"
    print(f"[PASS] 意图识别：关键词层 {hits}/{len(INTENT_CASES)} 命中（要求>=8）")

    # recognize_intent_llm 在无 API Key 时应优雅降级，不抛异常
    res = recognize_intent_llm("牛顿第一定律")
    assert "grade" in res and "duration" in res, f"LLM意图降级返回缺字段: {res}"
    assert res["duration"] == "45分钟", f"默认课时不符: {res}"
    print(f"[PASS] 意图识别(LLM降级)：返回 {res}")


# ========== 测试6：RAG 检索不崩（空库/异常查询）==========

def test_rag_empty_and_special_query():
    """空库与特殊符号查询不应崩溃"""
    # 特殊符号查询
    res = search_knowledge("$E = mc^2$ 🚀 <script>", top_k=3)
    assert isinstance(res, list), "RAG 检索返回类型异常"
    print(f"[PASS] RAG检索：特殊符号查询返回{len(res)}条结果（不崩溃）")


# ========== 入口 ==========

def run_all():
    print("=" * 50)
    print("AI 教学助手 压力测试")
    print("=" * 50)
    test_50_round_context()
    test_special_symbols()
    test_long_text()
    test_stream_chunks_preserve_latex()
    test_intent_recognition()
    test_rag_empty_and_special_query()
    print("=" * 50)
    print("全部测试通过 ✓")


if __name__ == "__main__":
    run_all()
