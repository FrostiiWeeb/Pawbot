import discord
import sys
import json
import random

from discord.ext import commands
from utils import repo, default, permissions, diceformatter


class Roller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")


    @commands.command(aliases=["r"])
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

    @commands.command()
    @commands.guild_only()
    async def dndchar(self, ctx):
        def roll_dice_discarding_lowest(n_dice, dice_rank):
            results = [  # Generate n_dice numbers between [1, dice_rank]
                random.randint(1, dice_rank)
                for n
                in range(n_dice)
            ]
            results.remove(min(results))
            return sum(results)  # Return the sum of the remaining results.

        diceResult = []
        for _ in range(6):
            result = roll_dice_discarding_lowest(4, 6)
            diceResult.append(result)
        await ctx.send(diceResult)

    

def setup(bot):
    bot.add_cog(Roller(bot))
