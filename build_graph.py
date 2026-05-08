import json
import os
import re
from datetime import datetime
from collections import defaultdict

GRAPH_FILE       = "person_graph.json"
TOPIC_GRAPH_FILE = "topic_graph.json"
CONTRA_FILE      = "contradiction_log.json"

TOPIC_KEYWORDS = {
    "exam":       ["exam", "test", "internal", "assessment", "quiz"],
    "deadline":   ["deadline", "last date", "due date", "submission", "submit"],
    "fee":        ["fee", "payment", "amount", "pay", "challan"],
    "hall ticket":["hall ticket", "hallticket", "admit card"],
    "attendance": ["attendance", "absent", "present", "percentage"],
    "syllabus":   ["syllabus", "portion", "unit", "chapter", "topic"],
    "result":     ["result", "marks", "score", "grade", "pass", "fail"],
    "holiday":    ["holiday", "leave", "vacation", "off"],
    "assignment": ["assignment", "project", "task", "work"],
    "schedule":   ["schedule", "timetable", "timing", "time table"],
}

def detect_topic(text):
    text_lower = (text or "").lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return topic
    return "general"

def extract_dates_from_text(text):
    text = text or ""
    patterns = [
        r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
        r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2}\b',
        r'\b\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\b',
    ]
    found = []
    for p in patterns:
        matches = re.findall(p, text.lower())
        found.extend(matches)
    return found

def build_graph(qa_pairs_with_meta):
    person_graph   = {}
    topic_graph    = {}
    contradictions = {}

    for qa in qa_pairs_with_meta:
        sender   = qa.get("sender",   "Unknown") or "Unknown"
        question = qa.get("question", "")         or ""
        answer   = qa.get("answer",   "")         or ""
        date_str = qa.get("date",     "")         or ""

        # Skip completely empty pairs
        if not question.strip() and not answer.strip():
            continue

        topic = detect_topic(question + " " + answer)

        # ── Person graph ──────────────────────────────────
        if sender not in person_graph:
            person_graph[sender] = {
                "answers_given":        0,
                "validations_received": 0,
                "authority_score":      0.3,
                "topics_covered":       [],
                "detected_role":        "Member",
                "first_seen":           date_str,
                "last_active":          date_str
            }

        person_graph[sender]["answers_given"] += 1
        person_graph[sender]["last_active"]    = date_str

        if topic not in person_graph[sender]["topics_covered"]:
            person_graph[sender]["topics_covered"].append(topic)

        ans_count = person_graph[sender]["answers_given"]
        if ans_count >= 15:
            person_graph[sender]["authority_score"] = 0.95
            person_graph[sender]["detected_role"]   = "Admin"
        elif ans_count >= 8:
            person_graph[sender]["authority_score"] = 0.75
            person_graph[sender]["detected_role"]   = "Representative"
        elif ans_count >= 3:
            person_graph[sender]["authority_score"] = 0.55
            person_graph[sender]["detected_role"]   = "Active Member"
        else:
            person_graph[sender]["authority_score"] = 0.3
            person_graph[sender]["detected_role"]   = "Member"

        # ── Topic graph ───────────────────────────────────
        if topic not in topic_graph:
            topic_graph[topic] = {
                "ask_count":         0,
                "answer_history":    [],
                "related_topics":    [],
                "has_contradiction": False,
                "urgency_score":     0.0,
                "last_answered":     date_str,
                "best_answer":       "",
                "best_sender":       "",
                "best_score":        0.0
            }

        topic_graph[topic]["ask_count"]    += 1
        topic_graph[topic]["last_answered"] = date_str

        history_entry = {
            "date":   date_str,
            "answer": answer[:200],
            "sender": sender,
            "score":  person_graph[sender]["authority_score"]
        }
        topic_graph[topic]["answer_history"].append(history_entry)

        if person_graph[sender]["authority_score"] >= topic_graph[topic]["best_score"]:
            topic_graph[topic]["best_answer"] = answer
            topic_graph[topic]["best_sender"] = sender
            topic_graph[topic]["best_score"]  = person_graph[sender]["authority_score"]

        topic_graph[topic]["urgency_score"] = min(10.0, topic_graph[topic]["ask_count"] * 0.5)

        # ── Contradiction detection ───────────────────────
        history = topic_graph[topic]["answer_history"]
        if len(history) >= 2:
            dates_in_answers = []
            for h in history:
                found = extract_dates_from_text(h.get("answer", ""))
                if found:
                    dates_in_answers.append({
                        "date":   h.get("date", ""),
                        "found":  found,
                        "answer": h.get("answer", ""),
                        "sender": h.get("sender", "")
                    })

            if len(dates_in_answers) >= 2:
                first = dates_in_answers[0]
                last  = dates_in_answers[-1]
                if first["found"] != last["found"]:
                    topic_graph[topic]["has_contradiction"] = True
                    contradictions[topic] = {
                        "original_answer": first["answer"],
                        "original_date":   first["date"],
                        "original_sender": first["sender"],
                        "updated_answer":  last["answer"],
                        "updated_date":    last["date"],
                        "updated_sender":  last["sender"],
                        "conflict":        True
                    }

    # ── Related topics ────────────────────────────────────
    topic_list = list(topic_graph.keys())
    for i, t1 in enumerate(topic_list):
        for t2 in topic_list[i+1:]:
            h1 = set(e["sender"] for e in topic_graph[t1]["answer_history"])
            h2 = set(e["sender"] for e in topic_graph[t2]["answer_history"])
            if h1 & h2:
                if t2 not in topic_graph[t1]["related_topics"]:
                    topic_graph[t1]["related_topics"].append(t2)
                if t1 not in topic_graph[t2]["related_topics"]:
                    topic_graph[t2]["related_topics"].append(t1)

    # ── Save ──────────────────────────────────────────────
    with open(GRAPH_FILE, "w", encoding="utf-8") as f:
        json.dump(person_graph, f, indent=2, ensure_ascii=False)

    with open(TOPIC_GRAPH_FILE, "w", encoding="utf-8") as f:
        json.dump(topic_graph, f, indent=2, ensure_ascii=False)

    with open(CONTRA_FILE, "w", encoding="utf-8") as f:
        json.dump(contradictions, f, indent=2, ensure_ascii=False)

    print(f"CMG built: {len(person_graph)} people · "
          f"{len(topic_graph)} topics · "
          f"{len(contradictions)} contradictions")

    return person_graph, topic_graph, contradictions

