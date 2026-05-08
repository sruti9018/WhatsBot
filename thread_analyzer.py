import re
import os
from datetime import datetime

# ── VALIDATION SIGNALS ────────────────────────────────────
VALIDATION_WORDS = [
    "yes", "correct", "confirmed", "confirm", "right",
    "true", "exactly", "absolutely", "agreed", "thanks",
    "thank you", "ok", "okay", "noted", "sure", "perfect",
    "great", "good", "understood", "got it", "👍", "✅", "🙏"
]

# ── CORRECTION SIGNALS ────────────────────────────────────
CORRECTION_WORDS = [
    "no ", "not ", "wrong", "incorrect", "actually",
    "correction", "updated", "changed", "postponed",
    "rescheduled", "extended", "revised", "new date",
    "new deadline", "please note", "update:"
]

# ── QUESTION SIGNALS ─────────────────────────────────────
QUESTION_WORDS = [
    "what", "when", "where", "who", "how", "why",
    "which", "is it", "are there", "can i", "can we",
    "do we", "does", "will", "should", "?"
]


def parse_timestamp(text):
    patterns = [
        r'(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}\s*[APap][Mm])',
        r'(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                date_str = match.group(0)
                for fmt in ["%d/%m/%Y, %I:%M %p", "%d/%m/%y, %I:%M %p",
                            "%m/%d/%Y, %I:%M %p", "%m/%d/%y, %I:%M %p",
                            "%d/%m/%Y, %H:%M", "%d/%m/%y, %H:%M"]:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except:
                        continue
            except:
                pass
    return None


def is_url(text):
    """Returns True if the text is a URL."""
    stripped = text.strip()
    return (stripped.startswith("http://") or
            stripped.startswith("https://") or
            stripped.startswith("www."))


def is_validation(text):
    text_lower = text.lower().strip()
    if len(text_lower) < 40:
        for word in VALIDATION_WORDS:
            if word in text_lower:
                return True
    return False


def is_correction(text):
    text_lower = text.lower().strip()
    for word in CORRECTION_WORDS:
        if text_lower.startswith(word) or f" {word}" in text_lower:
            return True
    return False


def is_question(text):
    """Returns True if this message is asking a question."""
    if not text or not text.strip():
        return False

    # Skip URLs — they are not questions
    if is_url(text):
        return False

    text_lower = text.lower().strip()
    if "?" in text_lower:
        return True
    for word in QUESTION_WORDS:
        if text_lower.startswith(word):
            return True
    return False


def analyze_threads(messages):
    threads = []
    i       = 0
    total   = len(messages)

    while i < total:
        msg  = messages[i]
        text = msg.get("text", "").strip()

        if is_question(text) and len(text) > 8:
            thread = {
                "question":        text,
                "question_sender": msg.get("sender", "Unknown"),
                "timestamp":       msg.get("timestamp", ""),
                "answers":         [],
                "validations":     0,
                "has_correction":  False,
                "correction_text": "",
                "is_unanswered":   True,
                "trust_score":     0.0
            }

            j = i + 1
            answer_count = 0
            while j < total and j < i + 10:
                next_msg  = messages[j]
                next_text = next_msg.get("text", "").strip()

                if next_msg.get("sender") == msg.get("sender"):
                    j += 1
                    continue

                if is_question(next_text) and answer_count == 0:
                    break

                if is_validation(next_text):
                    thread["validations"]  += 1
                    thread["is_unanswered"] = False

                elif is_correction(next_text) and answer_count > 0:
                    thread["has_correction"]  = True
                    thread["correction_text"] = next_text
                    thread["answers"].append({
                        "text":      next_text,
                        "sender":    next_msg.get("sender", "Unknown"),
                        "timestamp": next_msg.get("timestamp", ""),
                        "is_latest": True
                    })
                    thread["is_unanswered"] = False
                    answer_count += 1

                elif (not is_question(next_text)
                      and not is_url(next_text)
                      and len(next_text) > 5
                      and answer_count < 3):
                    thread["answers"].append({
                        "text":      next_text,
                        "sender":    next_msg.get("sender", "Unknown"),
                        "timestamp": next_msg.get("timestamp", ""),
                        "is_latest": False
                    })
                    thread["is_unanswered"] = False
                    answer_count += 1

                j += 1

            base_score = min(answer_count * 0.2, 0.6)
            val_score  = min(thread["validations"] * 0.15, 0.3)
            corr_score = 0.1 if thread["has_correction"] else 0.0
            thread["trust_score"] = round(base_score + val_score + corr_score, 2)

            if thread["answers"]:
                thread["answers"][-1]["is_latest"] = True

            threads.append(thread)

        i += 1

    return threads


def threads_to_qa_pairs(threads):
    qa_pairs = []

    # Load existing unanswered entries once to avoid duplicates
    existing_unanswered = set()
    if os.path.exists("unanswered.txt"):
        with open("unanswered.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    # Extract just the question part after [UNANSWERED]
                    clean = line.replace("[UNANSWERED]", "").strip()
                    existing_unanswered.add(clean)

    for thread in threads:
        question = thread["question"]
        answers  = thread["answers"]

        # Skip URLs that slipped through
        if is_url(question):
            continue

        if not answers:
            if thread["is_unanswered"] and question.strip() not in existing_unanswered:
                with open("unanswered.txt", "a", encoding="utf-8") as f:
                    f.write(f"[UNANSWERED] {question}\n")
                existing_unanswered.add(question.strip())
            continue

        if thread["has_correction"]:
            best_answer = thread["correction_text"]
        else:
            best_answer = answers[-1]["text"]

        best_sender = answers[-1].get("sender", "A group member")

        correction_note = ""
        if thread["has_correction"] and len(answers) > 1:
            old_answer      = answers[0]["text"][:80]
            correction_note = f"Earlier answer was: '{old_answer}' — this was corrected."

        qa_pairs.append({
            "question":        question,
            "answer":          best_answer,
            "sender":          best_sender,
            "original":        question,
            "trust_score":     thread["trust_score"],
            "validations":     thread["validations"],
            "has_correction":  thread["has_correction"],
            "correction_note": correction_note,
            "is_unanswered":   False
        })

    return qa_pairs


def get_unanswered_threads(threads):
    return [t for t in threads if t["is_unanswered"]]