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

def store_qa_pairs(qa_pairs, collection):
    existing = collection.count()
    for i, qa in enumerate(qa_pairs):
        doc = f"Q: {qa['question']}\nA: {qa['answer']}"
        collection.add(
            documents=[doc],
            ids=[f"qa_{existing + i}"]
        )
    print(f"Stored {len(qa_pairs)} Q&A pairs. Total: {collection.count()}")