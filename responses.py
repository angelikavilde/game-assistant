
def handle_response(msg: str, user: str) -> str:
    """Function that determines what to do with the responses from user"""
    if any(word in msg for word in ["hi","hello","hey","hola"]):
        return f"""```json
            "Hi {user} <3"
            ```"""
    if msg == "help":
        return "`I help!`"
