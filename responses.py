
def handle_response(msg: str) -> str:
    """Function that determines what to do with the responses from user"""

    if msg == "help" or msg == "h":
        return """ **I am in the testing mode so I do not currently run all of the below**
These are _some_ of the commands I respond to:
* !repeat - repeats a message after you and deletes your sent message
* !joke - sends programmer joke
* !play x - runs an event x. List of available events: rps, codenames, amongus.
**each event when activated has its own commands //h for help about the event**
* !kill - deletes last bots message and the command will be deleted off the screen too (!kill)"""
    if msg[:7] == "repeat ":
        return msg[7:]