def load_graphs():
    pg = {}
    tg = {}
    cg = {}
    if os.path.exists(GRAPH_FILE):
        with open(GRAPH_FILE, "r", encoding="utf-8") as f:
            pg = json.load(f)
    if os.path.exists(TOPIC_GRAPH_FILE):
        with open(TOPIC_GRAPH_FILE, "r", encoding="utf-8") as f:
            tg = json.load(f)
    if os.path.exists(CONTRA_FILE):
        with open(CONTRA_FILE, "r", encoding="utf-8") as f:
            cg = json.load(f)
    return pg, tg, cg

def get_top_authorities(person_graph, top_n=5):
    return sorted(
        person_graph.items(),
        key=lambda x: x[1]["authority_score"],
        reverse=True
    )[:top_n]

def get_trending_topics(topic_graph, top_n=5):
    return sorted(
        topic_graph.items(),
        key=lambda x: x[1]["ask_count"],
        reverse=True
    )[:top_n]

def get_contradictions(contradiction_log):
    return [
        {"topic": t, **v}
        for t, v in contradiction_log.items()
        if v.get("conflict")
    ]

def get_related_topics(topic_graph, topic_name):
    if topic_name in topic_graph:
        return topic_graph[topic_name].get("related_topics", [])
    return []

def get_answer_history(topic_graph, topic_name):
    if topic_name in topic_graph:
        return topic_graph[topic_name].get("answer_history", [])
    return []