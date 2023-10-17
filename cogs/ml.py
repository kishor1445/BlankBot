import discord
from datetime import datetime
from discord.ext import commands
import requests
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image

processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
model = ViTForImageClassification.from_pretrained("google/vit-base-patch16-224")


class ML(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="sentimentalanalysis", description="Set a channel for sentimental analysis"
    )
    @commands.has_guild_permissions(administrator=True)
    async def sentimental_analysis_enable(
        self, ctx, destination: discord.TextChannel, source: discord.TextChannel = None
    ):
        source = source or ctx.channel
        db = self.bot.cluster["guilds"]
        collection = db["sentimental"]
        embed = discord.Embed(
            colour=discord.Colour.green(),
            timestamp=datetime.now(),
        )
        if not collection.find_one({"_id": source.id}):
            collection.insert_one(
                {
                    "_id": source.id,
                    "destination": {
                        "channel_id": destination.id,
                        "guild_id": ctx.guild.id,
                    },
                }
            )
        else:
            collection.update_one(
                {"_id": source.id},
                {
                    "$push": {
                        "destination": {
                            "channel_id": destination.id,
                            "guild_id": ctx.guild.id,
                        }
                    }
                },
            )
        embed.description = f"{source.mention} is set for Sentimental Analysis and the output will sent to {destination.mention}"
        await ctx.send(embed=embed)

    @commands.command(name="disablesentimentalanalysis")
    async def sentimental_analysis_disable(
        self, ctx: commands.Context, channel: discord.TextChannel = None
    ):
        channel = channel or ctx.channel
        db = self.bot.cluster["guilds"]
        collection = db["sentimental"]
        embed = discord.Embed(
            title="Sentimental Analysis",
            description=f"Sentimental Analysis for channel ID [{collection['destination']['channel_id']}] Disabled.",
            timestamp=datetime.now(),
        )
        collection.remove(channel.id)
        await ctx.send(embed=embed)

    @commands.command(name="detect", description="Image detection")
    async def detect_image(self, ctx: commands.Context):
        attachment_url = ctx.message.attachments[0].url
        image = Image.open(requests.get(attachment_url, stream=True).raw)
        inputs = processor(images=image, return_tensors="pt")
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class_idx = logits.argmax(-1).item()
        await ctx.message.reply(f"{model.config.id2label[predicted_class_idx]}")


async def setup(bot):
    await bot.add_cog(ML(bot))
