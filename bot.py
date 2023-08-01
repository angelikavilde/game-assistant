"""File that executes our bots functions"""

import random

import discord
import requests
import asyncio
from dotenv import dotenv_values

import responses
import easter_egg

codename_event, rock_paper_scissors_event, amongus_event = False, False, False
users_playing = []
bot_message = None

async def send_message(message, user_message: str) -> None:
    """Sends an appropriate response to a query sent with '!' """
    try:
        response = responses.handle_response(user_message)
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
        global codename_event, rock_paper_scissors_event, bot_message
        global amongus_event
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
            if codename_event:
                await message.delete()
                response = start_codenames(msg, user)
                await handle_event_responses(message, response)
            elif rock_paper_scissors_event:
                response = r_p_s(msg, user)
                await handle_event_responses(message, response)
                if msg != "//q":
                    await asyncio.sleep(2)
                    response = r_p_s("play", user)
                    await handle_event_responses(message, response)
            elif amongus_event:
                await message.delete()
                await start_among_us(message, msg)
            else:
                await message.channel.send("""`Double slash commands only work for events.
             There is no event running! !h or !help for event list.`""")
        elif msg == "!joke":
            await send_joke(message)
        elif msg == "!kill":
            await bot_message.delete()
            await message.delete()
        elif msg[0] == "!":
            await send_message(message, msg[1:])
            await message.delete()
        else:
            await easter_egg(message, msg)
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
    global rock_paper_scissors_event, users_playing
    choices = ["rock","paper","scissors"]
    bot_chose = random.choice(choices)
    user_chose = user_chose.replace(" ", "")
    if user_chose == "play":
        # adds user to the game
        users_playing = []
        users_playing.append(user)
        return "`I have made my next choice!`"
    if user_chose[2:] in choices:
        # game play
        text = "`"
        user_chose = user_chose[2:]
        if user not in users_playing:
            text += "Although you were not the user that has started the game, we can still play. "
        if bot_chose == user_chose:
            return text + f"I also chose {bot_chose}. We tie!`"
        elif (user_chose,bot_chose) in [("scissors","rock"),("rock","paper"),("paper","scissors")]:
            return text + f"I chose {bot_chose}. You lose!`"
        else:
            return text + f"I chose {bot_chose}. You win!`"
    if user_chose == "//h":
        # returns help for the event
        return """
        Bot makes a choice before player. Run:
        * //paper - to choose paper
        * //rock - to choose rock
        * //scissors - to choose scissors
        * //q to finish the game
        * Spaces do not count and it is _not_ case sensitive."""
    if user_chose == "//q":
        # finishes the game
        rock_paper_scissors_event = False
        return "`Rock-Paper-Scissors event was ended!`"


def start_codenames(user_chose: str, user: str) -> str:
    """CodeNames event function"""
    global codename_event, users_playing
    if user_chose[:4] == "//d ":
        # allows to delete another user from the game
        user = user_chose[4:]
        user_chose = "//l"
    if user_chose == "//j":
        # adds the user to the game
        if user in users_playing:
            return f"`Cannot join! {user} has already joined the CodeNames event!`"
        users_playing.append(user)
        return f"`{user} was successfully added to the CodeNames event!`"
    if user_chose == "//l":
        # user leaves the game
        if user in users_playing:
            users_playing.remove(user)
            return f"`{user} successfully left CodeNames event!`"
        else:
            return f"`Cannot leave! {user} did not enter the game. '//j' to join!`"
    if user_chose == "//t":
        # game is started
        if len(users_playing) < 4:
            return "`This game is designed for minimum of 4 people. Preferably 6 or more. Add more players!`"
        team1 = users_playing.copy()
        team2 = []
        for _ in range(int(len(users_playing)/2)):
            team2.append(team1.pop(team1.index(random.choice(team1))))
        teams = f"""```Team 1: {team1}; Captain: {random.choice(team1)}
Team 2: {team2}; Captain: {random.choice(team2)}```"""
        return teams
    if user_chose == "//h":
        # return help about this event
        return """__Run:__
* //j - To join the event (will tell you if already joined)
* //l - To leave the event (this and below will tell you if not joined)
* //d x - To delete a player x from the game
* //t - To make teams
* //q - To finish the event"""
    if user_chose == "//q":
        # finishes the game
        codename_event = False
        users_playing = []
        return "`CodeNames event was ended!`"


async def start_among_us(message, user_chose: str) -> None:
    """AmongUs event function"""
    global users_playing, amongus_event
    if user_chose == "//d":
        # player has died and was given a dead role
        users_playing.append(message.author)
        await member_role_changed(message, message.author, True)
        await message.channel.send(f"`{str(message.author)} has been announced dead!`")
    if user_chose == "//n":
        # new game starts so all users' roles are reset
        for member in users_playing:
            await member_role_changed(message, member, False)
        await message.channel.send("`AmongUs event was restarted!`")
    if user_chose == "//h":
        await message.channel.send("-")
    if user_chose == "//q":
        # finishes the game
        amongus_event = False
        users_playing = []
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
    global codename_event, rock_paper_scissors_event, amongus_event
    if any([codename_event, rock_paper_scissors_event, amongus_event]):
        await message.channel.send("`There is already an event running. //h for event info or //q to finish!`")
        return
    match msg:
        case "codenames":
            if codename_event:
                await message.channel.send("`CodeNames event is already running!`")
            else:
                codename_event = True
                await message.channel.send("`CodeNames event was started!`")
        case "rps":
            if rock_paper_scissors_event:
                await message.channel.send("`Rock-Paper-Scissors event is already running!`")
            else:
                rock_paper_scissors_event = True
                await message.channel.send("`Rock-Paper-Scissors event was started!`")
                await asyncio.sleep(2)
                response = r_p_s("play", str(message.author))
                await handle_event_responses(message, response)
        case "amongus":
            if amongus_event:
                await message.channel.send("`AmongUs event is already running!`")
            else:
                amongus_event = True
                voice_channel = discord.utils.get(message.guild.channels, name="Meeting Time")
                if voice_channel:
                    await message.guild.change_voice_state(channel=voice_channel, self_mute=True, self_deaf=False)
                response = discord.Embed(title="Event was started:", description="* Among Us", color=discord.Colour(value=0x8f3ea3))
                response.set_image(url="https://media.discordapp.net/attachments/1115715187052392521/1121920595530108928/image.png?width=1038&height=372")
                await message.channel.send(embed=response)