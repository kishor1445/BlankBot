import discord
import os
from discord.ext import commands
import discord.ui as ui
from discord import Webhook
from discord import app_commands


class SuggestionModal(ui.Modal, title="Suggest a feature"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    feature = ui.TextInput(
        label="What feature would you like to suggest?", style=discord.TextStyle.short
    )
    description = ui.TextInput(label="Description:", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        web_hook = Webhook.from_url(
            os.getenv("SUGGESTION_WEBHOOK_URL", ""), session=self.bot.web_client
        )
        embed = discord.Embed(
            title="New Suggestion!",
            description=f"Feature: {self.feature}\n\nDescription: "
            + str(self.description),
            colour=discord.Colour.blurple(),
        )
        embed.set_footer(
            text=f"Author: {interaction.user} [{interaction.user.id}]",
            icon_url=interaction.user.avatar.url,
        )
        embed.add_field(
            name="Server", value=f"{interaction.guild} [{interaction.guild.id}]"
        )
        embed.add_field(
            name="Channel", value=f"{interaction.channel} [{interaction.channel.id}]"
        )
        embed.add_field(name="Timestamp", value=f"{interaction.created_at}")
        await web_hook.send(embed=embed, username="Suggestion || Webhook")
        await interaction.response.send_message(
            "Thanks for your feedback!", ephemeral=True
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )

        web_hook = Webhook.from_url(
            os.getenv("UNKNOWN_ERROR_WEBHOOK_URL", ""), session=self.bot.web_client
        )
        await web_hook.send(
            f"Type: {type(error)}\n\nError: {error}\n\nAuthor: {interaction.user} [{interaction.user.id}]",
            username="Error in Suggestion Modal || Webhook",
        )


class Improvement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="suggest", description="Suggest a feature for the bot!")
    async def suggest_slash(self, interaction: discord.Interaction):
        await interaction.response.send_modal(SuggestionModal(self.bot))

    @commands.command(name="suggest", description="Suggest a feature for the bot!")
    async def suggest(self, ctx):
        await ctx.message.reply("Please use the slash command for this!")


async def setup(bot):
    await bot.add_cog(Improvement(bot))
