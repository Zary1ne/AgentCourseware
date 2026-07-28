import os
import json
from datetime import datetime, timedelta
from fastapi import APIRouter
from app.config import OUTPUT_DIR
from app.services.rag_service import list_documents

router = APIRouter(prefix="/api/admin", tags=["admin"])

STATS_FILE = os.path.join(OUTPUT_DIR, "..", "stats.json")


def _load_stats() -> dict:
    """加载统计数据"""
    if not os.path.exists(STATS_FILE):
        return {
            "conversations": [],
            "generations": [],
            "activeUsers": 1,
        }
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"conversations": [], "generations": [], "activeUsers": 1}


def _save_stats(stats: dict):
    """保存统计数据"""
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def record_conversation():
    """记录一次对话"""
    stats = _load_stats()
    stats["conversations"].append(datetime.now().isoformat())
    # 只保留近 30 天
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    stats["conversations"] = [t for t in stats["conversations"] if t > cutoff]
    _save_stats(stats)


def record_generation():
    """记录一次课件生成"""
    stats = _load_stats()
    stats["generations"].append(datetime.now().isoformat())
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    stats["generations"] = [t for t in stats["generations"] if t > cutoff]
    _save_stats(stats)


@router.get("/stats")
async def get_stats():
    """获取管理后台统计数据"""
    stats = _load_stats()
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")

    # 今日统计
    today_conv = sum(1 for t in stats["conversations"] if t.startswith(today_str))
    yesterday_conv = sum(1 for t in stats["conversations"] if t.startswith(yesterday_str))
    today_gen = sum(1 for t in stats["generations"] if t.startswith(today_str))

    # 计算较昨日变化
    vs_yesterday = 0
    if yesterday_conv > 0:
        vs_yesterday = round((today_conv - yesterday_conv) / yesterday_conv * 100)
    elif today_conv > 0:
        vs_yesterday = 100

    # 知识库统计
    docs = list_documents()
    total_chunks = sum(d.get("chunk_count", 0) for d in docs)

    # 最近活动
    activities = []
    all_events = []
    for t in stats.get("conversations", [])[-10:]:
        all_events.append(("对话交互", t))
    for t in stats.get("generations", [])[-10:]:
        all_events.append(("课件生成", t))
    all_events.sort(key=lambda x: x[1], reverse=True)

    for event_type, t in all_events[:10]:
        try:
            dt = datetime.fromisoformat(t)
            time_str = dt.strftime("%m-%d %H:%M")
        except Exception:
            time_str = t[:16]
        activities.append({
            "text": event_type,
            "time": time_str,
        })

    return {
        "todayConversations": today_conv,
        "vsYesterday": max(vs_yesterday, 0),
        "totalDocuments": len(docs),
        "totalChunks": total_chunks,
        "totalGenerations": len(stats.get("generations", [])),
        "todayGenerations": today_gen,
        "activeUsers": stats.get("activeUsers", 1),
        "recentActivities": activities,
    }
