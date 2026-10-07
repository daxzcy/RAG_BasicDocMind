#!/usr/bin/env python3
"""
GitHub Agent 开发周报 — 每周汇总热门 Agent/MCP/Skills 项目
自动抓取 GitHub Trending，汇总后发到 QQ 邮箱
"""

import os
import re
import smtplib
import json
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from html import escape
from urllib.request import urlopen, Request
from urllib.parse import quote, urlencode

# ==================== 配置 ====================
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 587
# 邮箱地址从环境变量读取，避免把个人信息写进仓库
SENDER = os.environ.get("QQ_SMTP_SENDER", "")
RECEIVER = os.environ.get("QQ_SMTP_RECEIVER", SENDER)
AUTH_CODE = os.environ.get("QQ_SMTP_AUTH_CODE")

if not AUTH_CODE:
    raise ValueError("缺少 QQ_SMTP_AUTH_CODE 环境变量")
if not SENDER:
    raise ValueError("缺少 QQ_SMTP_SENDER 环境变量")

# 搜索关键词（覆盖 Agent / MCP / Skills / Python / 总榜）
SEARCH_QUERIES = [
    # ===== Agent 框架 =====
    "topic:ai-agent",
    "topic:agent-framework sort:stars",
    "agent framework llm",
    # ===== MCP =====
    "topic:mcp-server sort:stars",
    "mcp server model-context-protocol",
    "mcp tool ai",
    # ===== Skills =====
    "claude code skills sort:stars",
    "agent skills ai coding",
    # ===== Agent 热门综合 =====
    "ai agent sort:stars",
    "llm agent tool",
    # ===== Python & 后端框架 =====
    "topic:python sort:stars",
    "topic:python created:>2024-01-01 sort:stars",
    "python library stars:>1000",
    "topic:fastapi sort:stars",
    "topic:django sort:stars",
    "topic:flask sort:stars",
    "backend framework ORM python stars:>500",
    # ===== GitHub 总榜热门（新增） =====
    "stars:>10000 pushed:>2026-06-01",
    "topic:hacktoberfest sort:stars",
    "topic:open-source sort:stars",
    "stars:>5000 pushed:>2026-07-01",
    "topic:github-trending sort:stars",
]

# 本周一零点（UTC）
def get_this_monday():
    today = datetime.now(timezone.utc)
    return today - timedelta(days=today.weekday(), hours=today.hour, minutes=today.minute,
                            seconds=today.second, microseconds=today.microsecond)


# ==================== GitHub API ====================
def search_github(query: str, sort: str = "stars", order: str = "desc", per_page: int = 8):
    """搜索 GitHub 仓库"""
    q = query.strip()
    # 如果 query 不带额外排序，默认按 stars 排序
    if "sort:" not in q and "stars:>" not in q:
        full_query = f"{q} sort:stars"
    else:
        full_query = q

    url = f"https://api.github.com/search/repositories?q={quote(full_query)}&sort={sort}&order={order}&per_page={per_page}"
    req = Request(url, headers={
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "agent-weekly-digest",
    })
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  [!] API 请求失败: {e}")
        return {"items": []}


def fetch_trending_topic(topic: str, limit: int = 8):
    """按 topic 获取热门仓库"""
    return search_github(f"topic:{topic} sort:stars", per_page=limit)


# ==================== 翻译 ====================
_translate_cache = {}

def translate_text(text: str) -> str:
    """Google 免费翻译 API，英→中，带缓存"""
    if not text or text == "无描述":
        return text
    if text in _translate_cache:
        return _translate_cache[text]
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=zh-CN&dt=t&q=" + quote(text)
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        # 提取翻译结果
        result = "".join(part[0] for part in data[0] if part[0])
        _translate_cache[text] = result.strip() if result.strip() else text
        return _translate_cache[text]
    except Exception:
        _translate_cache[text] = text  # 翻译失败用原文
        return text


# ==================== 构建邮件 ====================
def categorize_repo(repo: dict) -> str:
    """给仓库打标签：Agent / MCP / Skills / Python / Hot / Other"""
    topics = [t.lower() for t in repo.get("topics", [])]
    desc = (repo.get("description") or "").lower()
    name = repo["full_name"].lower()

    # Agent 优先（命中 return）
    if "agent" in topics or "ai-agent" in topics or "agent-framework" in topics:
        return "Agent"
    if any(kw in desc for kw in ["agent", "autonomous", "ai agent"]):
        return "Agent"
    # MCP
    if "mcp" in topics or "mcp-server" in topics or "mcp" in name:
        return "MCP"
    if any(kw in desc for kw in ["mcp", "model context protocol"]):
        return "MCP"
    # Skills
    if "skill" in topics or "skills" in topics or "claude-code" in topics:
        return "Skills"
    if any(kw in desc for kw in ["skill", "claude code"]):
        return "Skills"
    # Python
    lang = repo.get("language") or ""
    if lang.lower() == "python" and repo["stargazers_count"] > 1000:
        if any(kw in desc for kw in ["python", "fastapi", "django", "flask", "pytest",
                                      "asyncio", "pydantic", "uvicorn", "sqlalchemy"]):
            return "Python"
        if "python" in topics or "fastapi" in topics or "django" in topics:
            return "Python"
        # 高星纯 Python 项目也归入 Python 类
        if repo["stargazers_count"] > 5000:
            return "Python"
    # 其他（总榜热门）
    return "Hot"


