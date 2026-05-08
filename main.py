import os
import json
import sys
from parse_chat import parse_whatsapp_chat, chunk_messages
from extract_qa import extract_qa_with_cti
from build_vectorstore import get_collection, store_qa_pairs
from build_graph import build_graph

CHECKPOINT_FILE = "last_processed.json"

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f)
    return {"last_message_count": 0}

def save_checkpoint(count):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"last_message_count": count}, f)

def run_pipeline(chat_file="chat.txt", force_rebuild=False):
    print("\n" + "="*50)
    print("  🤖 WhatsBot CMG Pipeline Starting...")
    print("="*50 + "\n")

    # ── Step 1: Parse ─────────────────────────────────────
    print("Step 1: Parsing chat...")
    messages = parse_whatsapp_chat(chat_file)
    total    = len(messages)
    print(f"  Found {total} messages")

    # ── Step 2: Checkpoint check ──────────────────────────
    checkpoint = load_checkpoint()
    last_count = checkpoint["last_message_count"]

    if force_rebuild:
        new_messages = messages
        print(f"  Force rebuild — processing all {total} messages")
    elif total <= last_count:
        print(f"  No new messages since last run ({last_count} processed).")

        # Still rebuild graph from full history
        print("\nStep 2: Rebuilding CMG from full history...")
        all_chunks = chunk_messages(messages, window=5)
        all_qa_full = []
        for chunk in all_chunks:
            pairs = extract_qa_with_cti(
                [{"text": line.split(": ", 1)[-1],
                  "sender": line.split(": ", 1)[0].strip("[]").split("] ")[-1]
                           if "]" in line else "Unknown",
                  "date": "", "time": ""}
                 for line in chunk.split("\n") if ": " in line]
            )
            all_qa_full.extend(pairs)

        if all_qa_full:
            person_graph, topic_graph, contradictions = build_graph(all_qa_full)
            print(f"  CMG ready: {len(person_graph)} people · "
                  f"{len(topic_graph)} topics · "
                  f"{len(contradictions)} contradictions ✅")

        print("\n  Knowledge base is already up to date. ✅")
        return
    else:
        new_messages = messages[last_count:]
        print(f"  {len(new_messages)} new messages found")

    # ── Step 3: CTI + LLM Extraction ─────────────────────
    print("\nStep 2: Running CTI + LLM Extraction...")
    all_qa = extract_qa_with_cti(new_messages)

    if not all_qa:
        print("  No Q&A pairs found.")
        save_checkpoint(total)
        return

    # ── Step 4: Store in vector DB ────────────────────────
    print("\nStep 3: Storing in vector database...")

    if force_rebuild:
        import chromadb
        client = chromadb.PersistentClient(path="./faq_db")
        try:
            client.delete_collection("faqs")
            print("  Cleared old database for full rebuild.")
        except:
            pass

    collection = get_collection()
    store_qa_pairs(all_qa, collection)

    # ── Step 5: Build CMG from ALL messages ───────────────
    print("\nStep 4: Building Conversational Memory Graph (CMG)...")
    print("  Analyzing authority · topics · contradictions...")

    # Build graph using all messages not just new ones
    all_chunks = chunk_messages(messages, window=5)
    all_qa_full = []
    for i, chunk in enumerate(all_chunks):
        pairs = extract_qa_with_cti(
            [{"text": line.split(": ", 1)[-1] if ": " in line else line,
              "sender": line.split(": ", 1)[0].strip("[]").split("] ")[-1]
                       if "]" in line and ": " in line else "Unknown",
              "date": "", "time": ""}
             for line in chunk.split("\n") if line.strip()]
        )
        all_qa_full.extend(pairs)
        if i % 20 == 0:
            print(f"  Graph progress: {i}/{len(all_chunks)} chunks...")

    if all_qa_full:
        person_graph, topic_graph, contradictions = build_graph(all_qa_full)
        print(f"\n  ✅ CMG Complete:")
        print(f"     People tracked:    {len(person_graph)}")
        print(f"     Topics mapped:     {len(topic_graph)}")
        print(f"     Contradictions:    {len(contradictions)}")
    else:
        print("  No data available for CMG.")

    # ── Step 6: Save checkpoint ───────────────────────────
    save_checkpoint(total)
    print(f"\n✅ Done! Checkpoint saved at message #{total}")
    print(f"   Total FAQ entries in DB: {collection.count()}")
    print(f"\n  Run: python -m streamlit run app.py\n")

if __name__ == "__main__":
    force = "--rebuild" in sys.argv
    run_pipeline(force_rebuild=force)