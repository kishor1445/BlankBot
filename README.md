# BlankBot

A discord bot written in python using the discord.py library.

> Our aim is to make a bot that can do everything you need it to do, and more.

## Features
- [x] Moderation
    - [x] Kick
    - [x] Ban
    - [x] Unban
    - [x] Custom prefix
    - [x] Link Perms
    - [ ] Mute
    - [ ] Unmute
    - [x] Warn
    - [x] Clear warnings
    - [x] Purge
    - [x] Slow mode
    - [ ] Lockdown
    - [ ] Unlock-down
    - [ ] Embed Message
- [x] Improvement
    - [x] Suggestions
    - [ ] Bug reports
- [x] Info
    - [x] About
    - [x] Ping
- [x] Converter
    - [x] ASCII to Text
    - [x] Text to ASCII
    - [x] Binary to Text
    - [x] Text to Binary
    - [x] Hex to Text
    - [x] Text to Hex
    - [x] Octal to Text
    - [x] Text to Octal
    - [x] Base64 to Text
    - [x] Text to Base64
    - [x] Morse to Text
    - [x] Text to Morse
    - [x] Reverse Text
    - [x] Reverse Words
- [x] Owner
    - [x] Sync
    - [x] Shutdown
    - [x] Birthday Party Activation/Deactivation
- [x] Utilities
    - [x] Say
    - [x] Server Info
- [x] Events
    - [x] On mentioning the bot, it will reply with the current prefix for the server
    - [x] Auto report unknown errors through a webhook
    - [x] Bot birthday party
    - [x] No discord invite links

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


## FAQ
### How to fix SSL: CERTIFICATE_VERIFY_FAILED error? (macOS)
1. Open `/Applications/Python 3.x/`
2. Double click on `Install Certificates.command`
3. Restart your terminal
4. Done!

### How to get Discord Bot Token?
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the bot tab
4. Click on `Add Bot`
5. Copy the token
6. Done!\
**Note:** Never share your token with anyone, keep it safe!

If you like this project, please consider giving it a star ⭐ <3