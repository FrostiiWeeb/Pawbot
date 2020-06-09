import random
import discord
import json
import requests
import aiohttp
import re

from lxml import html
from art import text2art
from io import BytesIO
from random import randint
from discord.ext import commands
from utils import lists, http, default, eapi, sfapi, permissions, pawgenator

processapi = eapi.processapi
processshowapi = eapi.processshowapi
search = sfapi.search


class InvalidHTTPResponse(Exception):
    """Used if non-200 HTTP Response got from server."""

    pass


class Misc(commands.Cog):
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
            return await ctx.send("I couldn't contact the api ;-;")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            return await ctx.send(r[endpoint])
        embed = discord.Embed(colour=249_742)
        embed.set_image(url=r[endpoint])
        await ctx.send(embed=embed)

    async def textapi(self, ctx, url, endpoint):
        try:
            r = await http.get(url, res_method="json", no_cache=True)
        except json.JSONDecodeError:
            return await ctx.send("I couldn't contact the api ;-;")

        await ctx.send(f"{r[endpoint]}")

    async def factapi(self, ctx, url, endpoint):
        try:
            r = await http.get(url, res_method="json", no_cache=True)
        except json.JSONDecodeError:
            return await ctx.send("I couldn't contact the api ;-;")

        await ctx.send(f"**Did you know?** 🤔\n\n{r[endpoint]}")

    @commands.command(aliases=["8ball"])
    @commands.guild_only()
    async def eightball(self, ctx, *, question: commands.clean_content):
        """ Consult 8ball to receive an answer """
        answer = random.choice(lists.ballresponse)
        await ctx.send(f"🎱 **Question:** {question}\n**Answer:** {answer}")

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def cat(self, ctx):
        """ Posts a random cat """
        await self.randomimageapi(ctx, "https://nekos.life/api/v2/img/meow", "url")

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def dog(self, ctx):
        """ Posts a random dog """
        await self.randomimageapi(ctx, "https://random.dog/woof.json", "url")

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def doggo(self, ctx):
        """ Posts a random dog """
        await self.randomimageapi(
            ctx, "https://dog.ceo/api/breeds/image/random", "message"
        )

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def neko(self, ctx):
        """ Posts a random neko """
        await self.randomimageapi(ctx, "https://nekos.life/api/v2/img/neko", "url")

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def duck(self, ctx):
        """ Posts a random duck """
        await self.randomimageapi(ctx, "https://random-d.uk/api/v1/random", "url")

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def fox(self, ctx):
        """ Posts a random fox girl """
        await self.randomimageapi(ctx, "https://nekos.life/api/v2/img/fox_girl", "url")

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def rabbit(self, ctx):
        """ Posts a random rabbit """
        await self.randomimageapi(
            ctx,
            f"https://api.chewey-bot.ga/rabbit?auth={self.config.cheweyauth}",
            "data",
        )

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def snek(self, ctx):
        """ Does a heckin snek image """
        await self.randomimageapi(
            ctx,
            f"https://api.chewey-bot.ga/snake?auth={self.config.cheweyauth}",
            "data",
        )

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def otter(self, ctx):
        """ Posts a random otter """
        await self.randomimageapi(
            ctx,
            f"https://api.chewey-bot.ga/otter?auth={self.config.cheweyauth}",
            "data",
        )

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def birb(self, ctx):
        """ Posts a random birb """
        await self.randomimageapi(
            ctx, f"https://api.chewey-bot.ga/birb?auth={self.config.cheweyauth}", "data"
        )

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def reverse(self, ctx, *, text: str):
        """ !poow ,ffuts esreveR """
        t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
        await ctx.send(f"🔁 {t_rev}")

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def rate(self, ctx, *, thing: commands.clean_content):
        """ Rates what you desire """
        numbers = random.randint(0, 100)
        decimals = random.randint(0, 9)

        if numbers == 100:
            decimals = 0

        await ctx.send(f"I'd rate {thing} a **{numbers}.{decimals} / 100**")

    @commands.command(aliases=["howhot", "hot"])
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def hotcalc(self, ctx, user: discord.Member = None):
        """ Returns a random percent for how hot is a discord user """
        if user is None:
            user = ctx.author

        random.seed(user.id)
        r = random.randint(1, 100)
        hot = r / 1.17

        emoji = "💔"
        if hot > 25:
            emoji = "❤"
        if hot > 50:
            emoji = "💖"
        if hot > 75:
            emoji = "💞"

        await ctx.send(f"**{user.name}** is **{hot:.2f}%** hot {emoji}")

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def e926(self, ctx, *args):
        """ Searches e926 with given tags. """
        msgtoedit = await ctx.send("Searching...")
        args = " ".join(args)
        args = str(args)
        print("------")
        print("Got command with args: " + args)
        if "order:score_asc" in args:
            await ctx.send("I'm not going to fall into that one, silly~")
            return
        if "score:" in args:
            apilink = f"https://e926.net/post/index.json?tags={args}&limit=320"
        else:
            apilink = (
                f"https://e926.net/post/index.json?tags={args}&score:>25&limit=320"
            )
        try:
            await eapi.processapi(apilink)
        except eapi.ResultNotFound:
            await ctx.send("Result not found!")
            return
        except InvalidHTTPResponse:
            await ctx.send(
                "We're getting invalid response from the API, please try again later!"
            )
            return
        msgtoedit = await ctx.channel.get_message(msgtoedit.id)
        msgtosend = f"Post link: `https://e926.net/post/show/{eapi.processapi.imgid}/`\r\nArtist: `{eapi.processapi.imgartist}`\r\nSource: `{eapi.processapi.imgsource}`\r\nRating: `{eapi.processapi.imgrating}`\r\nTags: `{eapi.processapi.imgtags}` ...and more\r\nImage link: {eapi.processapi.file_link}"
        await msgtoedit.edit(content=msgtosend)

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def yell(self, ctx, *, text: str):
        """ AAAAAAAAA! """
        t_upper = text.upper().replace("@", "@\u200B").replace("&", "&\u200B")
        await ctx.send(f"⬆️ {t_upper}")

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def whisper(self, ctx, *, text: str):
        """ Shh Be quiet.. """
        t_lower = text.lower().replace("@", "@\u200B").replace("&", "&\u200B")
        await ctx.send(f"⬇️ {t_lower}")

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def fact(self, ctx):
        """ sends a random fact """
        await self.factapi(ctx, "https://nekos.life/api/v2/fact", "fact")

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def bamboozle(self, ctx):
        """ You just got bamboozled! """
        await ctx.send(f"**{ctx.author.name}** just got heckin' bamboozled!")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def ship(self, ctx, user: discord.User, *, user2: discord.User = None):
        """Checks the shiprate for 2 users"""
        rowcheck = await self.getserverstuff(ctx)
        author = ctx.message.author
        if not user2:
            user2 = author
        if not user:
            await ctx.send("can't ship nothing y'know..")
        elif user.id == user2.id:
            await ctx.send("i-i can't ship the same person..")
        elif user.id == author.id and user2.id == author.id:
            await ctx.send(f"wow, you're in love with yourself, huh {ctx.author.name}?")
        elif (
            user == self.bot.user
            and user2 == author
            or user2 == self.bot.user
            and user == author
        ):
            blushes = ["m-me..? 0////0", "m-me..? >////<"]
            return await ctx.send(random.choice(blushes))

        else:
            n = randint(1, 100)
            if n == 100:
                bar = "██████████"
                heart = "💞"
            elif n >= 90:
                bar = "█████████."
                heart = "💕"
            elif n >= 80:
                bar = "████████.."
                heart = "😍"
            elif n >= 70:
                bar = "███████..."
                heart = "💗"
            elif n >= 60:
                bar = "██████...."
                heart = "❤"
            elif n >= 50:
                bar = "█████....."
                heart = "❤"
            elif n >= 40:
                bar = "████......"
                heart = "💔"
            elif n >= 30:
                bar = "███......."
                heart = "💔"
            elif n >= 20:
                bar = "██........"
                heart = "💔"
            elif n >= 10:
                bar = "█........."
                heart = "💔"
            elif n < 10:
                bar = ".........."
                heart = "🖤"
            else:
                bar = ".........."
                heart = "🖤"
            name1 = user.name.replace(" ", "")
            name1 = name1[: int(len(name1) / 2) :]
            name2 = user2.name.replace(" ", "")
            name2 = name2[int(len(name2) / 2) : :]
            if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
                return await ctx.send(
                    f"```\n{user.name} x {user2.name}\n\n{n}% {bar} {heart}\n\nShipname: {str(name1 + name2).lower()}\n```"
                )
            ship = discord.Embed(
                description=f"**{n}%** **`{bar}`** {heart}", color=ctx.me.colour
            )
            ship.title = f"{user.name} x {user2.name}"
            ship.set_footer(text=f"Shipname: {str(name1 + name2).lower()}")
            await ctx.send(embed=ship)

    @commands.command(aliases=["👏"])
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def emojify(self, ctx, emote, *, text_to_clap: str):
        """ 👏bottom👏text👏 """
        clapped_text = (
            text_to_clap.replace("@everyone", f"{emote}everyone")
            .replace("@here", f"{emote}here")
            .replace(" ", f"{emote}")
        )
        clapped_text = f"{emote}{clapped_text}{emote}"
        await ctx.send(clapped_text)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def owo(self, ctx):
        """Sends a random owo face"""
        owo = random.choice(lists.owos)
        await ctx.send(f"{owo} whats this~?")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def choose(self, ctx, *args):
        """Choose one of a lot (Split with |) """
        args = " ".join(args)
        args = str(args)
        choices = args.split("|")
        if len(choices) < 2:
            return await ctx.send("You need to send at least 2 choices!")
        await ctx.send(random.choice(choices))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def jpeg(self, ctx, urltojpeg: str):
        """ Does what it says on the can """
        if "http" not in urltojpeg:
            return await ctx.send("Include a url you dork!")
        await self.randomimageapi(
            ctx,
            f"https://nekobot.xyz/api/imagegen?type=jpeg&url={urltojpeg}",
            "message",
        )

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def deepfry(self, ctx, urltojpeg: str):
        """ Deepfries an image """
        if "http" not in urltojpeg:
            return await ctx.send("Include a url you dork!")
        await self.randomimageapi(
            ctx,
            f"https://nekobot.xyz/api/imagegen?type=deepfry&image={urltojpeg}",
            "message",
        )

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def clyde(self, ctx, clydetext: str):
        """ Makes Clyde say something """
        if clydetext is None:
            return await ctx.send("Include some text you dork!")
        await self.randomimageapi(
            ctx,
            f"https://nekobot.xyz/api/imagegen?type=clyde&text={clydetext}",
            "message",
        )

    # @commands.command()
    # @commands.guild_only()
    # @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    # async def magik(self, ctx, intensity: str, imgtomagik: str = None):
    #     """ why don'T WE JUST RELAX AND TURn on THe rADIO? """
    #     if imgtomagik is None:
    #         if not ctx.message.attachments
    #     if intensity not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
    #         return await ctx.send("Include an intensity to magik (1-10)")
    #     await self.randomimageapi(
    #         ctx,
    #         f"https://nekobot.xyz/api/imagegen?type=magik&image={imgtomagik}&intensity={intensity}",
    #         "message",
    #     )

    @commands.command(aliases=["ascii"])
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def asciify(self, ctx, *, text: str):
        """ Turns any text given into ascii """
        Art = text2art(text)
        asciiart = f"```\n{Art}\n```"
        if len(asciiart) > 2000:
            return await ctx.send("That art is too big")
        await ctx.send(asciiart)

    @commands.command(aliases=["say"])
    @commands.guild_only()
    async def echo(self, ctx, *, text: str):
        """ Says what you want """
        text = text.replace("@everyone", "@​everyone").replace("@here", "@​here")
        await ctx.send(text)

    @commands.command()
    @commands.guild_only()
    async def snipe(self, ctx, channel: discord.TextChannel = None, index: int = 0):
        """ Snipe deleted messages o3o """
        rowcheck = await self.getserverstuff(ctx)
        channel = channel or ctx.channel

        if index != 0:
            index = index - 1

        try:
            sniped = self.bot.snipes[channel.id][index]
        except KeyError:
            return await ctx.send(
                ":warning: | **No message to snipe or index must not be greater than 5 or lower than 1**",
                delete_after=10,
            )
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            return await ctx.send(
                f"```\n{sniped.author}: {sniped.clean_content}\n\nSniped by: {ctx.author}\n```"
            )

        embed = discord.Embed(
            color=randint(0x000000, 0xFFFFFF),
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

    @commands.command()
    @commands.guild_only()
    async def markov(self, ctx):
        """Generates a Markov Chain"""
        await ctx.send(
            " ".join(
                random.sample(
                    [
                        m.clean_content
                        for m in await ctx.channel.history(limit=150).flatten()
                        if not m.author.bot
                    ],
                    10,
                )
            )
        )

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def hug(self, ctx, user: discord.Member = None):
        """ Hug a user! """
        rowcheck = await self.getserverstuff(ctx)
        endpoint = "url"
        if user is None:
            user = ctx.author
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        try:
            r = await http.get(
                "https://nekos.life/api/v2/img/hug", res_method="json", no_cache=True
            )
        except json.JSONDecodeError:
            return await ctx.send("I couldn't contact the api ;-;")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            return await ctx.send(f"💖 | **{ctx.author.name}** hugs **{user.name}**")
        embed = discord.Embed(
            colour=249_742, description=f"**{ctx.author.name}** hugs **{user.name}**"
        )
        embed.set_image(url=r[endpoint])
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def kiss(self, ctx, user: discord.Member = None):
        """ Kiss a user! """
        rowcheck = await self.getserverstuff(ctx)
        endpoint = "url"
        if user is None:
            user = ctx.author
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        try:
            r = await http.get(
                "https://nekos.life/api/v2/img/kiss", res_method="json", no_cache=True
            )
        except json.JSONDecodeError:
            return await ctx.send("I couldn't contact the api ;-;")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            return await ctx.send(
                f"💗 | **{ctx.author.name}** gives **{user.name}** a kiss~!"
            )
        embed = discord.Embed(
            colour=249_742,
            description=f"**{ctx.author.name}** gives **{user.name}** a kiss~!",
        )
        embed.set_image(url=r[endpoint])
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def pat(self, ctx, user: discord.Member = None):
        """ Pat a user! """
        rowcheck = await self.getserverstuff(ctx)
        endpoint = "url"
        if user is None:
            user = ctx.author
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        try:
            r = await http.get(
                "https://nekos.life/api/v2/img/pat", res_method="json", no_cache=True
            )
        except json.JSONDecodeError:
            return await ctx.send("I couldn't contact the api ;-;")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            return await ctx.send(
                f"💗 | **{ctx.author.name}** pats **{user.name}** on the head"
            )
        embed = discord.Embed(
            colour=249_742,
            description=f"**{ctx.author.name}** pats **{user.name}** on the head",
        )
        embed.set_image(url=r[endpoint])
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def feed(self, ctx, user: discord.Member = None):
        """ Feed a user! """
        rowcheck = await self.getserverstuff(ctx)
        endpoint = "url"
        if user is None:
            user = ctx.author
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        try:
            r = await http.get(
                "https://nekos.life/api/v2/img/feed", res_method="json", no_cache=True
            )
        except json.JSONDecodeError:
            return await ctx.send("I couldn't contact the api ;-;")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            return await ctx.send(
                f"🍲 | **{ctx.author.name}** feeds **{user.name}** sum nums"
            )
        embed = discord.Embed(
            colour=249_742,
            description=f"**{ctx.author.name}** feeds **{user.name}** sum nums",
        )
        embed.set_image(url=r[endpoint])
        await ctx.send(embed=embed)

    @commands.command(aliases=["snuggle"])
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def cuddle(self, ctx, user: discord.Member = None):
        """ Cuddle a user! """
        rowcheck = await self.getserverstuff(ctx)
        endpoint = "url"
        if user is None:
            user = ctx.author
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        try:
            r = await http.get(
                "https://nekos.life/api/v2/img/cuddle", res_method="json", no_cache=True
            )
        except json.JSONDecodeError:
            return await ctx.send("I couldn't contact the api ;-;")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            return await ctx.send(
                f"😍 | **{ctx.author.name}** cuddles **{user.name}** tightly!"
            )
        embed = discord.Embed(
            colour=249_742,
            description=f"**{ctx.author.name}** cuddles **{user.name}** tightly!",
        )
        embed.set_image(url=r[endpoint])
        await ctx.send(embed=embed)

    @commands.command(aliases=["boop"])
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def poke(self, ctx, user: discord.Member = None):
        """ Poke a user! """
        rowcheck = await self.getserverstuff(ctx)
        endpoint = "url"
        if user is None:
            user = ctx.author
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        try:
            r = await http.get(
                "https://nekos.life/api/v2/img/poke", res_method="json", no_cache=True
            )
        except json.JSONDecodeError:
            return await ctx.send("I couldn't contact the api ;-;")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            return await ctx.send(
                f"🧡 | Boop! **{ctx.author.name}** pokes **{user.name}** on the nose!"
            )
        embed = discord.Embed(
            colour=249_742,
            description=f"Boop! **{ctx.author.name}** pokes **{user.name}** on the nose!",
        )
        embed.set_image(url=r[endpoint])
        await ctx.send(embed=embed)

    @commands.command(aliases=["bap"])
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def slap(self, ctx, user: discord.Member = None):
        """ Slap a user! """
        rowcheck = await self.getserverstuff(ctx)
        endpoint = "url"
        if user is None:
            user = ctx.author
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        try:
            r = await http.get(
                "https://nekos.life/api/v2/img/slap", res_method="json", no_cache=True
            )
        except json.JSONDecodeError:
            return await ctx.send("I couldn't contact the api ;-;")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            return await ctx.send(
                f"😢 | **{ctx.author.name}** slaps **{user.name}**! Yowch!"
            )
        embed = discord.Embed(
            colour=249_742,
            description=f"**{ctx.author.name}** slaps **{user.name}**! Yowch!",
        )
        embed.set_image(url=r[endpoint])
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def tickle(self, ctx, user: discord.Member = None):
        """ Tickle a user! """
        rowcheck = await self.getserverstuff(ctx)
        endpoint = "url"
        if user is None:
            user = ctx.author
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        try:
            r = await http.get(
                "https://nekos.life/api/v2/img/tickle", res_method="json", no_cache=True
            )
        except json.JSONDecodeError:
            return await ctx.send("I couldn't contact the api ;-;")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            return await ctx.send(f"😘 | **{ctx.author.name}** tickles **{user.name}**!")
        embed = discord.Embed(
            colour=249_742,
            description=f"**{ctx.author.name}** tickles **{user.name}**!",
        )
        embed.set_image(url=r[endpoint])
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=2, per=5.0, type=commands.BucketType.user)
    async def yt(self, ctx, *, video: str = None):
        """Search a YouTube video"""
        if video is None:
            return await ctx.send("You need to add text to search something.")
        results = await http.get(
            f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={video}&maxResults=1&type=video&key={self.config.ytkey}",
            res_method="json",
            no_cache=True,
        )
        results = results["items"][0]["id"]["videoId"]
        await ctx.send(f"http://www.youtube.com/watch?v={results}")

    @commands.command(aliases=["inspire"])
    @commands.guild_only()
    @commands.cooldown(rate=2, per=5.0, type=commands.BucketType.user)
    async def inspireme(self, ctx):
        """ Fetch a random "inspirational message" from the bot. """
        rowcheck = await self.getserverstuff(ctx)

        page = await http.get(
            "http://inspirobot.me/api?generate=true", res_method="text", no_cache=True
        )
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            return await ctx.send(page)
        embed = discord.Embed(colour=249_742)
        embed.set_image(url=page)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=2, per=5.0, type=commands.BucketType.user)
    async def spoiler(self, ctx, *, spoilertext: str):
        await ctx.message.delete()
        file = BytesIO(spoilertext.encode("utf-8"))
        await ctx.send(
            content=f"**{ctx.author}** has made a spoiler!",
            file=discord.File(file, filename="spoiler.txt"),
        )

    @commands.command(aliases=["t"])
    @commands.guild_only()
    async def tag(self, ctx, *, tagname: str):
        query = "SELECT * FROM tags WHERE serverid=$1 AND tagname=$2;"
        r = await self.bot.db.fetchrow(query, ctx.guild.id, tagname)
        if not r:
            return await ctx.send("No tag found...")
        await ctx.send(r["tagtext"])

    @commands.command(aliases=["tl"])
    @commands.guild_only()
    async def tags(self, ctx):
        query = "SELECT tagname FROM tags WHERE serverid=$1;"
        query = await self.bot.db.fetch(query, ctx.guild.id)
        msg = ""
        for r in query:
            msg += f"`{r['tagname']}` "
        if not msg:
            msg = "No tags found..."
        await ctx.send(msg)

    @commands.command(aliases=["at"])
    @commands.guild_only()
    @permissions.has_permissions(manage_messages=True)
    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    async def addtag(self, ctx, tagname: str, *, tagtext: str):
        query = "SELECT * FROM tags WHERE serverid=$1 AND tagname=$2;"
        query = await self.bot.db.fetchrow(query, ctx.guild.id, tagname)
        if query:
            return await ctx.send("That tag already exists!")
        query = "INSERT INTO tags VALUES ($1, $2, $3);"
        await self.bot.db.execute(query, ctx.guild.id, tagname, tagtext)
        await ctx.send(f"Created the tag `{tagname}`!")

    @commands.command(aliases=["dt"])
    @commands.guild_only()
    @permissions.has_permissions(manage_messages=True)
    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    async def deltag(self, ctx, tagname: str):
        query = "SELECT * FROM tags WHERE serverid=$1 AND tagname=$2;"
        query = await self.bot.db.fetchrow(query, ctx.guild.id, tagname)
        if not query:
            return await ctx.send("No tag found...")
        query = "DELETE FROM tags WHERE serverid=$1 AND tagname=$2;"
        query = await self.bot.db.execute(query, ctx.guild.id, tagname)
        await ctx.send(f"Successfully deleted {tagname}")

    @commands.command(aliases=["screenshot"])
    @commands.cooldown(rate=1, per=7.0, type=commands.BucketType.guild)
    async def ss(self, ctx, *, url: str):
        """ Screenshots as a service """
        if "<" in url or ">" in url:
            url = url.replace("<", "").replace(">", "")
        async with ctx.typing(), aiohttp.ClientSession() as session:
            screener = "http://magmachain.herokuapp.com/api/v1"
            async with session.post(screener, headers=dict(website=url)) as r:
                website = (await r.json())["snapshot"]
                await ctx.send(
                    embed=discord.Embed(color=249_742).set_image(url=website)
                )

    @commands.command(name="emojis", alisases=["emojis"])
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def _emojis(self, ctx, *, name: str = None):
        """ Display all emojis I can see in a paginated embed. """
        if name:
            emojis = [e for e in self.bot.emojis if name in e.name]
            if not emojis:
                return await ctx.send(
                    f"Could not find any emojis with search term: `{name}`"
                )

            chunks = [
                e
                async for e in pawgenator.pager(sorted(emojis, key=lambda _: _.name), 8)
            ]
        else:
            chunks = [
                e
                async for e in pawgenator.pager(
                    sorted(self.bot.emojis, key=lambda _: _.name), 8
                )
            ]

        pagey = pawgenator.EmojiPaginator(title="Emojis", chunks=chunks)
        self.bot.loop.create_task(pagey.paginate(ctx))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def card(self, ctx, *, name):
        """ Searches for a Hearthstone card """
        msg = await ctx.send("I'm looking for that card...")

        r = requests.get(
            f"https://omgvamp-hearthstone-v1.p.mashape.com/cards/{name}?collectible=1",
            headers={
                "X-Mashape-Key": "sly1A6Ur3tmshrDtRbWe4q738Afxp1cnkhajsnWqVf9HMJ7ZOJ"
            },
        )

        if r.status_code == 404:
            return await msg.edit(content=f"Card {name} not found.")
        await msg.edit(
            content="",
            embed=discord.Embed(
                title=name, description=r.json()[0]["flavor"], color=249_742
            ).set_image(url=r.json()[0]["img"]),
        )

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def gcard(self, ctx, *, name):
        """ Searches for a gold Hearthstone card """

        msg = await ctx.send("I'm looking for that card...")

        r = requests.get(
            f"https://omgvamp-hearthstone-v1.p.mashape.com/cards/{name}?collectible=1",
            headers={
                "X-Mashape-Key": "sly1A6Ur3tmshrDtRbWe4q738Afxp1cnkhajsnWqVf9HMJ7ZOJ"
            },
        )

        if r.status_code == 404:
            return await msg.edit(content=f"Card {name} not found.")
        await msg.edit(
            content="",
            embed=discord.Embed(
                title=name, description=r.json()[0]["flavor"], color=249_742
            ).set_image(url=r.json()[0]["imgGold"]),
        )

    @commands.command()
    async def hello(self, ctx):
        """ Hi """
        await ctx.send(f"Hello {ctx.author.name}! ^-^")

    @commands.command(pass_context=True)
    async def villager(self, ctx, villager):
        """ Returns info on a villager from animal crossing """
        description = "Villager info for " + villager
        data = discord.Embed(colour=0x67AC42)
        data.set_author(name=description, icon_url="https://i.imgur.com/ef8GJOL.png")
        attributes = [
            "species",
            "gender",
            "personality",
            "birthday",
            "clothes",
            "starsign",
            "phrase",
            "song",
        ]

        page = requests.get("https://nookipedia.com/wiki/" + villager)

        if page.status_code == 404:
            data.add_field(name="Error", value="Villager does not exist!")
        else:
            tree = html.fromstring(page.content)

            for att in attributes:
                villid = str("Infobox-villager-" + att)
                temp = str(tree.xpath('//td[@id="' + villid + '"]//text()'))
                if len(temp) > 2:
                    if att == "clothes":
                        temp = temp.replace("', '*', '", "\n")
                    temp = (
                        temp.replace("['", "")
                        .replace("']", "")
                        .replace("*", "")
                        .replace("', '", "")
                    )  # Remove list notation surrounding data
                    temp = temp[
                        :-2
                    ]  # Remove trailing '\n' at the end of each string; for some reason, .replace or .rstrip doesn't work
                    if att == "phrase":
                        temp = re.sub(
                            r"\([^)]*\)", "", temp
                        )  # Remove sets of parenthese and their contents (in this case, language indications: (EN), (JP), etc.)
                        temp = re.sub(
                            "[^a-zA-Z]", "", temp
                        )  # Remove any non-English alphabet characters (in this case, Japanese)
                    data.add_field(name=att.capitalize(), value=temp)
                else:
                    temp = "N/A"
                    data.add_field(name=att.capitalize(), value=temp)
        await ctx.send(embed=data)


def setup(bot):
    bot.add_cog(Misc(bot))
