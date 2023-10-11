"""File that executes the bots functions"""

from os import environ
from random import choice
import asyncio

import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
from discord.message import Message

from easter_egg import easter_egg_func
from dnd_event import start_dnd_event, MagicItemRarity, MagicItemType, MagicItemAttReq, DNDCog
from events_help import help_documentation
from codenames import start_codenames
from amongus import start_among_us
from rps import RockPaperScissors


class Servers():
    """Class for various servers"""

    def __init__(self):
        self.server_events = dict()

    @classmethod
    def create_instance(cls: type) -> 'Servers':
        """Create new instance of servers obj"""
        return cls()

    def get_server(self) -> 'BotEvents':
        """Returns events object relevant to current guild"""
        if guild_id not in self.server_events:
            self.add_server()
        return self.server_events[guild_id]

    def add_server(self) -> None:
        """Adds an events object to the servers object"""
        self.server_events[guild_id] = BotEvents.create_instance(guild_id)


class BotEvents():
    """Class for bot events"""

    def __init__ (self, guild_id: int):
        """Starting with all events set to False
        and users playing to an empty list"""
        self.codenames_event = False
        self.amongus_event = False
        self.dnd_event = False
        self.users_playing = []
        self.guild_id = guild_id

    @classmethod
    def create_instance(cls: type, guild_id: int) -> 'BotEvents':
        """Create new instance of bot-events obj"""
        return cls(guild_id)

    def get_all_event_statuses(self) -> bool:
        """Returns bool whether any event is running"""
        return any((self.codenames_event, self.amongus_event, self.dnd_event))


bot_message: discord.message.Message = None
guild_id: int = 404
servers_obj: 'Servers' = Servers.create_instance()


async def check_events_status(interaction: discord.Interaction, servers: 'Servers') -> bool:
    """Verifies the events' running statuses to make sure new event can be started"""
    if servers.get_server().get_all_event_statuses():
        await interaction.response.send_message("`There is already an event running. //h for event info or //q to finish!`")
        return True
    elif not bot_message or str(bot_message.content) != "Check game commands with //h":
        # If event was activated recently, the bot's last message would show it
        return False
    return True


class StartEvent(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)

    @discord.ui.button(label="CodeNames", row=0, style=discord.ButtonStyle.gray)
    async def codenames(self, interaction: discord.Interaction, Button: discord.ui.Button) -> None:
        if not await check_events_status(interaction, servers_obj):
            servers_obj.get_server().codenames_event = True
            link = "https://cdn.discordapp.com/attachments/1130455303087984704/1144308331922600026/Screenshot_2023-08-24_at_17.32.32.png"
            await embed_for_events(interaction, "CodeNames", link)

    @discord.ui.button(label="RockPaperScissors", row=0, style=discord.ButtonStyle.gray)
    async def rps(self, interaction: discord.Interaction, Button: discord.ui.Button) -> None:
        choices = ["scissors", "rock", "paper"]
        bot_chose = choice(choices)
        await interaction.response.send_message(content="I've made my choice. Choose yours!",
                                        view=RockPaperScissors(bot_chose, bot_message))

    @discord.ui.button(label="AmongUs", row=0, style=discord.ButtonStyle.gray)
    async def among_us(self, interaction: discord.Interaction, Button: discord.ui.Button) -> None:
        if not await check_events_status(interaction, servers_obj):
            servers_obj.get_server().amongus_event = True
            link = "https://media.discordapp.net/attachments/1115715187052392521/1121920595530108928/image.png?width=1038&height=372"
            await embed_for_events(interaction, "Among Us", link)

    @discord.ui.button(label="DnD", row=0, style=discord.ButtonStyle.gray)
    async def dnd(self, interaction: discord.Interaction, Button: discord.ui.Button) -> None:
        if not await check_events_status(interaction, servers_obj):
            servers_obj.get_server().dnd_event = True
            link = "https://db4sgowjqfwig.cloudfront.net/campaigns/112103/assets/550235/Bugbear.png?1453822798"
            await embed_for_events(interaction, "Dungeons & Dragons", link)


