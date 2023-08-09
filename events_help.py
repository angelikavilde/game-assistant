"""To keep codes readable, help commands are separated"""

def help_documentation(event: str):
    """Returns formatted string of documentation for an event"""
    match event:
        case "dnd":
            return """
__DnD event:__
* //j - Adds yourself as a player **to the database of players**
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
        case "r-p-s":
            return """
Bot makes a choice before player. Run:
* //paper - to choose paper
* //rock - to choose rock
* //scissors - to choose scissors
* //q to finish the game
**Spaces do not count and it is _not_ case sensitive**
"""
        case "codenames":
            return """
__Run:__
* //j - To join the event (will tell you if already joined)
* //l - To leave the event (this and below will tell you if not joined)
* //d x - To delete a player x from the game
* //t - To make teams
* //q - To finish the event
"""
        case "amongus":
            return """
AmongUs event commands:
* //d - pronounce yourself dead
* //n - resets the game
* //q - finishes the game
"""
        case "bot":
            return """
These are _some_ of the commands I respond to:
* !repeat - repeats a message after you and deletes your sent message
* !joke - sends programmer joke
* !kill - deletes last bots message and the command will be deleted off the screen too (!kill)
* !play x - runs an event x. List of available events: rps, codenames, amongus, dnd.
**each event when activated has its own commands //h for help about the event**
"""