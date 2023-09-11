"""Among-us event bot functionalities"""

import discord
from discord.message import Message

from events_help import help_documentation
from bot import BotEvents

async def start_among_us(message: Message, user_chose: str, events: BotEvents) -> None:
    """AmongUs event function"""

    if user_chose == "//d":
        if not message.author in events.users_playing:
            events.users_playing.append(message.author)
            await member_role_changed(message, message.author, True)
            await message.channel.send(f"`{str(message.author)} has been announced dead!`")
        else:
            await message.channel.send(f"`{str(message.author)} is already laying in the grave!`")

    elif user_chose == "//n":
        for member in events.users_playing:
            await member_role_changed(message, member, False)
        events.users_playing = []
        await message.channel.send("`AmongUs event was restarted!`")

    elif user_chose == "//h":
        await message.channel.send(help_documentation("amongus"))

    elif user_chose == "//q":
        for member in events.users_playing:
            await member_role_changed(message, member, False)

        events.amongus_event = False
        events.users_playing = []
        await message.channel.send("`AmongUs event was ended!`")
    else:
        await message.channel.send("This is not an allowed command for this event. Try '//h' for help!")


async def member_role_changed(message: Message, user, add: bool) -> None:
    """Gives a user a Dead Crewmate role or removes it"""

    role = discord.utils.get(message.guild.roles, name="Dead Crewmate")
    if add:
        await user.add_roles(role)
    else:
        await user.remove_roles(role)