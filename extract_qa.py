import requests, json

def extract_qa(chunk):
    prompt = f"""You are a smart knowledge extractor for a WhatsApp group chat.
Extract EVERY useful fact, event, date, announcement, birthday, deadline, or Q&A from the chat below.

STRICT RULES:
- For EVERY birthday wish like "Happy Birthday [Name]!" — create a Q&A:
  question: "When is [Name]'s birthday?"
  answer: "On [the date shown in brackets at the start of that message line]"
- Do this for EVERY person mentioned — not just one
- For deadlines, exam dates, events — create Q&A from them
- For every announcement — turn into a Q&A
- For real questions and answers — extract them
- ALWAYS extract the date from the [DD/MM/YYYY] timestamp shown in each message line
- Include sender name in "sender" field
- Return ONLY a valid JSON list. No extra text, no explanation.

Format:
[{{"question": "...", "answer": "...", "sender": "..."}}]

If nothing useful, return [].

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
        pairs = json.loads(text[start:end])
        for p in pairs:
            p['original'] = chunk
        return pairs
    except:
        return []
