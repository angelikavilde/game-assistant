from datetime import datetime

from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from dotenv import dotenv_values
import pandas as pd
from pandas import DataFrame

from events_help import help_documentation


def start_dnd_event(msg: str, user: str) -> str:
    """Runs sql queries to get data from the database for dnd"""
    config = dotenv_values()
    conn = connect(config["DATABASE_IP"], cursor_factory=RealDictCursor)
    if msg == "//h":
        return help_documentation("dnd")
    if msg == "//j":
        return join_dnd(conn, user)
    if msg == "//storyline":
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM log_story")
            data = pd.DataFrame(cur.fetchall())[["date_time","story"]]
        return table_returned(data)
    if msg[0:12] == "//storyline ":
        date = msg[12:].strip()
        try:
            with conn.cursor() as cur:
                cur.execute("""SELECT * FROM log_story WHERE EXTRACT(day
                FROM date_time) = %s AND EXTRACT(month
                    FROM date_time) = %s""", date.split("/"))
                data = cur.fetchall()
            return table_returned(pd.DataFrame(data)[["date_time", "story"]])
        except:
            return "```The date entered is in the wrong format or has no data. Try //storyline```"
    if msg[:8] == "//story ":
        return add_story(conn, msg)
    if msg[:7] == "//magic":
        with conn.cursor() as cur:
            cur.execute("""SELECT user_id FROM players WHERE username = %s""", user)
            user_id = cur.fetchone()
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM magic_items WHERE user_id = %s""", user_id)
            data = cur.fetchall()
        return f"`{user}: {data['item_name']},{data['race']},{data['class']},\
coins: {data['coins']}, age: {data['age']}`"


def join_dnd(conn, user: str) -> str:
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


def add_story(conn, msg: str):
    """Adds story logged into the chat into the database"""
    story = msg[8:]
    split_story = story.split(" ")
    stories = []
    add_story = True
    while add_story is True:
        story = ""
        for i, part in enumerate(split_story):
            if len(story + part) < 70:
                story += part + " "
            if split_story[i] is split_story[-1]:
                stories.append(story)
                add_story = False
            if len(story + part) > 70:
                split_story = split_story[i:]
                stories.append(story)
                break
    for piece in stories:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO log_story (story) VALUES (%s)""", [piece])
                conn.commit()
    return "`Story was successfully logged!`"


def table_returned(data: DataFrame) -> str:
    """Returns formatted data from DataFrame"""
    data["date"] = data["date_time"].apply(lambda timestamp: timestamp.strftime("%d/%m"))
    data = data.drop(columns="date_time")
    table = ""
    for day in data["date"].unique():
        table += f"`{day}`\n" + "```"
        for row in data[data["date"] == day]["story"]:
            table += str(row) + "\n"
        table += "```"
    return table