"""Rock-Paper-Scissors event functions"""

from discord import Interaction, ButtonStyle
from discord.message import Message
from discord.ui import button, Button, View


async def check_rps_played(interaction: Interaction, bot_message: Message) -> bool:
    """Verifies the event's activation status to make sure event can be played"""
    if not bot_message or "I've made my choice." not in str(bot_message.content):
        return False
    await interaction.response.send_message("Re-start the game!")
    return True


def who_won_rps(bot_chose: str, user_chose: str) -> str:
    """Returns text on who chose what and who won/lost"""
    if bot_chose == user_chose:
        return f"`I also chose {bot_chose}. We tie!`"
    if (user_chose,bot_chose) in [("scissors","rock"),("rock","paper"),("paper","scissors")]:
        return f"`I chose {bot_chose}. You lose!`"
    return f"`I chose {bot_chose}. You win!`"


class RockPaperScissors(View):
    def __init__(self, bot_choice: str, bot_msg: Message):
        super().__init__(timeout=10)
        self.bot_choice = bot_choice
        self.bot_msg = bot_msg #TODO currently has similar to old issue where it isn't the new one that is ran

    @button(label="Rock", row=0, style=ButtonStyle.red)
    async def rock(self, interaction: Interaction, Button: Button) -> None:
        if not await check_rps_played(interaction, self.bot_msg):
            await interaction.response.send_message(who_won_rps(self.bot_choice, "rock"))

    @button(label="Paper", row=0, style=ButtonStyle.red)
    async def paper(self, interaction: Interaction, Button: Button) -> None:
        if not await check_rps_played(interaction, self.bot_msg):
            await interaction.response.send_message(who_won_rps(self.bot_choice, "paper"))

    @button(label="Scissors", row=0, style=ButtonStyle.red)
    async def scissors(self, interaction: Interaction, Button: Button) -> None:
        if not await check_rps_played(interaction, self.bot_msg):
            await interaction.response.send_message(who_won_rps(self.bot_choice, "scissors"))
