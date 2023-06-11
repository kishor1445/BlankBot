import discord
import os
import aiohttp
from discord.ext import commands
import discord.ui as ui
from discord import Webhook
from discord import app_commands
import traceback


class SuggestionModal(ui.Modal, title="Suggest a feature"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
    feature = ui.TextInput(
        label="What feature would you like to suggest?", style=discord.TextStyle.short
    )
    description = ui.TextInput(label="Description:", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        web_hook = Webhook.from_url(os.getenv("SUGGESTION_WEBHOOK_URL", ""), session=self.bot.web_client)
        await web_hook.send(
            f"Author: {interaction.user} [{interaction.user.id}]\n\nFeature: {self.feature}\n\n"
            f"Description: {self.description}"
        )
        await interaction.response.send_message(
            "Thanks for your feedback!", ephemeral=True
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )

        web_hook = Webhook.from_url(os.getenv("UNKNOWN_ERROR_WEBHOOK_URL", ""), session=self.bot.web_client)
        await web_hook.send(
            f"Type: {type(error)}\n\nError: {error}\n\nAuthor: {interaction.user} [{interaction.user.id}]",
            username="Error in Suggestion Modal || Webhook"
        )


class Improvement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="suggest", description="Suggest a feature for the bot!")
    async def suggest_slash(self, interaction: discord.Interaction):
        print("Activated")
        await interaction.response.send_modal(SuggestionModal(self.bot))
        print("Finished")


async def setup(bot):
    await bot.add_cog(
        Improvement(bot), guild=discord.Object(int(os.getenv("TEST_GUILD_ID")))
    )
