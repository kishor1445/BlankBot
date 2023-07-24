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
        if res := collections.find_one({"_id": ctx.guild.id}):
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
            await ctx.send(
                embed=await self._unban(ctx.author, ctx.guild, member, reason)
            )
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
        if isinstance(error, discord.NotFound) or isinstance(
            error, app_commands.CommandInvokeError
        ):
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

    async def _warn(self, ctx, member: discord.Member, reason: str = None):
        mod = ctx.user if isinstance(ctx, discord.Interaction) else ctx.author
        db = self.bot.cluster["guilds"]
        collection = db["warns"]
        embed = discord.Embed(
            colour=discord.Colour.green(),
            timestamp=datetime.now(),
        )
        if reason:
            if not collection.find_one({"_id": member.id}):
                collection.insert_one(
                    {
                        "_id": member.id,
                        "warns": [
                            {
                                "reason": reason,
                                "moderator": mod.id,
                            }
                        ],
                    }
                )
            else:
                collection.update_one(
                    {"_id": member.id},
                    {
                        "$push": {
                            "warns": {
                                "reason": reason,
                                "moderator": mod.id,
                            }
                        }
                    },
                )
            embed.title = "Warning"
            embed.description = reason
            embed.add_field(name="Moderator", value=mod.mention)
            embed.set_footer(
                text=f"Requested by {mod}",
                icon_url=mod.avatar.url,
            )
        else:
            embed.title = "Warning Records"
            data = collection.find_one({"_id": member.id})
            if data:
                embed.description = f"All previous warnings for {member.mention}!"
                for num, warn in enumerate(data["warns"]):
                    moderator = ctx.guild.get_member(warn["moderator"])
                    embed.add_field(
                        name=f"ID: {num+1} || Mod: {moderator}",
                        value=warn["reason"],
                        inline=False,
                    )
            else:
                embed.description = f"No warnings found for {member.mention}!"
        return embed

    @commands.command(name="warn", aliases=["warns"])
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = None):
        if reason:
            await ctx.send(member.mention, embed=await self._warn(ctx, member, reason))
        else:
            await ctx.send(embed=await self._warn(ctx, member))

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(member="The member to warn")
    @app_commands.describe(reason="The reason for warning the member")
    async def warn_slash(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        *,
        reason: str = None,
    ):
        if reason:
            await interaction.response.send_message(
                member.mention, embed=await self._warn(interaction, member, reason)
            )
        else:
            await interaction.response.send_message(
                embed=await self._warn(interaction, member)
            )

    @warn_slash.error
    async def warn_slash_error(self, interaction, error):
        embed = discord.Embed(
            title="Warn Failed",
            colour=discord.Colour.red(),
            timestamp=datetime.now(),
        )
        if isinstance(error, app_commands.errors.MissingPermissions):
            embed.description = (
                "You don't have the required permissions to warn members!"
            )
        elif isinstance(error, app_commands.errors.BotMissingPermissions):
            embed.description = "I don't have the required permissions to warn members!"
        else:
            embed.description = "Unknown error!"
            await report_error(
                error_webhook_url=self.bot.unknown_error_webhook_url,
                session=self.bot.web_client,
                error=error,
                content="Warn Slash Command Error",
                author=interaction.user,
                guild=interaction.guild,
                channel=interaction.channel,
                username="Unknown Error || BlankBot",
            )
        await interaction.response.send_message(embed=embed)

    async def _unwarn(self, member: discord.Member, index: int = None):
        db = self.bot.cluster["guilds"]
        collection = db["warns"]
        embed = discord.Embed(
            colour=discord.Colour.green(),
            timestamp=datetime.now(),
        )
        if data := collection.find_one({"_id": member.id}):
            if index:
                try:
                    popped = data["warns"].pop(index)
                    collection.update_one(
                        {"_id": member.id},
                        {"$set": {"warns": data["warns"]}},
                    )
                    embed.description = (
                        f"Unwarned {member.mention} `{popped['reason']}`!"
                    )
                except IndexError:
                    embed.description = (
                        "Invalid ID number! use `warns` to see all warnings!"
                    )
            else:
                collection.delete_one({"_id": member.id})
                embed.description = f"Unwarned {member.mention} from all warnings!"
        else:
            embed.description = f"No warnings found for {member.mention}!"
        return embed

    @commands.command(name="unwarn", aliases=["uwarn", "unwarns", "uwarns"])
    @commands.has_permissions(manage_messages=True)
    async def unwarn(self, ctx, member: discord.Member, index: int = None):
        if index:
            await ctx.send(embed=await self._unwarn(member, index - 1))
        else:
            await ctx.send(embed=await self._unwarn(member))

    @app_commands.command(name="unwarn", description="Unwarn a member")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(member="The member to unwarn")
    @app_commands.describe(index="The ID of the warn to remove")
    async def unwarn_slash(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        index: int = None,
    ):
        if index:
            await interaction.response.send_message(
                embed=await self._unwarn(member, index - 1)
            )
        else:
            await interaction.response.send_message(embed=await self._unwarn(member))

    @unwarn_slash.error
    async def unwarn_slash_error(self, interaction, error):
        embed = discord.Embed(
            title="Unwarn Failed",
            colour=discord.Colour.red(),
            timestamp=datetime.now(),
        )
        if isinstance(error, app_commands.errors.MissingPermissions):
            embed.description = (
                "You don't have the required permissions to unwarn members!"
            )
        elif isinstance(error, app_commands.errors.BotMissingPermissions):
            embed.description = (
                "I don't have the required permissions to unwarn members!"
            )
        else:
            embed.description = "Unknown error!"
            await report_error(
                error_webhook_url=self.bot.unknown_error_webhook_url,
                session=self.bot.web_client,
                error=error,
                content="Unwarn Slash Command Error",
                author=interaction.user,
                guild=interaction.guild,
                channel=interaction.channel,
                username="Unknown Error || BlankBot",
            )
        await interaction.response.send_message(embed=embed)

    async def _link(self, guild_id, member, action):
        db = self.bot.cluster["guilds"]
        collection = db["link_perms"]
        embed = discord.Embed(
            colour=discord.Colour.green(),
            timestamp=datetime.now(),
        )
        data = collection.find_one({"_id": guild_id})
        if data:
            users = data["users"]
            if member.id in users and action:
                embed.description = f"{member.mention} already has this permission!"
            elif member.id not in users and action:
                collection.update_one(
                    {"_id": guild_id},
                    {"$push": {"users": member.id}},
                )
                embed.description = (
                    f"{member.mention} can send discord invite links now!"
                )
            elif member.id in users and not action:
                collection.update_one(
                    {"_id": guild_id},
                    {"$pull": {"users": member.id}},
                )
                embed.description = (
                    f"{member.mention} can't send discord invite links now!"
                )
            elif member.id not in users and not action:
                embed.description = (
                    f"{member.mention} already doesn't have this permission!"
                )
        else:
            if action:
                collection.insert_one({"_id": guild_id, "users": [member.id]})
                embed.description = (
                    f"{member.mention} can send discord invite links now!"
                )
            else:
                embed.description = (
                    f"{member.mention} already doesn't have this permission!"
                )
        return embed

    @commands.command(name="link_perm", aliases=["link_perms"])
    @commands.has_permissions(administrator=True)
    async def link_perm(self, ctx, member: discord.Member, action: bool):
        await ctx.send(embed=await self._link(ctx.guild.id, member, action))

    @app_commands.command(
        name="link_perm",
        description="Set a member's ability to send discord invite links",
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(member="The member to set the permission for")
    @app_commands.describe(
        action="Whether to allow or disallow the member to send discord invite links"
    )
    async def link_perm_slash(
        self, interaction: discord.Interaction, member: discord.Member, action: bool
    ):
        await interaction.response.send_message(
            embed=await self._link(interaction.guild_id, member, action)
        )

    @link_perm_slash.error
    async def link_perm_slash_error(self, interaction, error):
        embed = discord.Embed(
            title="Link Permission Failed",
            colour=discord.Colour.red(),
            timestamp=datetime.now(),
        )
        if isinstance(error, app_commands.errors.MissingPermissions):
            embed.description = (
                "You don't have the required permissions to set link permissions!"
            )
        elif isinstance(error, app_commands.errors.BotMissingPermissions):
            embed.description = (
                "I don't have the required permissions to set link permissions!"
            )
        else:
            embed.description = "Unknown error!"
            await report_error(
                error_webhook_url=self.bot.unknown_error_webhook_url,
                session=self.bot.web_client,
                error=error,
                content="Link Permission Slash Command Error",
                author=interaction.user,
                guild=interaction.guild,
                channel=interaction.channel,
                username="Unknown Error || BlankBot",
            )
        await interaction.response.send_message(embed=embed)

    @commands.command(name="slowmode", aliases=("sm", "slowm", "smode"))
    @commands.has_permissions(manage_channels=True)
    async def slow_mode(self, ctx, seconds: int):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"Slow mode in this channel set to {seconds} seconds!")


async def setup(bot):
    await bot.add_cog(Mod(bot))
