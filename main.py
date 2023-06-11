import asyncio
import os
import discord
from discord.ext import commands
from typing import Optional, List
from aiohttp import ClientSession
from dotenv import load_dotenv
import logging
import logging.handlers

load_dotenv()


class BlankBot(commands.Bot):
    def __init__(
        self,
        *args,
        initial_extensions: List[str],
        web_client: ClientSession,
        testing_guild_id: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(*args, intents=discord.Intents.all(), **kwargs)
        self.web_client = web_client
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_extensions
        self.unknown_error_webhook_url = os.getenv("UNKNOWN_ERROR_WEBHOOK_URL", "")
        self.suggestion_webhook_url = os.getenv("SUGGESTION_WEBHOOK_URL", "")

    async def setup_hook(self) -> None:
        for extension in self.initial_extensions:
            await self.load_extension(extension)

        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    async def on_ready(self):
        print(f"Logged in as {self.user} [ID: {self.user.id}]")


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
            command_prefix="^",
            web_client=our_client,
            initial_extensions=extensions,
            testing_guild_id=int(os.getenv("TEST_GUILD_ID", 0)),
        ) as bot:
            await bot.start(os.getenv("DISCORD_BOT_TOKEN", ""))


if __name__ == "__main__":
    asyncio.run(main())
