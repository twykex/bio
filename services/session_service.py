import threading

sessions = {}
session_lock = threading.Lock()

def get_session(token):
    if not token:
        raise ValueError("Token is required")

    with session_lock:
        if len(sessions) > 100 and token not in sessions:
            try:
                # Python 3.7+ dicts preserve insertion order.
                # next(iter(sessions)) gets the oldest inserted key (simple LRU approximation).
                first_key = next(iter(sessions))
                sessions.pop(first_key, None)
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
