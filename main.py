"""
BlankBot copyright under: MIT License
Copyright © 2023 Kishor Ramanan
"""

import os
import sys
import asyncio
import logging
import logging.handlers
import subprocess as sp  # nosec: B404
from datetime import datetime, timedelta

import discord
import requests
import pyfiglet
from dotenv import load_dotenv
from pymongo import MongoClient
from rich.console import Console
from aiohttp import ClientSession
from discord.ext import commands, tasks
from apscheduler.triggers.date import DateTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()
CONSOLE = Console()


async def custom_prefix(bot, message) -> str:
    """
    Returns the guild prefix from database if found else returns default prefix

    Default prefix: ^
    :param bot:
    :param message:
    :return:
    """
    if message.guild is None:  # If message is sent in DM
        return "^"
    prefix_db = bot.cluster["guilds"]["custom_prefix"]
    prefix = prefix_db.find_one({"_id": message.guild.id})
    if prefix is None:  # If guild prefix is not found in database
        return "^"
    return prefix["prefix"]


class BlankBot(commands.Bot):
    """
    BlankBot class to initialize the bot
    """

    console = CONSOLE
    unknown_error_webhook_url = os.getenv("UNKNOWN_ERROR_WEBHOOK_URL", "")
    suggestion_webhook_url = os.getenv("SUGGESTION_WEBHOOK_URL", "")
    cluster = MongoClient(os.getenv("MONGO_DB_URL"))

    def __init__(
        self,
        *args,
        web_client: ClientSession,
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
        self.birthday = False
        self.scheduler = AsyncIOScheduler()
        if datetime.now() > datetime(
            year=int(datetime.now().__format__("%Y")), month=6, day=11
        ):
            on_date = datetime(
                int(datetime.now().__format__("%Y")) + 1, month=6, day=11
            )
        else:
            on_date = datetime(int(datetime.now().__format__("%Y")), month=6, day=11)
        self.scheduler.add_job(self.on_birthday_party, DateTrigger(on_date))

    async def setup_hook(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")
        CONSOLE.print(
            f"[magenta]{pyfiglet.figlet_format(f'{self.user.name}', 'poison')}[/magenta]"
        )
        CONSOLE.print(
            f"[magenta]\t\tBlankBot copyright under: MIT License[/magenta]\t\t\n"
            + f"[magenta]\t\tCopyright © 2023 Kishor Ramanan\t\t\t"
        )
        extensions = [
            f"cogs.{x[:-3]}"
            for x in os.listdir("./cogs")
            if x.endswith(".py") and not x.startswith("_")
        ]
        for extension in extensions:
            await self.load_extension(extension)
        await self.tree.sync()
        self.scheduler.start()

    async def on_ready(self) -> None:
        """
        Called when the bot successfully connects to discord
        :return:
        """
        CONSOLE.print(
            f"[bold green][✓] Successfully Logged In as {self.user} [ID: {self.user.id}]![/bold green]"
        )

    async def on_birthday_party(self):
        """
        Calls on 11th of June every year to turn on birthday party for BlankBot
        :return:
        """
        self.birthday = True
        self.birthday_status_update.start()  # pylint: disable=no-member
        on_date = datetime(datetime.now().year + 1, 6, 11)  # 11th of June
        self.scheduler.add_job(self.on_birthday_party, DateTrigger(on_date))
        self.scheduler.add_job(
            self.off_birthday_party, DateTrigger(datetime.now() + timedelta(days=1))
        )

    async def off_birthday_party(self):
        """
        Calls on 12th of June every year to turn off birthday party for BlankBot
        :return:
        """
        self.birthday = False
        self.birthday_status_update.cancel()  # pylint: disable=no-member
        await self.change_presence(
            activity=discord.Activity(
                name="BlankPower", type=discord.ActivityType.listening
            )
        )

    @tasks.loop(minutes=5)
    async def birthday_status_update(self):
        """
        Called every 5 minutes to update the status of BlankBot to birthday status
        :return:
        """
        await self.change_presence(activity=discord.Game(name="Today is My Birthday 🥳"))


def update() -> None:
    """
    Updates the BlankBot using git and restarts the BlankBot
    :return:
    """
    CONSOLE.print("[bold blue]Updating BlankBot...[/bold blue]")
    try:
        sp.check_call(["git", "pull"])  # nosec: B603, B607
    except sp.CalledProcessError:
        CONSOLE.print("[bold red]Update Failed![/bold red]")
        CONSOLE.print(
            "[bold red] [!] Please ensure that you have git installed![/bold red]"
        )
        return
    CONSOLE.print("[bold green][✓] Update Successful![/bold green]")
    CONSOLE.print("[bold blue]Restarting BlankBot...[/bold blue]")
    os.execv(sys.executable, ["python"] + sys.argv)  # nosec: B606


def check_update() -> None:
    """
    Checks for BlankBot updates using version.txt
    :return:
    """
    CONSOLE.print("[bold blue]Checking for updates...[/bold blue]")
    with open("version.txt", encoding="utf-8") as version_file:
        version = version_file.read()
    if (
        version.strip()
        >= requests.get(
            "https://raw.githubusercontent.com/Kishor1445/BlankBot/main/version.txt",
            timeout=10,
        ).text.strip()
    ):
        CONSOLE.print("[bold green][✓] No New Update Available[/bold green]")
    else:
        CONSOLE.print("[bold purple][!] New Update Available[/bold purple]")
        update()


def install_requirements() -> None:
    """
    Installs BlankBot requirements using pip
    :return:
    """
    CONSOLE.print("[bold blue]Installing requirements...[/bold blue]")
    try:
        sp.check_call(["pip", "install", "-r", "requirements.txt"])  # nosec: B603, B607
    except sp.CalledProcessError:
        CONSOLE.print("[bold red]Installation Failed![/bold red]")
        return
    CONSOLE.print("[bold green][✓] Installation Successful![/bold green]")


async def main():
    """
    Main function to initialize and start the BlankBot
    :return:
    """
    check_update()
    install_requirements()
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
        async with BlankBot(
            command_prefix=custom_prefix,
            web_client=our_client,
        ) as bot:
            await bot.start(os.getenv("DISCORD_BOT_TOKEN", ""))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        CONSOLE.print("\n[bold red]Keyboard Interrupt Detected![/bold red]")
        CONSOLE.print("[bold blue]Exiting...[/bold blue]")
        exit(0)
