"""File that executes our bots functions"""

import time
import random

import discord
import requests
import asyncio
from dotenv import dotenv_values

import responses

codename_event = False
timeout_task = 0
users_playing = []

async def send_message(message, user_message: str, user: str) -> None:
    """Sends an appropriate response to a query sent with '!' """
    try:
        response = responses.handle_response(user_message, user)
        await message.channel.send(response)
    except Exception as e:
        print(e)
        await message.channel.send("Sorry, I do not currently have a response for you.")


def run_discord_bot():
    """Function that runs the bot with provided key,
    and listens to messages."""
    config = dotenv_values('.env')
    TOKEN = config["TOKEN"]
    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        global codename_event, timeout_task
        # No response if it was a message by our bot
        if message.author == client.user:
            return

        user = str(message.author)
        msg = str(message.content).lower()
        chnl = str(message.channel)

        print(f"{user} said: '{msg}' ({chnl})")

        greetings = ["hi", "hello", "hey", "hola"]
        bot_names = ["ga", "gameassist", "bot"]

        if msg[:6] == "!play ":
            #TODO make sure timeout task is cancelled if no appropriate game was chosen
            timeout_task = asyncio.create_task(timeout(message))
            match msg[6:]:
                case "codenames":
                    if codename_event:
                        await message.channel.send("`CodeNames event is already running!`")
                    else:
                        codename_event = True
                        await message.channel.send("`CodeNames event was started!`")
        elif msg[0:2] == "//":
            if codename_event:
                response = start_codenames(message, msg,user)
                await handle_event_responses(message, response)
                await message.delete()
        elif msg == "!joke":
            await send_joke(message)
        elif any(word in msg for word in greetings) and any(word in msg for word in bot_names):
            await send_message(message, msg, user)
        elif msg[0] == "!":
            await send_message(message, msg[1:], user)
            await message.delete()
        elif "lol" in msg:
            await message.channel.send("Haha you're funny!")

    client.run(TOKEN)


async def send_joke(message) -> None:
    request = requests.get("https://official-joke-api.appspot.com/jokes/programming/random")
    joke = request.json()
    await message.delete()
    await message.channel.send(joke[0]["setup"])
    time.sleep(int(len(joke[0]["setup"])/10))
    await message.channel.send(joke[0]["punchline"])


async def handle_event_responses(message, msg: str):
    """Events when activated allow to run '/' commands.
    Some might however not exist."""
    try:
        await message.channel.send(msg)
    except Exception as e:
        print(e)
        await message.channel.send("This is not an allowed command for this event. Try '/h' for help!")


async def timeout(message):
    await asyncio.sleep(20)
    response =  start_codenames(message, "//q", "timer")
    print("finished")
    await message.channel.send(response)


#starts an event which allows to add yourself to it and it'll print out the teams.
def start_codenames(message, user_chose: str, user: str) -> str:
    global codename_event, users_playing, timeout_task
    timeout_task.cancel()
    timeout_task = asyncio.create_task(timeout(message))
    if user_chose[:4] == "//d ":
        # allows to delete another user from the game
        user = user_chose[4:]
        user_chose = "//l"
    if user_chose == "//j":
        # adds the user to the game
        if user in users_playing:
            return f"`{user} has already joined the CodeNames event!`"
        users_playing.append(user)
        return f"`{user} was successfully added to the CodeNames event!`"
    if user_chose == "//l":
        # user leaves the game
        if user in users_playing:
            users_playing.remove(user)
            return f"`{user} successfully left CodeNames event!`"
        else:
            return f"`{user} did not enter the game. '//j' to join!`"
    if user_chose == "//s":
        # game is started
        if len(users_playing) < 4:
            return "`This game is designed for minimum of 4 people. Preferably 6 or more. Add more players!`"
        team1 = users_playing.copy()
        team2 = []
        for _ in range(int(len(users_playing)/2)):
            team2.append(team1.pop(team1.index(random.choice(team1))))
        teams = f"""``` Team 1: {team1}; Captain: {random.choice(team1)}
 Team 2: {team2}; Captain: {random.choice(team2)}```"""
        return teams
    if user_chose == "//h":
        # return help about this event
        return "-"
    if user_chose == "//q":
        # finishes the game
        codename_event = False
        users_playing = []
        return "`CodeNames event was ended!`"


async def start_among_us():

    #shuts off automatically if not used
    time.sleep(2400)
    """"""