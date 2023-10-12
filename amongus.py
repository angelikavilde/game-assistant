"""Among-us event bot functionalities"""

import discord
from discord.ext.commands import Cog, check, command
from discord.ext.commands.context import Context


def is_amongus_event_activated():
    """Predicate function to verify if command can be ran"""
    async def predicate(*args):
        from bot import servers_obj
        """Returns True if the AmongUs event is activated on a server"""
        return servers_obj.get_server().amongus_event
    return check(predicate)


class AmongUsCog(Cog):

    def __init__(self, bot):
        self.bot = bot

    @command(name="d")
    @is_amongus_event_activated()
    async def player_died(self, ctx: Context) -> None:
        """Changes the role of a player to a dead role if not already"""
        from bot import servers_obj
        if not ctx.author in servers_obj.get_server().users_playing:
            servers_obj.get_server().users_playing.append(ctx.author)
            await member_role_changed(ctx, ctx.author, True)
            await ctx.send(f"`{str(ctx.author)} has been pronounced dead!`")
        else:
            await ctx.send(f"`{str(ctx.author)} is already laying in the grave!`")


# if user_chose == "//n":
#     for member in events.users_playing:
#         await member_role_changed(message, member, False)
#     events.users_playing = []
#     await message.channel.send("`AmongUs event was restarted!`")


async def clean_dead_roles(ctx: Context) -> None:
    """Returns all players to a non dead crewmate role"""
    from bot import servers_obj
    for member in servers_obj.get_server().users_playing:
        await member_role_changed(ctx, member, False)


async def member_role_changed(ctx: Context, user: discord.member.Member, add: bool) -> None:
    """Gives a user a Dead Crewmate role or removes it"""

    role = discord.utils.get(ctx.guild.roles, name="Dead Crewmate")
    if not role:
        await ctx.send("```Dead Crewmate role does not exist on this channel!```")
    else:
        if add:
            await user.add_roles(role)
        else:
            await user.remove_roles(role)
