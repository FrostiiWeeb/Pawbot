import discord

from discord.ext import commands
from collections import deque
from random import randint as rint


class SnipeHistory(deque):
    def __init__(self):
        super().__init__(maxlen=5)

    def __repr__(self):
        return "Naoko Snipe History"


class Snipes:
    """Snipe anything deleted"""

    def __init__(self, bot):
        self.bot = bot
        self.snipes = {}
        self.thumbnail = "https://i.imgur.com/BHZU6zX.png"

    async def on_message_delete(self, message):
        """Event is triggered when message is deleted"""
        if message.channel.is_nsfw():
            return

        try:
            self.snipes[message.channel.id].appendleft(message)
        except:
            self.snipes[message.channel.id] = SnipeHistory()
            self.snipes[message.channel.id].appendleft(message)

    @commands.command()
    @commands.cooldown(1.0, 5.0, commands.BucketType.user)
    async def snipe(self, ctx, channel: discord.TextChannel = None, index: int = 0):

        channel = channel or ctx.channel

        if index != 0:
            index = index - 1

        if channel.is_nsfw():
            return await ctx.send(
                ":warning: | **Attempting to snipe a NSFW channel**", delete_after=5
            )

        try:
            sniped = self.snipes[channel.id][index]
        except ValueError:
            return await ctx.send(
                ":warning: | **No message to snipe or index must not be greater than 5 or lower than 1**",
                delete_after=10,
            )

        embed = discord.Embed(
            color=rint(0x000000, 0xFFFFFF),
            timestamp=sniped.created_at,
            title=f"{sniped.author} said",
            description=sniped.clean_content,
        )
        embed.set_footer(
            text=f"Sniped by {ctx.author} | Message created",
            icon_url=ctx.author.avatar_url,
        )
        embed.set_thumbnail(url=sniped.author.avatar_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Snipes(bot))
