import requests
import json
import re
from thread_analyzer import analyze_threads, threads_to_qa_pairs


def extract_qa(chunk):
    prompt = f"""You are a knowledge extractor for a WhatsApp group chat.
Extract ALL useful information from the chat below as question-answer pairs.

Rules:
- If someone asks and someone answers — extract it
- If someone shares ANY fact, date, event, announcement, link, or info — create a Q&A from it
- If someone shares a birthday wish — extract: Q: "When is [name]'s birthday?" A: "[date]"
- If someone shares a location, timing, deadline, result, or update — extract it
- Be creative — turn ANY statement into a useful Q&A
- Include the sender name in "sender" field

Return ONLY a JSON list. No explanation. No markdown.
Format: [{{"question": "...", "answer": "...", "sender": "..."}}]
If truly nothing useful, return [].

Chat:
{chunk}"""
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        })
        text = response.json()['response'].strip()
        text = re.sub(r'```json|```', '', text).strip()
        if not text.startswith('['):
            start = text.find('[')
            end   = text.rfind(']')
            if start != -1 and end != -1:
                text = text[start:end+1]
            else:
                return []
        pairs = json.loads(text)
        if isinstance(pairs, list):
            return pairs
        return []
    except Exception:
        return []


def extract_qa_with_cti(messages):
    print("  🧵 Running CTI Thread Analysis...")

    # ── Phase 1: CTI Thread Analysis ─────────────────────
    threads  = analyze_threads(messages)
    qa_pairs = threads_to_qa_pairs(threads)

    answered   = len([t for t in threads if not t["is_unanswered"]])
    unanswered = len([t for t in threads if t["is_unanswered"]])
    corrected  = len([t for t in threads if t["has_correction"]])
    validated  = len([t for t in threads if t["validations"] > 0])

    print(f"  📊 CTI Results:")
    print(f"     Threads found    : {len(threads)}")
    print(f"     Answered         : {answered}")
    print(f"     Unanswered       : {unanswered} (logged to unanswered.txt)")
    print(f"     Corrections found: {corrected}")
    print(f"     Validated answers: {validated}")
    print(f"     Q&A pairs from CTI: {len(qa_pairs)}")

    # ── Phase 2: LLM Fallback ─────────────────────────────
    print("\n  🤖 Running LLM fallback extraction...")

    llm_pairs = []
    window    = 5
    chunks    = []
    for i in range(0, len(messages), window):
        group = messages[i:i+window]
        chunk = "\n".join([
            f"[{m.get('date','')} {m.get('time','')}] {m.get('sender','?')}: {m.get('text','')}"
            for m in group
        ])
        chunks.append(chunk)

    for idx, chunk in enumerate(chunks):
        pairs = extract_qa(chunk)
        for p in pairs:
            p["trust_score"]     = 0.3
            p["validations"]     = 0
            p["has_correction"]  = False
            p["correction_note"] = ""
            p.setdefault("sender", "A group member")
            p["original"]        = p.get("question", "")
        llm_pairs.extend(pairs)

        if (idx + 1) % 10 == 0:
            print(f"     LLM: {idx+1}/{len(chunks)} chunks done, "
                  f"{len(llm_pairs)} pairs found...")

    print(f"  🤖 LLM fallback pairs: {len(llm_pairs)}")

    all_pairs = qa_pairs + llm_pairs
    print(f"\n  ✅ Total combined Q&A pairs: {len(all_pairs)}")
    print(f"     CTI pairs (smart) : {len(qa_pairs)}")
    print(f"     LLM pairs (fallback): {len(llm_pairs)}")

    return all_pairs