import discord


class Confirm(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=30)
        self.value = None
        self.user_id = user_id

    @discord.ui.button(
        label="Yes", style=discord.ButtonStyle.red, custom_id="confirm_btn"
    )
    async def confirm(self, interaction: discord.Interaction, _):
        self.value = True
        for x in self.children:
            x.disabled = True
            if x.custom_id == "cancel_btn":
                x.style = discord.ButtonStyle.grey
        await interaction.response.edit_message(view=self)
        self.stop()

    @discord.ui.button(
        label="No", style=discord.ButtonStyle.green, custom_id="cancel_btn"
    )
    async def cancel(self, interaction: discord.Interaction, _):
        self.value = False
        for x in self.children:
            x.disabled = True
            if x.custom_id == "confirm_btn":
                x.style = discord.ButtonStyle.grey
        await interaction.response.edit_message(view=self)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self.user_id:
            return True
        await interaction.response.send_message("This is not for you!", ephemeral=True)
        return False

