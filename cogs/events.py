import asyncio
import discord
import re
from discord.ext import commands
from .Utils.report import report_error

DISCORD_INVITE_LINK = re.compile(
    r"(?:https?://)?discord(?:(?:app)?\.com/invite|\.gg)/?[a-zA-Z0-9]+/?"
)


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        embed = discord.Embed(
            title="Error!",
            colour=discord.Colour.red(),
            timestamp=ctx.message.created_at,
        )
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )
        if isinstance(error, asyncio.TimeoutError):
            embed.description = "You took too long to respond! I can't wait forever."
        elif isinstance(error, commands.NotOwner):
            embed.description = (
                "You're not the owner of this bot! Only the owner can run this command."
            )
        elif isinstance(error, commands.MissingPermissions):
            embed.description = (
                "You don't have the required permissions to run this command."
            )
        elif isinstance(error, commands.BotMissingPermissions):
            embed.description = (
                "I don't have the required permissions to run this command."
            )
        elif isinstance(error, commands.CommandNotFound):
            embed.description = "That command doesn't exist! use `suggest` slash command to suggest a command."
        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = (
                "You're missing a required argument! Check the help command."
            )
        elif isinstance(error, commands.MemberNotFound):
            embed.description = "I couldn't find that member!"
        elif isinstance(error, commands.BadArgument):
            embed.description = "You gave me a bad argument! Check the help command."
        elif isinstance(error, commands.CheckFailure):
            embed.description = "You don't have permission to run this command!"
        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = (
                f"This command is on cooldown! Try again in {error.retry_after:.2f}s"
            )
        elif isinstance(error, commands.NoPrivateMessage):
            embed.description = "This command can't be used in DMs!"
        elif isinstance(error, commands.DisabledCommand):
            embed.description = "This command is disabled!"
        elif isinstance(error, commands.TooManyArguments):
            embed.description = "You gave me too many arguments!"
        elif isinstance(error, commands.UserInputError):
            embed.description = "You gave me bad input!"
        else:
            await report_error(
                error_webhook_url=self.bot.unknown_error_webhook_url,
                session=self.bot.web_client,
                error=error,
                content=ctx.message.content,
                author=ctx.author,
                guild=ctx.guild,
                channel=ctx.channel,
                username="Unknown Error || BlankBot",
            )
            embed.description = "An unknown error occurred!"

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return
        if isinstance(msg.channel, discord.DMChannel):
            if re.search(r"(happy|belated) birthday", msg.content.lower()):
                if self.bot.birthday:
                    await msg.reply("Thank you! ❤️ ^^")
                    return
                await msg.reply(
                    "Today is not my birthday! My birthday is on 11th of June"
                )
        dc_invite = re.search(DISCORD_INVITE_LINK, msg.content)
        if dc_invite and not msg.author.guild_permissions.administrator:
            db = self.bot.cluster["guilds"]
            collection = db["link_perms"]
            users = collection.find_one({"_id": msg.guild.id})
            if users is not None:
                users = users["users"]
            else:
                users = []
            if msg.author.id in users:
                return
            await msg.delete()
            await msg.channel.send(
                f"{msg.author.mention}, you can't send discord invite links here!\n"
                f"Ask a moderator to whitelist you if you want to send discord invite "
                f"links by using `link_perm` command."
            )

        msg_ = msg.content.split()[0]
        if msg_ == f"<@!{self.bot.user.id}>" or msg_ == f"<@{self.bot.user.id}>":
            db = self.bot.cluster["guilds"]
            collection = db["custom_prefix"]
            data = collection.find_one({"_id": msg.guild.id})
            if data is None:
                prefix = "^"
            else:
                prefix = data["prefix"]
            await msg.reply(f"My prefix for this server is `{prefix}`")


async def setup(bot):
    await bot.add_cog(Events(bot))
