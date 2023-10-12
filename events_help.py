"""To keep scripts more readable, help commands are separated"""

def help_documentation(event: str):
    """Returns formatted string of documentation for an event"""

    match event:
        case "Dungeons & Dragons":
            return """
__DnD event:__
* //j - Adds yourself as a player **to the database of players**
* //story x - Logs in a story (x) and saved for an event on today's date
* //storyline - Shows all recorded history log
* //story_date 05/06 - Shows all recorded log on 5th of June
* //magic - Shows all **your** magic items recorded
* //use_magic x - Uses magic object by the **item name** (x = item name)
** Items with the same name must be recorded as <name> x2 or else will use both at once**
* //add_magic x - Adds a magic item with the name 'x'
* //q - To finish the event
**DnD event is associated with database live on cloud so answer's wait-time might vary**
"""
        case "CodeNames":
            return """
__Run:__
* //j - To join the event
* //a x - To add player x to the game
* //l - To leave the event
* //d x - To delete a player x from the game
* //t - To make teams
* //q - To finish the event
* //show - To show currently joined players
"""
        case "AmongUs":
            return """
AmongUs event commands:
* //d - Pronounce yourself dead
* //n - Resets the game
* //q - To finish the event
"""
        case "bot":
            return """
These are _some_ of the commands I respond to:
* /repeat - repeats a message after you and deletes your sent message
* /joke - sends a random programmer joke
* /aff - sends a random affirmation
* /kill - deletes last bots message and the command will be deleted off the screen too (!kill)
* /play - shows events that could be activated
**each event when activated has its own commands //h for help about the event**
"""
