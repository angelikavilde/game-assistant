import random

from events_help import help_documentation

def r_p_s(user_chose: str, user: str, events: dict) -> tuple[str,dict]:
    """Bot plays rock-paper-scissors against a player"""
    choices = ["rock","paper","scissors"]
    bot_chose = random.choice(choices)
    user_chose = user_chose.replace(" ", "")
    if user_chose == "play":
        # adds user to the game
        events["users_playing"] = []
        events["users_playing"].append(user)
        return "`I have made my next choice!`", events
    if user_chose[2:] in choices:
        # game play
        text = "`"
        user_chose = user_chose[2:]
        if user not in events["users_playing"]:
            text += "Although you were not the user that has started the game, we can still play. "
        if bot_chose == user_chose:
            return text + f"I also chose {bot_chose}. We tie!`", events
        elif (user_chose,bot_chose) in [("scissors","rock"),("rock","paper"),("paper","scissors")]:
            return text + f"I chose {bot_chose}. You lose!`", events
        else:
            return text + f"I chose {bot_chose}. You win!`", events
    if user_chose == "//h":
        # returns help for the event
        return help_documentation("r-p-s"), events
    if user_chose == "//q":
        # finishes the game
        events["rock_paper_scissors_event"] = False
        events["users_playing"] = []
        return "`Rock-Paper-Scissors event was ended!`", events
    return "", events