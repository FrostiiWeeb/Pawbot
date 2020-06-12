import time
import discord
import psutil
import os
import asyncio
import io
import requests
import dhooks
import json
import unicodedata
import inspect
import random

from urllib.parse import quote
from collections import Counter
from dhooks import Webhook
from discord.ext import commands
from datetime import datetime
from utils import repo, default, permissions, pawgenator


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self.process = psutil.Process(os.getpid())
        self.counter = Counter()

    def cleanup_code(self, content):
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])
        return content.strip("` \n")

    async def getserverstuff(self, ctx):
        query = "SELECT * FROM adminpanel WHERE serverid = $1;"
        row = await self.bot.db.fetchrow(query, ctx.guild.id)
        if row is None:
            query = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(query, ctx.guild.id, 0, 0, 1, 0, 0, 0)
            query = "SELECT * FROM adminpanel WHERE serverid = $1;"
            row = await self.bot.db.fetchrow(query, ctx.guild.id)
        return row

    def get_bot_uptime(self, *, brief=False):
        now = datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if not brief:
            if days:
                fmt = "{d} days, {h} hours, {m} minutes, and {s} seconds"
            else:
                fmt = "{h} hours, {m} minutes, and {s} seconds"
        else:
            fmt = "{h}h {m}m {s}s"
            if days:
                fmt = "{d}d " + fmt

        return fmt.format(d=days, h=hours, m=minutes, s=seconds)

    async def category_gen(self, ctx):
        categories = {}

        for command in set(ctx.bot.walk_commands()):
            try:
                if command.category not in categories:
                    categories.update({command.category: []})
            except AttributeError:
                cog = command.cog_name or "Bot"
                if command.cog_name not in categories:
                    categories.update({cog: []})

        for command in set(ctx.bot.walk_commands()):
            if not command.hidden:
                try:
                    if command.category:
                        categories[command.category].append(command)
                except AttributeError:
                    cog = command.cog_name or "Bot"
                    categories[cog].append(command)

        return categories

    async def commandMapper(self, ctx):
        pages = []

        for category, commands in (await self.category_gen(ctx)).items():
            if not commands:
                continue
            cog = ctx.bot.get_cog(category)
            if cog:
                category = f"**⚙️ {category}**"
            commands = ", ".join([c.qualified_name for c in commands])
            embed = (
                discord.Embed(
                    color=random.randint(0x000000, 0xFFFFFF),
                    title=f"{ctx.bot.user.display_name} Commands",
                    description=f"{category}",
                )
                .set_footer(
                    text=f"Type {ctx.prefix}help <command> for more help".replace(
                        ctx.me.mention, "@Pawbot "
                    ),
                    icon_url=ctx.author.avatar_url,
                )
                .add_field(name="**Commands:**", value=f"``{commands}``")
            )
            pages.append(embed)
        await pawgenator.SimplePaginator(
            extras=sorted(pages, key=lambda d: d.description)
        ).paginate(ctx)

    async def cogMapper(self, ctx, entity, cogname: str):
        try:
            await ctx.send(
                embed=discord.Embed(
                    color=random.randint(0x000000, 0xFFFFFF),
                    title=f"{ctx.bot.user.display_name} Commands",
                    description=f"**⚙️ {cogname}**",
                )
                .add_field(
                    name="**Commands:**",
                    value=f"``{', '.join([c.qualified_name for c in set(ctx.bot.walk_commands()) if c.cog_name == cogname])}``",
                )
                .set_footer(
                    text=f"Type {ctx.prefix}help <command> for more help".replace(
                        ctx.me.mention, "@Pawbot "
                    ),
                    icon_url=ctx.author.avatar_url,
                )
            )
        except BaseException:
            await ctx.send(
                f":x: | **Command or category not found. Use {ctx.prefix}help**",
                delete_after=10,
            )

    @commands.command(aliases=["?"])
    async def help(self, ctx, *, command: str = None):
        """View Bot Help Menu"""
        if not command:
            await self.commandMapper(ctx)
        else:
            entity = self.bot.get_cog(command) or self.bot.get_command(command)
            if entity is None:
                return await ctx.send(
                    f":x: | **Command or category not found. Use {ctx.prefix}help**",
                    delete_after=10,
                )
            if isinstance(entity, commands.Command):
                await pawgenator.SimplePaginator(
                    title=f"Command: {entity.name}",
                    entries=[
                        f"**:bulb: Command Help**\n```ini\n[{entity.help}]```",
                        f"**:video_game: Command Signature**\n```ini\n{entity.signature}```",
                    ],
                    length=1,
                    colour=random.randint(0x000000, 0xFFFFFF),
                ).paginate(ctx)
            else:
                await self.cogMapper(ctx, entity, command)

    @commands.command()
    async def ping(self, ctx):
        """ Pong! """
        before = time.monotonic()
        message = await ctx.send("Did you just ping me?!")
        ping = (time.monotonic() - before) * 1000
        await message.edit(
            content=f"`MSG :: {int(ping)}ms\nAPI :: {round(self.bot.latency * 1000)}ms`"
        )

    @commands.command(aliases=["joinme", "join", "botinvite"])
    async def invite(self, ctx):
        """ Invite me to your server """
        await ctx.send(
            f"**{ctx.author.name}**, use this URL to invite me\n<https://discordapp.com/oauth2/authorize?client_id=460383314973556756&scope=bot&permissions=469888118>"
        )

    @commands.command(aliases=["supportserver", "feedbackserver"])
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def botserver(self, ctx):
        """ Get an invite to our support server! """
        if (
            isinstance(ctx.channel, discord.DMChannel)
            or ctx.guild.id != 711685458714689616
        ):
            return await ctx.send(
                f"**{ctx.author.name}**, you can join here! 🍻\n<{repo.invite}>"
            )

        await ctx.send(f"**{ctx.author.name}**, this is my home.")

    @commands.command()
    async def about(self, ctx):
        """Tells you information about the bot itself."""
        cmd = r'git show -s HEAD~3..HEAD --format="[{}](https://github.com/pawbot-discord/Pawbot/commit/%H) %s (%cr)"'
        if os.name == "posix":
            cmd = cmd.format(r"\`%h\`")
        else:
            cmd = cmd.format(r"`%h`")

        try:
            revision = os.popen(cmd).read().strip()
        except OSError:
            revision = "Could not fetch due to memory error. Sorry."

        embed = discord.Embed(description="Latest Changes:\n" + revision)
        embed.title = "Official Bot Server Invite"
        embed.url = repo.invite
        embed.colour = discord.Colour.blurple()

        botinfo = self.bot.get_user(460_383_314_973_556_756)
        embed.set_author(name=str(botinfo), icon_url=botinfo.avatar_url)

        # statistics
        total_members = sum(1 for _ in self.bot.get_all_members())
        total_online = len(
            {
                m.id
                for m in self.bot.get_all_members()
                if m.status is not discord.Status.offline
            }
        )
        total_unique = len(self.bot.users)

        voice_channels = []
        text_channels = []
        for guild in self.bot.guilds:
            voice_channels.extend(guild.voice_channels)
            text_channels.extend(guild.text_channels)

        text = len(text_channels)
        voice = len(voice_channels)

        embed.add_field(
            name="Members",
            value=f"{total_members} total\n{total_unique} unique\n{total_online} unique online",
        )
        embed.add_field(
            name="Channels", value=f"{text + voice} total\n{text} text\n{voice} voice"
        )

        memory_usage = self.process.memory_full_info().uss / 1024 ** 2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
        embed.add_field(
            name="Process", value=f"{memory_usage:.2f} MiB\n{cpu_usage:.2f}% CPU"
        )

        embed.add_field(name="Guilds", value=len(self.bot.guilds))
        embed.add_field(name="Uptime", value=self.get_bot_uptime(brief=True))
        embed.add_field(name="Owner", value="Paws#7605")
        embed.set_footer(
            text="Made with discord.py", icon_url="http://i.imgur.com/5BFecvA.png"
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def avatar(self, ctx, user: discord.Member = None):
        """ Get the avatar of you or someone else """
        rowcheck = await self.getserverstuff(ctx)

        if user is None:
            user = ctx.author

        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            return await ctx.send(user.avatar_url)

        embed = discord.Embed(colour=249_742)
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def joinedat(self, ctx, user: discord.Member = None):
        """ Check when a user joined the current server """
        rowcheck = await self.getserverstuff(ctx)

        if user is None:
            user = ctx.author

        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            return await ctx.send(
                f"**{user}** joined **{ctx.guild.name}**\n{default.date(user.joined_at)}"
            )

        embed = discord.Embed(colour=249_742)
        embed.set_thumbnail(url=user.avatar_url)
        embed.description = (
            f"**{user}** joined **{ctx.guild.name}**\n{default.date(user.joined_at)}"
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def server(self, ctx):
        """ Check info about current server """
        if ctx.invoked_subcommand is None:

            rowcheck = await self.getserverstuff(ctx)

            findbots = sum(1 for member in ctx.guild.members if member.bot)

            emojilist = "​"
            for Emoji in ctx.guild.emojis:
                emojilist += f"{Emoji} "
            if len(emojilist) > 1024:
                emojilist = "Too long!"

            if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
                return await ctx.send(
                    f"```\nServer Name: {ctx.guild.name}\nServer ID: {ctx.guild.id}\nMembers: {ctx.guild.member_count}\nBots: {findbots}\nOwner: {ctx.guild.owner}\nRegion: {ctx.guild.region}\nCreated At: {default.date(ctx.guild.created_at)}\n```\nEmojis: {emojilist}"
                )

            embed = discord.Embed(colour=249_742)
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.add_field(name="Server Name", value=ctx.guild.name, inline=True)
            embed.add_field(name="Server ID", value=ctx.guild.id, inline=True)
            embed.add_field(name="Members", value=ctx.guild.member_count, inline=True)
            embed.add_field(name="Bots", value=findbots, inline=True)
            embed.add_field(name="Owner", value=ctx.guild.owner, inline=True)
            embed.add_field(name="Region", value=ctx.guild.region, inline=True)
            embed.add_field(name="Emojis", value=emojilist, inline=False)
            embed.add_field(
                name="Created", value=default.date(ctx.guild.created_at), inline=False
            )
            await ctx.send(
                content=f"ℹ information about **{ctx.guild.name}**", embed=embed
            )

    @commands.command()
    @commands.guild_only()
    async def user(self, ctx, user: discord.Member = None):
        """ Get user information """
        rowcheck = await self.getserverstuff(ctx)

        if user is None:
            user = ctx.author

        embed = discord.Embed(colour=249_742)

        usrstatus = user.status

        if usrstatus == "online" or usrstatus == discord.Status.online:
            usrstatus = "<:online:514203909363859459> Online"
        elif usrstatus == "idle" or usrstatus == discord.Status.idle:
            usrstatus = "<:away:514203859057639444> Away"
        elif usrstatus == "dnd" or usrstatus == discord.Status.dnd:
            usrstatus = "<:dnd:514203823888138240> DnD"
        elif usrstatus == "offline" or usrstatus == discord.Status.offline:
            usrstatus = "<:offline:514203770452836359> Offline"
        else:
            usrstatus = "Broken"

        if user.nick:
            nick = user.nick
        else:
            nick = "No Nickname"

        if user.activity:
            usrgame = f"{user.activity.name}"
        else:
            usrgame = "No current game"

        usrroles = ""

        for Role in user.roles:
            if "@everyone" in Role.name:
                usrroles += "| @everyone | "
            else:
                usrroles += f"{Role.name} | "

        if len(usrroles) > 1024:
            usrroles = "Too many to count!"

        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            return await ctx.send(
                f"Name: `{user.name}#{user.discriminator}`\nNick: `{nick}`\nUID: `{user.id}`\nStatus: {usrstatus}\nGame: `{usrgame}`\nIs a bot? `{user.bot}`\nCreated On: `{default.date(user.created_at)}`\nRoles:\n```\n{usrroles}\n```"
            )

        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(
            name="Name",
            value=f"{user.name}#{user.discriminator}\n{nick}\n({user.id})",
            inline=True,
        )
        embed.add_field(name="Status", value=usrstatus, inline=True)
        embed.add_field(name="Game", value=usrgame, inline=True)
        embed.add_field(name="Is bot?", value=user.bot, inline=True)
        embed.add_field(name="Roles", value=usrroles, inline=False)
        embed.add_field(
            name="Created On", value=default.date(user.created_at), inline=True
        )
        if hasattr(user, "joined_at"):
            embed.add_field(
                name="Joined this server",
                value=default.date(user.joined_at),
                inline=True,
            )
        await ctx.send(content=f"ℹ About **{user.name}**", embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def poll(self, ctx, time, *, question):
        """
        Creates a poll
        """
        await ctx.message.delete()
        time = int(time)
        pollmsg = await ctx.send(
            f"{ctx.message.author.mention} created a poll that will end after {time} seconds!\n**{question}**\n\nReact with :thumbsup: or :thumbsdown: to vote!"
        )
        await pollmsg.add_reaction("👍")
        await pollmsg.add_reaction("👎")
        await asyncio.sleep(time)
        reactiongrab = await ctx.channel.fetch_message(pollmsg.id)
        for reaction in reactiongrab.reactions:
            if reaction.emoji == str("👍"):
                upvote_count = reaction.count
            else:
                if reaction.emoji == str("👎"):
                    downvote_count = reaction.count
                else:
                    pass
        await pollmsg.clear_reactions()
        await pollmsg.edit(
            content=f"{ctx.message.author.mention} created a poll that will end after {time} seconds!\n**{question}**\n\nTime's up!\n👍 = {upvote_count-1}\n\n👎 = {downvote_count-1}"
        )

    @commands.command()
    async def args(self, ctx, *args):
        """Returns the number of args"""
        await ctx.send("{} arguments: {}".format(len(args), ", ".join(args)))

    @commands.command()
    async def compare(self, ctx, str1: str = None, str2: str = None):
        """ Compare 2 strings, put in "" for multiple words per string """
        if str1 == str2:
            await ctx.send("The two strings are the same!")
        else:
            await ctx.send("The two strings are different...")

    @commands.command()
    @commands.guild_only()
    async def remindme(self, ctx, time: int, *, reminder):
        """ Pings you with the reminder after an amount of minutes """
        if self.counter[f"{ctx.author.id}.reminder"] == 1:
            return await ctx.send("You already have a current reminder!")
        if len(reminder) > 1500:
            return ctx.send("That reminder is too big!")
        timetowait = int(time * 60)
        if timetowait > 604_800:
            return await ctx.send(
                "That's too long! I can wait up to 7 days (10080 mins)."
            )
        timetowait = int(timetowait)
        await ctx.send(f"Ok! I'll remind you in `{time}` minute(s) about `{reminder}`")
        self.counter[f"{ctx.author.id}.reminder"] += 1
        await asyncio.sleep(timetowait)
        await ctx.send(f"{ctx.author.mention} your reminder: `{reminder}` is complete!")
        self.counter[f"{ctx.author.id}.reminder"] -= 1

    @commands.command()
    async def jumbo(self, ctx, emoji: discord.PartialEmoji):
        """ Makes your emoji  B I G """
        def url_to_bytes(url):
            data = requests.get(url)
            content = io.BytesIO(data.content)
            tempurl = str(url)
            filename = tempurl.rsplit("/", 1)[-1]
            return {"content": content, "filename": filename}

        file = url_to_bytes(emoji.url)
        await ctx.send(file=discord.File(file["content"], file["filename"]))

    @commands.command()
    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    async def nitro(self, ctx, *, emoji: commands.clean_content):
        """ Allows you to use nitro emojis """
        nitromote = discord.utils.find(
            lambda e: e.name.lower() == emoji.lower(), self.bot.emojis
        )
        if nitromote is None:
            return await ctx.send(
                f":warning: | **Sorry, no matches found for `{emoji.lower()}`**"
            )
        await ctx.send(f"{nitromote}")

    @commands.command()
    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    async def calc(self, ctx, *, calculation: str):
        """ Performs a calculation """
        r = requests.get(
            f"http://api.mathjs.org/v4/?expr={quote(calculation)}"
        )
        await ctx.send(r.text)

    @commands.command(name="eval")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def _eval(self, ctx, *, code: commands.clean_content):
        """ Runs a piece of python code """
        r = requests.post(
            "http://coliru.stacked-crooked.com/compile",
            data=json.dumps(
                {"cmd": "python3 main.cpp", "src": self.cleanup_code(code)}
            ),
        )
        emoji = self.bot.get_emoji(508_388_437_661_843_483)
        await ctx.message.add_reaction(emoji)
        await ctx.send(
            f"```py\n{r.text}\n```\n(This is **not** an open eval, everything is sandboxed)"
        )

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=2, per=5.0, type=commands.BucketType.user)
    async def charinfo(self, ctx, *, characters: str):
        """ Shows you information about a number of characters. """

        def to_string(c):
            digit = f"{ord(c):x}"
            name = unicodedata.name(c, "Name not found.")
            return f"`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>"

        msg = "\n".join(map(to_string, characters))
        if len(msg) > 2000:
            return await ctx.send("Output too long to display.")
        await ctx.send(msg)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def osu(self, ctx, osuplayer, usrhex: str = 170_041):
        """ Shows an osu! profile. """
        embed = discord.Embed(color=random.randint(0x000000, 0xFFFFFF))
        embed.set_image(
            url="http://lemmmy.pw/osusig/sig.php?colour=hex{0}&uname={1}&pp=1&countryrank&removeavmargin&flagshadow&flagstroke&darktriangles&onlineindicator=undefined&xpbar&xpbarhex".format(
                usrhex, osuplayer
            )
        )
        embed.set_footer(
            text="Powered by lemmmy.pw",
            icon_url="https://raw.githubusercontent.com/F4stZ4p/resources-for-discord-bot/master/osusmall.ico",
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def source(self, ctx):
        """ Where did you come from where did you go? """
        await ctx.send(
            "You can find my source @ https://github.com/pawbot-discord/Pawbot x3"
        )


def setup(bot):
    bot.add_cog(Information(bot))
