"""To keep scripts more readable, help commands are separated"""

def help_documentation(event: str):
    """Returns formatted string of documentation for an event"""

    match event:
        case "Dungeons & Dragons":
            return """
__DnD event:__
* //add_user - Adds yourself as a player **to the database of players**
* //story x - Logs in a story (x) and saved for an event on today's date
* //storyline - Shows all recorded history log
* //story_date 05/06 - Shows all recorded log on 5th of June
* //magic - Shows all **your** magic items recorded
* //use_magic x - Uses magic object by the **item name** (x = item name)
**Items with the same name must be recorded as <name> x2 or else will use both at once**
* //add_magic x - Adds a magic item with the name 'x'
* //q - To finish the event
**DnD event is associated with database live on cloud so answer's wait-time might vary**
"""
        case "CodeNames":
            return """
__Run:__
* //join - To join the event
* //add x - To add player x to the game
* //leave - To leave the event
* //rm x - To delete a player x from the game
* //teams - To make teams
* //show - To show currently joined players
* //q - To finish the event
"""
        case "AmongUs":
            return """
AmongUs event commands:
* //dead - Pronounce yourself dead
* //new - Resets the game
* //q - To finish the event
"""
        case "bot":
            return """
These are _some_ of the commands I respond to:
* /repeat - Repeats a message after you and deletes your sent message
* /joke - Sends a random programmer joke
* /aff - Sends a random affirmation
* /play - Shows events that could be activated
* /rps - Play rock-paper-scissors with the bot
**Each event when activated has its own commands //h for help about the event**
"""
