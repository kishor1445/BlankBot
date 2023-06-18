# BlankBot

A discord bot written in python using the discord.py library.

> Our aim is to make a bot that can do everything you need it to do, and more.

## Features
- [x] Moderation
    - [x] Kick
    - [x] Ban
    - [x] Unban
    - [x] Custom prefix
    - [x] No discord invite links
    - [ ] Mute
    - [ ] Unmute
    - [ ] Warn
    - [ ] Clear warnings
    - [x] Purge
    - [ ] Slow mode
    - [ ] Lockdown
    - [ ] Unlock-down
- [x] Improvement
    - [x] Suggestions
    - [ ] Bug reports
- [x] Info
    - [x] about
    - [x] ping
- [x] Owner
    - [x] Sync
- [x] Utilities
    - [x] Say
    - [x] Server Info
- [x] Events
    - [x] On mentioning the bot, it will reply with the current prefix for the server
    - [x] auto report unknown errors through a webhook

## Installation
1. Clone the repository using 
```commandline
git clone https://github.com/Kishor1445/BlankBot
```
2. Install the requirements using `pip install -r requirements.txt`
3. Create a file called `.env` in the root directory of the project and add the following:
```
DISCORD_BOT_TOKEN=your bot token
BOT_OWNER_ID=your discord id
UNKNOWN_ERROR_WEBHOOK_URL=your unknown error channel webhook url
SUGGESTION_WEBHOOK_URL=your suggestion channel webhook url
MONGO_DB_URL=your mongodb url
```
4. Run the bot using `python bot.py`
5. Enjoy!

If you like this project, please consider giving it a star ⭐ <3