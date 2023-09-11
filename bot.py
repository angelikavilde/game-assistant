"""File that executes the bots functions"""

from os import environ
import asyncio

import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
from discord.message import Message

from easter_egg import easter_egg_func
from dnd_event import start_dnd_event, DNDAddMagic
from events_help import help_documentation
from codenames import start_codenames
from amongus import start_among_us
from rps import r_p_s


class BotEvents():
    """Class for bot events"""

    def __init__ (self, guild: any):
        # check the type of a guild object
        """Starting with all events set to False
        and users playing to an empty list"""
        self.codenames_event = False
        self.rock_paper_scissors_event = False
        self.amongus_event = False
        self.dnd_event = False
        self.users_playing = []
        self.all_event_statuses = [self.codenames_event,
            self.rock_paper_scissors_event, self.amongus_event, self.dnd_event]
        self.guild = guild
        # add a check if correct guild

events = BotEvents()
bot_message = None


async def check_events_status(interaction: discord.Interaction) -> bool:
    """Verifies the events running statuses to make sure new event can be started"""
    global events, bot_message
    if any(e for e in events.all_event_statuses):
        await interaction.response.send_message("`There is already an event running. //h for event info or //q to finish!`")
        return True
    elif not bot_message or str(bot_message.content) != "Check game commands with //h":
        # If event was activated recently, the bot's last message would show it
        return False
    return False


class StartEvent(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)

    @discord.ui.button(label="CodeNames", row=0, style=discord.ButtonStyle.gray)
    async def codenames(self, interaction: discord.Interaction, Button: discord.ui.Button) -> None:
        if not await check_events_status(interaction):
            global events
            events.codenames_event = True
            link = "https://cdn.discordapp.com/attachments/1130455303087984704/1144308331922600026/Screenshot_2023-08-24_at_17.32.32.png"
            await embed_for_events(interaction, "CodeNames", link)

    @discord.ui.button(label="RockPaperScissors", row=0, style=discord.ButtonStyle.gray)
    async def rps(self, interaction: discord.Interaction, Button: discord.ui.Button) -> None:
    #     events["amongus_event"] = True
    #     link = "https://media.discordapp.net/attachments/1115715187052392521/1121920595530108928/image.png?width=1038&height=372"
    #     await embed_for_events(interaction, "Among Us", link)
        pass

    @discord.ui.button(label="AmongUs", row=0, style=discord.ButtonStyle.gray)
    async def among_us(self, interaction: discord.Interaction, Button: discord.ui.Button) -> None:
        if not await check_events_status(interaction):
            global events
            events.amongus_event = True
            link = "https://media.discordapp.net/attachments/1115715187052392521/1121920595530108928/image.png?width=1038&height=372"
            await embed_for_events(interaction, "Among Us", link)

    @discord.ui.button(label="DnD", row=0, style=discord.ButtonStyle.gray)
    async def dnd(self, interaction: discord.Interaction, Button: discord.ui.Button) -> None:
        if not await check_events_status(interaction):
            global events
            events.dnd_event = True
            link = "https://db4sgowjqfwig.cloudfront.net/campaigns/112103/assets/550235/Bugbear.png?1453822798"
            await embed_for_events(interaction, "Dungeons & Dragons", link)


