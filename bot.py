"""File that includes the bot's commands and event data"""

from os import environ
from random import choice

from discord import ButtonStyle, Colour, Embed, Interaction, Intents
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.message import Message
from discord.ui import Button, View, button
from dotenv import load_dotenv
from requests import get

from amongus import AmongUsCog, clean_dead_roles
from codenames import CodeNamesCog
from dnd_event import DNDCog
from easter_egg import easter_egg_func
from events_help import help_documentation
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

    def get_active_event_name(self) -> str:
        """Returns the name of the active event"""
        if self.codenames_event:
            return "CodeNames"
        if self.amongus_event:
            return "AmongUs"
        if self.dnd_event:
            return "Dungeons & Dragons"

    def disable_events(self) -> None:
        """Resets all bot's events"""
        self.codenames_event = False
        self.amongus_event = False
        self.dnd_event = False
        self.users_playing = []


bot_message: Message = None
guild_id: int = 404
servers_obj: 'Servers' = Servers.create_instance()


async def check_if_any_events_are_running(ctx : Context) -> bool:
    """Returns bool whether any event is active"""
    if not servers_obj.get_server().get_all_event_statuses():
        await ctx.send("```There is currently no event running. Activate one -> /play```")
        return False
    return True


async def can_new_even_start(interaction: Interaction, servers: 'Servers') -> bool:
    """Verifies the events' running statuses to make sure new event can be started"""
    if servers.get_server().get_all_event_statuses():
        await interaction.response.send_message("`There is already an event running. //h for event info or //q to finish!`")
        return True
    elif not bot_message or str(bot_message.content) != "Check game commands with //h":
        # If event was activated recently, the bot's last message would show it
        return False
    return True


class StartEvent(View):
    """Class for buttons to choose an event to start"""
    def __init__(self):
        super().__init__(timeout=30)

    @button(label="CodeNames", row=0, style=ButtonStyle.gray)
    async def codenames(self, interaction: Interaction, Button: Button) -> None:
        """Starts a CodeNames event"""
        if not await can_new_even_start(interaction, servers_obj):
            servers_obj.get_server().codenames_event = True
            link = "https://cdn.discordapp.com/attachments/1130455303087984704/1144308331922600026/Screenshot_2023-08-24_at_17.32.32.png"
            await embed_for_events(interaction, "CodeNames", link)

    @button(label="RockPaperScissors", row=0, style=ButtonStyle.gray)
    async def rps(self, interaction: Interaction, Button: Button) -> None:
        """Starts a rock paper scissors game"""
        choices = ["scissors", "rock", "paper"]
        bot_chose = choice(choices)
        await interaction.response.send_message(content="I've made my choice. Choose yours!",
                                        view=RockPaperScissors(bot_chose))

    @button(label="AmongUs", row=0, style=ButtonStyle.gray)
    async def among_us(self, interaction: Interaction, Button: Button) -> None:
        """Starts a AmongUs event"""
        if not await can_new_even_start(interaction, servers_obj):
            servers_obj.get_server().amongus_event = True
            link = "https://media.discordapp.net/attachments/1115715187052392521/1121920595530108928/image.png?width=1038&height=372"
            await embed_for_events(interaction, "Among Us", link)

    @button(label="DnD", row=0, style=ButtonStyle.gray)
    async def dnd(self, interaction: Interaction, Button: Button) -> None:
        """Starts a DnD event"""
        if not await can_new_even_start(interaction, servers_obj):
            servers_obj.get_server().dnd_event = True
            link = "https://db4sgowjqfwig.cloudfront.net/campaigns/112103/assets/550235/Bugbear.png?1453822798"
            await embed_for_events(interaction, "Dungeons & Dragons", link)


def run_discord_bot() -> None:
    """Function that runs the bot with a provided key,
    and listens to messages"""

    load_dotenv()
    TOKEN = environ["TOKEN"]
    intents = Intents.default()
    intents.message_content = True
    intents.guilds = True
    client = commands.Bot(intents=intents, command_prefix="//")


    @client.tree.command(name="aff")
    async def affirm(interaction: Interaction) -> None:
        """Returns an affirmation text from an API"""

        request = get("https://www.affirmations.dev/")
        affirmation = request.json()
        await interaction.response.send_message(affirmation["affirmation"])

    @client.tree.command(name="joke")
    async def joke(interaction: Interaction) -> None:
        """Returns programmer joke from an API"""

        request = get("https://official-joke-api.appspot.com/jokes/programming/random")
        joke = request.json()
        await interaction.response.send_message(joke[0]["setup"] + "\n" + joke[0]["punchline"])

    @client.tree.command(name="play")
    async def play(interaction: Interaction) -> None:
        """Gives options for games to activate"""
        await interaction.response.send_message(
            content="Let's play a game!", view=StartEvent())

    @client.tree.command(name="rps")
    async def r_p_s(interaction: Interaction) -> None:
        """Play rock-paper-scissors with the bot"""
        choices = ["scissors", "rock", "paper"]
        bot_chose = choice(choices)
        await interaction.response.send_message(content="I've made my choice. Choose yours!",
                                        view=RockPaperScissors(bot_chose))
    
    @client.tree.command(name="help")
    async def help(interaction: Interaction) -> None:
        """Sends bot's help documentation"""
        await interaction.response.send_message(help_documentation("bot"))


    # Global event commands
    @client.command(name="q")
    async def quit_event(ctx: Context):
        """Finishes any currently running event"""
        if await check_if_any_events_are_running(ctx):
            event = servers_obj.get_server().get_active_event_name()
            if event == "AmongUs":
                await clean_dead_roles(ctx)
            servers_obj.get_server().disable_events()
            await ctx.send(f"`{event} event was finished!`")
    
    @client.command(name="h")
    async def help_event(ctx: Context):
        """Sends a help documentation for the currently running event"""
        if await check_if_any_events_are_running(ctx):
            event = servers_obj.get_server().get_active_event_name()
            await ctx.send(help_documentation(event))


    @client.event
    async def on_ready() -> None:
        """Syncs in additional bot's commands"""
        print(f"{client.user} is now running!")
        await client.tree.sync()
        dnd_cog = DNDCog(client)
        amongus_cog = AmongUsCog(client)
        codenames_cog = CodeNamesCog(client)
        await client.add_cog(dnd_cog)
        await client.add_cog(amongus_cog)
        await client.add_cog(codenames_cog)
        print("Added event commands!")


    @client.event
    async def on_message(message: Message) -> None:
        """Every time a new message comes in,
        check if it is a command and save
        last bot's message"""

        await client.process_commands(message)

        global bot_message, guild_id

        if not message.content:
            return
        guild_id = message.guild.id

        if message.author == client.user:
            bot_message = message
            return

        user = str(message.author.global_name)
        msg = str(message.content).lower()
        chnl = str(message.channel)

        print(f"{user} said: '{msg}' ({chnl}), guild: {guild_id}")

        await easter_egg_func(message, msg)

    client.run(TOKEN)


async def embed_for_events(interaction: Interaction, event: str, image_url: str) -> None:
    """Sends an event started embed"""
    response = Embed(title="Event was started:", description=f"* {event}", color=Colour(value=0x8f3ea3))
    response.set_image(url=image_url)
    await interaction.response.send_message(content="Check game commands with //h", embed=response)
