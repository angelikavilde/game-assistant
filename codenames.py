"""Codenames event bot functionalities"""

from random import choice

from discord.ext.commands import Cog, check, command
from discord.ext.commands.context import Context


def is_codenames_event_activated():
    """Predicate function to verify if command can be ran"""
    async def predicate(*args):
        from bot import servers_obj
        """Returns True if the CodeNames event is activated on a server"""
        return servers_obj.get_server().codenames_event
    return check(predicate)


class CodeNamesCog(Cog):

    def __init__(self, bot):
        self.bot = bot

    @command(name="d")
    @is_codenames_event_activated()
    async def delete_user(self, ctx: Context, *args) -> None:
        """Deletes a chosen player (not yourself) from an event"""
        user = " ".join(args)
        await ctx.send(remove_a_player(user))

    @command(name="l")
    @is_codenames_event_activated()
    async def leave_event(self, ctx: Context) -> None:
        """Removes a player from an event"""
        user = str(ctx.author)
        await ctx.send(remove_a_player(user))

    @command(name="j")
    @is_codenames_event_activated()
    async def join_event(self, ctx: Context) -> None:
        """Adds a player to the event"""
        user = str(ctx.author)
        await ctx.send(add_player(user))

    @command(name="a")
    @is_codenames_event_activated()
    async def add_to_event(self, ctx: Context, *args) -> None:
        """Adds another player (not yourself) to the event"""
        user = " ".join(args)
        await ctx.send(add_player(user))

    @command(name="t")
    @is_codenames_event_activated()
    async def display_teams(self, ctx: Context) -> None:
        """Displays random teams"""
        from bot import servers_obj
        if len(servers_obj.get_server().users_playing) < 4:
            return "`This game is designed for minimum of 4 people. Preferably 6 or more. Add more players!`"
        team1 = servers_obj.get_server().users_playing.copy()
        team2 = []
        for _ in range(int(len(servers_obj.get_server().users_playing)/2)):
            team2.append(team1.pop(team1.index(choice(team1))))
            team_1_formatted = ", ".join(team1)
            team_2_formatted = ", ".join(team2)
        teams = f"""```Team 1: {team_1_formatted}; Captain: {choice(team1)}
Team 2: {team_2_formatted}; Captain: {choice(team2)}```"""
        return teams

    @command(name="show")
    @is_codenames_event_activated()
    async def show_current_players(self, ctx: Context) -> None:
        """Displays current players to the chat"""
        from bot import servers_obj
        users_playing = ", ".join(servers_obj.get_server().users_playing)
        return f"`Currently playing are: {users_playing}`"


def remove_a_player(player: str) -> str:
    """Removes a player from the code-names event"""
    from bot import servers_obj
    if player in servers_obj.get_server().users_playing:
        servers_obj.get_server().users_playing.remove(player)
        return f"`{player} successfully left CodeNames event!`"
    else:
        return f"`Cannot leave! {player} did not enter the game. '//j' to join!`"


def add_player(player: str) -> str:
    """Adds a player to the code-names event"""
    from bot import servers_obj
    if player in servers_obj.get_server().users_playing:
        return f"`Cannot join! {player} has already joined the CodeNames event!`"
    servers_obj.get_server().users_playing.append(player)
    return f"`{player} was successfully added to the CodeNames event!`"
