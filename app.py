import streamlit as st
import requests
from build_vectorstore import get_collection
from build_graph import load_graphs, get_top_authorities, get_trending_topics, get_contradictions, detect_topic
from datetime import datetime
import os
import json
import subprocess
import sys

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
    display: block !important;
}

[data-testid="collapsedControl"] {
    display: none !important;
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
    width: 48px; height: 48px;
    background: #25D366; border-radius: 50%;
    display: flex; align-items: center;
    justify-content: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    flex-shrink: 0;
}

.wa-brand-text {
    font-family: 'Sora', sans-serif;
    font-size: 1.25rem; font-weight: 700; color: #ffffff;
}

.wa-brand-sub { font-size: 0.7rem; color: #9de3d3; margin-top: 2px; }

.wa-section-label {
    font-size: 0.65rem; font-weight: 600; color: #9de3d3;
    letter-spacing: 1.5px; text-transform: uppercase;
    padding: 1.2rem 1.2rem 0.5rem;
}

.wa-stat-item {
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 0.65rem 1.2rem;
    border-bottom: 1px solid #064d46;
}

.wa-stat-label { font-size: 0.82rem; color: #c5e8e3; }

.wa-stat-value {
    background: #25D366; color: #fff;
    font-size: 0.72rem; font-weight: 700;
    padding: 0.15rem 0.6rem; border-radius: 10px;
    min-width: 26px; text-align: center;
}

.wa-status-item {
    display: flex; align-items: center; gap: 8px;
    padding: 0.55rem 1.2rem; font-size: 0.8rem; color: #9de3d3;
}

.wa-dot {
    width: 8px; height: 8px; background: #25D366;
    border-radius: 50%; flex-shrink: 0;
    animation: blink 2s infinite;
}

.wa-dot-off {
    width: 8px; height: 8px; background: #888;
    border-radius: 50%; flex-shrink: 0;
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

.wa-chat-body {
    padding: 1rem 2rem 1.5rem;
    max-width: 900px; margin: 0 auto;
}

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

.wa-welcome-sub {
    font-size: 0.86rem; color: #666;
    line-height: 1.75; margin-bottom: 0.5rem;
}

.wa-msg-user-row {
    display: flex; justify-content: flex-end; margin: 3px 0 8px;
}

.wa-bubble-user {
    background: #DCF8C6; color: #1a1a1a;
    padding: 0.6rem 1rem; border-radius: 12px 12px 2px 12px;
    max-width: 62%; font-size: 0.9rem; line-height: 1.55;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.wa-msg-bot-row {
    display: flex; align-items: flex-end;
    gap: 7px; margin: 3px 0 8px;
}

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

.wa-msg-time {
    font-size: 0.6rem; color: #888;
    margin-top: 2px; text-align: right;
}

.wa-msg-time-left {
    font-size: 0.6rem; color: #888;
    margin-top: 2px; padding-left: 37px;
}

.wa-source-tag {
    font-size: 0.63rem; color: #25D366;
    margin-top: 5px; font-weight: 600;
}

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
    background: #ffffff !important;
    border: 1.5px solid #25D366 !important;
    border-radius: 24px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    color: #1a1a1a !important;
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
    font-family: 'Sora', sans-serif; font-size: 1.1rem;
    font-weight: 700; color: #075E54; margin-bottom: 1rem;
    padding-bottom: 0.5rem; border-bottom: 2px solid #25D366;
}

.admin-entry {
    background: #f8fffe; border: 1px solid #c8e6c0;
    border-radius: 10px; padding: 0.7rem 1rem;
    margin-bottom: 0.5rem; font-size: 0.82rem;
    color: #1a1a1a; line-height: 1.5;
}

.unanswered-entry {
    background: #fff8e1; border: 1px solid #ffe082;
    border-radius: 10px; padding: 0.6rem 1rem;
    margin-bottom: 0.4rem; font-size: 0.82rem; color: #5d4037;
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

.cmg-card {
    background: #ffffff; border-radius: 14px;
    padding: 1.2rem 1.5rem; margin: 0.8rem 2rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-left: 4px solid #25D366;
}

.cmg-title {
    font-family: 'Sora', sans-serif; font-size: 1rem;
    font-weight: 700; color: #075E54; margin-bottom: 0.8rem;
}

.cmg-person-row {
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid #f0fdf4;
    font-size: 0.83rem;
}

.cmg-person-name { color: #1a1a1a; font-weight: 600; }
.cmg-person-role {
    font-size: 0.7rem; color: #25D366;
    background: #f0fdf4; border-radius: 8px;
    padding: 0.1rem 0.5rem; margin-left: 6px;
}

.cmg-trust-bar {
    display: flex; align-items: center; gap: 6px;
    font-size: 0.75rem; color: #555;
}

.cmg-topic-row {
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 0.45rem 0;
    border-bottom: 1px solid #f0fdf4;
    font-size: 0.83rem;
}

.cmg-topic-name { color: #075E54; font-weight: 600; text-transform: capitalize; }
.cmg-urgency-high  { color: #c62828; font-weight: 700; font-size: 0.75rem; }
.cmg-urgency-med   { color: #f57c00; font-weight: 700; font-size: 0.75rem; }
.cmg-urgency-low   { color: #388e3c; font-weight: 700; font-size: 0.75rem; }

.cmg-contra-row {
    background: #fff3e0; border: 1px solid #ffcc02;
    border-radius: 10px; padding: 0.7rem 1rem;
    margin-bottom: 0.5rem; font-size: 0.8rem; color: #5d4037;
}

.cmg-history-row {
    background: #f8fffe; border-left: 3px solid #25D366;
    padding: 0.5rem 0.8rem; margin-bottom: 0.4rem;
    font-size: 0.78rem; color: #333; border-radius: 0 8px 8px 0;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_collection():
    return get_collection()

@st.cache_data(ttl=60)
def load_cmg():
    return load_graphs()

collection = load_collection()
total_docs = collection.count()
person_graph, topic_graph, contradiction_log = load_cmg()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None
if "page" not in st.session_state:
    st.session_state.page = "chat"
if "anon_mode" not in st.session_state:
    st.session_state.anon_mode = False

def get_checkpoint_info():
    if os.path.exists("last_processed.json"):
        with open("last_processed.json", "r") as f:
            data = json.load(f)
        return data.get("last_message_count", 0)
    return 0

# ── LANGUAGE DETECTION — separate dedicated call ──────────
def detect_language(text):
    prompt = f"""You are a language detector. Look at the text below and reply with ONLY the language name. Nothing else. No explanation.

Examples of correct replies: Tamil, Hindi, English, Telugu, Malayalam, Kannada, Bengali

Text to detect: {text}

Reply with only the language name:"""
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral", "prompt": prompt, "stream": False
        }, timeout=30)
        lang = response.json()['response'].strip().split("\n")[0].strip()
        # Clean up common mistakes
        lang = lang.replace(".", "").replace(":", "").strip()
        if not lang or len(lang) > 20:
            return "English"
        return lang
    except Exception:
        return "English"

# ── LANGUAGE INSTRUCTION MAP ──────────────────────────────
LANG_INSTRUCTIONS = {
    "Tamil":     "நீங்கள் தமிழில் மட்டுமே பதில் சொல்ல வேண்டும். ஆங்கிலம் வேண்டாம்.",
    "Hindi":     "आपको केवल हिंदी में जवाब देना है। अंग्रेजी में मत बोलो।",
    "Telugu":    "మీరు తెలుగులో మాత్రమే సమాధానం చెప్పాలి. ఇంగ్లీష్ వేద్దు.",
    "Malayalam": "നിങ്ങൾ മലയാളത്തിൽ മാത്രം മറുപടി പറയണം. ഇംഗ്ലീഷ് വേണ്ട.",
    "Kannada":   "ನೀವು ಕನ್ನಡದಲ್ಲಿ ಮಾತ್ರ ಉತ್ತರಿಸಬೇಕು. ಇಂಗ್ಲಿಷ್ ಬೇಡ.",
    "Bengali":   "আপনাকে শুধুমাত্র বাংলায় উত্তর দিতে হবে। ইংরেজি নয়।",
    "English":   "Reply in English only.",
}

def get_lang_instruction(lang):
    for key in LANG_INSTRUCTIONS:
        if key.lower() in lang.lower():
            return LANG_INSTRUCTIONS[key]
    return f"You MUST reply in {lang} only. Do not use English."

# ── GET ANSWER ────────────────────────────────────────────
def get_answer(question, anon_mode=False):
    if total_docs == 0:
        return "⚠️ Knowledge base is empty. Please run python main.py first to build the database."

    results = collection.query(
        query_texts=[question],
        n_results=min(3, total_docs),
        include=["documents", "metadatas", "distances"]
    )
    context   = "\n\n".join(results['documents'][0])
    distances = results['distances'][0]
    metadatas = results['metadatas'][0]

    # ── Detect language first ─────────────────────────────
    detected_lang    = detect_language(question)
    lang_instruction = get_lang_instruction(detected_lang)

    if anon_mode:
        import re
        context = re.sub(r'Q: .+?\n', 'Q: [A group member asked]\n', context)

    topic    = detect_topic(question)
    cmg_note = ""

    if topic in topic_graph:
        tdata = topic_graph[topic]
        if tdata.get("has_contradiction") and topic in contradiction_log:
            cd = contradiction_log[topic]
            cmg_note += (
                f"\n\n⚠️ Note: This answer has been updated. "
                f"Original: '{cd.get('original_answer','')[:80]}' "
                f"→ Updated: '{cd.get('updated_answer','')[:80]}'"
            )
        related = tdata.get("related_topics", [])[:2]
        if related:
            cmg_note += f"\n\n📌 Related topics you may want to know: {', '.join(related)}"

    best_authority = ""
    best_score     = 0.0
    for person, pdata in person_graph.items():
        if topic in pdata.get("topics_covered", []):
            if pdata["authority_score"] > best_score:
                best_score     = pdata["authority_score"]
                best_authority = person

    # ── Build language-enforced prompt ───────────────────
    # The native-script instruction at the top forces Mistral
    # to activate the correct language mode before reading anything else
    llm_prompt = f"""{lang_instruction}

LANGUAGE RULE: Your response must be written entirely in {detected_lang}. Every single word must be in {detected_lang}. If you write even one word in English (and {detected_lang} is not English), that is wrong.

You are WhatsBot, a helpful WhatsApp group FAQ assistant.
Answer like a friendly group admin sending a short text message.
Use ONLY the context below to answer. Do NOT mention any person's name.
If the answer is not in the context, say it hasn't been discussed in the group (in {detected_lang}).

Context:
{context}

Question: {question}

Write your complete answer in {detected_lang} now:"""

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral", "prompt": llm_prompt, "stream": False
    })
    answer = response.json()['response'].strip()

    # ── Post-process: if answer still came in English but Tamil was asked,
    #    send a second stricter pass ─────────────────────────────────────
    if detected_lang != "English":
        # Check if answer is mostly ASCII (English letters) — if so, retry
        ascii_ratio = sum(1 for c in answer if ord(c) < 128 and c.isalpha()) / max(len(answer), 1)
        if ascii_ratio > 0.7:
            retry_prompt = f"""{lang_instruction}

The user asked: {question}
The answer from group chat context is: {answer}

Now translate and rewrite the above answer completely in {detected_lang}.
Do not include any English words.
Write only in {detected_lang}:"""
            retry_response = requests.post("http://localhost:11434/api/generate", json={
                "model": "mistral", "prompt": retry_prompt, "stream": False
            })
            answer = retry_response.json()['response'].strip()

    avg_distance = sum(distances) / len(distances) if distances else 1.0
    if avg_distance < 0.4:
        confidence, conf_note = "🟢 High confidence", "Answer found in multiple group messages"
    elif avg_distance < 0.7:
        confidence, conf_note = "🟡 Medium confidence", "Partial match found in group history"
    else:
        confidence, conf_note = "🔴 Low confidence", "Weak match — verify with group members"

    if "not been discussed" in answer.lower() or "hasn't been discussed" in answer.lower():
        existing_content = ""
        if os.path.exists("unanswered.txt"):
            with open("unanswered.txt", "r", encoding="utf-8") as f:
                existing_content = f.read()
        if question.strip() not in existing_content:
            with open("unanswered.txt", "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().strftime('%d/%m/%Y %I:%M %p')}] {question}\n")

    cti_lines = []
    top_meta  = metadatas[0] if metadatas else {}
    trust_score     = float(top_meta.get("trust_score",    "0.3"))
    validations     = int(top_meta.get("validations",      "0"))
    has_correction  = top_meta.get("has_correction",  "False") == "True"
    correction_note = top_meta.get("correction_note", "")

    if validations > 0:
        cti_lines.append(f"👍 Validated by {validations} group member{'s' if validations > 1 else ''}")
    if trust_score >= 0.7:
        cti_lines.append(f"🧵 CTI Trust: {int(trust_score * 100)}% — High")
    elif trust_score >= 0.4:
        cti_lines.append(f"🧵 CTI Trust: {int(trust_score * 100)}% — Medium")
    if best_authority and not anon_mode:
        cti_lines.append(f"👤 Top authority on this: {best_authority} ({int(best_score*100)}%)")
    if has_correction and correction_note:
        cti_lines.append(f"⚠️ Correction: {correction_note[:80]}")

    lang_tag = f"\n🌐 Replied in: {detected_lang}"
    anon_tag = "\n🔒 Anonymous mode ON" if anon_mode else ""
    cti_tag  = ("\n" + " · ".join(cti_lines)) if cti_lines else ""

    return f"{answer}{cmg_note}\n\n{confidence} · {conf_note}{lang_tag}{cti_tag}{anon_tag}"

def generate_report():
    now_str     = datetime.now().strftime("%d %B %Y, %I:%M %p")
    all_results = collection.get(include=["documents", "metadatas"])
    docs        = all_results.get("documents", [])
    metas       = all_results.get("metadatas", [])

    unanswered_lines = []
    if os.path.exists("unanswered.txt"):
        with open("unanswered.txt", "r", encoding="utf-8") as f:
            unanswered_lines = [l.strip() for l in f.readlines() if l.strip()]

    faq_rows = ""
    for i, (doc, meta) in enumerate(zip(docs, metas)):
        q     = meta.get("question",        "N/A")
        a     = meta.get("answer",          "N/A")
        s     = meta.get("sender",          "N/A")
        ts    = float(meta.get("trust_score", "0.3"))
        vals  = meta.get("validations",     "0")
        corr  = meta.get("has_correction",  "False")
        cnote = meta.get("correction_note", "")
        trust_bar = "🟢" if ts >= 0.7 else ("🟡" if ts >= 0.4 else "🔴")
        corr_html = f'<br><span style="color:#e65100;font-size:0.78em;">⚠️ {cnote}</span>' if corr == "True" and cnote else ""
        faq_rows += f"""
        <tr>
            <td style="padding:10px;border:1px solid #c8e6c0;color:#075E54;vertical-align:top;width:30px;">{i+1}</td>
            <td style="padding:10px;border:1px solid #c8e6c0;vertical-align:top;">
                <strong>Q:</strong> {q}<br>
                <span style="color:#555;font-size:0.88em;"><strong>A:</strong> {a}</span><br>
                <span style="color:#25D366;font-size:0.78em;">— {s}</span>{corr_html}
            </td>
            <td style="padding:10px;border:1px solid #c8e6c0;text-align:center;vertical-align:top;">
                {trust_bar} {int(ts*100)}%<br>
                <span style="font-size:0.75em;color:#888;">👍 {vals} votes</span>
            </td>
        </tr>"""

    authority_rows = ""
    for name, pdata in get_top_authorities(person_graph, top_n=5):
        role  = pdata.get("detected_role", "Member")
        score = int(pdata.get("authority_score", 0.3) * 100)
        ans   = pdata.get("answers_given", 0)
        authority_rows += f"""
        <tr>
            <td style="padding:8px;border:1px solid #c8e6c0;">{name}</td>
            <td style="padding:8px;border:1px solid #c8e6c0;">{role}</td>
            <td style="padding:8px;border:1px solid #c8e6c0;text-align:center;">{score}%</td>
            <td style="padding:8px;border:1px solid #c8e6c0;text-align:center;">{ans}</td>
        </tr>"""

    trending_rows = ""
    for tname, tdata in get_trending_topics(topic_graph, top_n=5):
        ask_count = tdata.get("ask_count", 0)
        urgency   = tdata.get("urgency_score", 0)
        contra    = "⚠️ Yes" if tdata.get("has_contradiction") else "✅ No"
        trending_rows += f"""
        <tr>
            <td style="padding:8px;border:1px solid #c8e6c0;text-transform:capitalize;">{tname}</td>
            <td style="padding:8px;border:1px solid #c8e6c0;text-align:center;">{ask_count}</td>
            <td style="padding:8px;border:1px solid #c8e6c0;text-align:center;">{urgency:.1f}/10</td>
            <td style="padding:8px;border:1px solid #c8e6c0;text-align:center;">{contra}</td>
        </tr>"""

    unanswered_rows = ""
    for i, line in enumerate(unanswered_lines):
        unanswered_rows += f"""
        <tr>
            <td style="padding:8px;border:1px solid #ffe082;color:#5d4037;">{i+1}</td>
            <td style="padding:8px;border:1px solid #ffe082;color:#5d4037;">{line}</td>
        </tr>"""
    if not unanswered_rows:
        unanswered_rows = """<tr><td colspan="2" style="padding:10px;border:1px solid #ffe082;color:#888;text-align:center;">✅ No unanswered questions.</td></tr>"""

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>WhatsBot CMG Report</title>
<style>
  body {{ font-family:'Segoe UI',Arial,sans-serif; background:#f5f5f5; color:#1a1a1a; margin:0; padding:2rem; }}
  .wrap {{ max-width:960px; margin:0 auto; background:#fff; border-radius:16px; padding:2.5rem; box-shadow:0 4px 24px rgba(0,0,0,0.08); }}
  .hdr {{ background:#075E54; color:white; border-radius:12px; padding:1.8rem 2rem; margin-bottom:2rem; }}
  .hdr-title {{ font-size:1.8rem; font-weight:800; margin-bottom:0.3rem; }}
  .hdr-sub {{ font-size:0.9rem; color:#9de3d3; }}
  .stats {{ display:flex; gap:1rem; margin-bottom:2rem; flex-wrap:wrap; }}
  .stat {{ background:#e8f5e1; border:2px solid #25D366; border-radius:12px; padding:1rem 1.5rem; flex:1; min-width:120px; text-align:center; }}
  .stat-num {{ font-size:2rem; font-weight:800; color:#075E54; }}
  .stat-lbl {{ font-size:0.78rem; color:#555; margin-top:2px; }}
  .sec-title {{ font-size:1.1rem; font-weight:700; color:#075E54; border-bottom:3px solid #25D366; padding-bottom:0.4rem; margin:1.5rem 0 1rem; }}
  table {{ width:100%; border-collapse:collapse; font-size:0.88rem; }}
  .footer {{ text-align:center; font-size:0.72rem; color:#888; margin-top:2rem; padding-top:1rem; border-top:1px solid #eee; }}
  .cmg-box {{ background:#e8f5e1; border:2px solid #25D366; border-radius:12px; padding:1rem 1.5rem; margin-bottom:1.5rem; font-size:0.85rem; color:#075E54; }}
</style></head><body>
<div class="wrap">
  <div class="hdr">
    <div class="hdr-title">📋 WhatsBot CMG Report</div>
    <div class="hdr-sub">Generated: {now_str} · Powered by Mistral 7B · 100% Offline · CMG Active</div>
  </div>
  <div class="cmg-box">🧠 <strong>Conversational Memory Graph (CMG)</strong> is active. Authority scores, trending topics, contradiction detection included.</div>
  <div class="stats">
    <div class="stat"><div class="stat-num">{total_docs}</div><div class="stat-lbl">FAQ Entries</div></div>
    <div class="stat"><div class="stat-num">{len(person_graph)}</div><div class="stat-lbl">People Tracked</div></div>
    <div class="stat"><div class="stat-num">{len(topic_graph)}</div><div class="stat-lbl">Topics Mapped</div></div>
    <div class="stat"><div class="stat-num">{len(unanswered_lines)}</div><div class="stat-lbl">Unanswered</div></div>
  </div>
  <div class="sec-title">👤 Top Authorities</div>
  <table><thead><tr style="background:#075E54;color:white;">
    <th style="padding:8px;border:1px solid #064d46;">Name</th>
    <th style="padding:8px;border:1px solid #064d46;">Role</th>
    <th style="padding:8px;border:1px solid #064d46;">Authority</th>
    <th style="padding:8px;border:1px solid #064d46;">Answers</th>
  </tr></thead><tbody>{authority_rows}</tbody></table>
  <div class="sec-title">🔥 Trending Topics</div>
  <table><thead><tr style="background:#075E54;color:white;">
    <th style="padding:8px;border:1px solid #064d46;">Topic</th>
    <th style="padding:8px;border:1px solid #064d46;">Asks</th>
    <th style="padding:8px;border:1px solid #064d46;">Urgency</th>
    <th style="padding:8px;border:1px solid #064d46;">Contradiction</th>
  </tr></thead><tbody>{trending_rows}</tbody></table>
  <div class="sec-title">📚 FAQ Knowledge Base</div>
  <table><thead><tr style="background:#075E54;color:white;">
    <th style="padding:10px;border:1px solid #064d46;">#</th>
    <th style="padding:10px;border:1px solid #064d46;text-align:left;">Q / A / Sender</th>
    <th style="padding:10px;border:1px solid #064d46;">Trust</th>
  </tr></thead><tbody>{faq_rows}</tbody></table>
  <div class="sec-title">❓ Unanswered Questions</div>
  <table><thead><tr style="background:#f9a825;color:white;">
    <th style="padding:8px;border:1px solid #f9a825;width:30px;">#</th>
    <th style="padding:8px;border:1px solid #f9a825;text-align:left;">Question</th>
  </tr></thead><tbody>{unanswered_rows}</tbody></table>
  <div class="footer">WhatsBot · CMG-Powered · Mistral 7B + ChromaDB · 100% Offline 🔒</div>
</div></body></html>"""

WA_LOGO = """<svg viewBox="0 0 48 48" width="{size}" height="{size}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M24 4C13 4 4 13 4 24c0 3.6 1 7 2.7 9.9L4 44l10.4-2.7C17.2 43 20.5 44 24 44c11 0 20-9 20-20S35 4 24 4z" fill="{outer}"/>
  <path d="M33.5 28.4c-.5-.2-2.9-1.4-3.3-1.6-.4-.2-.7-.2-1 .2-.3.4-1.2 1.6-1.5 1.9-.3.3-.5.4-1 .1-.5-.2-2-.7-3.8-2.3-1.4-1.2-2.3-2.8-2.6-3.2-.3-.5 0-.7.2-1 .2-.2.4-.5.6-.8.2-.3.2-.5.4-.8.1-.3 0-.6-.1-.8-.1-.2-1-2.4-1.4-3.3-.4-.9-.8-.7-1-.7h-.9c-.3 0-.8.1-1.2.6-.4.5-1.6 1.6-1.6 3.8s1.7 4.4 1.9 4.7c.2.3 3.3 5 8 7 1.1.5 2 .8 2.7 1 1.1.3 2.1.3 2.9.2.9-.1 2.8-1.1 3.2-2.2.4-1.1.4-2 .3-2.2-.1-.2-.4-.3-.9-.5z" fill="{inner}"/>
</svg>"""

# ══════════════════════════════════════════════════════════
# ── SIDEBAR ───────────────────────────────────────────────
# ══════════════════════════════════════════════════════════
with st.sidebar:
    logo_white       = WA_LOGO.format(size="26", outer="white", inner="#075E54")
    checkpoint_count = get_checkpoint_info()
    anon_dot  = '<div class="wa-dot"></div>' if st.session_state.anon_mode else '<div class="wa-dot-off"></div>'
    cmg_people = len(person_graph)
    cmg_topics = len(topic_graph)
    cmg_contra = len(contradiction_log)

    st.markdown(f"""
    <div class="wa-sidebar-header">
        <div class="wa-sidebar-brand">
            <div class="wa-logo-circle">{logo_white}</div>
            <div>
                <div class="wa-brand-text">WhatsBot</div>
                <div class="wa-brand-sub">CMG + CTI FAQ Agent</div>
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
    """, unsafe_allow_html=True)

    st.write("")
    if st.button("💬  Chat", use_container_width=True):
        st.session_state.page = "chat"; st.rerun()
    if st.button("🧠  CMG Dashboard", use_container_width=True):
        st.session_state.page = "cmg"; st.rerun()
    if st.button("🛠️  Admin Panel", use_container_width=True):
        st.session_state.page = "admin"; st.rerun()
    if st.button("🔄  Update Knowledge Base", use_container_width=True):
        st.session_state.page = "update"; st.rerun()
    if st.button("📋  FAQ Report", use_container_width=True):
        st.session_state.page = "report"; st.rerun()
    anon_label = "🔒  Anonymous: ON" if st.session_state.anon_mode else "👁️  Anonymous: OFF"
    if st.button(anon_label, use_container_width=True):
        st.session_state.anon_mode = not st.session_state.anon_mode
        st.rerun()
    if st.button("🗑️  Clear Chat", use_container_width=True):
        st.session_state.messages      = []
        st.session_state.pending_query = None
        st.rerun()

    st.markdown("""
    <div class="wa-privacy">
        🔒 End-to-end encrypted<br>
        100% Offline · Zero data leaves your device<br>
        <span style="color:#25D366;font-weight:600;">Mistral 7B + CMG + CTI</span>
    </div>
    """, unsafe_allow_html=True)

# ── ANON BANNER ───────────────────────────────────────────
if st.session_state.anon_mode:
    st.markdown(
        '<div class="anon-banner">🔒 ANONYMOUS MODE — All sender names hidden</div>',
        unsafe_allow_html=True)

# ── CHAT HEADER ───────────────────────────────────────────
logo_header = WA_LOGO.format(size="28", outer="white", inner="#075E54")
anon_status = " · 🔒 Anon ON" if st.session_state.anon_mode else ""
st.markdown(f"""
<div class="wa-chat-header">
    <div class="wa-header-avatar">{logo_header}</div>
    <div>
        <div class="wa-header-name">WhatsBot 🤖</div>
        <div class="wa-header-status">🟢 online · CMG Memory Graph · CTI Intelligence{anon_status}</div>
    </div>
    <div class="wa-header-icons">&nbsp;&nbsp;⋮</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── CMG DASHBOARD ─────────────────────────────────────────
# ══════════════════════════════════════════════════════════
if st.session_state.page == "cmg":
    st.markdown("<div style='padding:1.5rem 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("## 🧠 Conversational Memory Graph")
    st.markdown("</div>", unsafe_allow_html=True)

    if not person_graph and not topic_graph:
        st.markdown("""
        <div class="update-box" style="margin:1rem 2rem;">
            <div class="update-title">⚠️ CMG Not Built Yet</div>
            <div class="update-info">Run <strong>python main.py</strong> first.</div>
        </div>""", unsafe_allow_html=True)
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="cmg-card"><div class="cmg-title">👤 Top Authorities in Group</div>', unsafe_allow_html=True)
            for name, pdata in get_top_authorities(person_graph, top_n=6):
                role  = pdata.get("detected_role", "Member")
                score = int(pdata.get("authority_score", 0.3) * 100)
                ans   = pdata.get("answers_given", 0)
                icon  = "🟢" if score >= 70 else ("🟡" if score >= 40 else "🔴")
                display_name = "🔒 Hidden" if st.session_state.anon_mode else name
                st.markdown(f"""
                <div class="cmg-person-row">
                    <div><span class="cmg-person-name">{display_name}</span>
                    <span class="cmg-person-role">{role}</span></div>
                    <div class="cmg-trust-bar">{icon} {score}% · {ans} answers</div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="cmg-card"><div class="cmg-title">🔥 Trending Topics</div>', unsafe_allow_html=True)
            for tname, tdata in get_trending_topics(topic_graph, top_n=6):
                ask_count   = tdata.get("ask_count", 0)
                urgency     = tdata.get("urgency_score", 0)
                contra      = tdata.get("has_contradiction", False)
                contra_flag = " ⚠️" if contra else ""
                if urgency >= 7:
                    urg_class, urg_label = "cmg-urgency-high", f"🔥 {urgency:.1f}/10"
                elif urgency >= 4:
                    urg_class, urg_label = "cmg-urgency-med",  f"⚡ {urgency:.1f}/10"
                else:
                    urg_class, urg_label = "cmg-urgency-low",  f"✅ {urgency:.1f}/10"
                st.markdown(f"""
                <div class="cmg-topic-row">
                    <div><span class="cmg-topic-name">{tname}{contra_flag}</span>
                    <span style="font-size:0.72rem;color:#888;margin-left:6px;">{ask_count} asks</span></div>
                    <span class="{urg_class}">{urg_label}</span>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="cmg-card" style="margin:0.8rem 2rem;"><div class="cmg-title">⚠️ Contradiction Detector</div>', unsafe_allow_html=True)
        contras = get_contradictions(contradiction_log)
        if contras:
            for cd in contras:
                st.markdown(f"""
                <div class="cmg-contra-row">
                    <strong>📌 Topic: {cd.get('topic','').capitalize()}</strong><br>
                    <span style="color:#555;">Original ({cd.get('original_date','')}): {cd.get('original_answer','')[:100]}</span><br>
                    <span style="color:#c62828;">Updated ({cd.get('updated_date','')}): {cd.get('updated_answer','')[:100]}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="admin-entry">✅ No contradictions detected.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="cmg-card" style="margin:0.8rem 2rem;"><div class="cmg-title">📅 Answer Evolution Timeline</div>', unsafe_allow_html=True)
        if topic_graph:
            selected_topic = st.selectbox("Select topic:", options=sorted(topic_graph.keys()), key="cmg_topic_select")
            if selected_topic:
                for h in topic_graph[selected_topic].get("answer_history", [])[-5:]:
                    sender_display = "🔒 Hidden" if st.session_state.anon_mode else h.get("sender", "Unknown")
                    score = int(h.get("score", 0.3) * 100)
                    st.markdown(f"""
                    <div class="cmg-history-row">
                        📅 <strong>{h.get('date','')}</strong> · {sender_display} ({score}% authority)<br>
                        <span style="color:#333;">{h.get('answer','')[:150]}</span>
                    </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── REPORT PAGE ───────────────────────────────────────────
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "report":
    st.markdown("## 📋 FAQ Summary Report")
    st.markdown(f"""
    <div class="update-box">
        <div class="update-title">📊 Report Summary</div>
        <div class="update-info">
            📚 FAQ entries: <strong>{total_docs}</strong><br>
            👤 People tracked: <strong>{len(person_graph)}</strong><br>
            🗺️ Topics mapped: <strong>{len(topic_graph)}</strong><br>
            ⚠️ Contradictions: <strong>{len(contradiction_log)}</strong><br>
            💬 Messages processed: <strong>{get_checkpoint_info()}</strong><br>
            🕒 As of: <strong>{datetime.now().strftime("%d %B %Y, %I:%M %p")}</strong>
        </div>
    </div>""", unsafe_allow_html=True)
    if st.button("📥 Generate & Download Report", use_container_width=True):
        html_content    = generate_report()
        report_filename = f"whatsbot_cmg_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        st.download_button("⬇️ Click here to save the report", data=html_content,
                           file_name=report_filename, mime="text/html", use_container_width=True)
        st.success(f"Ready! Download: {report_filename}")

# ══════════════════════════════════════════════════════════
# ── UPDATE PAGE ───────────────────────────────────────────
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "update":
    st.markdown("## 🔄 Update Knowledge Base")
    checkpoint_count = get_checkpoint_info()
    st.markdown(f"""
    <div class="update-box">
        <div class="update-title">📊 Current Status</div>
        <div class="update-info">
            ✅ Messages processed: <strong>{checkpoint_count}</strong><br>
            📚 FAQ entries: <strong>{total_docs}</strong><br>
            🧠 CMG rebuilds automatically on update.<br><br>
            Replace <strong>chat.txt</strong> with a newer export, then click update.
        </div>
    </div>""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚡ Run Incremental Update", use_container_width=True):
            with st.spinner("Processing..."):
                result = subprocess.run([sys.executable, "main.py"], capture_output=True, text=True)
            st.success("Done!")
            st.code(result.stdout or "No new messages.", language="bash")
            if result.stderr: st.error(result.stderr)
            st.cache_resource.clear(); st.cache_data.clear(); st.rerun()
    with col2:
        if st.button("🔁 Force Full Rebuild", use_container_width=True):
            with st.spinner("Rebuilding..."):
                result = subprocess.run([sys.executable, "main.py", "--rebuild"], capture_output=True, text=True)
            st.success("Done!")
            st.code(result.stdout, language="bash")
            if result.stderr: st.error(result.stderr)
            st.cache_resource.clear(); st.cache_data.clear(); st.rerun()

# ══════════════════════════════════════════════════════════
# ── ADMIN PAGE ────────────────────────────────────────────
# ══════════════════════════════════════════════════════════
elif st.session_state.page == "admin":
    st.markdown("## 🛠️ Admin Panel")
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
            st.markdown('<div class="unanswered-entry">✅ No unanswered questions.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="unanswered-entry">✅ No unanswered questions.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
    st.markdown(f'<div class="admin-title">📚 FAQ Knowledge Base ({total_docs} entries)</div>', unsafe_allow_html=True)
    if total_docs > 0:
        all_results = collection.get(include=["documents", "metadatas"])
        for i, (doc_id, doc, meta) in enumerate(zip(all_results["ids"], all_results["documents"], all_results["metadatas"])):
            sender_display = "🔒 Hidden" if st.session_state.anon_mode else meta.get("sender", "N/A")
            trust_score    = float(meta.get("trust_score", "0.3"))
            trust_icon     = "🟢" if trust_score >= 0.7 else ("🟡" if trust_score >= 0.4 else "🔴")
            has_correction = meta.get("has_correction", "False") == "True"
            corr_flag      = " ⚠️ Corrected" if has_correction else ""
            with st.expander(f"{trust_icon} Entry {i+1} — {meta.get('question','')[:55]}...{corr_flag}"):
                st.markdown(f"**Q:** {meta.get('question','N/A')}")
                st.markdown(f"**A:** {meta.get('answer','N/A')}")
                st.markdown(f"**Sender:** {sender_display}")
                st.markdown(f"**Trust Score:** {trust_icon} {int(trust_score*100)}%")
                st.markdown(f"**Validations:** 👍 {meta.get('validations','0')}")
                if has_correction:
                    st.markdown(f"**Correction:** ⚠️ {meta.get('correction_note','')}")
                if st.button(f"🗑️ Delete", key=f"del_{doc_id}"):
                    collection.delete(ids=[doc_id])
                    st.success("Deleted"); st.cache_resource.clear(); st.rerun()
    else:
        st.markdown('<div class="admin-entry">No entries. Run python main.py first.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── CHAT PAGE ─────────────────────────────────────────────
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
                CMG + CTI Powered WhatsApp FAQ Agent.<br>
                I know who to trust, what topics matter,<br>
                and when answers have changed!<br><br>
                👇 Tap a quick question or type below
            </div>
        </div>""", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="wa-msg-user-row"><div>
                <div class="wa-bubble-user">{msg["content"]}</div>
                <div class="wa-msg-time">{time_str} &nbsp;✓✓</div>
            </div></div>""", unsafe_allow_html=True)
        else:
            logo_mini = WA_LOGO.format(size="16", outer="#ffffff", inner="#25D366")
            st.markdown(f"""
            <div class="wa-msg-bot-row">
                <div class="wa-bot-mini-avatar">{logo_mini}</div>
                <div>
                    <div class="wa-bubble-bot">{msg["content"]}
                        <div class="wa-source-tag">✦ WhatsBot · CMG Memory Graph · CTI Intelligence</div>
                    </div>
                    <div class="wa-msg-time-left">{time_str}</div>
                </div>
            </div>""", unsafe_allow_html=True)

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
        with st.spinner("WhatsBot is thinking..."):
            answer = get_answer(q, anon_mode=st.session_state.anon_mode)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

    if prompt := st.chat_input("Message WhatsBot..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("WhatsBot is thinking..."):
            answer = get_answer(prompt, anon_mode=st.session_state.anon_mode)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()