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
* //use magic x - Uses magic object by the **item name** (x = item name)
** Items with the same name must be recorded as <name> x2 or else will use both at once**
* //add magic x - Adds a magic item following this format:
```
x =  item name, item type, rarity, attunement required, item class, description

Attunement required can only be yes/no, if yes - mention class (if no, put "-" for item class)

Item type must be a number! See below:
1 - Armour, 2 - Potion, 3 - Ring, 4 - Rod, 5 - Scroll,
6 - Staff, 7 - Wand, 8 - Weapon, 9 - Wondrous Item

Rarity must be a number! See below:
1 - Common, 2 - Uncommon, 3 - Rare, 4 - Very Rare, 5 - Legendary,
6 - Artifact, 7 - Varies, 8 - Unknown Rarity
```
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
* /repeat - repeats a message after you and deletes your sent message
* /joke - sends programmer joke
* /kill - deletes last bots message and the command will be deleted off the screen too (!kill)
* /play - shows events that could be activated
**each event when activated has its own commands //h for help about the event**
"""