def run_discord_bot() -> None:
    """Function that runs the bot with a provided key,
    and listens to messages"""

    load_dotenv()
    TOKEN = environ["TOKEN"]
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    client = commands.Bot(intents=intents, command_prefix="//")


    @client.tree.command(name="aff")
    async def affirm(interaction: discord.Interaction) -> None:
        """Returns an affirmation text from an API"""

        request = requests.get("https://www.affirmations.dev/")
        affirmation = request.json()
        await interaction.response.send_message(affirmation["affirmation"])

    @client.tree.command(name="joke")
    async def joke(interaction: discord.Interaction) -> None:
        """Returns programmer joke from an API"""

        request = requests.get("https://official-joke-api.appspot.com/jokes/programming/random")
        joke = request.json()
        await interaction.response.send_message(joke[0]["setup"] + "\n" + joke[0]["punchline"])

    @client.tree.command(name="play")
    async def play(interaction: discord.Interaction) -> None:
        """Gives options for games to activate"""
        await interaction.response.send_message(
            content="Let's play a game!", view=StartEvent())

    @client.tree.command(name="rps")
    async def r_p_s(interaction: discord.Interaction) -> None:
        """Play rock-paper-scissors with the bot"""
        choices = ["scissors", "rock", "paper"]
        bot_chose = choice(choices)
        await interaction.response.send_message(content="I've made my choice. Choose yours!",
                                        view=RockPaperScissors(bot_chose, bot_message))

    @client.tree.command(name="kill")
    async def kill(self: discord.interactions.Interaction) -> None:
        """Kills last bot's message"""
        if bot_message is not None:
            await bot_message.delete()
    
    @client.tree.command(name="help")
    async def help(interaction: discord.Interaction) -> None:
        """Sends bot's help documentation"""
        await interaction.response.send_message(help_documentation("bot"))


    @client.event
    async def on_ready() -> None:
        print(f"{client.user} is now running!")
        await client.tree.sync()
        dnd_cog = DNDCog(client)
        await client.add_cog(dnd_cog)
        print("Added event commands!")


    @client.event
    async def on_message(message: Message) -> None:
        await client.process_commands(message)
        global bot_message, guild_id
        if not message.content:
            return
        guild_id = message.guild.id

        if message.author == client.user:
            bot_message = message
            return

        user = str(message.author.global_name) #TODO fix the name (only nickname vers used in text else dis name)
        username = str(message.author)
        msg = str(message.content).lower()
        chnl = str(message.channel)

        print(f"{user} said: '{msg}' ({chnl}), guild: {guild_id}")

        # if msg[0:2] == "//":
        #     await event_run(message, msg, username)
        # else:
        #     await easter_egg_func(message, msg)

    client.run(TOKEN)


async def handle_event_responses(message: Message, msg: str) -> None:
    """Events when activated allow to run '/' commands.
    Some might however not exist"""

    try:
        if msg == "add magic item":
            await message.channel.send(content="test-2", view=MagicItemRarity())
            await message.channel.send(content="t", view=MagicItemType())
            await message.channel.send(content="t", view=MagicItemAttReq())
            from dnd_event import magic_item
            if magic_item.get("att_req", None) == "yes":
                await message.channel.send(content="""This item requires a specific class
                        to use it. Please share - which""", view=MagicItemAttReq())
            # await message.channel.send("Please enter the first piece of text:")
            # response1 = await client.wait_for("message", check=lambda m: m.author == ctx.author)
        else:
            await message.channel.send(msg)
    except Exception as e:
        print(e)
        await message.channel.send("This is not an allowed command for this event. Try '//h' for help!")


async def event_run(message: Message, msg: str, user: str) -> None:
    """Handles // commands"""

    if servers_obj.get_server().codenames_event:
        await message.delete()
        response = start_codenames(msg, user, servers_obj)
        await handle_event_responses(message, response)

    elif servers_obj.get_server().amongus_event:
        await message.delete()
        await start_among_us(message, msg, servers_obj)

    elif servers_obj.get_server().dnd_event:
        response = start_dnd_event(msg, user, servers_obj)
        await handle_event_responses(message, response)

    else:
        await message.channel.send("""`Double slash commands only work during server events.
There is no event running! !h or !help for event list.`""")


async def embed_for_events(interaction: discord.Interaction, event: str, image_url: str) -> None:
    """Sends an event started embed"""

    response = discord.Embed(title="Event was started:", description=f"* {event}", color=discord.Colour(value=0x8f3ea3))
    response.set_image(url=image_url)
    await interaction.response.send_message(content="Check game commands with //h", embed=response)