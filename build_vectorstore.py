import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction


def get_collection():
    embedding_fn = OllamaEmbeddingFunction(
        url="http://localhost:11434/api/embeddings",
        model_name="nomic-embed-text"
    )
    client = chromadb.PersistentClient(path="./faq_db")
    collection = client.get_or_create_collection(
        name="faqs",
        embedding_function=embedding_fn
    )
    return collection


def is_duplicate(question, collection, threshold=0.1):
    """
    Checks if a very similar question already exists in ChromaDB.
    Lower distance = more similar.
    threshold=0.1 means 90%+ similarity = duplicate.
    Returns True if duplicate found, False if it is new.
    """
    if collection.count() == 0:
        return False
    try:
        results = collection.query(
            query_texts=[question],
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
    new_index = existing

    for qa in qa_pairs:
        question = str(qa.get("question", "")).strip()
        answer   = str(qa.get("answer",   "")).strip()

        if not question or not answer:
            skipped += 1
            continue

        # Novelty 4: Skip if very similar Q&A already exists
        if is_duplicate(question, collection):
            skipped += 1
            continue

        doc = f"Q: {question}\nA: {answer}"
        collection.add(
            documents=[doc],
            ids=[f"qa_{new_index}"],
            metadatas=[{
                "question": question[:500],
                "answer":   answer[:500],
                "sender":   str(qa.get("sender",   "A group member"))[:100],
                "original": str(qa.get("original", ""))[:300]
            }]
        )
        stored    += 1
        new_index += 1

    print(f"Stored : {stored} new Q&A pairs")
    print(f"Skipped: {skipped} duplicates or empty pairs")
    print(f"Total in DB: {collection.count()}")
