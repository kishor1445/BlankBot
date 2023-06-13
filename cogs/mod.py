import discord
from discord.ext import commands
from discord import app_commands


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
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):
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

    @staticmethod
    async def _server_info_embed(guild: discord.Guild):
        embed = discord.Embed(
            title=guild.name, description=guild.description, color=discord.Color.blue()
        )
        embed.add_field(name="Server Owner", value=f"{guild.owner.mention}")
        embed.add_field(name="Server ID", value=f"{guild.id}")
        embed.add_field(
            name="Server Created At",
            value=f"{guild.created_at.strftime('%m/%d/%Y, %I:%M %p UTC')}",
            inline=False,
        )
        embed.add_field(name="Member Count", value=f"{guild.member_count}")
        embed.add_field(name="No. of roles", value=f"{len(guild.roles) - 1}")
        embed.add_field(name="No. of text channels", value=f"{len(guild.text_channels)}")
        embed.add_field(name="No. of voice channels", value=f"{len(guild.voice_channels)}")
        embed.set_author(name=f"{guild.owner}", icon_url=f"{guild.owner.avatar.url}")
        if guild.icon:
            embed.set_thumbnail(url=f"{guild.icon.url}")
        return embed

    @commands.command()
    async def server_info(self, ctx):
        await ctx.send(embed=await self._server_info_embed(ctx.guild))

    @app_commands.command(name="server_info", description="Get info about the server")
    async def server_info_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=await self._server_info_embed(interaction.guild)
        )


async def setup(bot):
    await bot.add_cog(Mod(bot))