def build_html() -> str:
    """生成 HTML 邮件内容"""
    this_monday = get_this_monday()
    week_str = this_monday.strftime("%Y-%m-%d")

    # 分批搜索
    all_repos = {}
    seen_ids = set()

    for q in SEARCH_QUERIES:
        print(f"[*] 搜索: {q}")
        data = search_github(q)
        for r in data.get("items", []):
            rid = r["id"]
            if rid not in seen_ids:
                seen_ids.add(rid)
                r["_cat"] = categorize_repo(r)
                all_repos[rid] = r

    # 按 stars 排序
    sorted_repos = sorted(all_repos.values(), key=lambda r: r["stargazers_count"], reverse=True)

    # 分类
    categories = {"Agent": [], "MCP": [], "Skills": [], "Python": [], "Hot": []}
    for r in sorted_repos:
        cat = r["_cat"]
        if cat in categories:
            categories[cat].append(r)
        else:
            categories["Hot"].append(r)

    print(f"  共抓取 {len(sorted_repos)} 个仓库")
    for cat, repos in categories.items():
        print(f"    {cat}: {len(repos)} 个")

    # ---- 构建 HTML ----
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html_parts = []
    html_parts.append(f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 720px; margin: 0 auto; padding: 20px; color: #1a1a1a;">
<div style="text-align: center; margin-bottom: 32px;">
    <h1 style="font-size: 24px; margin: 0; letter-spacing: 1px;">📡 GitHub 开发周报</h1>
    <p style="color: #888; font-size: 12px; margin-top: 4px;">🤖 Agent · 🔌 MCP · 🧠 Skills · 🐍 Python · 🔥 总榜</p>
    <p style="color: #666; font-size: 13px; margin-top: 6px;">{week_str}  ·  数据更新至 {now_str}</p>
</div>
""")

    section_index = 0
    for cat_name, cat_label in [("Agent", "🤖 Agent 框架"), ("MCP", "🔌 MCP 服务器"), ("Skills", "🧠 Skills 技能"), ("Python", "🐍 Python 热门"), ("Hot", "🔥 GitHub 总榜")]:
        repos = categories[cat_name]
        if not repos:
            continue
        section_index += 1

        html_parts.append(f"""
<div style="margin-bottom: 28px;">
    <h2 style="font-size: 18px; border-left: 4px solid #2563eb; padding-left: 12px; margin: 0 0 12px 0;">{cat_label}</h2>
    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
""")
        for repo in repos[:12]:  # 每类最多12个
            name = repo["full_name"]
            desc = translate_text((repo.get("description") or "无描述").strip())
            stars = repo["stargazers_count"]
            lang = repo.get("language") or "-"
            url = repo["html_url"]
            topics = [t for t in repo.get("topics", []) if t not in ("ai-agent", "agent", "agent-framework", "mcp", "mcp-server")]
            topics_html = " ".join(f'<span style="display:inline-block;background:#e8f0fe;color:#1a56db;font-size:11px;padding:1px 7px;border-radius:8px;margin:1px 3px 1px 0;">{t}</span>' for t in topics[:4])

            # 计算周增长（近似）
            weekly = repo.get("extra", {}).get("weekly_stars", 0)

            html_parts.append(f"""
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 10px 8px 10px 0; vertical-align: top; width: 40px; color: #999; font-weight: 500;">{repos.index(repo) + 1}.</td>
            <td style="padding: 10px 0;">
                <a href="{url}" style="color: #0969da; text-decoration: none; font-weight: 600;">{escape(name)}</a>
                <span style="color: #666; font-size: 12px; margin-left: 6px;">⭐ {stars}</span>
                <div style="color: #444; font-size: 13px; margin-top: 3px;">{escape(desc[:120])}</div>
                <div style="margin-top: 4px;">{topics_html} <span style="color: #888; font-size: 11px;">{escape(lang)}</span></div>
            </td>
        </tr>
""")

        html_parts.append("</table></div>")

    # 底部
    html_parts.append(f"""
<div style="margin-top: 32px; padding-top: 16px; border-top: 1px solid #ddd; font-size: 12px; color: #888; text-align: center;">
    <p>由 GitHub Actions 自动生成 · 每周一早 8:00 UTC 发送</p>
    <p>数据来源：<a href="https://github.com/search" style="color: #0969da;">GitHub Search API</a> + <a href="https://translate.googleapis.com" style="color: #0969da;">Google 翻译</a></p>
    <p style="margin-top: 4px;">
            <a href="{os.environ.get('REPO_URL', 'https://github.com')}" style="color: #0969da;">项目仓库</a>
    </p>
</div>
</body></html>""")

    return "\n".join(html_parts)


# ==================== 发送邮件 ====================
def send_email(html: str):
    """通过 QQ 邮箱 SMTP 发送 HTML 邮件"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📡 GitHub 开发周报 (Agent/Python/总榜 · {datetime.now(timezone.utc).strftime('%m/%d')})"
    msg["From"] = SENDER
    msg["To"] = RECEIVER
    msg.attach(MIMEText(html, "html", "utf-8"))

    print(f"[*] 连接 SMTP 服务器 {SMTP_SERVER}:{SMTP_PORT}...")
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as s:
        s.starttls()
        s.login(SENDER, AUTH_CODE)
        s.send_message(msg)
    print("[✓] 邮件发送成功")


# ==================== 主入口 ====================
def main():
    print("=" * 50)
    print("GitHub Agent 开发周报生成器")
    print(f"时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 50)

    html = build_html()

    print("[*] 发送邮件...")
    send_email(html)

    print("=" * 50)
    print("完成！")


if __name__ == "__main__":
    main()
