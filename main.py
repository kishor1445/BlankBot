import asyncio
import os
import discord
from discord.ext import commands, tasks
from typing import Optional, List
from aiohttp import ClientSession
from dotenv import load_dotenv
import logging
import logging.handlers
from pymongo import MongoClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta


load_dotenv()


async def custom_prefix(bot, message):
    if message.guild is None:
        return "^"
    else:
        db = bot.cluster["guilds"]
        collection = db["custom_prefix"]
        data = collection.find_one({"_id": message.guild.id})
        if data is None:
            return "^"
        return data["prefix"]


class BlankBot(commands.Bot):
    def __init__(
        self,
        *args,
        initial_extensions: List[str],
        web_client: ClientSession,
        testing_guild_id: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(
            *args,
            intents=discord.Intents.all(),
            activity=discord.Activity(
                name="BlankPower", type=discord.ActivityType.listening
            ),
            status=discord.Status.idle,
            **kwargs,
        )
        self.web_client = web_client
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_extensions
        self.unknown_error_webhook_url = os.getenv("UNKNOWN_ERROR_WEBHOOK_URL", "")
        self.suggestion_webhook_url = os.getenv("SUGGESTION_WEBHOOK_URL", "")
        self.cluster = MongoClient(os.getenv("MONGO_DB_URL"))
        self.birthday = False
        self.scheduler = AsyncIOScheduler()
        if datetime.now() > datetime(year=int(datetime.now().__format__('%Y')), month=6, day=11):
            on_date = datetime(int(datetime.now().__format__('%Y')) + 1, month=6, day=11)
        else:
            on_date = datetime(int(datetime.now().__format__('%Y')), month=6, day=11)
        self.scheduler.add_job(
            self.on_birthday_party,
            DateTrigger(
                on_date
            )
        )

    async def setup_hook(self) -> None:
        for extension in self.initial_extensions:
            await self.load_extension(extension)
        await self.tree.sync()
        self.scheduler.start()

    async def on_ready(self):
        print(f"Logged in as {self.user} [ID: {self.user.id}]")

    async def on_birthday_party(self):
        self.birthday = True
        self.birthday_status_update.start()
        on_date = datetime(int(datetime.now().__format__('%Y')) + 1, 6, 11)
        self.scheduler.add_job(
            self.on_birthday_party,
            DateTrigger(
                on_date
            )
        )
        self.scheduler.add_job(
            self.off_birthday_party,
            DateTrigger(
                datetime.now() + timedelta(days=1)
            )
        )

    async def off_birthday_party(self):
        self.birthday = False
        self.birthday_status_update.cancel()
        await self.change_presence(
            activity=discord.Activity(
                name="BlankPower", type=discord.ActivityType.listening
            )
        )

    @tasks.loop(minutes=5)
    async def birthday_status_update(self):
        await self.change_presence(
            activity=discord.Game(
                name="Today is My Birthday 🥳"
            )
        )


async def main():
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename="discord.log",
        encoding="utf-8",
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    async with ClientSession() as our_client:
        extensions = [
            f"cogs.{x[:-3]}"
            for x in os.listdir("./cogs")
            if x.endswith(".py") and not x.startswith("_")
        ]
        async with BlankBot(
            command_prefix=custom_prefix,
            web_client=our_client,
            initial_extensions=extensions,
        ) as bot:
            await bot.start(os.getenv("DISCORD_BOT_TOKEN", ""))


if __name__ == "__main__":
    asyncio.run(main())
