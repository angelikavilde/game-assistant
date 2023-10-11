"""Dnd Event functions"""

from os import environ
import asyncio

import discord
from discord.ext import commands
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
from dotenv import load_dotenv
from pandas import DataFrame

from events_help import help_documentation


magic_item: dict = dict()

#! LOG STORY GUILD SPECIFIC

class MagicItemAttReq(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=15)

    @discord.ui.button(label="yes", row=0, style=discord.ButtonStyle.green)
    async def att_req(self, interaction: discord.Interaction, Button: discord.ui.Button):
        global magic_item
        magic_item["att_req"] = "yes"
        await interaction.response.send_message("`This item does require a specific class to use it`")
    @discord.ui.button(label="no", row=0, style=discord.ButtonStyle.red)
    async def att_not_req(self, interaction: discord.Interaction, Button: discord.ui.Button):
        global magic_item
        magic_item["att_req"] = "no"
        await interaction.response.send_message("`This item does not require a specific class to use it`")


class MagicItemRarity(discord.ui.View):

    @discord.ui.select(placeholder = "Choose an item rarity", min_values=1, max_values=1,
        options = [discord.SelectOption(label="Common"), discord.SelectOption(label="Uncommon"),
            discord.SelectOption(label="Rare"), discord.SelectOption(label="Very Rare"),
            discord.SelectOption(label="Legendary"), discord.SelectOption(label="Artifact"),
            discord.SelectOption(label="Varies"), discord.SelectOption(label="Unknown Rarity")])

    async def select_callback(self, interaction, select):
        """Saves selected item rarity into the magical item dict"""
        global magic_item
        item_rarity = select.values[0]
        magic_item["item_rarity"] = item_rarity
        indefinite_article = 'an' if item_rarity[0] == "U" or item_rarity[0] == "A" else "a"
        await interaction.response.send_message(f"`Wow it is {indefinite_article} {item_rarity.lower()} item!`")


class MagicItemType(discord.ui.View):

    @discord.ui.select(placeholder = "Choose an item type", min_values=1, max_values=1,
        options = [discord.SelectOption(label="Armour"), discord.SelectOption(label="Potion"),
            discord.SelectOption(label="Ring"), discord.SelectOption(label="Rod"),
            discord.SelectOption(label="Scroll"), discord.SelectOption(label="Staff"),
            discord.SelectOption(label="Wand"), discord.SelectOption(label="Weapon"),
            discord.SelectOption(label="Wondrous Item")])

    async def select_callback(self, interaction, select):
        """Saves selected item type into the magical item dict"""
        global magic_item
        item_type = select.values[0]
        magic_item["item_type"] = item_type
        indefinite_article = "an" if item_type[0] == "A" else "a"
        await interaction.response.send_message(f"`Oooo you found {indefinite_article} {item_type.lower()}!`")


def is_dnd_event_activated():
    """Predicate function to verify if command can be ran"""
    async def predicate(*args):
        from bot import servers_obj
        """Returns True if the DnD event is activated on a server"""
        return servers_obj.get_server().dnd_event
    return commands.check(predicate)


class DNDCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="add_magic")
    @is_dnd_event_activated()
    async def get_magical_item_values(self, ctx, *args) -> None:
        """Retrieves values for a magical item to be added"""
        item_name = " ".join(args)
        global magic_item
        if len(item_name) > 35:
            await ctx.send(f"`Item name is too long! Try again!`")
            clean_magic_item()
            return
        magic_item["name"] = item_name
        await ctx.send(content=f"`You are adding an item:` **{item_name}**")
        await ctx.send(content="Choose an item rarity:", view=MagicItemRarity())
        await asyncio.sleep(3)
        await ctx.send(content="Choose an item type:", view=MagicItemType())
        await asyncio.sleep(3)
        await ctx.send(content="Can only a specific class use this item?", view=MagicItemAttReq())
        await asyncio.sleep(10)
        if magic_item.get("att_req") == "yes":
            await ctx.send("Please enter the name of the class that can use this item:")
            try:
                item_class = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout = 25)
                if len(item_class.content) > 25:
                    await ctx.send(f"`Class name is too long! Try again!`")
                    clean_magic_item()
                    return
                magic_item["class"] = item_class.content
                await ctx.send(f"`The selected class that can use this item is {magic_item['class']}`")
            except asyncio.TimeoutError: 
                await ctx.send(f"**{ctx.author}**, you didn't send the class for this item in time. `Try again!`")
                clean_magic_item()
                return
        try:
            await ctx.send("Please enter the item description:")
            description = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout = 60)
            magic_item["description"] = description.content
            await ctx.send(f"`The item's description is: ` ```{magic_item['description']}```")
        except asyncio.TimeoutError: 
            await ctx.send(f"**{ctx.author}**, you didn't send the description for this item in time. `Try again!`")
            clean_magic_item()
            return
        await ctx.send(add_magic_item(ctx.author))


    @commands.command(name="j")
    @is_dnd_event_activated()
    async def join_dnd(self, ctx) -> None:
        """Verifies if a player is already in the game
        and adds a player if not"""

        conn = get_db_conn()
        user = str(ctx.author)

        user_id = find_user(conn, str(user))
        if user_id is None:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO players(username) VALUES (%s)""", [user])
                conn.commit()
            conn.close()
            await ctx.send(f"`{user} was successfully added into the game!`")
        else:
            conn.close()
            await ctx.send(f"`{user} is already in the game!`")


    @commands.command(name="h")
    @is_dnd_event_activated()
    async def dnd_help(self, ctx) -> None:
        """Returns help command to the user"""
        await ctx.send(help_documentation("dnd"))


    @commands.command(name="magic")
    @is_dnd_event_activated()
    async def all_magic_items(self, ctx) -> None:
        """Shows user all of their magical items"""
        conn = get_db_conn()
        user_id = find_user(conn, str(ctx.author))
        if user_id is None:
            await ctx.send("`User not found! Add yourself to the game -> //j`")
        else:
            magic_items_held = get_all_magic_items(conn, user_id)
            await ctx.send(format_magic_items_displayed(conn, magic_items_held))
        conn.close()

def get_db_conn():
    """Retrieves database connection"""
    load_dotenv()
    return connect(environ["DATABASE_IP"], cursor_factory=RealDictCursor)


def clean_magic_item() -> None:
    """Returns magical item global var to a clean state"""
    global magic_item
    magic_item = dict()


def start_dnd_event(msg: str, user: str, events) -> str:
    """Runs psql queries to get data from the database for dnd"""

    conn = get_db_conn()

    if msg == "//storyline":
        return full_story(conn)

    if msg[0:12] == "//storyline ":
        date = msg[12:].strip()
        try:
            return part_story(conn, date)
        except:
            return "```The date entered is in the wrong format or has no data. Try //storyline```"

    if msg[:8] == "//story ":
        return log_story(conn, msg)

    if msg[0:12] == "//use magic ":
        #! might be able to loop for a select bar 'for loop' to show which item to use
        return use_magic_item(conn, user, msg)
    if msg == "//q":
        events.dnd_event = False
        return "`Dungeons & Dragons event was ended!`"
    return "" #! Will have to change to be an overall command


def get_all_magic_items(conn: connection, user_id) -> dict:
    """Returns all magic items user holds"""

    with conn.cursor() as cur:
        cur.execute("""SELECT * FROM magic_items WHERE user_id = %s""", [user_id])
        return cur.fetchall()


def use_magic_item(conn: connection, user: str, msg: str) -> str:
    """Deletes a magic item from user's magic items if exists"""

    user_id = find_user(conn, user)
    item_name = msg[12:].strip()

    all_users_magic_items = get_all_magic_items(conn, user_id)
    all_users_magic_items = [item["item_name"] for item in all_users_magic_items]

    if user_id is None:
        return "`User not found! Add yourself to the game -> //j`"

    if not item_name in all_users_magic_items:
        return f"`{user} does not currently hold {item_name}! Check //magic for your magical items!`"

    with conn.cursor() as cur:
        cur.execute("""DELETE FROM magic_items WHERE user_id = %s AND item_name = %s""", [user_id, item_name])
        conn.commit()
    return f"`{item_name} was successfully used by {user}`"


def format_magic_items_displayed(conn: connection, magic_items_data: dict) -> str:
    """Returns formatted magical items data for a given user"""

    data_displayed = ""

    for item in magic_items_data:
        data_displayed += "`" + item["item_name"] + "`\n"
        data_displayed += f"```Item type: {get_magic_item_type(conn, item['item_type_id'])}\n"
        data_displayed += f"Item rarity: {get_magic_item_rarity(conn, item['rarity_id'])}\n"
        att_req = item["attunement_req"]
        data_displayed += f"Is attunement required: {att_req}\n"
        if att_req == "yes":
            data_displayed += f"Attunement class: {item['class']}\n"
        data_displayed += f"Description: {item['description']}```"
    return data_displayed if data_displayed else "`You do not hold any magical items currently!`"


