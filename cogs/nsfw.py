import random
import discord
import json

from discord.ext import commands
from utils import http, default, sfapi, eapi, permissions

bannedtags = ["loli", "shota"]

processapi = eapi.processapi
processshowapi = eapi.processshowapi
search = sfapi.search


class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")

    async def getserverstuff(self, ctx):
        query = "SELECT * FROM adminpanel WHERE serverid = $1;"
        row = await self.bot.db.fetchrow(query, ctx.guild.id)
        if row is None:
            query = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(query, ctx.guild.id, 0, 0, 1, 0, 0, 0)
            query = "SELECT * FROM adminpanel WHERE serverid = $1;"
            row = await self.bot.db.fetchrow(query, ctx.guild.id)
        return row

    async def randomimageapi(self, ctx, url, endpoint):
        rowcheck = await self.getserverstuff(ctx)
        try:
            urltouse = url.replace("webp", "png")
            r = await http.get(urltouse, res_method="json", no_cache=True)
        except json.JSONDecodeError:
            return await ctx.send("Couldn't find anything from the API")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            return await ctx.send(r[endpoint])
        embed = discord.Embed(colour=249_742)
        embed.set_image(url=r[endpoint])
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_nsfw()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=7.0, type=commands.BucketType.user)
    async def lewdneko(self, ctx):
        """Posts a lewd neko"""
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["nsfw"] == 0:
            return await ctx.send(";w; NSFW is disabled in the config...")
        await self.randomimageapi(ctx, "https://nekos.life/api/v2/img/lewd", "url")

    @commands.command()
    @commands.is_nsfw()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=7.0, type=commands.BucketType.user)
    async def lewdfeet(self, ctx):
        """Posts a lewd foot image or gif"""
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["nsfw"] == 0:
            return await ctx.send(";w; NSFW is disabled in the config...")
        randomfoot = ["feet", "feetg"]
        await self.randomimageapi(
            ctx, f"https://nekos.life/api/v2/img/{random.choice(randomfoot)}", "url"
        )

    @commands.command()
    @commands.is_nsfw()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=7.0, type=commands.BucketType.user)
    async def lewdkemo(self, ctx):
        """Posts a lewd kemonomimi character"""
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["nsfw"] == 0:
            return await ctx.send(";w; NSFW is disabled in the config...")
        randomfox = ["holoero", "erokemo", "hololewd"]
        await self.randomimageapi(
            ctx, f"https://nekos.life/api/v2/img/{random.choice(randomfox)}", "url"
        )

    @commands.command()
    @commands.is_nsfw()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=7.0, type=commands.BucketType.user)
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def lewdanal(self, ctx):
        """Posts a lewd anal gif/picture"""
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["nsfw"] == 0:
            return await ctx.send(";w; NSFW is disabled in the config...")
        await self.randomimageapi(ctx, f"https://nekos.life/api/v2/img/anal", "url")

    @commands.command()
    @commands.is_nsfw()
    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    async def urban(self, ctx, *, search: str):
        """ Find the 'best' definition to your words """
        url = await http.get(
            f"http://api.urbandictionary.com/v0/define?term={search}", res_method="json"
        )

        if url is None:
            return await ctx.send("I think the API broke...")

        count = len(url["list"])
        if count == 0:
            return await ctx.send("Couldn't find your search in the dictionary...")
        result = url["list"][random.randint(0, count - 1)]

        definition = result["definition"]
        if len(definition) >= 1000:
            definition = definition[:1000]
            definition = definition.rsplit(" ", 1)[0]
            definition += "..."

        embed = discord.Embed(
            colour=0xC29FAF,
            description=f"**{result['word']}**\n*by: {result['author']}*",
        )
        embed.add_field(name="Definition", value=definition, inline=False)
        embed.add_field(name="Example", value=result["example"], inline=False)
        embed.set_footer(text=f"👍 {result['thumbs_up']} | 👎 {result['thumbs_down']}")

        try:
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(
                "I found something, but have no access to post it... [Embed permissions]"
            )


def setup(bot):
    bot.add_cog(NSFW(bot))
