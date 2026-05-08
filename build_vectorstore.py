import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
import re
import requests
import math


def clean_text(text, max_chars=400):
    """
    Stronger cleaner for BGE-M3 compatibility.
    Handles WhatsApp special characters, emojis, mixed scripts.
    """
    if not text:
        return ""
    text = re.sub(r'[^\w\s\u0900-\u097F\u0B80-\u0BFF\u0600-\u06FF\u0C00-\u0C7F.,!?:;()\-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_chars]


def safe_embed_test(text, model="bge-m3"):
    """
    Pre-tests if text can be embedded without NaN.
    Returns True if safe, False if it would crash.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": model, "prompt": text},
            timeout=30
        )
        data      = response.json()
        embedding = data.get("embedding", [])
        if not embedding:
            return False
        for val in embedding:
            if math.isnan(val) or math.isinf(val):
                return False
        return True
    except Exception:
        return False


def get_collection():
    """
    Upgrade A — BGE-M3 Embeddings (K. Anjali et al., 2025)
    100+ languages, dense + sparse + multi-vector retrieval.
    """
    embedding_fn = OllamaEmbeddingFunction(
        url="http://localhost:11434/api/embeddings",
        model_name="bge-m3"
    )
    client = chromadb.PersistentClient(path="./faq_db")
    collection = client.get_or_create_collection(
        name="faqs",
        embedding_function=embedding_fn,
        metadata={"embedding_model": "bge-m3"}
    )
    return collection


def is_duplicate(question, collection, threshold=0.1):
    """
    Novelty 4 — Smart FAQ Deduplication.
    BGE-M3 produces more accurate distances so
    deduplication is now more reliable.
    """
    if collection.count() == 0:
        return False
    try:
        results = collection.query(
            query_texts=[clean_text(question)],
            n_results=1,
            include=["distances"]
        )
        distance = results['distances'][0][0]
        return distance < threshold
    except Exception:
        return False


def store_qa_pairs(qa_pairs, collection):
    existing  = collection.count()
    stored    = 0
    skipped   = 0
    nan_skip  = 0
    new_index = existing

    # CTI statistics
    cti_stored      = 0
    corrections_stored = 0
    validated_stored   = 0

    for qa in qa_pairs:
        question = clean_text(str(qa.get("question", "")).strip())
        answer   = clean_text(str(qa.get("answer",   "")).strip())
        sender   = clean_text(str(qa.get("sender",   "A group member")), max_chars=100)
        original = clean_text(str(qa.get("original", "")), max_chars=200)

        # CTI metadata fields
        trust_score     = float(qa.get("trust_score",     0.3))
        validations     = int(qa.get("validations",       0))
        has_correction  = bool(qa.get("has_correction",   False))
        correction_note = clean_text(str(qa.get("correction_note", "")), max_chars=300)

        # Skip empty or too short
        if len(question) < 5 or len(answer) < 5:
            skipped += 1
            continue

        # Novelty 4: Skip duplicates
        if is_duplicate(question, collection):
            skipped += 1
            continue

        doc = f"Q: {question}\nA: {answer}"

        # Pre-test embedding safety
        if not safe_embed_test(doc):
            nan_skip += 1
            continue

        try:
            collection.add(
                documents=[doc],
                ids=[f"qa_{new_index}"],
                metadatas=[{
                    # Standard fields
                    "question":        question[:500],
                    "answer":          answer[:500],
                    "sender":          sender,
                    "original":        original,
                    # CTI fields — NEW
                    "trust_score":     str(round(trust_score, 2)),
                    "validations":     str(validations),
                    "has_correction":  str(has_correction),
                    "correction_note": correction_note
                }]
            )
            stored    += 1
            new_index += 1

            # Track CTI stats
            if trust_score > 0.3:
                cti_stored += 1
            if has_correction:
                corrections_stored += 1
            if validations > 0:
                validated_stored += 1

        except Exception:
            nan_skip += 1
            continue

    # ── Summary ───────────────────────────────────────────
    print(f"\n{'='*50}")
    print(f"  Stored       : {stored} new Q&A pairs")
    print(f"  Skipped      : {skipped} duplicates or empty")
    print(f"  Filtered     : {nan_skip} NaN embedding errors")
    print(f"  Total in DB  : {collection.count()}")
    print(f"{'─'*50}")
    print(f"  CTI Smart pairs    : {cti_stored}")
    print(f"  Corrections stored : {corrections_stored}")
    print(f"  Validated answers  : {validated_stored}")
    print(f"  Embedding model    : bge-m3 (100+ languages)")
    print(f"{'='*50}")