def get_magic_item_type(conn: connection, item_id: int) -> str:
    """Returns magic item type from its type id"""

    with conn.cursor() as cur:
        cur.execute("""SELECT item_type_name FROM item_types WHERE item_type_id = %s""", [item_id])
        return cur.fetchone()["item_type_name"]


def get_magic_item_rarity(conn: connection, rarity_id: int) -> str:
    """Returns magic item rarity from its rarity id"""

    with conn.cursor() as cur:
        cur.execute("""SELECT rarity_name FROM rarity WHERE rarity_id = %s""", [rarity_id])
        return cur.fetchone()["rarity_name"]


def add_magic_item(user: str) -> str:
    """Adds a magical item to your username"""

    conn = get_db_conn()

    user_id = find_user(conn, str(user))
    if user_id is None:
        conn.close()
        return "`User not found! Add yourself to the game -> //j`"

    item_type_id = get_item_type(conn, magic_item["item_type"])
    item_rarity_id = get_item_rarity_type(conn, magic_item["item_rarity"])

    item_values = [user_id, magic_item["name"], item_type_id, item_rarity_id, 
        magic_item["att_req"], magic_item.get("class"), magic_item["description"]]

    with conn.cursor() as cur:
        cur.execute("""INSERT INTO magic_items(user_id, item_name, item_type_id, rarity_id,
        attunement_req, class, description) VALUES (%s, %s, %s, %s, %s, %s, %s)""", item_values)
        conn.commit()
    conn.close()
    return f"`{magic_item['name']} item is successfully added to your magic items!`"


def get_item_rarity_type(conn: connection, rarity_name: str) -> int:
    """Retrieves rarity id by a provided type"""
    with conn.cursor() as cur:
        cur.execute("""SELECT rarity_id FROM rarity WHERE rarity_name = %s""", [rarity_name])
        return cur.fetchone()["rarity_id"]


def get_item_type(conn: connection, item_type: str) -> int:
    """Retrieves item type id by item type's name"""
    with conn.cursor() as cur:
        cur.execute("""SELECT item_type_id FROM item_types WHERE item_type_name = %s""", [item_type])
        return cur.fetchone()["item_type_id"]


def find_user(conn: connection, user: str) -> int | None:
    """Returns user id from a discord username"""

    with conn.cursor() as cur:
        cur.execute("""SELECT user_id FROM players WHERE username = %s""", [user])
        id = cur.fetchone()
        return id["user_id"] if id is not None else id


def full_story(conn: connection) -> str:
    """Returns full previously logged story"""

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM log_story")
        data = DataFrame(cur.fetchall())[["date_time","story"]]
    return story_table_displayed(data)


def part_story(conn: connection, date: str) -> str:
    """Returns all the story logged from a provided date"""

    with conn.cursor() as cur:
        cur.execute("""SELECT * FROM log_story WHERE EXTRACT(day
        FROM date_time) = %s AND EXTRACT(month
            FROM date_time) = %s""", date.split("/"))
        data = cur.fetchall()
    return story_table_displayed(DataFrame(data)[["date_time", "story"]])


def log_story(conn, msg: str):
    """Adds story logged into the chat into the database"""

    story = msg[8:]
    split_story = story.split(" ")
    stories = []
    story = ""

    for piece in split_story:
        if len(story + piece) <= 70:
            story += " " + piece
        else:
            stories.append(story.strip())
            story = piece
        if piece is split_story[-1]:
            stories.append(story.strip())

    for piece in stories:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO log_story(story) VALUES (%s)""", [piece])
                conn.commit()
    return "`Story was successfully logged!`"


def story_table_displayed(data: DataFrame) -> str:
    """Returns formatted stroy data from DataFrame"""

    data["date"] = data["date_time"].apply(lambda timestamp: timestamp.strftime("%d/%m"))
    data = data.drop(columns="date_time")
    table = ""

    for day in data["date"].unique():
        table += f"`{day}`\n" + "```"
        for row in data[data["date"] == day]["story"]:
            table += str(row) + "\n"
        table += "```"
    return table
