import requests
from build_vectorstore import get_collection

collection = get_collection()

def query_chatbot(user_question, top_k=3):
    results = collection.query(
        query_texts=[user_question],
        n_results=min(top_k, collection.count())
    )
    context = "\n\n".join(results['documents'][0])

    prompt = f"""You are a helpful FAQ assistant for this community group.
Answer using ONLY the context below.
If the answer is not in the context, say "I don't have information on that."

Context:
{context}

Question: {user_question}
Answer:"""

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })
    return response.json()['response'].strip()
