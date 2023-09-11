"""Codenames event bot functionalities"""

import random

from events_help import help_documentation


def start_codenames(user_chose: str, user: str, events) -> str:
    """CodeNames event function"""

    if user_chose[:4] == "//d ":
        user = user_chose[4:]
        user_chose = "//l"

    elif user_chose == "//j":
        if user in events.users_playing:
            return f"`Cannot join! {user} has already joined the CodeNames event!`"
        events.users_playing.append(user)
        return f"`{user} was successfully added to the CodeNames event!`"

    elif user_chose == "//l":
        if user in events.users_playing:
            events.users_playing.remove(user)
            return f"`{user} successfully left CodeNames event!`"
        else:
            return f"`Cannot leave! {user} did not enter the game. '//j' to join!`"

    elif user_chose == "//t":
        if len(events.users_playing) < 4:
            return "`This game is designed for minimum of 4 people. Preferably 6 or more. Add more players!`"
        team1 = events["users_playing"].copy()
        team2 = []
        for _ in range(int(len(events["users_playing"])/2)):
            team2.append(team1.pop(team1.index(random.choice(team1))))
            team_1_formatted = ", ".join(team1)
            team_2_formatted = ", ".join(team2)
        teams = f"""```Team 1: {team_1_formatted}; Captain: {random.choice(team1)}
Team 2: {team_2_formatted}; Captain: {random.choice(team2)}```"""
        return teams

    elif user_chose == "//h":
        return help_documentation("codenames")
    
    elif user_chose == "//sp":
        users_playing = ", ".join(events.users_playing)
        return f"`Currently playing are: {users_playing}`"

    elif user_chose == "//q":
        events.codenames_event = False
        events.users_playing = []
        return "`CodeNames event was ended!`"
    return ""