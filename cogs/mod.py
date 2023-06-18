import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from typing import Any, Union
from .Utils.report import report_error
from .Utils.buttons import Confirm


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def set_prefix(self, ctx, prefix):
        db = self.bot.cluster["guilds"]
        collections = db["custom_prefix"]
        print(collections.find_one({"_id": ctx.guild.id}))
        if res := collections.find_one({"_id": ctx.guild.id}):
            print(res["prefix"])
            if res["prefix"] == prefix:
                await ctx.send("That's already the prefix!")
                return
            else:
                collections.update_one(
                    {"_id": ctx.guild.id}, {"$set": {"prefix": prefix}}
                )
                await ctx.send(f"Changed prefix to `{prefix}`")
        else:
            collections.insert_one({"_id": ctx.guild.id, "prefix": prefix})
            await ctx.send(f"Changed prefix to `{prefix}`")

    async def _kick_ban(
        self,
        guild: discord.Guild,
        member: discord.Member,
        reason: str,
        kick: bool = True,
    ):
        embed = discord.Embed(
            title=f"{'Kicked' if kick else 'Banned'} Successfully",
            colour=discord.Colour.red(),
            timestamp=datetime.now(),
        )
        if member == guild.owner:
            embed.description = (
                f"You can't {'kick' if kick else 'ban'} the owner of the server!"
            )
            return embed
        if member == self.bot.user:
            embed.description = f"I can't {'kick' if kick else 'ban'} myself! :("
            return embed
        embed.description = f"{'Kicked' if kick else 'Banned'} {member} for {reason}"
        embed.colour = discord.Colour.green()
        if kick:
            await member.kick(reason=reason)
        else:
            await member.ban(reason=reason)
        return embed

    async def _helper_kick_ban(
        self,
        ctx: Union[discord.Interaction, commands.Context],
        member: discord.Member,
        reason: str,
        kick: bool = True,
    ):
        user = ctx.user if isinstance(ctx, discord.Interaction) else ctx.author
        send = (
            ctx.response.send_message
            if isinstance(ctx, discord.Interaction)
            else ctx.message.reply
        )
        if member == user:
            view = Confirm(user.id)
            await send(
                content=f"Are you sure you want to {'kick' if kick else 'ban'} yourself?",
                view=view,
            )
            await view.wait()
            if isinstance(ctx, discord.Interaction):
                send = ctx.followup.send
            if view.value is None:
                await send(content="Timed out.")
                return
            elif view.value:
                await send(embed=await self._kick_ban(ctx.guild, member, reason, kick))
            else:
                await send(content="Cancelled.")
        else:
            await send(embed=await self._kick_ban(ctx.guild, member, reason, kick))

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
        await self._helper_kick_ban(interaction, member, reason, True)

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(member="The member to ban")
    @app_commands.describe(reason="The reason for banning the member")
    async def ban_slash(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = None,
    ):
        await self._helper_kick_ban(interaction, member, reason, False)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        await self._helper_kick_ban(ctx, member, reason, True)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):
        await self._helper_kick_ban(ctx, member, reason, False)

    @kick_slash.error
    @ban_slash.error
    async def kick_ban_error(self, interaction, error):
        cmd = "Kick" if interaction.command.name == "kick" else "Ban"
        embed = discord.Embed(
            title=f"{cmd} Failed", colour=discord.Colour.red(), timestamp=datetime.now()
        )
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.avatar.url,
        )
        if isinstance(error, app_commands.errors.MissingPermissions):
            embed.description = (
                f"You don't have the required permissions to {cmd.lower()} members!"
            )
        else:
            embed.description = "Unknown error!"
        await interaction.response.send_message(embed=embed)

    @staticmethod
    async def _purge(channel: Any, limit: int = 100, check=None) -> int:
        return len(await channel.purge(limit=limit, check=check))

    @staticmethod
    def _purge_check(msg, _id):
        return msg.author.id == _id

    @commands.command(name="purge", description="Purge messages in a channel")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, limit_n: int = 100, user: discord.User = None):
        if user:
            deleted = await self._purge(
                ctx.channel, limit_n + 1, check=lambda m: self._purge_check(m, user.id)
            )
        else:
            deleted = await self._purge(ctx.channel, limit_n + 1)
        await ctx.send(f"Purged {deleted} messages!", delete_after=3)

    @app_commands.command(name="purge", description="Purge messages in a channel")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(limit="The number of messages to purge")
    async def purge_slash(
        self,
        interaction: discord.Interaction,
        limit: int = 100,
        user: discord.User = None,
    ):
        await interaction.response.defer()
        if user:
            deleted = await self._purge(
                interaction.channel,
                limit,
                check=lambda m: self._purge_check(m, user.id),
            )
        else:
            deleted = await self._purge(interaction.channel, limit)
        await interaction.channel.send(f"Purged {deleted} messages!", delete_after=3)

    @purge_slash.error
    async def purge_slash_error(self, interaction, error):
        embed = discord.Embed(
            title="Purge Failed",
            colour=discord.Colour.red(),
        )
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.avatar.url,
        )
        if isinstance(error, app_commands.errors.MissingPermissions):
            embed.description = (
                "You don't have the required permissions to purge messages!"
            )
        elif isinstance(error, app_commands.errors.BotMissingPermissions):
            embed.description = (
                "I don't have the required permissions to purge messages!"
            )
        else:
            embed.description = "Unknown error!"
        await interaction.response.send_message(embed=embed)

    @staticmethod
    async def _unban(
        author, guild: discord.Guild, member: discord.User, reason: str = None
    ):
        await guild.unban(member, reason=reason)
        embed = discord.Embed(
            title="Unban Successful",
            description=f"Unbanned {member.mention}!",
            colour=discord.Colour.green(),
            timestamp=datetime.now(),
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(
            text=f"Requested by {author}",
            icon_url=author.avatar.url,
        )
        return embed

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: discord.User, *, reason: str = None):
        try:
            await ctx.send(embed=await self._unban(ctx.author, ctx.guild, member, reason))
        except discord.NotFound:
            embed = discord.Embed(
                title="Unban Failed",
                description="The member you tried to unban is not banned!",
                colour=discord.Colour.red(),
                timestamp=datetime.now(),
            )
            embed.set_footer(
                text=f"Requested by {ctx.author}",
                icon_url=ctx.author.avatar.url,
            )
            await ctx.send(embed=embed)

    @app_commands.command(name="unban", description="Unban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(member="The member to unban")
    @app_commands.describe(reason="The reason for unbanning the member")
    async def unban_slash(
        self, interaction: discord.Interaction, member: discord.User, reason: str = None
    ):
        await interaction.response.send_message(
            embed=await self._unban(interaction.user, interaction.guild, member, reason)
        )

    @unban_slash.error
    async def unban_slash_error(self, interaction, error):
        embed = discord.Embed(
            title="Unban Failed",
            colour=discord.Colour.red(),
            timestamp=datetime.now(),
        )
        if isinstance(error, discord.NotFound) or isinstance(error, app_commands.CommandInvokeError):
            embed.description = "The member you tried to unban is not banned!"
        elif isinstance(error, app_commands.errors.MissingPermissions):
            embed.description = (
                "You don't have the required permissions to unban members!"
            )
        elif isinstance(error, app_commands.errors.BotMissingPermissions):
            embed.description = (
                "I don't have the required permissions to unban members!"
            )
        else:
            embed.description = "Unknown error!"
            await report_error(
                error_webhook_url=self.bot.unknown_error_webhook_url,
                session=self.bot.web_client,
                error=error,
                content="Unban Slash Command Error",
                author=interaction.user,
                guild=interaction.guild,
                channel=interaction.channel,
                username="Unknown Error || BlankBot",
            )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Mod(bot))
