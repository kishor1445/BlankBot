from discord.ext import commands


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sync", description="Syncs slash commands")
    @commands.is_owner()
    async def sync_slash(self, ctx):
        await self.bot.tree.sync()
        await ctx.send("Synced!")


async def setup(bot):
    await bot.add_cog(Owner(bot))
