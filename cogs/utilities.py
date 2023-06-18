import discord
from discord.ext import commands
from discord import app_commands
from .events import DISCORD_INVITE_LINK


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def _server_info(guild: discord.Guild):
        embed = (
            discord.Embed(
                title=guild.name,
                description=guild.description,
                color=discord.Color.blue(),
            )
            .add_field(name="Server Owner", value=f"{guild.owner.mention}")
            .add_field(name="Server ID", value=f"{guild.id}")
            .add_field(
                name="Server Created At",
                value=f"{guild.created_at.strftime('%m/%d/%Y, %I:%M %p UTC')}",
                inline=False,
            )
            .add_field(name="Member Count", value=f"{guild.member_count}")
            .add_field(name="No. of roles", value=f"{len(guild.roles) - 1}")
            .add_field(name="No. of text channels", value=f"{len(guild.text_channels)}")
            .add_field(
                name="No. of voice channels", value=f"{len(guild.voice_channels)}"
            )
            .set_author(name=f"{guild.owner}", icon_url=f"{guild.owner.avatar.url}")
        )
        if guild.icon:
            embed.set_thumbnail(url=f"{guild.icon.url}")
        return embed

    @commands.command()
    async def server_info(self, ctx):
        await ctx.send(embed=await self._server_info(ctx.guild))

    @app_commands.command(name="server_info", description="Get info about the server")
    async def server_info_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=await self._server_info(interaction.guild)
        )

    @commands.command(name="say", description="Make the bot say something")
    async def say(self, ctx, *, message: str):
        if DISCORD_INVITE_LINK.match(message):
            await ctx.send(
                f"{ctx.author.mention}, Really? You think I'm gonna do that?"
            )
            return
        await ctx.send(message)

    @app_commands.command(name="say", description="Make the bot say something")
    @app_commands.describe(message="What the bot should say")
    async def say_slash(self, interaction: discord.Interaction, *, message: str):
        if DISCORD_INVITE_LINK.search(message):
            await interaction.response.send_message(
                f"{interaction.user.mention}, Really? You think I'm gonna do that?",
                ephemeral=True,
            )
            return
        await interaction.response.send_message("Got it!", ephemeral=True)
        await interaction.channel.send(message)


async def setup(bot):
    await bot.add_cog(Utilities(bot))
