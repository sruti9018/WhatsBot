import streamlit as st
import requests
from build_vectorstore import get_collection
from datetime import datetime
import os
import json
import subprocess
import sys
import threading
import time
import schedule

st.set_page_config(
    page_title="WhatsBot - WhatsApp FAQ Agent",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Sora:wght@700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #e8f5e1 !important;
    font-family: 'Inter', sans-serif !important;
    color: #1a1a1a !important;
}

[data-testid="stSidebar"] {
    background: #075E54 !important;
    border-right: none !important;
}

[data-testid="stSidebar"] > div {
    padding: 0 !important;
}

[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

section[data-testid="stSidebar"] {
    width: 280px !important;
    min-width: 280px !important;
    transform: none !important;
    visibility: visible !important;
}

[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
    background: #e8f5e1 !important;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
.stChatMessage { background: transparent !important; }

.stButton > button {
    background: #ffffff !important;
    color: #075E54 !important;
    border: 1.5px solid #25D366 !important;
    border-radius: 22px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    padding: 0.45rem 0.7rem !important;
    width: 100% !important;
    cursor: pointer !important;
    box-shadow: 0 1px 4px rgba(37,211,102,0.15) !important;
    transition: none !important;
}

.stButton > button:hover {
    background: #ffffff !important;
    color: #075E54 !important;
    border: 1.5px solid #25D366 !important;
    box-shadow: 0 1px 4px rgba(37,211,102,0.15) !important;
}

.stButton > button:focus {
    background: #ffffff !important;
    color: #075E54 !important;
    border: 1.5px solid #25D366 !important;
    box-shadow: none !important;
    outline: none !important;
}

.stButton > button:active {
    background: #f0fdf4 !important;
    color: #075E54 !important;
    transform: none !important;
}

.wa-sidebar-header {
    background: #075E54;
    padding: 1.4rem 1.2rem 1.2rem;
    border-bottom: 1px solid #064d46;
}

.wa-sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1rem;
}

.wa-logo-circle {
    width: 48px;
    height: 48px;
    background: #25D366;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    flex-shrink: 0;
}

.wa-brand-text {
    font-family: 'Sora', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: #ffffff;
}

.wa-brand-sub {
    font-size: 0.7rem;
    color: #9de3d3;
    margin-top: 2px;
}

.wa-section-label {
    font-size: 0.65rem;
    font-weight: 600;
    color: #9de3d3;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 1.2rem 1.2rem 0.5rem;
}

.wa-stat-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.65rem 1.2rem;
    border-bottom: 1px solid #064d46;
}

.wa-stat-label { font-size: 0.82rem; color: #c5e8e3; }

.wa-stat-value {
    background: #25D366;
    color: #fff;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.15rem 0.6rem;
    border-radius: 10px;
    min-width: 26px;
    text-align: center;
}

.wa-dot {
    width: 8px; height: 8px;
    background: #25D366; border-radius: 50%;
    flex-shrink: 0; animation: blink 2s infinite;
}

.wa-dot-off {
    width: 8px; height: 8px;
    background: #888; border-radius: 50%; flex-shrink: 0;
}

.wa-status-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0.55rem 1.2rem;
    font-size: 0.8rem;
    color: #9de3d3;
}

@keyframes blink {
    0%, 100% { opacity: 1; } 50% { opacity: 0.3; }
}

.wa-privacy {
    padding: 1.2rem; font-size: 0.68rem; color: #6aada4;
    text-align: center; line-height: 1.9;
    border-top: 1px solid #064d46; margin-top: 1rem;
}

.wa-chat-header {
    background: #075E54; padding: 1.1rem 1.8rem;
    display: flex; align-items: center; gap: 14px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.18);
}

