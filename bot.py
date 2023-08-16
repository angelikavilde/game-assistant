"""File that executes the bots functions"""

import random

import discord
import requests
import asyncio
from dotenv import dotenv_values

from easter_egg import easter_egg_func
from dnd_event import start_dnd_event
from events_help import help_documentation


events = {"codename_event": False, "rock_paper_scissors_event": False,
           "amongus_event": False, "dnd_event": False, "users_playing": []}
bot_message = None


def handle_response(msg: str) -> str:
    """Function that determines what to do with the responses from user"""

    if msg == "help" or msg == "h":
        return help_documentation("bot")
    if msg[:7] == "repeat ":
        return msg[7:]

async def send_message(message, user_message: str) -> None:
    """Sends an appropriate response to a query sent with '!' """
    try:
        response = handle_response(user_message)
        await message.channel.send(response)
    except Exception as e:
        print(e)
        await message.channel.send("Sorry, I do not currently have a response for you.")


def run_discord_bot():
    """Function that runs the bot with provided key,
    and listens to messages."""
    config = dotenv_values()
    TOKEN = config["TOKEN"]
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        global events
        if message.content == "":
            # to kill errors with an empty message/image
            return
        # No response if it was a message by our bot
        if message.author == client.user:
            bot_message = message # for killing last bots message
            return
        user = str(message.author)
        msg = str(message.content).lower()
        chnl = str(message.channel)

        print(f"{user} said: '{msg}' ({chnl})")

        if msg[:6] == "!play ":
            await play_event_run(message, msg[6:])
        elif msg[0:2] == "//":
            if events["codename_event"]:
                await message.delete()
                response = start_codenames(msg, user)
                await handle_event_responses(message, response)
            elif events["rock_paper_scissors_event"]:
                response = r_p_s(msg, user)
                await handle_event_responses(message, response)
                if msg != "//q":
                    await asyncio.sleep(2)
                    response = r_p_s("play", user)
                    await handle_event_responses(message, response)
            elif events["amongus_event"]:
                await message.delete()
                await start_among_us(message, msg)
            elif events["dnd_event"]:
                response = start_dnd_event(msg, user)
                await handle_event_responses(message, response)
            else:
                await message.channel.send("""`Double slash commands only work for events.
There is no event running! !h or !help for event list.`""")
        elif msg == "!joke":
            await send_joke(message)
        elif msg == "!kill":
            await message.delete()
            await bot_message.delete()
        elif msg[0] == "!":
            await message.delete()
            await send_message(message, msg[1:])
        else:
            await easter_egg_func(message, msg)
    client.run(TOKEN)


async def send_joke(message) -> None:
    request = requests.get("https://official-joke-api.appspot.com/jokes/programming/random")
    joke = request.json()
    await message.channel.send(joke[0]["setup"])
    await asyncio.sleep(3)
    await message.channel.send(joke[0]["punchline"])


async def handle_event_responses(message, msg: str):
    """Events when activated allow to run '/' commands.
    Some might however not exist."""
    try:
        await message.channel.send(msg)
    except Exception as e:
        print(e)
        await message.channel.send("This is not an allowed command for this event. Try '//h' for help!")


def r_p_s(user_chose: str, user: str) -> str:
    """Bot plays rock-paper-scissors against a player"""
    global events
    choices = ["rock","paper","scissors"]
    bot_chose = random.choice(choices)
    user_chose = user_chose.replace(" ", "")
    if user_chose == "play":
        # adds user to the game
        events["users_playing"] = []
        events["users_playing"].append(user)
        return "`I have made my next choice!`"
    if user_chose[2:] in choices:
        # game play
        text = "`"
        user_chose = user_chose[2:]
        if user not in events["users_playing"]:
            text += "Although you were not the user that has started the game, we can still play. "
        if bot_chose == user_chose:
            return text + f"I also chose {bot_chose}. We tie!`"
        elif (user_chose,bot_chose) in [("scissors","rock"),("rock","paper"),("paper","scissors")]:
            return text + f"I chose {bot_chose}. You lose!`"
        else:
            return text + f"I chose {bot_chose}. You win!`"
    if user_chose == "//h":
        # returns help for the event
        return help_documentation("r-p-s")
    if user_chose == "//q":
        # finishes the game
        events["rock_paper_scissors_event"] = False
        return "`Rock-Paper-Scissors event was ended!`"


