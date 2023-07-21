"""File that executes our bots functions"""

import discord
import requests
from dotenv import dotenv_values

import responses


async def send_message(message, user_message: str, user: str) -> None:
    """Sends an appropriate response to a query sent with '!' """
    try:
        response = responses.handle_response(user_message, user)
        await message.channel.send(response)
    except Exception as e:
        print(e)
        #await message.channel.send("Sorry, I do not currently have a response for you.")


def run_discord_bot():
    """Function that runs the bot with provided key and """
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
        # No response if it was a message by our bot
        if message.author == client.user:
            return

        user = str(message.author)
        msg = str(message.content).lower()
        channel = str(message.channel)

        print(f"{user} said: '{msg}' ({channel})")

        if msg == "!joke":
            request = requests.get("https://official-joke-api.appspot.com/jokes/programming/random")
            joke = request.json()
            await message.channel.send(joke[0]["setup"])
            await message.channel.send(joke[0]["punchline"])
            await message.delete()
        elif "hi ga" in msg or "hello ga" in msg:
            await send_message(message, msg, user)
        elif msg[0] == "!":
            await send_message(message, msg[1:], user)
            await message.delete()
        elif "lol" in msg:
            await message.channel.send("Haha you're funny!")

    client.run(TOKEN)
