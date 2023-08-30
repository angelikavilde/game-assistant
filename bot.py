"""File that executes the bots functions"""

import discord
import requests
import asyncio
from dotenv import dotenv_values
from discord.message import Message

from easter_egg import easter_egg_func
from dnd_event import start_dnd_event
from events_help import help_documentation
from codenames import start_codenames
from amongus import start_among_us
from rps import r_p_s


events = {"codename_event": False, "rock_paper_scissors_event": False,
           "amongus_event": False, "dnd_event": False, "users_playing": []}
bot_message = None


async def handle_response(message: Message, msg: str) -> None:
    """Function that determines what to do with the responses from
    user that starts with '!' """

    if msg[:5] == "play ":
        await play_event_run(message, msg[5:])

    elif msg == "joke":
        await send_joke(message)

    elif msg == "kill":
        global bot_message
        if bot_message is not None:
            await bot_message.delete()

    elif msg == "help" or msg == "h":
        await message.channel.send(help_documentation("bot"))

    elif msg[:7] == "repeat ":
        await message.channel.send(msg[7:])
    else:
        await message.channel.send("Sorry, I do not currently have a response for you.")


def run_discord_bot() -> None:
    """Function that runs the bot with provided key,
    and listens to messages"""

    config = dotenv_values()
    TOKEN = config["TOKEN"]
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready() -> None:
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message: Message) -> None:
        global events, bot_message
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

        if msg[0:2] == "//":
            await event(message, msg, user)
        elif msg[0] == "!":
            await handle_response(message, msg[1:])
            await message.delete()
        else:
            await easter_egg_func(message, msg)
        
    client.run(TOKEN)


async def send_joke(message: Message) -> None:
    """Returns programmer joke from an API"""

    request = requests.get("https://official-joke-api.appspot.com/jokes/programming/random")
    joke = request.json()
    await message.channel.send(joke[0]["setup"])
    await asyncio.sleep(3)
    await message.channel.send(joke[0]["punchline"])


async def handle_event_responses(message: Message, msg: str):
    """Events when activated allow to run '/' commands.
    Some might however not exist"""

    try:
        await message.channel.send(msg)
    except Exception as e:
        print(e)
        await message.channel.send("This is not an allowed command for this event. Try '//h' for help!")


async def event(message: Message, msg: str, user: str) -> None:
    global events
    """Handles // commands"""

    if events["codename_event"]:
        await message.delete()
        response, events = start_codenames(msg, user, events)
        await handle_event_responses(message, response)

    elif events["rock_paper_scissors_event"]:
        response, events = r_p_s(msg, user, events)
        await handle_event_responses(message, response)
        if msg != "//q":
            await asyncio.sleep(2)
            response, events = r_p_s("play", user, events)
            await handle_event_responses(message, response)

    elif events["amongus_event"]:
        await message.delete()
        events = await start_among_us(message, msg, events)
        if msg not in ["//h", "//d", "//n", "//q"]:
            await handle_event_responses(message, "")

    elif events["dnd_event"]:
        response = start_dnd_event(msg, user)
        await handle_event_responses(message, response)

    else:
        await message.channel.send("""`Double slash commands only work during events.
There is no event running! !h or !help for event list.`""")


async def play_event_run(message: Message, msg:str) -> None:
    """Handles the event start"""

    global events
    if any(e for e in events.values()):
        await message.channel.send("`There is already an event running. //h for event info or //q to finish!`")
        return

    match msg:
        case "codenames":
            if not events["codename_event"]:
                events["codename_event"] = True
                link = "https://cdn.discordapp.com/attachments/1130455303087984704/1144308331922600026/Screenshot_2023-08-24_at_17.32.32.png"
                await embed_for_events(message, "CodeNames", link)
        case "rps":
            if not events["rock_paper_scissors_event"]:
                events["rock_paper_scissors_event"] = True
                await message.channel.send("`Rock-Paper-Scissors event was started!`")
                await asyncio.sleep(2)
                response, events = r_p_s("play", str(message.author), events)
                await handle_event_responses(message, response)
        case "amongus":
            if not events["amongus_event"]:
                events["amongus_event"] = True
                link = "https://media.discordapp.net/attachments/1115715187052392521/1121920595530108928/image.png?width=1038&height=372"
                await embed_for_events(message, "Among Us", link)
        case "dnd":
            if not events["dnd_event"]:
                events["dnd_event"] = True
                link = "https://db4sgowjqfwig.cloudfront.net/campaigns/112103/assets/550235/Bugbear.png?1453822798"
                await embed_for_events(message, "Dungeons & Dragons", link)


async def embed_for_events(message: Message, event: str, image_url: str) -> None:
    """Sends an event started embed"""

    response = discord.Embed(title="Event was started:", description=f"* {event}", color=discord.Colour(value=0x8f3ea3))
    response.set_image(url=image_url)
    await message.channel.send(embed=response)