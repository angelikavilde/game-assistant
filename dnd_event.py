from datetime import datetime

from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from dotenv import dotenv_values
import pandas as pd
from pandas import DataFrame

def start_dnd_event(msg: str, user: str) -> str:
    """Runs sql queries to get data from the database for dnd"""
    config = dotenv_values()
    conn = connect(config["DATABASE_IP"], cursor_factory=RealDictCursor)
    if msg == "//h":
        return """__DnD event:__
* //story x - Logs in a story (x) and saved for an event on today's date
* //storyline - Shows all recorded history log
* //storyline 05/06 - Shows all recorded log on 5th of June
* //magic - Shows all **your** magic items recorded
* //use magic x - Uses magic object by the **id**
* //add magic x - Adds a magic item following this format:
`x =  ` 
* //q - Quits the event
**DnD event is associated with database live on cloud so answer's wait-time might vary**
    """
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
        add_story(conn, msg)
    if msg[:7] == "//magic":
        with conn.cursor() as cur:
            cur.execute("""SELECT user_id FROM players WHERE username = %s""", user)
            user_id = cur.fetchone()
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM magic_items WHERE user_id = %s""", user_id)
            data = cur.fetchall()
        return f"`{user}: {data['item_name']},{data['race']},{data['class']},\
coins: {data['coins']}, age: {data['age']}`"


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