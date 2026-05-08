from parse_chat import parse_whatsapp_chat, chunk_messages
from extract_qa import extract_qa
from build_vectorstore import get_collection, store_qa_pairs

print("Step 1: Parsing chat...")
messages = parse_whatsapp_chat("chat.txt")
print(f"  Found {len(messages)} messages")

print("Step 2: Chunking messages...")
chunks = chunk_messages(messages, window=5)
print(f"  Created {len(chunks)} chunks")

print("Step 3: Extracting Q&A pairs (this takes time)...")
collection = get_collection()
all_qa = []
for i, chunk in enumerate(chunks):
    pairs = extract_qa(chunk)
    if pairs:
        all_qa.extend(pairs)
    if i % 10 == 0:
        print(f"  Processed {i}/{len(chunks)} chunks, found {len(all_qa)} pairs so far...")

print(f"\nTotal Q&A pairs extracted: {len(all_qa)}")

print("Step 4: Storing in vector database...")
store_qa_pairs(all_qa, collection)

print("\nDone! Run: streamlit run app.py")
