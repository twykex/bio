sessions = {}

def get_session(token):
    # Basic memory management
    if len(sessions) > 100 and token not in sessions:
        # Remove oldest (insertion order preserved in Python 3.7+)
        try:
            sessions.pop(next(iter(sessions)), None)
        except (RuntimeError, StopIteration):
            pass

    if token not in sessions:
        sessions[token] = {
            "blood_context": {},
            "weekly_plan": [],
            "workout_plan": [],
            "chat_history": []
        }
    return sessions[token]
