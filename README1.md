# WhatsBot 🤖💬
### Domain-Specific FAQ Chatbot Built from WhatsApp Group Chat Export Using Local LLMs

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Mistral](https://img.shields.io/badge/LLM-Mistral_7B-orange)
![Ollama](https://img.shields.io/badge/Runtime-Ollama-black)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-purple)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)
![Offline](https://img.shields.io/badge/Mode-100%25_Offline-green)

---

## Table of Contents
- [Introduction](#introduction)
- [Technologies Used](#technologies-used)
- [Architecture](#architecture)
- [System Components](#system-components)
- [Methodology](#methodology)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Privacy & Security](#privacy--security)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Author](#author)

---

## Introduction

WhatsBot is a domain-specific FAQ chatbot that transforms a WhatsApp group chat export into an intelligent, locally-running AI agent using Retrieval-Augmented Generation (RAG).

Every WhatsApp group — whether a college department, office team, or community — accumulates thousands of messages containing valuable knowledge. This knowledge gets buried, repeated, or lost entirely. WhatsBot solves this by mining the group's full chat history, extracting Q&A pairs, and serving accurate, grounded answers through a WhatsApp-themed chat interface.

**No API keys. No cloud services. No cost. No data leaves your device.**

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core application logic |
| Ollama | Local LLM serving runtime |
| Mistral 7B | Q&A extraction + answer generation |
| nomic-embed-text | Text-to-vector embeddings |
| ChromaDB | Persistent vector database with duplicate detection |
| Streamlit | Multi-page WhatsApp-themed chat UI |

---

## Architecture

WhatsBot follows a two-phase RAG pipeline:

**Phase 1 — Ingestion (run once)**
```
WhatsApp Export (chat.txt)
        ↓
parse_chat.py → Cleans messages, creates sliding windows of 5
        ↓
extract_qa.py → Mistral 7B extracts Q&A pairs, events, birthdays, announcements as JSON
        ↓
build_vectorstore.py → Deduplication check → nomic-embed-text embeds Q&A → stored in ChromaDB
        ↓
Knowledge Base Ready ✅
```

**Phase 2 — Querying (real-time)**
```
User Question
        ↓
nomic-embed-text → Embeds the question as a vector
        ↓
ChromaDB → Retrieves top 3 semantically similar Q&A pairs
        ↓
Mistral 7B → Generates a grounded, context-aware answer
        ↓
WhatsBot UI → Displays answer in WhatsApp-styled chat interface
```

---

## System Components

| Component | File | Function |
|---|---|---|
| Chat Parser | `parse_chat.py` | Cleans and chunks raw WhatsApp export |
| Q&A Extractor | `extract_qa.py` | Uses Mistral 7B to extract structured Q&A pairs, birthdays, events, and announcements |
| Vector Store | `build_vectorstore.py` | Embeds Q&A, performs duplicate detection, and persists in ChromaDB |
| RAG Engine | `chatbot.py` | Retrieves context and generates answers |
| Pipeline Runner | `main.py` | Executes ingestion phases 1–3 in sequence; supports incremental and full rebuild modes |
| Chat Interface | `app.py` | Multi-page Streamlit UI with WhatsApp theme |

---

## Methodology

**Step 1 — Data Parsing**
The WhatsApp `.txt` export is parsed using regex to extract sender names, timestamps, and message text. System messages, media omissions, and very short messages are filtered out. Messages are grouped using a sliding window of 5 to preserve conversational context.

**Step 2 — Q&A Extraction (Mistral 7B)**
Each message chunk is sent to the locally-running Mistral 7B model via Ollama. The model is prompted to extract not just question-answer pairs, but also birthdays, deadlines, exam dates, and announcements — returning them as structured JSON. Sender names and original timestamps are preserved.

```
Input  → "[15/03/2025] Admin: Exam is on March 20th at 9 AM"
Output → {"question": "When is the exam?", "answer": "March 20th at 9 AM", "sender": "Admin"}

Input  → "[10/01/2025] Members: Happy Birthday Priya! 🎉"
Output → {"question": "When is Priya's birthday?", "answer": "January 10th", "sender": "Members"}
```

**Step 3 — Duplicate Detection + Vector Embedding**
Before storing, each extracted Q&A pair is checked against existing entries in ChromaDB. If a semantically similar question (≥90% similarity) already exists, the pair is skipped to avoid redundancy. New pairs are embedded using `nomic-embed-text` and persisted under `faq_db/`.

**Step 4 — Retrieval-Augmented Generation**
At query time, the user's question is embedded and compared against the vector store. The top 3 closest matches are retrieved and passed as context to Mistral 7B, which generates a final natural-language answer grounded in the group's actual conversations. Questions the bot cannot answer are automatically logged to `unanswered.txt`.

---

## Project Structure

```
whatsbot/
│
├── chat.txt                  # WhatsApp exported chat (user input)
├── parse_chat.py             # Phase 1 — Parse and clean chat export
├── extract_qa.py             # Phase 2 — Extract Q&A, birthdays, events using Mistral 7B
├── build_vectorstore.py      # Phase 3 — Deduplicate, embed, and store in ChromaDB
├── chatbot.py                # RAG query engine with unanswered question logging
├── main.py                   # Runs the full ingestion pipeline (incremental + rebuild modes)
├── app.py                    # Multi-page Streamlit WhatsApp-themed UI
│
├── faq_db/                   # ChromaDB persistent vector store (auto-generated)
├── schedule_log.txt          # Scheduled rebuild event log (auto-generated)
├── unanswered.txt            # Log of questions WhatsBot couldn't answer (auto-generated)
│
└── README.md
```

---

## Installation

### Prerequisites
- Python 3.10 or higher
- [Ollama](https://ollama.com) installed
- 8GB RAM minimum (16GB recommended)
- ~5GB free disk space for models

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/whatsbot.git
cd whatsbot
```

### 2. Pull AI Models *(one-time, requires internet)*
```bash
ollama pull mistral
ollama pull nomic-embed-text
```

### 3. Install Python Dependencies
```bash
pip install chromadb requests streamlit schedule
```

### 4. Export Your WhatsApp Chat
On your phone:
1. Open the WhatsApp group → tap ⋮ → **More** → **Export Chat**
2. Select **Without Media**
3. Send to yourself → download → rename to `chat.txt`
4. Place `chat.txt` inside the project folder

### 5. Build the Knowledge Base
```bash
python main.py
```

Expected output:
```
Step 1: Parsing chat...
  Found 332 messages
Step 2: Chunking messages...
  Created 67 chunks
Step 3: Extracting Q&A pairs (this takes time)...
  Processed 10/67 chunks, found 28 pairs so far...
Total Q&A pairs extracted: 87
Step 4: Storing in vector database...
  Stored : 84 new Q&A pairs
  Skipped: 3 duplicates or empty pairs
  Total in DB: 87
Done! Run: streamlit run app.py
```

> ⏱️ This step may take 10–30 minutes depending on chat size.

### 6. Launch WhatsBot
```bash
python -m streamlit run app.py
```

Open your browser at: **http://localhost:8501**

---

## Usage

| Page | How to use |
|---|---|
| 💬 Chat | Type any question and press Enter, or tap a Quick Question button |
| 🛠️ Admin Panel | Browse all FAQ entries, view senders, delete entries, review unanswered questions |
| 🔄 Update Knowledge Base | Run incremental update or force full rebuild after replacing `chat.txt` |
| 📋 FAQ Report | Generate and download an HTML report of the full knowledge base |
| ⏰ Scheduled Rebuild | Set WhatsBot to auto-rebuild daily, hourly, or every minute |
| 🔒 Anonymous Mode | Toggle from the sidebar to hide sender names |

---

## Privacy & Security

| Concern | How WhatsBot Handles It |
|---|---|
| Chat data | Never sent to any external server |
| API keys | Not required — zero external API calls |
| Internet | Only needed once for model download |
| Storage | All data stays on your local disk only |
| Network | All calls go to `localhost:11434` (your own machine) |
| Sender names | Can be hidden using Anonymous Mode |

> Turn off your WiFi and WhatsBot still works. Everything runs locally.

---

## Troubleshooting

| Error | Fix |
|---|---|
| `ollama not found` | Restart terminal after Ollama installation |
| `connection refused` | Open a new terminal and run `ollama serve` |
| `chat.txt not found` | Ensure the file is in the project root folder |
| `chromadb error` | Run `pip install chromadb --upgrade` |
| `streamlit not found` | Use `python -m streamlit run app.py` |
| `schedule not found` | Run `pip install schedule` |
| No Q&A extracted | Your chat date format may differ — open an issue with a sample line |

---

## Roadmap

- [x] Core RAG pipeline (parse → extract → embed → query)
- [x] Duplicate detection in vector store
- [x] Rich extraction (birthdays, events, deadlines, announcements)
- [x] Multi-page UI (Chat, Admin, Update, Report, Schedule)
- [x] Unanswered questions log
- [x] Scheduled auto-rebuild
- [x] Incremental update + force rebuild
- [x] FAQ HTML report export
- [x] Anonymous mode
- [x] Multi-language support (Tamil, Hindi, English)
- [ ] Drag-and-drop chat file upload in UI
- [ ] Support for multiple group chats
- [ ] Docker deployment
- [ ] Export knowledge base as PDF

---

## Author

**S. Sruti** — B.Tech. Information Technology

**Kavi Nisha MP** — B.Tech. Artificial Intelligence and Data Science

---

*Built using open-source AI tools — completely free, completely private.*

> **WhatsBot — Because no one should have to answer the same question twice.**

![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?logo=whatsapp&logoColor=white)
![Made with Python](https://img.shields.io/badge/Made_with-Python-blue?logo=python)
![100% Offline](https://img.shields.io/badge/100%25-Offline-brightgreen)
