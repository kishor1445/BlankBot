import discord
import os
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from typing import Union


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _ping(self, ctx: Union[discord.Interaction, commands.Context]):
        user = ctx.user if isinstance(ctx, discord.Interaction) else ctx.author
        embed = discord.Embed(
            title="Pong!",
            description=f"Latency: {round(self.bot.latency * 1000)}ms",
            timestamp=datetime.now(),
        )
        embed.set_footer(
            text=f"Requested by {user}",
            icon_url=user.avatar.url,
        )
        return embed

    @app_commands.command(name="ping", description="Get the bots latency!")
    async def ping_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=self._ping(interaction))

    @commands.command()
    async def ping(self, ctx):
        embed = discord.Embed(
            title="Pong!",
            description=f"Latency: {round(self.bot.latency * 1000)}ms",
            timestamp=ctx.message.created_at,
        )
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )
        await ctx.send(embed=embed)

    def _about(self, ctx: Union[discord.Interaction, commands.Context]):
        dev = self.bot.get_user(int(os.getenv("BOT_OWNER_ID")))
        user = ctx.user if isinstance(ctx, discord.Interaction) else ctx.author
        embed = (
            discord.Embed(
                title="About",
                description=f"A discord bot made using discord.py [{discord.__version__}]",
                color=discord.Color.blue(),
                timestamp=datetime.now(),
            )
            .add_field(name="Developer", value=f"{dev if dev else 'Unknown'}")
            .add_field(name="Developer ID", value=f"{dev.id}")
            .add_field(name="No. of Servers", value=f"{len(self.bot.guilds)}")
            .add_field(name="No. of Commands", value=f"{len(self.bot.commands)}")
            .add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms")
            .add_field(
                name="Source Code",
                value="[GitHub](https://github.com/Kishor1445/BlankBot)",
            )
            .set_footer(
                text=f"Requested by {user}",
                icon_url=user.avatar.url,
            )
            .set_thumbnail(url=self.bot.user.avatar.url)
        )
        return embed

    @commands.command()
    async def about(self, ctx):
        await ctx.send(embed=self._about(ctx))

    @app_commands.command(name="about", description="Get info about the bot")
    async def about_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=self._about(interaction))


async def setup(bot):
    await bot.add_cog(Info(bot))
