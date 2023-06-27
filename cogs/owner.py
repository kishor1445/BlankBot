import discord
from discord.ext import commands
from .Utils.buttons import Confirm
from datetime import datetime


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sync", description="Syncs slash commands")
    @commands.is_owner()
    async def sync(self, ctx):
        await self.bot.tree.sync()
        await ctx.send("Synced!")

    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown(self, ctx):
        view = Confirm(ctx.author.id)
        embed = discord.Embed(
            title="Shutdown Request Received",
            description="Are you sure you want to shutdown the bot?",
            color=discord.Color.blurple(),
            timestamp=datetime.now(),
        )
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )
        msg = await ctx.send(embed=embed, view=view)
        await view.wait()
        if view.value is None:
            await msg.reply("You took too long to respond!")
            return
        elif view.value:
            await msg.reply("Shutting down... bye bye! 👋")
            await self.bot.close()
        else:
            await msg.reply("Shutdown cancelled!")

    @commands.command(name="bot_birthday")
    @commands.is_owner()
    async def birthday_party(self, ctx, action: bool = True):
        self.bot.birthday = action
        await ctx.send(f"Bot birthday is now {'enabled' if action else 'disabled'}!")


async def setup(bot):
    await bot.add_cog(Owner(bot))
