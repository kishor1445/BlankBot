import discord
from discord import Webhook, Embed
from datetime import datetime


async def report_error(
    error_webhook_url, session, error, content, author, guild, channel, username
):
    web_hook = Webhook.from_url(error_webhook_url, session=session)
    embed = Embed(
        title="An error occurred!",
        description=error,
        colour=discord.Colour.red(),
        timestamp=datetime.now(),
    )
    embed.add_field(name="Content", value=content)
    embed.add_field(name="Guild", value=f"{guild} [{guild.id}]")
    embed.add_field(name="Channel", value=f"{channel} [{channel.id}]")
    embed.set_author(name=f"{author} [{author.id}]", icon_url=author.avatar.url)
    await web_hook.send(embed=embed, username=username)
