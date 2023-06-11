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
    async def ban(self, ctx, member: discord.Member, *, reason: str=None):
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

    @commands.command()
    async def server_info(self, ctx):
        embed = discord.Embed(
            title=ctx.guild.name,
            description=ctx.guild.description,
            color=discord.Color.blue()
        )
        embed.add_field(name="Server Owner", value=f"{ctx.guild.owner.mention}")
        embed.add_field(name="Server ID", value=f"{ctx.guild.id}")
        embed.add_field(name="Server Created At", value=f"{ctx.guild.created_at.strftime('%m/%d/%Y, %I:%M %p UTC')}", inline=False)
        embed.add_field(name="Member Count", value=f"{ctx.guild.member_count}")
        embed.add_field(name="No. of channels", value=f"{len(ctx.guild.channels)}")
        embed.add_field(name="No. of roles", value=f"{len(ctx.guild.roles)}")
        embed.set_author(name=f"{ctx.guild.owner}", icon_url=f"{ctx.guild.owner.avatar.url}")
        if ctx.guild.icon:
            embed.set_thumbnail(url=f"{ctx.guild.icon.url}")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Mod(bot))
