# BlankBot

A discord bot written in python using the discord.py library.

> Our aim is to make a bot that can do everything you need it to do, and more.

## Features
- [x] Moderation
    - [x] Kick**
    - [x] Ban**
    - [x] Server Info**
    - [x] No discord invite links
    - [ ] Mute
    - [ ] Unmute
    - [ ] Warn
    - [ ] Unban
    - [ ] Purge
    - [ ] Slow mode
    - [ ] Lockdown
    - [ ] Unlock-down
- [x] Improvement
    - [x] Suggestions
    - [ ] Bug reports

** Slash commands and Application commands are not implemented yet, but will be soon!

## Installation
1. Clone the repository
2. Install the requirements using `pip install -r requirements.txt`
3. Create a file called `.env` in the root directory of the project and add the following:
```
DISCORD_BOT_TOKEN=your bot token
BOT_OWNER_ID=your discord id
DISCORD_BOT_CLIENT_SECRET=your bot client secret
DISCORD_BOT_CLIENT_ID=your bot client id
UNKNOWN_ERROR_WEBHOOK_URL=your unknown error channel webhook url
SUGGESTION_WEBHOOK_URL=your suggestion channel webhook url
TEST_GUILD_ID=your test guild id
```
4. Run the bot using `python bot.py`
5. Enjoy!

If you like this project, please consider giving it a star ⭐ <3