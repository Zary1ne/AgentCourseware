"""用户服务：注册、登录、用户数据管理（SQLite 数据库存储）

使用 SQLite 替代 JSON 文件 —— 只需将 backend/data/database.db 文件
随项目一起分发，即可在任意电脑上共享全部数据。
"""
import json
import os
import hashlib
import sqlite3
import uuid
from datetime import datetime
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
DB_FILE = os.path.join(DATA_DIR, "database.db")

# 管理员联系邮箱
ADMIN_EMAIL = "admin@teaching-agent.ai"

os.makedirs(DATA_DIR, exist_ok=True)


# ===== 数据库初始化 =====

def _get_conn() -> sqlite3.Connection:
    """获取数据库连接。check_same_thread=False 允许跨线程访问（FastAPI 异步环境）。"""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")       # 写前日志，提升并发性能
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """创建所有表（幂等：IF NOT EXISTS）"""
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          TEXT PRIMARY KEY,
            username    TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role        TEXT NOT NULL DEFAULT 'user',
            created_at  TEXT NOT NULL,
            banned      INTEGER NOT NULL DEFAULT 0,
            ban_reason  TEXT DEFAULT '',
            banned_at   TEXT,
            stats_json  TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS courseware (
            id              TEXT PRIMARY KEY,
            user_id         TEXT NOT NULL,
            author          TEXT NOT NULL,
            title           TEXT NOT NULL,
            description     TEXT DEFAULT '',
            category        TEXT DEFAULT '其他',
            tags_json       TEXT DEFAULT '[]',
            files_json      TEXT DEFAULT '{}',
            status          TEXT NOT NULL DEFAULT 'pending',
            created_at      TEXT NOT NULL,
            reviewed_at     TEXT,
            review_comment  TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS notifications (
            id          TEXT PRIMARY KEY,
            user_id     TEXT NOT NULL,
            type        TEXT NOT NULL,
            title       TEXT NOT NULL,
            content     TEXT NOT NULL,
            related_id  TEXT DEFAULT '',
            read        INTEGER NOT NULL DEFAULT 0,
            created_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id          TEXT PRIMARY KEY,
            user_id     TEXT NOT NULL,
            username    TEXT NOT NULL,
            type        TEXT NOT NULL,
            title       TEXT NOT NULL,
            content     TEXT NOT NULL,
            status      TEXT NOT NULL DEFAULT 'pending',
            admin_reply TEXT DEFAULT '',
            created_at  TEXT NOT NULL,
            reviewed_at TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        CREATE INDEX IF NOT EXISTS idx_courseware_status ON courseware(status);
        CREATE INDEX IF NOT EXISTS idx_courseware_user ON courseware(user_id);
        CREATE INDEX IF NOT EXISTS idx_notif_user ON notifications(user_id);
        CREATE INDEX IF NOT EXISTS idx_feedback_status ON feedback(status);
    """)
    conn.commit()
    conn.close()


# ===== 密码工具 =====

def _hash_password(password: str) -> str:
    """SHA256 + 固定盐值哈希"""
    return hashlib.sha256(f"ai_teach_salt_{password}".encode()).hexdigest()


# ===== 用户管理 =====

def create_user(username: str, password: str) -> dict:
    """注册新用户"""
    conn = _get_conn()
    user_id = uuid.uuid4().hex[:12]
    now = datetime.now().isoformat()
    try:
        conn.execute(
            "INSERT INTO users (id, username, password_hash, role, created_at) VALUES (?, ?, ?, 'user', ?)",
            (user_id, username, _hash_password(password), now)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError("用户名已存在")
    conn.close()
    return _get_user_safe(user_id)


def authenticate_user(username: str, password: str) -> dict:
    """验证登录。返回 {success, user?} 或 {success:False, reason, banned?, ...}"""
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username, _hash_password(password))
    ).fetchone()
    conn.close()

    if not row:
        return {"success": False, "reason": "invalid_credentials"}

    if row["banned"]:
        return {
            "success": False, "reason": "account_banned", "banned": True,
            "ban_reason": row["ban_reason"] or "您的账户已被管理员封禁",
            "banned_at": row["banned_at"] or "", "admin_email": ADMIN_EMAIL,
        }
    return {"success": True, "user": _row_to_user(row)}


def get_user(user_id: str) -> Optional[dict]:
    return _get_user_safe(user_id)


def get_user_by_username(username: str) -> Optional[dict]:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def _get_user_safe(user_id: str) -> Optional[dict]:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return _row_to_user(row) if row else None


def _row_to_user(row) -> dict:
    return {
        "id": row["id"], "username": row["username"],
        "role": row["role"], "created_at": row["created_at"],
        "stats": json.loads(row["stats_json"]) if row["stats_json"] else {},
    }


def update_user_stats(user_id: str, field: str, delta: int = 1):
    conn = _get_conn()
    row = conn.execute("SELECT stats_json FROM users WHERE id = ?", (user_id,)).fetchone()
    if row:
        stats = json.loads(row["stats_json"]) if row["stats_json"] else {}
        stats[field] = stats.get(field, 0) + delta
        conn.execute("UPDATE users SET stats_json = ? WHERE id = ?", (json.dumps(stats, ensure_ascii=False), user_id))
        conn.commit()
    conn.close()


def get_all_users() -> list:
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    result = []
    for row in rows:
        u = _row_to_user(row)
        u["banned"] = bool(row["banned"])
        u["ban_reason"] = row["ban_reason"] or ""
        u["banned_at"] = row["banned_at"]
        result.append(u)
    return result


def ban_user(target_user_id: str, reason: str, admin_id: str = "admin") -> dict:
    if not reason.strip():
        raise ValueError("封禁理由不能为空")
    conn = _get_conn()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (target_user_id,)).fetchone()
    if not row:
        conn.close(); raise ValueError("用户不存在")
    if row["role"] == "admin":
        conn.close(); raise ValueError("不能封禁管理员")
    now = datetime.now().isoformat()
    conn.execute("UPDATE users SET banned = 1, ban_reason = ?, banned_at = ? WHERE id = ?",
                 (reason.strip(), now, target_user_id))
    conn.commit()
    conn.close()
    _add_notification(target_user_id, "account_banned", "账户已被封禁",
        f"您的账户已被管理员封禁。\n封禁理由：{reason.strip()}\n如有疑问，请联系管理员：{ADMIN_EMAIL}")
    return _get_user_safe(target_user_id)


def unban_user(target_user_id: str) -> dict:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (target_user_id,)).fetchone()
    if not row:
        conn.close(); raise ValueError("用户不存在")
    conn.execute("UPDATE users SET banned = 0, ban_reason = '', banned_at = NULL WHERE id = ?", (target_user_id,))
    conn.commit()
    conn.close()
    _add_notification(target_user_id, "account_unbanned", "账户已解封", "您的账户已被管理员解封，现在可以正常使用了。")
    return _get_user_safe(target_user_id)


def update_user_info(user_id: str, data: dict) -> dict:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        conn.close(); raise ValueError("用户不存在")

    new_username = data.get("username", "").strip()
    if new_username and new_username != row["username"]:
        existing = conn.execute("SELECT id FROM users WHERE username = ? AND id != ?", (new_username, user_id)).fetchone()
        if existing:
            conn.close(); raise ValueError("用户名已存在")
        conn.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, user_id))

    new_password = data.get("password", "").strip()
    if new_password:
        if len(new_password) < 3:
            conn.close(); raise ValueError("密码至少需要3个字符")
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (_hash_password(new_password), user_id))

    conn.commit()
    conn.close()
    return _get_user_safe(user_id)


# ===== 课件社区管理 =====

def upload_courseware(user_id: str, data: dict, file_bytes: bytes = None, filename: str = "") -> dict:
    if not file_bytes and not data.get("files"):
        raise ValueError("必须上传课件文件")

    conn = _get_conn()
    cw_id = uuid.uuid4().hex[:12]
    now = datetime.now().isoformat()

    files_info = {}
    if file_bytes and filename:
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "community")
        os.makedirs(uploads_dir, exist_ok=True)
        safe_filename = f"{cw_id}_{filename}"
        with open(os.path.join(uploads_dir, safe_filename), "wb") as f:
            f.write(file_bytes)
        ext = os.path.splitext(filename)[1].lower()
        type_map = {".pptx": "PPT课件", ".ppt": "PPT课件", ".docx": "Word教案", ".doc": "Word教案", ".html": "互动课程", ".pdf": "其他"}
        auto_category = type_map.get(ext, "其他")
        files_info = {"filename": filename, "saved_name": safe_filename, "size": len(file_bytes), "type": ext}
        if data.get("category") == "其他" and auto_category != "其他":
            data["category"] = auto_category

    user = get_user(user_id)
    author = user.get("username", "匿名用户") if user else "匿名用户"

    tags = data.get("tags", [])
    conn.execute(
        "INSERT INTO courseware (id, user_id, author, title, description, category, tags_json, files_json, status, created_at) VALUES (?,?,?,?,?,?,?,?, 'pending', ?)",
        (cw_id, user_id, author, data.get("title", "未命名课件"), data.get("description", ""),
         data.get("category", "其他"), json.dumps(tags, ensure_ascii=False),
         json.dumps(files_info, ensure_ascii=False), now)
    )
    conn.commit()
    conn.close()

    update_user_stats(user_id, "uploads")
    _add_notification("admin", "new_courseware", "新课件待审核",
        f"用户「{author}」提交了课件「{data.get('title', '未命名课件')}」（{files_info.get('filename', '未知文件')}），请前往审核。", cw_id)
    return _get_courseware(cw_id)


def _get_courseware(cw_id: str) -> Optional[dict]:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM courseware WHERE id = ?", (cw_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row["id"], "user_id": row["user_id"], "author": row["author"],
        "title": row["title"], "description": row["description"], "category": row["category"],
        "tags": json.loads(row["tags_json"]) if row["tags_json"] else [],
        "files": json.loads(row["files_json"]) if row["files_json"] else {},
        "status": row["status"], "created_at": row["created_at"],
        "reviewed_at": row["reviewed_at"], "review_comment": row["review_comment"] or "",
    }


def list_approved_courseware(category: str = None) -> list:
    conn = _get_conn()
    if category:
        rows = conn.execute("SELECT * FROM courseware WHERE status = 'approved' AND category = ? ORDER BY created_at DESC", (category,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM courseware WHERE status = 'approved' ORDER BY created_at DESC").fetchall()
    conn.close()
    return [_row_to_courseware(r) for r in rows]


def list_pending_courseware(status_filter: str = "pending") -> list:
    """获取课件列表（管理员用）。status_filter='pending' 仅待审核，'all' 全部"""
    conn = _get_conn()
    if status_filter == "all":
        rows = conn.execute("SELECT * FROM courseware ORDER BY created_at DESC").fetchall()
    else:
        rows = conn.execute("SELECT * FROM courseware WHERE status = ? ORDER BY created_at DESC", (status_filter,)).fetchall()
    conn.close()
    return [_row_to_courseware(r) for r in rows]


def _row_to_courseware(row) -> dict:
    return {
        "id": row["id"], "user_id": row["user_id"], "author": row["author"],
        "title": row["title"], "description": row["description"], "category": row["category"],
        "tags": json.loads(row["tags_json"]) if row["tags_json"] else [],
        "files": json.loads(row["files_json"]) if row["files_json"] else {},
        "status": row["status"], "created_at": row["created_at"],
        "reviewed_at": row["reviewed_at"], "review_comment": row["review_comment"] or "",
    }


def review_courseware(cw_id: str, approved: bool, comment: str = "") -> dict:
    if not approved and not comment.strip():
        raise ValueError("拒绝课件时必须填写拒绝理由")

    conn = _get_conn()
    row = conn.execute("SELECT * FROM courseware WHERE id = ?", (cw_id,)).fetchone()
    if not row:
        conn.close(); raise ValueError("课件不存在")

    status = "approved" if approved else "rejected"
    now = datetime.now().isoformat()
    conn.execute("UPDATE courseware SET status = ?, reviewed_at = ?, review_comment = ? WHERE id = ?",
                 (status, now, comment.strip(), cw_id))
    conn.commit()
    conn.close()

    cw = _get_courseware(cw_id)
    if approved:
        _add_notification(cw["user_id"], "review_result", "课件审核通过",
            f"您提交的课件「{cw['title']}」已审核通过，现已上架开源社区！", cw_id)
    else:
        _add_notification(cw["user_id"], "review_result", "课件审核未通过",
            f"您提交的课件「{cw['title']}」审核未通过。\n拒绝理由：{comment.strip()}\n请修改后重新上传。", cw_id)
    _clear_notification_by_related("new_courseware", cw_id)
    return cw


def get_user_courseware(user_id: str) -> list:
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM courseware WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
    conn.close()
    return [_row_to_courseware(r) for r in rows]


# ===== 通知系统 =====

def _add_notification(user_id: str, msg_type: str, title: str, content: str, related_id: str = ""):
    conn = _get_conn()
    nid = uuid.uuid4().hex[:8]
    conn.execute(
        "INSERT INTO notifications (id, user_id, type, title, content, related_id, read, created_at) VALUES (?,?,?,?,?,?,0,?)",
        (nid, user_id, msg_type, title, content, related_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def _clear_notification_by_related(msg_type: str, related_id: str):
    conn = _get_conn()
    conn.execute("DELETE FROM notifications WHERE type = ? AND related_id = ?", (msg_type, related_id))
    conn.commit()
    conn.close()


def get_user_notifications(user_id: str, unread_only: bool = False) -> list:
    conn = _get_conn()
    if unread_only:
        rows = conn.execute(
            "SELECT * FROM notifications WHERE user_id = ? AND read = 0 ORDER BY created_at DESC", (user_id,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_notification_read(nid: str):
    conn = _get_conn()
    conn.execute("UPDATE notifications SET read = 1 WHERE id = ?", (nid,))
    conn.commit()
    conn.close()


def mark_all_read(user_id: str):
    conn = _get_conn()
    conn.execute("UPDATE notifications SET read = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_unread_count(user_id: str) -> int:
    conn = _get_conn()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM notifications WHERE user_id = ? AND read = 0", (user_id,)).fetchone()
    conn.close()
    return row["cnt"] if row else 0


# ===== 管理员仪表盘统计 =====

def get_admin_stats() -> dict:
    conn = _get_conn()
    total_users = conn.execute("SELECT COUNT(*) as cnt FROM users WHERE role != 'admin'").fetchone()["cnt"]
    banned_users = conn.execute("SELECT COUNT(*) as cnt FROM users WHERE banned = 1").fetchone()["cnt"]
    total_cw = conn.execute("SELECT COUNT(*) as cnt FROM courseware").fetchone()["cnt"]
    approved_cw = conn.execute("SELECT COUNT(*) as cnt FROM courseware WHERE status = 'approved'").fetchone()["cnt"]
    pending_cw = conn.execute("SELECT COUNT(*) as cnt FROM courseware WHERE status = 'pending'").fetchone()["cnt"]
    rejected_cw = conn.execute("SELECT COUNT(*) as cnt FROM courseware WHERE status = 'rejected'").fetchone()["cnt"]
    pending_fb = conn.execute("SELECT COUNT(*) as cnt FROM feedback WHERE status = 'pending'").fetchone()["cnt"]
    total_fb = conn.execute("SELECT COUNT(*) as cnt FROM feedback").fetchone()["cnt"]

    # 生成统计
    total_generations = 0
    stats_path = os.path.join(DATA_DIR, "..", "stats.json")
    if os.path.exists(stats_path):
        try:
            with open(stats_path, "r", encoding="utf-8") as f:
                total_generations = len(json.load(f).get("generations", []))
        except Exception:
            pass

    conn.close()
    return {
        "totalUsers": total_users, "bannedUsers": banned_users,
        "totalGenerations": total_generations, "totalCourseware": total_cw,
        "approvedCourseware": approved_cw, "pendingCourseware": pending_cw,
        "rejectedCourseware": rejected_cw,
        "pendingFeedback": pending_fb, "totalFeedback": total_fb,
    }


# ===== 反馈系统 =====

def submit_feedback(user_id: str, fb_type: str, title: str, content: str) -> dict:
    if not title.strip():
        raise ValueError("反馈标题不能为空")
    if not content.strip():
        raise ValueError("反馈内容不能为空")

    conn = _get_conn()
    fb_id = uuid.uuid4().hex[:12]
    now = datetime.now().isoformat()
    user = get_user(user_id)
    username = user.get("username", "匿名") if user else "匿名"
    conn.execute(
        "INSERT INTO feedback (id, user_id, username, type, title, content, status, created_at) VALUES (?,?,?,?,?,?,'pending',?)",
        (fb_id, user_id, username, fb_type, title.strip(), content.strip(), now))
    conn.commit()
    conn.close()

    type_labels = {"bug": "Bug反馈", "feature": "功能建议", "improvement": "改进意见", "other": "其他反馈"}
    _add_notification("admin", "new_feedback",
        f"新反馈：{type_labels.get(fb_type, fb_type)}",
        f"用户「{username}」提交了{type_labels.get(fb_type, '')}：{title.strip()}", fb_id)
    return {"id": fb_id, "user_id": user_id, "username": username, "type": fb_type,
            "title": title.strip(), "content": content.strip(), "status": "pending",
            "admin_reply": "", "created_at": now, "reviewed_at": None}


def list_feedback(status: str = None) -> list:
    conn = _get_conn()
    if status:
        rows = conn.execute("SELECT * FROM feedback WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM feedback ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def review_feedback(fb_id: str, status: str, reply: str = "") -> dict:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM feedback WHERE id = ?", (fb_id,)).fetchone()
    if not row:
        conn.close(); raise ValueError("反馈不存在")
    now = datetime.now().isoformat()
    conn.execute("UPDATE feedback SET status = ?, admin_reply = ?, reviewed_at = ? WHERE id = ?",
                 (status, reply.strip(), now, fb_id))
    conn.commit()
    conn.close()

    fb = dict(row)
    fb["status"] = status
    fb["admin_reply"] = reply.strip()
    fb["reviewed_at"] = now

    labels = {"reviewed": "已查看", "closed": "已处理"}
    msg = f"您提交的反馈「{fb['title']}」已被管理员{labels.get(status, status)}。"
    if reply.strip():
        msg += f"\n回复：{reply.strip()}"
    _add_notification(fb["user_id"], "feedback_reviewed", "反馈已处理", msg, fb_id)
    _clear_notification_by_related("new_feedback", fb_id)
    return fb


# ===== 初始化管理员账号 =====

def init_admin():
    conn = _get_conn()
    row = conn.execute("SELECT id FROM users WHERE role = 'admin'").fetchone()
    if not row:
        conn.execute(
            "INSERT INTO users (id, username, password_hash, role, created_at) VALUES (?, ?, ?, 'admin', ?)",
            ("admin", "admin", _hash_password("admin"), datetime.now().isoformat()))
        conn.commit()
    conn.close()


# 应用启动时初始化
init_db()
init_admin()
