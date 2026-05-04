import streamlit as st
import requests
from build_vectorstore import get_collection
from datetime import datetime

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

[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
    background: #e8f5e1 !important;
}

/* Hide streamlit defaults */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
.stChatMessage { background: transparent !important; }

/* Remove default button styles completely */
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

/* Clear chat button special */
.clear-btn .stButton > button {
    background: transparent !important;
    color: #9de3d3 !important;
    border: 1px solid #9de3d3 !important;
    border-radius: 8px !important;
}

/* Sidebar */
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

.wa-stat-label {
    font-size: 0.82rem;
    color: #c5e8e3;
}

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

.wa-status-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0.55rem 1.2rem;
    font-size: 0.8rem;
    color: #9de3d3;
}

.wa-dot {
    width: 8px;
    height: 8px;
    background: #25D366;
    border-radius: 50%;
    flex-shrink: 0;
    animation: blink 2s infinite;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

.wa-privacy {
    padding: 1.2rem;
    font-size: 0.68rem;
    color: #6aada4;
    text-align: center;
    line-height: 1.9;
    border-top: 1px solid #064d46;
    margin-top: 1rem;
}

/* Chat header - bigger */
.wa-chat-header {
    background: #075E54;
    padding: 1.1rem 1.8rem;
    display: flex;
    align-items: center;
    gap: 14px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.18);
}

.wa-header-avatar {
    width: 52px;
    height: 52px;
    background: #25D366;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.wa-header-name {
    font-family: 'Sora', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.2px;
}

.wa-header-status {
    font-size: 0.75rem;
    color: #9de3d3;
    margin-top: 2px;
}

.wa-header-icons {
    margin-left: auto;
    display: flex;
    gap: 20px;
    font-size: 1.2rem;
    color: #ffffff;
}

/* Chat body */
.wa-chat-body {
    padding: 1rem 2rem 1.5rem;
    max-width: 900px;
    margin: 0 auto;
}

.wa-date-badge {
    text-align: center;
    margin: 0.8rem 0 1.2rem;
}

.wa-date-badge span {
    background: #c8e6c0;
    color: #2d6a2d;
    font-size: 0.7rem;
    padding: 0.28rem 0.9rem;
    border-radius: 8px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* Welcome card */
.wa-welcome {
    background: #ffffff;
    border-radius: 16px;
    padding: 2.2rem 1.8rem;
    text-align: center;
    margin: 0.5rem auto 1.5rem;
    max-width: 500px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.07);
}

.wa-welcome-title {
    font-family: 'Sora', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: #075E54;
    margin-bottom: 0.6rem;
    margin-top: 0.5rem;
}

.wa-welcome-sub {
    font-size: 0.86rem;
    color: #666;
    line-height: 1.75;
    margin-bottom: 0.5rem;
}

/* Messages */
.wa-msg-user-row {
    display: flex;
    justify-content: flex-end;
    margin: 3px 0 8px;
}

