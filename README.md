# Game Assistant

## Overview

This project is a discord bot that can be added to any discord server with an invite link provided with permissions. The bot is able to interact with messages and has commands that it could perform when activated. The bot is created with Discord Developer Portal that provides the bot's token and adds the permissions required for the bot. The main functionalities of the bot is to facilitate various gaming experiences within the Discord server. Whether it's orchestrating games like Among Us by granting and revoking channel speaking permissions, assisting in team management for Codenames, or enhancing the Dungeons and Dragons (DnD) experience by managing player inventories with a PostgreSQL (PSQL) database hosted on the cloud and maintaining a storyline log for user reference during future sessions.

The bot is hosted on cloud to be constantly online for users to use, just like its database for DnD items (**Reference [setting-up with cloud](#setting-up-on-cloud)**). With the use of the bot - many possible errors were managed and handled to ensure the bot's other functionalities would not be affected. One of the huge additions was the class to manage various servers as if an event was activated on one server - it is desired to not activate the event globally but only on that one server. Similar thing was implemented for logging in the story for the DnD event as it'd be more preferable to only show the logged story for the server that has interacted with the command to log in the story previously.

The script includes a file named `easter_egg.py` which is not uploaded on github but it includes extra secret interactions that the bot will do upon reading specific words in the user's message. Those interactions include direct replies to messages, reactions to messages and personalised replies.

The script for the bot uses various UI components from the discord.py from select manus to buttons. In future, the project could be expanded to keep more user's data in the database and to include more available UI components available with Python as currently, the bot's functionalities are quite limited.


## Interactive Features

![DnD event activated image shown of the bot's command and response](snippets/Screenshot%202023-08-09%20at%2023.08.52.jpg)
![Commands that show up when bot is added to the server in autocomplete commands](snippets/Screenshot%202023-10-13%20at%2015.31.20.png)
![Buttons shown when /play is ran (Codenames, Rock-paper-scissors, AmongUs, DnD)](snippets/Screenshot%202023-10-13%20at%2015.31.38.jpg)
![Embed that shows up after activating Codenames event which shows an image with the game name and a recommendation of running //h command to see commands for the event. The screenshot then shows an example of //h command being ran which shows event specific commands](snippets/Screenshot%202023-10-13%20at%2015.31.59.jpg)
![Screenshot showing an error message on screen when attempting to activate an event when another one is currently running on a server - telling the user to finish the event first](snippets/Screenshot%202023-10-13%20at%2015.33.10.jpg)
![Screenshot example of a user adding a magical item to the Dnd items on cloud. It shows 2 drop down menus of item type and rarity collected with a button choice of choosing whether this item can only be used by a specific class of a character only](snippets/Screenshot%202023-10-13%20at%2015.34.59.jpg)
![Continuing the previous magic item addition - the bot then asks the user for the item description and shows it on screen before saying that the item was successfully added to the user's magical items](snippets/Screenshot%202023-10-13%20at%2015.35.09.jpg)
![Screenshot of a user trying //magic command during the Dnd event which shows the user's magical items' information](snippets/Screenshot%202023-10-13%20at%2015.36.31.jpg)

## Set-up

Clone the repository and follow the next steps to set up the bot yourself:

* Create a bot with discord developer portal
* Create .env file with `TOKEN=***` - can be obtained after creating a bot

### Setting up locally

1. Set-up virtual environment
2. `pip install -r requirements.txt`
3. `psql postgres` - Make sure PSQL is installed
4. (in PSQL) `CREATE DATABASE <db_name>;`
5. `psql -U <user_name> -d <db_name> < dnd_db.sql`

**For local use - change line 228 in dnd_event.py to: return connect(host=localhost, dbname=<db_name>, cursor_factory=RealDictCursor)**

6. Run the bot: `python3 main.py`

**Steps 1,2 and 6 could be changed to running a Dockerfile (as below)**

### Setting up locally with Dockerfile

1. `docker build . -t <image_name>` - Make sure Docker is installed
2. Steps 3-5 & **line change** from the set-up above
3. `docker run -d <image_name>`

### Setting up on cloud

To set up the project on cloud, the only 2 required steps are to create PSQL database and add its info to .env file with any neccessary changes in the line 228 in `dnd_event.py`. This project is currently using [ElephantSQL](https://www.elephantsql.com/) to host the PSQL database, for connection of which - only the database IP is required (.env file has `DATABASE_IP=***`). The next required step to host the bot on cloud is the Dockerfile hosting. For which, this project is using [FlyIO](https://fly.io/) (the toml file for which is labelled as `fly.toml`). To run it with fly, next commands need to be ran after installing Fly:

1. `fly launch`
2. `fly secrets set <secret>` - add .env file secret values
3. `fly deploy`
4. `fly scale count 1` - fly automatically creates 2 machines but this causes the bot to repeat its messages

**When using fly to host the bot, it is important that the following is added to the fly.toml file:**
`auto_stop_machines = false` - as it would prevent the bot from not running when not in use