sessions = {}

def get_session(token):
    if len(sessions) > 100 and token not in sessions:
        try:
            sessions.pop(next(iter(sessions)), None)
        except (RuntimeError, StopIteration):
            pass

    if token not in sessions:
        sessions[token] = {
            "blood_context": {},
            "raw_text_chunks": [],
            "embeddings": [],
            "chat_history": []
        }
    return sessions[token]
