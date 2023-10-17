import discord
from discord.ext import commands


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="avatar", aliases=["av"])
    async def avatar(self, ctx, user: discord.User = None):
        user = user or ctx.author
        await ctx.send(user.display_avatar.url)


async def setup(bot):
    await bot.add_cog(User(bot))