def run_discord_bot() -> None:
    """Function that runs the bot with a provided key,
    and listens to messages"""

    load_dotenv()
    TOKEN = environ["TOKEN"]
    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(intents=intents, command_prefix="//")

    @client.tree.command(name="joke")
    async def joke(message: Message) -> None:
        """Returns programmer joke from an API"""

        request = requests.get("https://official-joke-api.appspot.com/jokes/programming/random")
        joke = request.json()
        await message.channel.send(joke[0]["setup"])
        await asyncio.sleep(3)
        await message.channel.send(joke[0]["punchline"])

    @client.tree.command(name="play")
    async def play(interaction: discord.Interaction) -> None:
        """Gives options for games to activate"""
        await interaction.response.send_message(
            content="Let's play a game!", view=StartEvent())
    
    @client.tree.command(name="kill")
    async def kill(self: discord.interactions.Interaction) -> None:
        """Kills last bot's message"""
        global bot_message
        if bot_message is not None:
            await bot_message.delete()
    
    @client.tree.command(name="help")
    async def help(interaction: discord.Interaction) -> None:
        """Sends bot's help documentation"""
        await interaction.response.send_message(help_documentation("bot"))

    @client.event
    async def on_ready() -> None:
        print(f'{client.user} is now running!')
        await client.tree.sync()

    @client.event
    async def on_message(message: Message) -> None:
        global bot_message
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
        else:
            await easter_egg_func(message, msg)
        
    client.run(TOKEN)


async def handle_event_responses(message: Message, msg: str):
    """Events when activated allow to run '/' commands.
    Some might however not exist"""

    try:
        if msg == "add magic item":
            await message.channel.send(content="test-2", view=DNDAddMagic())
        else:
            await message.channel.send(msg)
    except Exception as e:
        print(e)
        await message.channel.send("This is not an allowed command for this event. Try '//h' for help!")


async def event(message: Message, msg: str, user: str) -> None:
    """Handles // commands"""

    global events
    if events.codenames_event:
        await message.delete()
        response = start_codenames(msg, user, events)
        await handle_event_responses(message, response)

    elif events.rock_paper_scissors_event:
        pass
        # response, events = r_p_s(msg, user, events)
        # await handle_event_responses(message, response)
        # if msg != "//q":
        #     await asyncio.sleep(2)
        #     response = r_p_s("play", user, events)
        #     await handle_event_responses(message, response)

    elif events.amongus_event:
        await message.delete()
        events = start_among_us(message, msg, events)

    elif events.dnd_event:
        response = start_dnd_event(msg, user, events)
        await handle_event_responses(message, response)

    else:
        await message.channel.send("""`Double slash commands only work during events.
There is no event running! !h or !help for event list.`""")


# async def play_event_run(message: Message, msg:str) -> None:
#     """Handles the event start"""

#     global events
    # if any(e for e in events.values()):
    #     await message.channel.send("`There is already an event running. //h for event info or //q to finish!`")
    #     return

    # match msg:
    #     case "codenames":
    #         if not events["codename_event"]:
    #             events["codename_event"] = True
    #             link = "https://cdn.discordapp.com/attachments/1130455303087984704/1144308331922600026/Screenshot_2023-08-24_at_17.32.32.png"
    #             await embed_for_events(message, "CodeNames", link)
        # case "rps":
    # if not events.rock_paper_scissors_event:
        # events.rock_paper_scissors_event = True
        # await message.channel.send("`Rock-Paper-Scissors event was started!`")
        # await asyncio.sleep(2)
        # response = r_p_s("play", str(message.author), events)
        # await handle_event_responses(message, response)
        # case "amongus":
        #     if not events["amongus_event"]:
        #         events["amongus_event"] = True
        #         link = "https://media.discordapp.net/attachments/1115715187052392521/1121920595530108928/image.png?width=1038&height=372"
        #         await embed_for_events(message, "Among Us", link)
        # case "dnd":
        #     if not events["dnd_event"]:
        #         events["dnd_event"] = True
        #         link = "https://db4sgowjqfwig.cloudfront.net/campaigns/112103/assets/550235/Bugbear.png?1453822798"
        #         await embed_for_events(message, "Dungeons & Dragons", link)


async def embed_for_events(interaction: discord.Interaction, event: str, image_url: str) -> None:
    """Sends an event started embed"""

    response = discord.Embed(title="Event was started:", description=f"* {event}", color=discord.Colour(value=0x8f3ea3))
    response.set_image(url=image_url)
    await interaction.response.send_message(content="Check game commands with //h", embed=response)