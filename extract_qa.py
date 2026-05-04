import requests, json

def extract_qa(chunk):
    prompt = f"""From the chat below, extract question-answer pairs.
Return ONLY as JSON list: [{{"question": "...", "answer": "..."}}]
If none found, return [].

Chat:
{chunk}"""
    
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })
    try:
        text = response.json()['response']
        start = text.find('[')
        end = text.rfind(']') + 1
        return json.loads(text[start:end])
    except:
        return []