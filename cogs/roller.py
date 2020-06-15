import discord
import sys
import json

from discord.ext import commands
from utils import repo, default, permissions, diceformatter


class Roller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")


    @commands.command()
    @commands.guild_only()
    async def roll(self, ctx, *, dicerolls: str = None):

        def format_roll(result, requester):
            individual = ' + '.join(result['individual'])
            return f"{requester}: `{dicerolls}` = ({individual}) = {result['total']}"

        if dicerolls is None:
            return
        result = diceformatter.get_dice_formula_result(dicerolls)
        message = format_roll(result, ctx.message.author.mention)
        await ctx.send(message)

    

def setup(bot):
    bot.add_cog(Roller(bot))
