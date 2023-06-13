import discord
from discord.ext import commands
from discord import app_commands


class Confirm(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=30)
        self.value = None
        self.user_id = user_id

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.red, custom_id="confirm_btn")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        for x in self.children:
            x.disabled = True
            if x.custom_id == "cancel_btn":
                x.style = discord.ButtonStyle.grey
        await interaction.response.edit_message(view=self)
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.green, custom_id="cancel_btn")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
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


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    async def _kick(self, guild: discord.Guild, member: discord.Member, reason: str):
        if member == guild.owner:
            embed = discord.Embed(
                title="Kick Failed",
                description="You can't kick the owner of the server!",
                colour=discord.Colour.red(),
            )
            return embed
        if member == self.bot.user:
            embed = discord.Embed(
                title="Kick Failed",
                description="I can't kick myself! :(",
                colour=discord.Colour.red(),
            )
            return embed
        embed = discord.Embed(
            title="Kick Successful",
            description=f"Kicked {member} for {reason}",
            colour=discord.Colour.green(),
        )
        await member.kick(reason=reason)
        return embed

    @commands.command()
    async def server_info(self, ctx):
        await ctx.send(embed=await self._server_info(ctx.guild))

    @app_commands.command(name="server_info", description="Get info about the server")
    async def server_info_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=await self._server_info(interaction.guild)
        )

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.describe(member="The member to kick")
    @app_commands.describe(reason="The reason for kicking the member")
    async def kick_slash(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = None,
    ):
        if member == interaction.user:
            view = Confirm(interaction.user.id)
            await interaction.response.send_message(
                "Are you sure you want to kick yourself?", view=view
            )
            await view.wait()
            if view.value is None:
                await interaction.message.send_message("Timed out.")
                return
            elif view.value:
                await interaction.message.send_message(
                    embed=await self._kick(interaction.guild, member, reason)
                )
            else:
                await interaction.message.send_message("Cancelled.")
        else:
            await interaction.message.send_message(
                embed=await self._kick(interaction.guild, member, reason)
            )

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        if member == ctx.author:
            view = Confirm(ctx.author.id)
            msg = await ctx.send("Are you sure you want to kick yourself?", view=view)
            await view.wait()
            if view.value is None:
                for x in view.children:
                    x.disabled = True
                await msg.edit(content="[**Time Out**] Are you sure you want to kick yourself?", view=view)
                return
            elif view.value:
                await ctx.send(embed=await self._kick(ctx.guild, member, reason))
            else:
                await msg.reply(content="Cancelled.")
        else:
            await ctx.send(embed=await self._kick(ctx.guild, member, reason))

    @kick_slash.error
    async def kick_slash_error(self, interaction: discord.Interaction, error: Exception):
        if isinstance(error, commands.MissingPermissions):
            await interaction.response.send_message("You can't do that!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await interaction.response.send_message(
                "You need to specify a member to kick!"
            )
        elif isinstance(error, commands.MemberNotFound):
            await interaction.response.send_message("Member not found!")
        elif isinstance(error, commands.CommandInvokeError):
            await interaction.response.send_message(
                "I don't have permission to do that!"
            )
        else:
            await interaction.response.send_message(
                "An unknown error occurred. Please try again later."
            )
            raise error

async def setup(bot):
    await bot.add_cog(Mod(bot))