.wa-header-avatar {
    width: 52px; height: 52px; background: #25D366;
    border-radius: 50%; display: flex; align-items: center;
    justify-content: center; flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.wa-header-name {
    font-family: 'Sora', sans-serif; font-size: 1.15rem;
    font-weight: 700; color: #ffffff; letter-spacing: -0.2px;
}

.wa-header-status { font-size: 0.75rem; color: #9de3d3; margin-top: 2px; }

.wa-header-icons {
    margin-left: auto; display: flex;
    gap: 20px; font-size: 1.2rem; color: #ffffff;
}

.wa-chat-body { padding: 1rem 2rem 1.5rem; max-width: 900px; margin: 0 auto; }

.wa-date-badge { text-align: center; margin: 0.8rem 0 1.2rem; }

.wa-date-badge span {
    background: #c8e6c0; color: #2d6a2d; font-size: 0.7rem;
    padding: 0.28rem 0.9rem; border-radius: 8px;
    font-weight: 600; letter-spacing: 0.5px;
}

.wa-welcome {
    background: #ffffff; border-radius: 16px;
    padding: 2.2rem 1.8rem; text-align: center;
    margin: 0.5rem auto 1.5rem; max-width: 500px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.07);
}

.wa-welcome-title {
    font-family: 'Sora', sans-serif; font-size: 1.35rem;
    font-weight: 700; color: #075E54;
    margin-bottom: 0.6rem; margin-top: 0.5rem;
}

.wa-welcome-sub { font-size: 0.86rem; color: #666; line-height: 1.75; margin-bottom: 0.5rem; }

.wa-msg-user-row { display: flex; justify-content: flex-end; margin: 3px 0 8px; }

.wa-bubble-user {
    background: #DCF8C6; color: #1a1a1a;
    padding: 0.6rem 1rem; border-radius: 12px 12px 2px 12px;
    max-width: 62%; font-size: 0.9rem; line-height: 1.55;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.wa-msg-bot-row { display: flex; align-items: flex-end; gap: 7px; margin: 3px 0 8px; }

.wa-bot-mini-avatar {
    width: 30px; height: 30px; background: #25D366;
    border-radius: 50%; display: flex; align-items: center;
    justify-content: center; font-size: 0.72rem;
    color: white; font-weight: 700; flex-shrink: 0;
}

.wa-bubble-bot {
    background: #ffffff; color: #1a1a1a;
    padding: 0.6rem 1rem; border-radius: 12px 12px 12px 2px;
    max-width: 65%; font-size: 0.9rem; line-height: 1.65;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.wa-msg-time { font-size: 0.6rem; color: #888; margin-top: 2px; text-align: right; }
.wa-msg-time-left { font-size: 0.6rem; color: #888; margin-top: 2px; padding-left: 37px; }
.wa-source-tag { font-size: 0.63rem; color: #25D366; margin-top: 5px; font-weight: 600; }

.quick-label {
    font-size: 0.72rem; font-weight: 600; color: #2d6a2d;
    letter-spacing: 1px; text-transform: uppercase;
    margin-bottom: 0.6rem; padding: 0 2rem;
}

.quick-btn-area {
    background: #d4edcc; border-top: 1px solid #b5d9ac;
    padding: 0.9rem 1.5rem 1rem;
}

[data-testid="stChatInput"] textarea {
    background: #ffffff !important; border: 1.5px solid #25D366 !important;
    border-radius: 24px !important; font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important; color: #1a1a1a !important;
    padding: 0.7rem 1.2rem !important;
}

[data-testid="stMarkdownContainer"] p { color: #2d4a2d !important; }
.stMarkdown { color: #2d4a2d !important; }
hr { border: none !important; border-top: 1px solid #b5d9ac !important; margin: 0 !important; }

.admin-panel {
    background: #ffffff; border-radius: 16px; padding: 1.5rem;
    margin: 1rem 2rem; box-shadow: 0 2px 16px rgba(0,0,0,0.07);
}

.admin-title {
    font-family: 'Sora', sans-serif; font-size: 1.1rem; font-weight: 700;
    color: #075E54; margin-bottom: 1rem; padding-bottom: 0.5rem;
    border-bottom: 2px solid #25D366;
}

.admin-entry {
    background: #f8fffe; border: 1px solid #c8e6c0; border-radius: 10px;
    padding: 0.7rem 1rem; margin-bottom: 0.5rem;
    font-size: 0.82rem; color: #1a1a1a; line-height: 1.5;
}

.unanswered-entry {
    background: #fff8e1; border: 1px solid #ffe082; border-radius: 10px;
    padding: 0.6rem 1rem; margin-bottom: 0.4rem;
    font-size: 0.82rem; color: #5d4037;
}

.update-box {
    background: #e8f5e1; border: 2px solid #25D366;
    border-radius: 14px; padding: 1.2rem 1.5rem; margin: 1rem 2rem;
}

.update-title {
    font-family: 'Sora', sans-serif; font-size: 1rem;
    font-weight: 700; color: #075E54; margin-bottom: 0.5rem;
}

.update-info { font-size: 0.8rem; color: #2d6a2d; line-height: 1.7; }

.anon-banner {
    background: #1a1a2e; color: #a0c4ff; text-align: center;
    font-size: 0.75rem; font-weight: 600;
    padding: 0.4rem 1rem; letter-spacing: 1px;
}

.schedule-box {
    background: #fff8e1; border: 2px solid #f9a825;
    border-radius: 14px; padding: 1.2rem 1.5rem; margin: 1rem 2rem;
}

.schedule-title {
    font-family: 'Sora', sans-serif; font-size: 1rem;
    font-weight: 700; color: #e65100; margin-bottom: 0.5rem;
}

.schedule-info { font-size: 0.8rem; color: #5d4037; line-height: 1.7; }

.schedule-log-entry {
    background: #f1f8e9; border: 1px solid #aed581; border-radius: 8px;
    padding: 0.5rem 0.9rem; margin-bottom: 0.35rem;
    font-size: 0.78rem; color: #33691e; font-family: monospace;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_collection():
    return get_collection()

collection = load_collection()
total_docs = collection.count()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None
if "page" not in st.session_state:
    st.session_state.page = "chat"
if "anon_mode" not in st.session_state:
    st.session_state.anon_mode = False
if "scheduler_running" not in st.session_state:
    st.session_state.scheduler_running = False
if "schedule_interval" not in st.session_state:
    st.session_state.schedule_interval = "daily"

SCHEDULE_LOG = "schedule_log.txt"

def log_schedule_event(msg):
    with open(SCHEDULE_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%d/%m/%Y %I:%M %p')}] {msg}\n")

def run_scheduled_rebuild():
    log_schedule_event("⏰ Scheduled rebuild started...")
    try:
        result = subprocess.run(
            [sys.executable, "main.py"],
            capture_output=True, text=True, timeout=300
        )
        log_schedule_event(f"✅ Rebuild complete. Output: {result.stdout.strip()[:120]}")
    except Exception as e:
        log_schedule_event(f"❌ Rebuild failed: {str(e)}")

def scheduler_loop(interval):
    schedule.clear()
    if interval == "hourly":
        schedule.every(1).hours.do(run_scheduled_rebuild)
    elif interval == "daily":
        schedule.every().day.at("02:00").do(run_scheduled_rebuild)
    elif interval == "every_minute":
        schedule.every(1).minutes.do(run_scheduled_rebuild)
    log_schedule_event(f"🟢 Scheduler started — interval: {interval}")
    while True:
        schedule.run_pending()
        time.sleep(30)

def start_scheduler(interval="daily"):
    t = threading.Thread(target=scheduler_loop, args=(interval,), daemon=True)
    t.start()

def get_checkpoint_info():
    if os.path.exists("last_processed.json"):
        with open("last_processed.json", "r") as f:
            data = json.load(f)
        return data.get("last_message_count", 0)
    return 0

def detect_language(text):
    prompt = f"""Detect the language of this text and reply with ONLY the language name.
Examples: English, Tamil, Hindi, Telugu, Malayalam, French, Arabic
Text: {text}
Language:"""
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral", "prompt": prompt, "stream": False
    })
    lang = response.json()['response'].strip().split("\n")[0].strip()
    return lang if lang else "English"

def get_answer(question, anon_mode=False):
    results = collection.query(
        query_texts=[question],
        n_results=min(3, total_docs),
        include=["documents"]
    )
    context = "\n\n".join(results['documents'][0])
    detected_lang = detect_language(question)

    if anon_mode:
        import re
        context = re.sub(r'Q: .+?\n', 'Q: [A group member asked]\n', context)

    llm_prompt = f"""You are WhatsBot, an official WhatsApp FAQ Agent for a group.
The user asked in {detected_lang}. You MUST reply in {detected_lang} only.
Reply like a helpful, warm group admin texting back — short, friendly, and clear.
Use ONLY the context below to answer.
Do NOT mention any names of people in your answer.
If the answer is not there, reply in {detected_lang}: "That hasn't been discussed in the group yet 🤔"

Context:
{context}

Question: {question}
Answer (in {detected_lang}):"""

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral", "prompt": llm_prompt, "stream": False
    })
    answer = response.json()['response'].strip()

    if "not been discussed" in answer.lower() or "hasn't been discussed" in answer.lower():
        with open("unanswered.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%d/%m/%Y %I:%M %p')}] {question}\n")

    lang_tag = f"\n🌐 Replied in: {detected_lang}"
    anon_tag = "\n🔒 Anonymous mode ON — no names shown" if anon_mode else ""
    return f"{answer}{lang_tag}{anon_tag}"

def generate_report():
    now_str = datetime.now().strftime("%d %B %Y, %I:%M %p")
    all_results = collection.get(include=["documents", "metadatas"])
    docs  = all_results.get("documents", [])
    metas = all_results.get("metadatas", [])

    unanswered_lines = []
    if os.path.exists("unanswered.txt"):
        with open("unanswered.txt", "r", encoding="utf-8") as f:
            unanswered_lines = [l.strip() for l in f.readlines() if l.strip()]

    faq_rows = ""
    for i, (doc, meta) in enumerate(zip(docs, metas)):
        q = meta.get("question", "N/A")
        a = meta.get("answer", "N/A")
        s = meta.get("sender", "N/A")
        faq_rows += f"""<tr>
            <td style="padding:10px;border:1px solid #c8e6c0;font-weight:600;color:#075E54;vertical-align:top;width:30px;">{i+1}</td>
            <td style="padding:10px;border:1px solid #c8e6c0;vertical-align:top;">
                <strong>Q:</strong> {q}<br>
                <span style="color:#555;font-size:0.88em;"><strong>A:</strong> {a}</span><br>
                <span style="color:#25D366;font-size:0.78em;">— {s}</span>
            </td></tr>"""

    unanswered_rows = ""
    for i, line in enumerate(unanswered_lines):
        unanswered_rows += f"""<tr>
            <td style="padding:8px;border:1px solid #ffe082;color:#5d4037;">{i+1}</td>
            <td style="padding:8px;border:1px solid #ffe082;color:#5d4037;">{line}</td></tr>"""

    if not unanswered_rows:
        unanswered_rows = """<tr><td colspan="2" style="padding:10px;border:1px solid #ffe082;color:#888;text-align:center;">✅ No unanswered questions logged yet.</td></tr>"""

    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>WhatsBot FAQ Report</title>
<style>
body{{font-family:'Segoe UI',Arial,sans-serif;background:#f5f5f5;color:#1a1a1a;margin:0;padding:2rem;}}
.report-wrap{{max-width:900px;margin:0 auto;background:#fff;border-radius:16px;padding:2.5rem;box-shadow:0 4px 24px rgba(0,0,0,0.08);}}
.report-header{{background:#075E54;color:white;border-radius:12px;padding:1.8rem 2rem;margin-bottom:2rem;}}
.report-title{{font-size:1.8rem;font-weight:800;margin-bottom:0.3rem;}}
.report-sub{{font-size:0.9rem;color:#9de3d3;}}
.stat-row{{display:flex;gap:1rem;margin-bottom:2rem;flex-wrap:wrap;}}
.stat-card{{background:#e8f5e1;border:2px solid #25D366;border-radius:12px;padding:1rem 1.5rem;flex:1;min-width:140px;text-align:center;}}
.stat-num{{font-size:2rem;font-weight:800;color:#075E54;}}
.stat-label{{font-size:0.78rem;color:#555;margin-top:2px;}}
.section-title{{font-size:1.1rem;font-weight:700;color:#075E54;border-bottom:3px solid #25D366;padding-bottom:0.4rem;margin:1.5rem 0 1rem;}}
table{{width:100%;border-collapse:collapse;font-size:0.88rem;}}
.footer{{text-align:center;font-size:0.72rem;color:#888;margin-top:2rem;padding-top:1rem;border-top:1px solid #eee;}}
</style></head><body>
<div class="report-wrap">
  <div class="report-header">
    <div class="report-title">📋 WhatsBot FAQ Report</div>
    <div class="report-sub">Generated on {now_str} · Powered by Mistral 7B · 100% Offline</div>
  </div>
  <div class="stat-row">
    <div class="stat-card"><div class="stat-num">{total_docs}</div><div class="stat-label">FAQ Entries</div></div>
    <div class="stat-card"><div class="stat-num">{len(unanswered_lines)}</div><div class="stat-label">Unanswered Questions</div></div>
    <div class="stat-card"><div class="stat-num">{get_checkpoint_info()}</div><div class="stat-label">Messages Processed</div></div>
  </div>
  <div class="section-title">📚 FAQ Knowledge Base</div>
  <table><thead><tr style="background:#075E54;color:white;">
    <th style="padding:10px;border:1px solid #064d46;">#</th>
    <th style="padding:10px;border:1px solid #064d46;text-align:left;">Question / Answer / Sender</th>
  </tr></thead><tbody>{faq_rows}</tbody></table>
  <div class="section-title">❓ Unanswered Questions Log</div>
  <table><thead><tr style="background:#f9a825;color:white;">
    <th style="padding:8px;border:1px solid #f9a825;width:30px;">#</th>
    <th style="padding:8px;border:1px solid #f9a825;text-align:left;">Question &amp; Timestamp</th>
  </tr></thead><tbody>{unanswered_rows}</tbody></table>
  <div class="footer">WhatsBot · Mistral 7B + ChromaDB + Streamlit · 100% Offline 🔒</div>
</div></body></html>"""

WA_LOGO = """<svg viewBox="0 0 48 48" width="{size}" height="{size}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M24 4C13 4 4 13 4 24c0 3.6 1 7 2.7 9.9L4 44l10.4-2.7C17.2 43 20.5 44 24 44c11 0 20-9 20-20S35 4 24 4z" fill="{outer}"/>
  <path d="M33.5 28.4c-.5-.2-2.9-1.4-3.3-1.6-.4-.2-.7-.2-1 .2-.3.4-1.2 1.6-1.5 1.9-.3.3-.5.4-1 .1-.5-.2-2-.7-3.8-2.3-1.4-1.2-2.3-2.8-2.6-3.2-.3-.5 0-.7.2-1 .2-.2.4-.5.6-.8.2-.3.2-.5.4-.8.1-.3 0-.6-.1-.8-.1-.2-1-2.4-1.4-3.3-.4-.9-.8-.7-1-.7h-.9c-.3 0-.8.1-1.2.6-.4.5-1.6 1.6-1.6 3.8s1.7 4.4 1.9 4.7c.2.3 3.3 5 8 7 1.1.5 2 .8 2.7 1 1.1.3 2.1.3 2.9.2.9-.1 2.8-1.1 3.2-2.2.4-1.1.4-2 .3-2.2-.1-.2-.4-.3-.9-.5z" fill="{inner}"/>
</svg>"""

# ── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    logo_white = WA_LOGO.format(size="26", outer="white", inner="#075E54")
    checkpoint_count = get_checkpoint_info()
    anon_dot  = '<div class="wa-dot"></div>' if st.session_state.anon_mode else '<div class="wa-dot-off"></div>'
    sched_dot = '<div class="wa-dot"></div>' if st.session_state.scheduler_running else '<div class="wa-dot-off"></div>'

    st.markdown(f"""
    <div class="wa-sidebar-header">
        <div class="wa-sidebar-brand">
            <div class="wa-logo-circle">{logo_white}</div>
            <div>
                <div class="wa-brand-text">WhatsBot</div>
                <div class="wa-brand-sub">Official WhatsApp FAQ Agent</div>
            </div>
        </div>
    </div>
    <div class="wa-section-label">Knowledge Base</div>
    <div class="wa-stat-item">
        <span class="wa-stat-label">📚 FAQ Entries</span>
        <span class="wa-stat-value">{total_docs}</span>
    </div>
    <div class="wa-stat-item">
        <span class="wa-stat-label">💬 Messages Processed</span>
        <span class="wa-stat-value">{checkpoint_count}</span>
    </div>
    <div class="wa-stat-item">
        <span class="wa-stat-label">🗨️ Chat Turns</span>
        <span class="wa-stat-value">{len(st.session_state.messages)}</span>
    </div>
    <div class="wa-section-label">Features</div>
    <div class="wa-status-item">{anon_dot}Anonymous Mode · {"ON" if st.session_state.anon_mode else "OFF"}</div>
    <div class="wa-status-item">{sched_dot}Scheduler · {"Running" if st.session_state.scheduler_running else "Stopped"}</div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding: 0 0.8rem; margin-top:1.2rem;'>", unsafe_allow_html=True)

    if st.button("💬  Chat", use_container_width=True):
        st.session_state.page = "chat"; st.rerun()
    if st.button("🛠️  Admin Panel", use_container_width=True):
        st.session_state.page = "admin"; st.rerun()
    if st.button("🔄  Update Knowledge Base", use_container_width=True):
        st.session_state.page = "update"; st.rerun()
    if st.button("📋  FAQ Report", use_container_width=True):
        st.session_state.page = "report"; st.rerun()
    if st.button("⏰  Scheduled Rebuild", use_container_width=True):
        st.session_state.page = "schedule"; st.rerun()

    anon_label = "🔒  Anonymous Mode: ON" if st.session_state.anon_mode else "👁️  Anonymous Mode: OFF"
    if st.button(anon_label, use_container_width=True):
        st.session_state.anon_mode = not st.session_state.anon_mode; st.rerun()
    if st.button("🗑️  Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_query = None; st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="wa-privacy">
        🔒 End-to-end encrypted<br>
        100% Offline · Zero data leaves your device<br>
        <span style="color:#25D366;font-weight:600;">Powered by Mistral 7B</span>
    </div>
    """, unsafe_allow_html=True)

# ── ANON BANNER ───────────────────────────────────────────
if st.session_state.anon_mode:
    st.markdown('<div class="anon-banner">🔒 ANONYMOUS MODE ACTIVE — All sender names are hidden</div>', unsafe_allow_html=True)

# ── CHAT HEADER ───────────────────────────────────────────
logo_header  = WA_LOGO.format(size="28", outer="white", inner="#075E54")
anon_status  = " · 🔒 Anonymous" if st.session_state.anon_mode else ""
sched_status = " · ⏰ Auto-Rebuild ON" if st.session_state.scheduler_running else ""
st.markdown(f"""
<div class="wa-chat-header">
    <div class="wa-header-avatar">{logo_header}</div>
    <div>
        <div class="wa-header-name">WhatsBot 🤖</div>
        <div class="wa-header-status">🟢 online · Multi-Language FAQ Agent{anon_status}{sched_status}</div>
    </div>
    <div class="wa-header-icons"> &nbsp; &nbsp; ⋮</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── SCHEDULE PAGE ─────────────────────────────────────────
# ══════════════════════════════════════════════════════════
if st.session_state.page == "schedule":
    st.markdown("<div style='padding:1.5rem 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("## ⏰ Scheduled Rebuild")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="schedule-box">
        <div class="schedule-title">🔁 Auto-Rebuild Settings</div>
        <div class="schedule-info">
            WhatsBot can automatically re-scan your <strong>chat.txt</strong> on a schedule
            and add any new messages — without you doing anything.<br><br>
            Status: <strong>{"🟢 Scheduler is running" if st.session_state.scheduler_running else "🔴 Scheduler is stopped"}</strong><br>
            Interval: <strong>{st.session_state.schedule_interval}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:0 2rem;margin-top:1rem;'>", unsafe_allow_html=True)
    interval_choice = st.selectbox("Select rebuild interval:",
        options=["daily","hourly","every_minute"],
        index=["daily","hourly","every_minute"].index(st.session_state.schedule_interval),
        format_func=lambda x: {"daily":"🌙 Daily (2:00 AM)","hourly":"🕐 Every Hour","every_minute":"⚡ Every Minute (testing)"}[x]
    )
    st.session_state.schedule_interval = interval_choice

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("▶️ Start Scheduler", use_container_width=True):
            if not st.session_state.scheduler_running:
                start_scheduler(interval=interval_choice)
                st.session_state.scheduler_running = True
                log_schedule_event(f"▶️ Scheduler started — interval: {interval_choice}")
                st.success(f"Started! Interval: {interval_choice}")
                st.rerun()
            else:
                st.info("Already running.")
    with col2:
        if st.button("⏹️ Stop Scheduler", use_container_width=True):
            schedule.clear()
            st.session_state.scheduler_running = False
            log_schedule_event("⏹️ Scheduler stopped.")
            st.warning("Scheduler stopped.")
            st.rerun()
    with col3:
        if st.button("🔨 Run Now", use_container_width=True):
            with st.spinner("Running rebuild..."):
                run_scheduled_rebuild()
            st.success("Done!")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='padding:0 2rem;margin-top:1.5rem;'>", unsafe_allow_html=True)
    st.markdown("### 📜 Rebuild Log")
    if os.path.exists(SCHEDULE_LOG):
        with open(SCHEDULE_LOG, "r", encoding="utf-8") as f:
            log_lines = [l.strip() for l in f.readlines() if l.strip()]
        if log_lines:
            for line in reversed(log_lines[-20:]):
                st.markdown(f'<div class="schedule-log-entry">{line}</div>', unsafe_allow_html=True)
            if st.button("🗑️ Clear Log", key="clear_sched_log"):
                open(SCHEDULE_LOG, "w").close()
                st.success("Cleared!"); st.rerun()
        else:
            st.markdown('<div class="schedule-log-entry">No events yet.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="schedule-log-entry">No events yet.</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── REPORT PAGE ───────────────────────────────────────────
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "report":
    st.markdown("<div style='padding:1.5rem 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("## 📋 FAQ Summary Report")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="update-box">
        <div class="update-title">📊 Report Summary</div>
        <div class="update-info">
            📚 FAQ entries: <strong>{total_docs}</strong><br>
            💬 Messages processed: <strong>{get_checkpoint_info()}</strong><br>
            🕒 As of: <strong>{datetime.now().strftime("%d %B %Y, %I:%M %p")}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='padding:0 2rem;margin-top:1rem;'>", unsafe_allow_html=True)
    if st.button("📥 Generate & Download Report", use_container_width=True):
        html_content = generate_report()
        fname = f"whatsbot_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        st.download_button("⬇️ Click here to save the report", data=html_content,
                           file_name=fname, mime="text/html", use_container_width=True)
        st.success(f"Ready! Download: {fname}")
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── UPDATE PAGE ───────────────────────────────────────────
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "update":
    st.markdown("<div style='padding:1.5rem 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("## 🔄 Update Knowledge Base")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="update-box">
        <div class="update-title">📊 Current Status</div>
        <div class="update-info">
            ✅ Messages processed: <strong>{get_checkpoint_info()}</strong><br>
            📚 FAQ entries: <strong>{total_docs}</strong><br><br>
            Replace <strong>chat.txt</strong> with a newer export, then click update.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='padding:0 2rem;margin-top:1rem;'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚡ Run Incremental Update", use_container_width=True):
            with st.spinner("Processing new messages..."):
                result = subprocess.run([sys.executable, "main.py"], capture_output=True, text=True)
            st.success("Done!")
            st.code(result.stdout or "No new messages found.", language="bash")
            if result.stderr: st.error(result.stderr)
            st.cache_resource.clear(); st.rerun()
    with col2:
        if st.button("🔁 Force Full Rebuild", use_container_width=True):
            with st.spinner("Rebuilding..."):
                result = subprocess.run([sys.executable, "main.py", "--rebuild"], capture_output=True, text=True)
            st.success("Done!")
            st.code(result.stdout, language="bash")
            if result.stderr: st.error(result.stderr)
            st.cache_resource.clear(); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── ADMIN PAGE ────────────────────────────────────────────
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "admin":
    st.markdown("<div style='padding:1.5rem 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("## 🛠️ Admin Panel")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
    st.markdown('<div class="admin-title">❓ Unanswered Questions Log</div>', unsafe_allow_html=True)
    unanswered_path = "unanswered.txt"
    if os.path.exists(unanswered_path):
        with open(unanswered_path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        if lines:
            for line in lines:
                st.markdown(f'<div class="unanswered-entry">🔸 {line}</div>', unsafe_allow_html=True)
            col_a, col_b = st.columns([1, 4])
            with col_a:
                if st.button("🗑️ Clear Log", use_container_width=True):
                    open(unanswered_path, "w").close()
                    st.success("Cleared!"); st.rerun()
        else:
            st.markdown('<div class="unanswered-entry">✅ No unanswered questions yet.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="unanswered-entry">✅ No unanswered questions yet.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
    st.markdown(f'<div class="admin-title">📚 FAQ Knowledge Base ({total_docs} entries)</div>', unsafe_allow_html=True)
    if total_docs > 0:
        all_results = collection.get(include=["documents", "metadatas"])
        docs  = all_results["documents"]
        ids   = all_results["ids"]
        metas = all_results["metadatas"]
        for i, (doc_id, doc, meta) in enumerate(zip(ids, docs, metas)):
            sender_display = "🔒 Hidden" if st.session_state.anon_mode else meta.get("sender", "N/A")
            with st.expander(f"📌 Entry {i+1} — {meta.get('question','')[:60]}..."):
                st.markdown(f"**Q:** {meta.get('question','N/A')}")
                st.markdown(f"**A:** {meta.get('answer','N/A')}")
                st.markdown(f"**Sender:** {sender_display}")
                if st.button("🗑️ Delete this entry", key=f"del_{doc_id}"):
                    collection.delete(ids=[doc_id])
                    st.success("Deleted!")
                    st.cache_resource.clear(); st.rerun()
    else:
        st.markdown('<div class="admin-entry">No FAQ entries. Run python main.py first.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── CHAT PAGE ─────────────────────────────────════════════
# ══════════════════════════════════════════════════════════
else:
    now      = datetime.now()
    date_str = now.strftime("%B %d, %Y")
    time_str = now.strftime("%I:%M %p")
    logo_welcome = WA_LOGO.format(size="60", outer="#25D366", inner="white")

    st.markdown('<div class="wa-chat-body">', unsafe_allow_html=True)
    st.markdown(f'<div class="wa-date-badge"><span>TODAY · {date_str.upper()}</span></div>', unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown(f"""
        <div class="wa-welcome">
            {logo_welcome}
            <div class="wa-welcome-title">Hi! I'm WhatsBot 👋</div>
            <div class="wa-welcome-sub">
                Your Official WhatsApp Group FAQ Agent.<br>
                Ask me in any language —<br>
                Tamil, Hindi, English and more!<br><br>
                👇 Tap a quick question or type below
            </div>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="wa-msg-user-row"><div>
                <div class="wa-bubble-user">{msg["content"]}</div>
                <div class="wa-msg-time">{time_str} &nbsp;✓✓</div>
            </div></div>
            """, unsafe_allow_html=True)
        else:
            logo_mini = WA_LOGO.format(size="16", outer="#ffffff", inner="#25D366")
            st.markdown(f"""
            <div class="wa-msg-bot-row">
                <div class="wa-bot-mini-avatar">{logo_mini}</div>
                <div>
                    <div class="wa-bubble-bot">{msg["content"]}
                        <div class="wa-source-tag">✦ WhatsBot · sourced from group chat</div>
                    </div>
                    <div class="wa-msg-time-left">{time_str}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="quick-btn-area"><div class="quick-label">⚡ Quick Questions</div></div>', unsafe_allow_html=True)

    questions = ["📅 What is the deadline?", "📝 How do I submit?", "📚 When is the exam?", "📌 What are the rules?"]
    col1, col2, col3, col4 = st.columns(4)
    for col, question in zip([col1, col2, col3, col4], questions):
        with col:
            if st.button(question, use_container_width=True, key=f"btn_{question}"):
                st.session_state.pending_query = question

    if st.session_state.pending_query:
        q = st.session_state.pending_query
        st.session_state.pending_query = None
        st.session_state.messages.append({"role": "user", "content": q})
        with st.spinner("WhatsBot is typing..."):
            answer = get_answer(q, anon_mode=st.session_state.anon_mode)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

    if prompt := st.chat_input("Message WhatsBot..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("WhatsBot is typing..."):
            answer = get_answer(prompt, anon_mode=st.session_state.anon_mode)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()
