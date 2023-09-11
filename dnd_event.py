"""Dnd Event functions"""

from os import environ

import discord
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
from dotenv import load_dotenv
from pandas import DataFrame

from events_help import help_documentation


class DNDAddMagic(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)

    @discord.ui.button(label="test", row=0, style=discord.ButtonStyle.red)
    async def test1(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.send_message("I've been clicked")
    @discord.ui.button(label="test2", row=0, style=discord.ButtonStyle.blurple)
    async def test2(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.send_message("I've been clicked")
    @discord.ui.button(label="test3", row=0, style=discord.ButtonStyle.danger)
    async def test3(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.send_message("I've been clicked")
    @discord.ui.button(label="test4", row=1, style=discord.ButtonStyle.secondary)
    async def test4(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.send_message("I've been clicked")
    @discord.ui.button(label="test5", row=1, style=discord.ButtonStyle.primary)
    async def test5(self, interaction: discord.Interaction, Button: discord.ui.Button, ):
        await interaction.response.send_message("I've been clicked")


def start_dnd_event(msg: str, user: str, events: dict) -> str:
    """Runs sql queries to get data from the database for dnd"""

    load_dotenv()
    conn = connect(environ["DATABASE_IP"], cursor_factory=RealDictCursor)

    if msg == "//h":
        return help_documentation("dnd"), events

    if msg == "//j":
        return join_dnd(conn, user), events

    if msg == "//storyline":
        return full_story(conn), events

    if msg[0:12] == "//storyline ":
        date = msg[12:].strip()
        try:
            return part_story(conn, date), events
        except:
            return "```The date entered is in the wrong format or has no data. Try //storyline```", events

    if msg[:8] == "//story ":
        return log_story(conn, msg), events

    if msg[:7] == "//magic":
        user_id = find_user(conn, user)
        if user_id is None:
            return "`User not found! Add yourself to the game -> //j`", events

        magic_items_held = get_all_magic_items(conn, user_id)
        return format_magic_items_displayed(conn, magic_items_held), events

    if msg[0:12] == "//add magic ":
        return "add magic item", events
        # return add_magic_item(conn, user, msg), events

    if msg[0:12] == "//use magic ":
        return use_magic_item(conn, user, msg), events
    if msg == "//q":
        events["dnd_event"] = False
        return "`Dungeons & Dragons event was ended!`", events
    return "", events


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


def add_magic_item(conn: connection, user: str, msg: str) -> str:
    """Adds a magical item to your username"""

    incorrect_format = "`Incorrect format for adding a magic item! Refer to //h`"

    user_id = find_user(conn, user)
    if user_id is None:
        return "`User not found! Add yourself to the game -> //j`"

    try:
        item_values = [user_id]
        values_from_message = msg[12:].replace(", ",",").replace(" ,", ",").split(",")
        values_from_message = [val if val != "-" else None for val in values_from_message]
        item_values.extend(values_from_message)

        # if cannot be made into integer - wrong format
        int(item_values[2])
        int(item_values[3])

        # if out of range
        item_values[6]

    except (IndexError, ValueError):
        return incorrect_format

    if not 10 > int(item_values[2]) > 0 or not 9 > int(item_values[3]) > 0:
        return incorrect_format
    if not item_values[4] in ["yes","no"]:
        return incorrect_format
    if item_values[4] == "yes" and item_values[5] is None:
        return incorrect_format
    if item_values[4] == "no" and item_values[5] is not None:
        return incorrect_format

    item_values[2] = get_item_type(conn, item_values)
    item_values[3] = get_item_rarity_type(conn, item_values)

    with conn.cursor() as cur:
        cur.execute("""INSERT INTO magic_items(user_id, item_name, item_type_id, rarity_id,
        attunement_req, class, description) VALUES (%s, %s, %s, %s, %s, %s, %s)""", item_values)
        conn.commit()
    return f"`{values_from_message[0]} item is successfully added to your magic items!`"


def get_item_rarity_type(conn: connection, item_values: list) -> str:
    """Retrieves rarity id by a provided type"""

    item_rarity_type = ['Common', 'Uncommon', 'Rare', 'Very Rare', 'Legendary','Artifact', 'Varies', 'Unknown Rarity']
    rarity_index = int(item_values[3]) - 1
    with conn.cursor() as cur:
        cur.execute("""SELECT rarity_id FROM rarity WHERE rarity_name = %s""", [item_rarity_type[rarity_index]])
        return cur.fetchone()["rarity_id"]


def get_item_type(conn: connection, item_values: list) -> str:
    """Retrieves item type id by item type's name"""

    item_type_name = ['Armour','Potion','Ring','Rod','Scroll','Staff','Wand','Weapon','Wondrous Item']
    type_index = int(item_values[2]) - 1

    with conn.cursor() as cur:
        cur.execute("""SELECT item_type_id FROM item_types WHERE item_type_name = %s""", [item_type_name[type_index]])
        return cur.fetchone()["item_type_id"]


def find_user(conn: connection, user: str) -> int | None:
    """Returns user id from a discord username"""

    with conn.cursor() as cur:
        cur.execute("""SELECT user_id FROM players WHERE username = %s""", [user])
        id = cur.fetchone()
        return id["user_id"] if id is not None else id


def join_dnd(conn: connection, user: str) -> str:
    """Verifies if a player is already in the game
    and adds a player if not"""

    with conn.cursor() as cur:
        cur.execute("""SELECT username FROM players""")
        users_playing = {i["username"] for i in cur.fetchall()}
    if user in users_playing:
        return f"`{user} is already in the game!`"
    else:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO players(username) VALUES (%s)""", [user])
            conn.commit()
        return f"`{user} was successfully added into the game!`"


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
