
def handle_response(msg: str) -> str:
    """Function that determines what to do with the responses from user"""

    if msg == "help":
        return "`I help!`"
    if msg[:7] == "repeat ":
        return msg[7:]

