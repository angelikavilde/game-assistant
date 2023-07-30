from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from dotenv import dotenv_values

def dnd_event(msg: str, user: str) -> str:
    """Runs sql queries to get data from the database for dnd"""
    config = dotenv_values()
    conn = connect(config["DATABASE_IP"],cursor_factory=RealDictCursor)
    if msg == "//h":
        return """__DnD event:__
* //user - Shows character data associated with discord username
* //story x - Logs in a story (x) and saved for an event on today's date
* //q - Quits the event
* DnD event is associated with database live on cloud so answer's wait-time might vary
"""
    if msg == "//user":
        with conn.cursor() as cur:
            cur.execute("""SELECT character_name, age, race, class,
                username,coins FROM characters LEFT JOIN players 
                ON characters.character_id=players.character_id WHERE 
                username=%s GROUP BY characters.character_id,
                players.username, players.coins;""", [user])
            data = cur.fetchone()
            return f"`{data['username']}: {data['character_name']},{data['race']},{data['class']},\
coins: {data['coins']}, age: {data['age']}`"
    if msg[:8] == "//story ":
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
                    split_story = split_story[i+1:]
                    stories.append(story)
                    break
        for piece in stories:
             with conn.cursor() as cur:
                 cur.execute("""INSERT INTO log_story (story) VALUES (%s)""",[piece])
                 conn.commit()
        return "`Story was successfully logged!`"
