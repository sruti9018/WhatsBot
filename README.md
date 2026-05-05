# WhatsBot
A privacy preserving domain specific FAQs chatbot built from WhatsApp group chat export using local LLM.
# WhatsBot 🤖💬
### Domain-Specific FAQ Chatbot Built from WhatsApp Group Chat Export Using Local LLMs

![WhatsBot](https://img.shields.io/badge/WhatsBot-WhatsApp%20FAQ%20Agent-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Mistral](https://img.shields.io/badge/Mistral-7B-orange?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=for-the-badge)
![ChromaDB](https://img.shields.io/badge/ChromaDB-VectorDB-blue?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Offline](https://img.shields.io/badge/100%25-Offline-25D366?style=for-the-badge)

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

**WhatsBot** is a domain-specific FAQ chatbot that transforms a WhatsApp group chat export into an intelligent, locally-running AI agent using Retrieval-Augmented Generation (RAG).

Every WhatsApp group — whether a college department, office team, or community — accumulates thousands of messages containing valuable knowledge. This knowledge gets buried, repeated, or lost entirely. WhatsBot solves this by mining the group's full chat history, extracting Q&A pairs, and serving accurate, grounded answers through a WhatsApp-themed chat interface.

> **No API keys. No cloud services. No cost. No data leaves your device.**

---

## Technologies Used

| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core application logic |
| **Ollama** | Local LLM serving runtime |
| **Mistral 7B** | Q&A extraction + answer generation |
| **nomic-embed-text** | Text-to-vector embeddings |
| **ChromaDB** | Persistent vector database |
| **Streamlit** | Web-based chat UI |

---

## Architecture

WhatsBot follows a two-phase RAG pipeline:

**Phase 1 — Ingestion (run once)**
WhatsApp Export (chat.txt)
↓
parse_chat.py       →  Cleans messages, creates sliding windows of 5
↓
extract_qa.py       →  Mistral 7B extracts Q&A pairs as JSON
↓
build_vectorstore.py →  nomic-embed-text embeds Q&A → stored in ChromaDB
↓
Knowledge Base Ready ✅

**Phase 2 — Querying (real-time)**
User Question
↓
nomic-embed-text    →  Embeds the question as a vector
↓
ChromaDB            →  Retrieves top 3 semantically similar Q&A pairs
↓
Mistral 7B          →  Generates a grounded, context-aware answer
↓
WhatsBot UI         →  Displays answer in WhatsApp-styled chat interface

---

## System Components

| Component | File | Function |
|---|---|---|
| Chat Parser | `parse_chat.py` | Cleans and chunks raw WhatsApp export |
| Q&A Extractor | `extract_qa.py` | Uses Mistral 7B to extract structured Q&A pairs |
| Vector Store | `build_vectorstore.py` | Embeds Q&A and persists in ChromaDB |
| RAG Engine | `chatbot.py` | Retrieves context and generates answers |
| Pipeline Runner | `main.py` | Executes ingestion phases 1–3 in sequence |
| Chat Interface | `app.py` | Streamlit UI with full WhatsApp theme |

---

## Methodology

<p align="center">
  <img src="system_design.jpg" width="900"/>
</p>

### Step 1 — Data Parsing

The WhatsApp `.txt` export is parsed using regex to extract sender names and message text. System messages, media omissions, and very short messages are filtered out. Messages are grouped using a sliding window of 5 to preserve conversational context.

### Step 2 — Q&A Extraction (Mistral 7B)

Each message chunk is sent to the locally-running Mistral 7B model via Ollama. The model is prompted to extract question-answer pairs and return them as structured JSON. This step runs entirely offline.
Input  → "When is the exam? / Admin: It's on March 15th at 9 AM"
Output → {"question": "When is the exam?", "answer": "March 15th at 9 AM"}

### Step 3 — Vector Embedding (nomic-embed-text)

Each extracted Q&A pair is converted into a high-dimensional vector using `nomic-embed-text`. These vectors are stored persistently in ChromaDB under the `faq_db/` directory. This enables semantic search — finding relevant answers even when the wording of a question differs from the stored one.

### Step 4 — Retrieval-Augmented Generation

At query time, the user's question is embedded and compared against the vector store. The top 3 closest matches are retrieved and passed as context to Mistral 7B, which generates a final natural-language answer grounded in the group's actual conversations.

---

## Project Structure
whatsbot/
│
├── chat.txt                  # WhatsApp exported chat (user input)
│
├── parse_chat.py             # Phase 1 — Parse and clean chat export
├── extract_qa.py             # Phase 2 — Extract Q&A using Mistral 7B
├── build_vectorstore.py      # Phase 3 — Embed and store in ChromaDB
├── chatbot.py                # RAG query engine
├── main.py                   # Runs the full ingestion pipeline
├── app.py                    # Streamlit WhatsApp-themed UI
│
├── faq_db/                   # ChromaDB persistent vector store (auto-generated)
│
└── README.md

---

## Installation

### Prerequisites

- Python 3.10 or higher
- [Ollama](https://ollama.com) installed
- 8GB RAM minimum (16GB recommended)
- ~5GB free disk space for models

---

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/whatsbot.git
cd whatsbot
```

### 2. Pull AI Models (one-time, requires internet)

```bash
ollama pull mistral
ollama pull nomic-embed-text
```

### 3. Install Python Dependencies

```bash
pip install chromadb requests streamlit
```

### 4. Export Your WhatsApp Chat

On your phone:
1. Open the WhatsApp group → tap **⋮** → **More** → **Export Chat**
2. Select **Without Media**
3. Send to yourself → download → rename to `chat.txt`
4. Place `chat.txt` inside the project folder

### 5. Build the Knowledge Base

```bash
python main.py
```

Expected output:
Step 1: Parsing chat...
Found 523 messages
Step 2: Chunking messages...
Created 104 chunks
Step 3: Extracting Q&A pairs (this takes time)...
Processed 10/104 chunks, found 28 pairs so far...
Total Q&A pairs extracted: 87
Step 4: Storing in vector database...
Stored 87 Q&A pairs. Total: 87
Done! Run: streamlit run app.py

> This step may take 10–30 minutes depending on chat size.

### 6. Launch WhatsBot

```bash
python -m streamlit run app.py
```

Open your browser at: **http://localhost:8501**

---

## Usage

- Type any question in the chat input and press Enter
- Use the **Quick Question buttons** for one-click answers
- The sidebar shows live stats: FAQ entries, message count, engine status
- Click **Clear Chat** to reset the conversation

---

## Privacy & Security

| Concern | How WhatsBot Handles It |
|---|---|
| Chat data | Never sent to any external server |
| API keys | Not required — zero external API calls |
| Internet | Only needed once for model download |
| Storage | All data stays on your local disk only |
| Network | All calls go to `localhost:11434` (your own machine) |

Turn off your WiFi and WhatsBot still works. Everything runs locally.

---

## Troubleshooting

| Error | Fix |
|---|---|
| `ollama not found` | Restart terminal after Ollama installation |
| `connection refused` | Open a new terminal and run `ollama serve` |
| `chat.txt not found` | Ensure the file is in the project root folder |
| `chromadb error` | Run `pip install chromadb --upgrade` |
| `streamlit not found` | Use `python -m streamlit run app.py` |
| No Q&A extracted | Your chat date format may differ — open an issue with a sample line |

---

## Roadmap

- [ ] Multi-language support (Tamil, Hindi, etc.)
- [ ] Drag-and-drop chat file upload in UI
- [ ] Support for multiple group chats
- [ ] Export knowledge base as PDF
- [ ] Docker deployment

---

## Author

**S.SRUTI**
B.Tech. Information Technology

**Kavi Nisha MP**
B.Tech. Artificial Intelligence and Data Science

Built using open-source AI tools — completely free, completely private.

---

<div align="center">

**WhatsBot** — Because no one should have to answer the same question twice.

![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)
![Made with Python](https://img.shields.io/badge/Made%20with-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![100% Offline](https://img.shields.io/badge/100%25-Offline-success?style=for-the-badge)

</div>

How to add this to GitHub:

In VS Code → New File → name it README.md
Paste everything above → Ctrl+S
Push to GitHub:

bashgit init
git add .
git commit -m "WhatsBot - Domain-Specific FAQ Chatbot using Local LLMs"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/whatsbot.git
git push -u origin main