def start_codenames(user_chose: str, user: str) -> str:
    """CodeNames event function"""
    global events
    if user_chose[:4] == "//d ":
        # allows to delete another user from the game
        user = user_chose[4:]
        user_chose = "//l"
    if user_chose == "//j":
        # adds the user to the game
        if user in events["users_playing"]:
            return f"`Cannot join! {user} has already joined the CodeNames event!`"
        events["users_playing"].append(user)
        return f"`{user} was successfully added to the CodeNames event!`"
    if user_chose == "//l":
        # user leaves the game
        if user in events["users_playing"]:
            events["users_playing"].remove(user)
            return f"`{user} successfully left CodeNames event!`"
        else:
            return f"`Cannot leave! {user} did not enter the game. '//j' to join!`"
    if user_chose == "//t":
        # game is started
        if len(events["users_playing"]) < 4:
            return "`This game is designed for minimum of 4 people. Preferably 6 or more. Add more players!`"
        team1 = events["users_playing"].copy()
        team2 = []
        for _ in range(int(len(events["users_playing"])/2)):
            team2.append(team1.pop(team1.index(random.choice(team1))))
        teams = f"""```Team 1: {team1}; Captain: {random.choice(team1)}
Team 2: {team2}; Captain: {random.choice(team2)}```"""
        return teams
    if user_chose == "//h":
        # return help about this event
        return help_documentation("codenames")
    if user_chose == "//q":
        # finishes the game
        events["codename_event"] = False
        events["users_playing"] = []
        return "`CodeNames event was ended!`"


async def start_among_us(message, user_chose: str) -> None:
    """AmongUs event function"""
    global events
    if user_chose == "//d":
        # player has died and was given a dead role
        if not message.author in events["users_playing"]:
            events["users_playing"].append(message.author)
            await member_role_changed(message, message.author, True)
            await message.channel.send(f"`{str(message.author)} has been announced dead!`")
        else:
            await message.channel.send(f"`{str(message.author)} is already laying in the grave!`")
    if user_chose == "//n":
        # new game starts so all users' roles are reset
        for member in users_playing:
            await member_role_changed(message, member, False)
        await message.channel.send("`AmongUs event was restarted!`")
    if user_chose == "//h":
        await message.channel.send(help_documentation("amongus"))
    if user_chose == "//q":
        # finishes the game
        events["amongus_event"] = False
        events["users_playing"] = []
        await message.channel.send("`AmongUs event was ended!`")


async def member_role_changed(message, user, add: bool) -> None:
    """Gives a user a Dead Crewmate role or removes it"""
    role = discord.utils.get(message.guild.roles, name="Dead Crewmate")
    if add:
        await user.add_roles(role)
    else:
        await user.remove_roles(role)


async def play_event_run(message, msg:str) -> None:
    """Handles the event start"""
    global events
    if any(e for e in events.values()):
        await message.channel.send("`There is already an event running. //h for event info or //q to finish!`")
        return
    match msg:
        case "codenames":
            if events["codename_event"]:
                await message.channel.send("`CodeNames event is already running!`")
            else:
                events["codename_event"] = True
                await message.channel.send("`CodeNames event was started!`")
        case "rps":
            if events["rock_paper_scissors_event"]:
                await message.channel.send("`Rock-Paper-Scissors event is already running!`")
            else:
                events["rock_paper_scissors_event"] = True
                await message.channel.send("`Rock-Paper-Scissors event was started!`")
                await asyncio.sleep(2)
                response = r_p_s("play", str(message.author))
                await handle_event_responses(message, response)
        case "amongus":
            if events["amongus_event"]:
                await message.channel.send("`AmongUs event is already running!`")
            else:
                events["amongus_event"] = True
                response = discord.Embed(title="Event was started:", description="* Among Us", color=discord.Colour(value=0x8f3ea3))
                response.set_image(url="https://media.discordapp.net/attachments/1115715187052392521/1121920595530108928/image.png?width=1038&height=372")
                await message.channel.send(embed=response)
        case "dnd":
            if events["amongus_event"]:
                await message.channel.send("`Dungeons&Dragons event is already running!`")
            else:
                events["dnd_event"] = True
                await message.channel.send("`Dungeons&Dragons event was started!`")