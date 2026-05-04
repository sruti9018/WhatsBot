import re

def parse_whatsapp_chat(filepath):
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?[APap][Mm]\s-\s(.+?):\s(.+)'
    messages = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(pattern, line)
            if match:
                sender = match.group(1).strip()
                text = match.group(2).strip()
                if text in ['<Media omitted>', 'This message was deleted', 'null']:
                    continue
                if len(text) < 5:
                    continue
                messages.append({'sender': sender, 'text': text})
    return messages

def chunk_messages(messages, window=5):
    chunks = []
    for i in range(0, len(messages), window):
        group = messages[i:i+window]
        chunk = "\n".join([f"{m['sender']}: {m['text']}" for m in group])
        chunks.append(chunk)
    return chunks