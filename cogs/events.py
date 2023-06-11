import asyncio
import discord
from discord.ext import commands
from discord import Webhook


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
        if isinstance(error, asyncio.TimeoutError):
            embed.description = "You took too long to respond! I can't wait forever."
        elif isinstance(error, commands.MissingPermissions):
            embed.description = (
                "You don't have the required permissions to run this command."
            )
        elif isinstance(error, commands.BotMissingPermissions):
            embed.description = (
                "I don't have the required permissions to run this command."
            )
        elif isinstance(error, commands.CommandNotFound):
            embed.description = (
                "That command doesn't exist! use `^suggest` to suggest a command."
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = (
                "You're missing a required argument! Check the help command."
            )
        elif isinstance(error, commands.BadArgument):
            embed.description = "You gave me a bad argument! Check the help command."
        elif isinstance(error, commands.NotOwner):
            embed.description = (
                "You're not the owner of this bot! Only the owner can run this command."
            )
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
        elif isinstance(error, commands.CommandInvokeError):
            embed.description = "An error occurred while running this command!"
        elif isinstance(error, commands.TooManyArguments):
            embed.description = "You gave me too many arguments!"
        elif isinstance(error, commands.UserInputError):
            embed.description = "You gave me bad input!"
        elif isinstance(error, commands.CommandError):
            embed.description = "An error occurred while running this command!"
        else:
            web_hook = Webhook.from_url(
                self.bot.unknown_error_webhook_url, session=self.bot.web_client
            )
            await web_hook.send(
                f"Error: {error}\n\nContent: {ctx.message.content}\n\nAuthor: {ctx.author} [{ctx.author.id}]\n\n"
                f"Guild: {ctx.guild} [{ctx.guild.id}]\n\nChannel: {ctx.channel} [{ctx.channel.id}]\n"
                f"{'-'*50}",
                username="Unknown Error || BlankBot",
            )
            embed.description = "An unknown error occurred!"

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Events(bot))
