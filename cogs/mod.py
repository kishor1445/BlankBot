import discord
from discord.ext import commands


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if member == ctx.guild.owner:
            await ctx.send("You can't kick the owner of the server!")
            return
        if member == self.bot.user:
            await ctx.send("I can't kick myself! :(")
            return
        if member == ctx.author:
            await ctx.send("Are you sure you want to kick yourself?")
            res = await self.bot.wait_for(
                "message",
                timeout=20,
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            )
            if res.content.lower() in ("yes", "y", "yeah", "yeh", "yah"):
                await member.kick(reason=reason)
                await ctx.send(f"Kicked {member} for {reason}")
            else:
                await ctx.send("Cancelled.")
        else:
            await member.kick(reason=reason)
            await ctx.send(f"Kicked {member} for {reason}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if member == ctx.guild.owner:
            await ctx.send("You can't ban the owner of the server!")
            return
        if member == self.bot.user:
            await ctx.send("I can't ban myself! :(")
            return
        if member == ctx.author:
            await ctx.send("Are you sure you want to ban yourself?")
            res = await self.bot.wait_for(
                "message",
                timeout=20,
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            )
            if res.content.lower() in ("yes", "y", "yeah", "yeh", "yah"):
                await member.ban(reason=reason)
                await ctx.send(f"Banned {member} for {reason}")
            else:
                await ctx.send("Cancelled.")
        else:
            await member.ban(reason=reason)
            await ctx.send(f"Banned {member} for {reason}")


async def setup(bot):
    await bot.add_cog(Mod(bot))