.wa-bubble-user {
    background: #DCF8C6;
    color: #1a1a1a;
    padding: 0.6rem 1rem;
    border-radius: 12px 12px 2px 12px;
    max-width: 62%;
    font-size: 0.9rem;
    line-height: 1.55;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.wa-msg-bot-row {
    display: flex;
    align-items: flex-end;
    gap: 7px;
    margin: 3px 0 8px;
}

.wa-bot-mini-avatar {
    width: 30px;
    height: 30px;
    background: #25D366;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.72rem;
    color: white;
    font-weight: 700;
    flex-shrink: 0;
}

.wa-bubble-bot {
    background: #ffffff;
    color: #1a1a1a;
    padding: 0.6rem 1rem;
    border-radius: 12px 12px 12px 2px;
    max-width: 65%;
    font-size: 0.9rem;
    line-height: 1.65;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.wa-msg-time {
    font-size: 0.6rem;
    color: #888;
    margin-top: 2px;
    text-align: right;
}

.wa-msg-time-left {
    font-size: 0.6rem;
    color: #888;
    margin-top: 2px;
    padding-left: 37px;
}

.wa-source-tag {
    font-size: 0.63rem;
    color: #25D366;
    margin-top: 5px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 3px;
}

/* Quick questions section */
.quick-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #2d6a2d;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
    padding: 0 2rem;
}

.quick-btn-area {
    background: #d4edcc;
    border-top: 1px solid #b5d9ac;
    padding: 0.9rem 1.5rem 1rem;
}

/* Chat input */
[data-testid="stChatInput"] textarea {
    background: #ffffff !important;
    border: 1.5px solid #25D366 !important;
    border-radius: 24px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    color: #1a1a1a !important;
    padding: 0.7rem 1.2rem !important;
}

/* Remove all dark/black colors from streamlit defaults */
[data-testid="stMarkdownContainer"] p {
    color: #2d4a2d !important;
}

.stMarkdown { color: #2d4a2d !important; }

/* Horizontal rule */
hr {
    border: none !important;
    border-top: 1px solid #b5d9ac !important;
    margin: 0 !important;
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

def get_answer(question):
    results = collection.query(
        query_texts=[question],
        n_results=min(3, total_docs)
    )
    context = "\n\n".join(results['documents'][0])
    llm_prompt = f"""You are WhatsBot, an official WhatsApp FAQ Agent for a group.
Reply like a helpful, warm group admin texting back — short, friendly, and clear.
Use ONLY the context below to answer.
If the answer is not there, reply: "That hasn't been discussed in the group yet 🤔"

Context:
{context}

Question: {question}
Answer:"""
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": llm_prompt,
        "stream": False
    })
    return response.json()['response'].strip()

WA_LOGO = """<svg viewBox="0 0 48 48" width="{size}" height="{size}" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M24 4C13 4 4 13 4 24c0 3.6 1 7 2.7 9.9L4 44l10.4-2.7C17.2 43 20.5 44 24 44c11 0 20-9 20-20S35 4 24 4z" fill="{outer}"/>
  <path d="M33.5 28.4c-.5-.2-2.9-1.4-3.3-1.6-.4-.2-.7-.2-1 .2-.3.4-1.2 1.6-1.5 1.9-.3.3-.5.4-1 .1-.5-.2-2-.7-3.8-2.3-1.4-1.2-2.3-2.8-2.6-3.2-.3-.5 0-.7.2-1 .2-.2.4-.5.6-.8.2-.3.2-.5.4-.8.1-.3 0-.6-.1-.8-.1-.2-1-2.4-1.4-3.3-.4-.9-.8-.7-1-.7h-.9c-.3 0-.8.1-1.2.6-.4.5-1.6 1.6-1.6 3.8s1.7 4.4 1.9 4.7c.2.3 3.3 5 8 7 1.1.5 2 .8 2.7 1 1.1.3 2.1.3 2.9.2.9-.1 2.8-1.1 3.2-2.2.4-1.1.4-2 .3-2.2-.1-.2-.4-.3-.9-.5z" fill="{inner}"/>
</svg>"""

# ── SIDEBAR ──────────────────────────────────────────────
with st.sidebar:
    logo_white = WA_LOGO.format(size="26", outer="white", inner="#075E54")
    logo_green_big = WA_LOGO.format(size="56", outer="#25D366", inner="white")

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
        <span class="wa-stat-label">💬 Messages</span>
        <span class="wa-stat-value">{len(st.session_state.messages)}</span>
    </div>

    <div class="wa-section-label">System Status</div>
    <div class="wa-status-item"><div class="wa-dot"></div>Mistral 7B · Running Locally</div>
    <div class="wa-status-item"><div class="wa-dot"></div>Embeddings · Active</div>
    <div class="wa-status-item"><div class="wa-dot"></div>ChromaDB · Connected</div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding: 0 0.8rem; margin-top:1.2rem;'>", unsafe_allow_html=True)
    if st.button("🗑️  Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_query = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="wa-privacy">
        🔒 End-to-end encrypted<br>
        100% Offline · Zero data leaves your device<br>
        <span style="color:#25D366; font-weight:600;">Powered by Mistral 7B</span>
    </div>
    """, unsafe_allow_html=True)

# ── CHAT HEADER ───────────────────────────────────────────
logo_header = WA_LOGO.format(size="28", outer="white", inner="#075E54")
st.markdown(f"""
<div class="wa-chat-header">
    <div class="wa-header-avatar">{logo_header}</div>
    <div>
        <div class="wa-header-name">WhatsBot 🤖</div>
        <div class="wa-header-status">🟢 online · WhatsApp FAQ Agent · End-to-end encrypted</div>
    </div>
    <div class="wa-header-icons"> &nbsp; &nbsp; ⋮</div>
</div>
""", unsafe_allow_html=True)

# ── CHAT BODY ────────────────────────────────────────────
now = datetime.now()
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
            I've read your entire group chat history<br>
            and I'm ready to answer any question!<br><br>
            👇 Tap a quick question or type below
        </div>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="wa-msg-user-row">
            <div>
                <div class="wa-bubble-user">{msg["content"]}</div>
                <div class="wa-msg-time">{time_str} &nbsp;✓✓</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        logo_mini = WA_LOGO.format(size="16", outer="#ffffff", inner="#25D366")
        st.markdown(f"""
        <div class="wa-msg-bot-row">
            <div class="wa-bot-mini-avatar">{logo_mini}</div>
            <div>
                <div class="wa-bubble-bot">
                    {msg["content"]}
                    <div class="wa-source-tag">✦ WhatsBot · sourced from group chat</div>
                </div>
                <div class="wa-msg-time-left">{time_str}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── QUICK QUESTIONS (WORKING BUTTONS) ─────────────────────
st.markdown("""
<div class="quick-btn-area">
<div class="quick-label">⚡ Quick Questions</div>
</div>
""", unsafe_allow_html=True)

questions = [
    "📅 What is the deadline?",
    "📝 How do I submit?",
    "📚 When is the exam?",
    "📌 What are the rules?",
]

col1, col2, col3, col4 = st.columns(4)
for col, question in zip([col1, col2, col3, col4], questions):
    with col:
        if st.button(question, use_container_width=True, key=f"btn_{question}"):
            st.session_state.pending_query = question

# ── PROCESS BUTTON CLICK ──────────────────────────────────
if st.session_state.pending_query:
    q = st.session_state.pending_query
    st.session_state.pending_query = None
    st.session_state.messages.append({"role": "user", "content": q})
    with st.spinner("WhatsBot is typing..."):
        answer = get_answer(q)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()

# ── CHAT INPUT ────────────────────────────────────────────
if prompt := st.chat_input("Message WhatsBot..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.spinner("WhatsBot is typing..."):
        answer = get_answer(prompt)
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()