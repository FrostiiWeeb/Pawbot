import dhooks
import discord
import traceback
import psutil
import os
import random
from utils import eapi

from datetime import datetime
from collections import deque
from dhooks import Webhook, Embed
from discord.ext import commands
from discord.ext.commands import errors
from utils import default, lists


class SnipeHistory(deque):
    def __init__(self):
        super().__init__(maxlen=5)

    def __repr__(self):
        return "Pawbot Snipe History"


async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        _help = await ctx.bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
    else:
        _help = await ctx.bot.formatter.format_help_for(ctx, ctx.command)

    for page in _help:
        await ctx.send(page)


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self.process = psutil.Process(os.getpid())

    @staticmethod
    def generatecase():
        case = random.randint(11111, 99999)
        return f"{int(case)}"

    async def getserverstuff(self, member):
        query = "SELECT * FROM adminpanel WHERE serverid = $1;"
        row = await self.bot.db.fetchrow(query, member.guild.id)
        if row is None:
            query = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(query, member.guild.id, 0, 0, 1, 0, 0, 0)
            query = "SELECT * FROM adminpanel WHERE serverid = $1;"
            row = await self.bot.db.fetchrow(query, member.guild.id)
        return row

    async def getautomod(self, member):
        query = "SELECT * FROM automod WHERE serverid = $1;"
        row = await self.bot.db.fetchrow(query, member.guild.id)
        if row is None:
            query = "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            await self.bot.db.execute(query, member.guild.id, 0, 0, 0, 0, 10, 10, 0, 0)
            query = "SELECT * FROM automod WHERE serverid = $1;"
            row = await self.bot.db.fetchrow(query, member.guild.id)
        return row

    async def getstorestuff(self, member):
        storequery = "SELECT * FROM idstore WHERE serverid = $1;"
        storerow = await self.bot.db.fetchrow(storequery, member.guild.id)
        if storerow is None:
            query = "INSERT INTO idstore VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            await self.bot.db.execute(
                query, member.guild.id, "Default", "Default", 0, 0, 0, 0, 0, 0
            )
            query = "SELECT * FROM idstore WHERE serverid = $1;"
            storerow = await self.bot.db.fetchrow(query, member.guild.id)
        return storerow

    async def getserverstuffalt(self, guild):
        query = "SELECT * FROM adminpanel WHERE serverid = $1;"
        row = await self.bot.db.fetchrow(query, guild.id)
        if row is None:
            query = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(query, guild.id, 0, 0, 1, 0, 0, 0)
            query = "SELECT * FROM adminpanel WHERE serverid = $1;"
            row = await self.bot.db.fetchrow(query, guild.id)
        return row

    async def getstorestuffalt(self, guild):
        storequery = "SELECT * FROM idstore WHERE serverid = $1;"
        storerow = await self.bot.db.fetchrow(storequery, guild.id)
        if storerow is None:
            query = "INSERT INTO idstore VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            await self.bot.db.execute(
                query, guild.id, "Default", "Default", 0, 0, 0, 0, 0, 0
            )
            query = "SELECT * FROM idstore WHERE serverid = $1;"
            storerow = await self.bot.db.fetchrow(query, guild.id)
        return storerow

    async def getstorestuffmessages(self, message):
        storequery = "SELECT * FROM idstore WHERE serverid = $1;"
        storerow = await self.bot.db.fetchrow(storequery, message.guild.id)
        if storerow is None:
            query = "INSERT INTO idstore VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            await self.bot.db.execute(
                query, message.guild.id, "Default", "Default", 0, 0, 0, 0, 0, 0
            )
            query = "SELECT * FROM idstore WHERE serverid = $1;"
            storerow = await self.bot.db.fetchrow(query, message.guild.id)
        return storerow

    async def getserverstuffmessages(self, message):
        query = "SELECT * FROM adminpanel WHERE serverid = $1;"
        row = await self.bot.db.fetchrow(query, message.guild.id)
        if row is None:
            query = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(query, message.guild.id, 0, 0, 1, 0, 0, 0)
            query = "SELECT * FROM adminpanel WHERE serverid = $1;"
            row = await self.bot.db.fetchrow(query, message.guild.id)
        return row

    async def getautomodmessages(self, message):
        query = "SELECT * FROM automod WHERE serverid = $1;"
        row = await self.bot.db.fetchrow(query, message.guild.id)
        if row is None:
            query = "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            await self.bot.db.execute(query, message.guild.id, 0, 0, 0, 0, 10, 10, 0, 0)
            query = "SELECT * FROM automod WHERE serverid = $1;"
            row = await self.bot.db.fetchrow(query, message.guild.id)
        return row

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, (errors.BadArgument, errors.MissingRequiredArgument)):
            await send_cmd_help(ctx)

        elif isinstance(err, eapi.ResultNotFound):
            pass

        elif isinstance(err, errors.CommandInvokeError):
            err = err.original

            _traceback = traceback.format_tb(err.__traceback__)
            _traceback = "".join(_traceback)
            error = "```py\n{2}{0}: {3}\n```".format(
                type(err).__name__, ctx.message.content, _traceback, err
            )
            logchannel = self.bot.get_channel(508_420_200_815_656_966)
            await ctx.send(
                "There was an error in processing the command, our staff team have been notified, and will be in contact soon."
            )
            errorlog = f"`[WARN]` `Command Error`\n{error}\nRoot Server: {ctx.guild.name} ({ctx.guild.id})\nRoot Channel: {ctx.channel.name} ({ctx.channel.id})\nRoot User: {ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id})\n\n<@127452209070735361>"
            if len(errorlog) > 1500:
                print(errorlog)
            await logchannel.send(f"{errorlog}")

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.CommandOnCooldown):
            await ctx.send(
                f"You're being rate limited... Try again in {err.retry_after:.0f} seconds.",
                delete_after=4,
            )

        elif isinstance(err, errors.CommandNotFound):
            pass

    @commands.Cog.listener()
    async def on_ready(self):
        if not hasattr(self.bot, "uptime"):
            self.bot.uptime = datetime.utcnow()
        webhook = Webhook(self.config.readywebhook, is_async=True)
        embed = Embed(
            title=f"Reconnected, Online and Operational!",
            description="Ready Info",
            color=5_810_826,
            timestamp=True,
        )
        embed.set_author(
            name=f"PawBot",
            url="https://discordapp.com/oauth2/authorize?client_id=460383314973556756&scope=bot&permissions=469888118",
            icon_url="https://cdn.discordapp.com/avatars/460383314973556756/2814a7328962f7947a25ccd2ee177ac1.webp",
        )
        embed.add_field(name="Guilds", value=f"**{len(self.bot.guilds)}**", inline=True)
        embed.add_field(name="Users", value=f"**{len(self.bot.users)}**", inline=True)
        await webhook.execute(embeds=embed)
        await webhook.close()
        await self.bot.change_presence(
            activity=discord.Game(
                type=0, name=f"{random.choice(lists.randomPlayings)} | paw help"
            ),
            status=discord.Status.online,
        )

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if not guild.icon_url:
            guildicon = "https://cdn.discordapp.com/attachments/443347566231289856/513380120451350541/2mt196.jpg"
        else:
            guildicon = guild.icon_url
        findbots = sum(1 for member in guild.members if member.bot)
        findusers = sum(1 for member in guild.members if not member.bot)
        webhook = Webhook(self.config.guildjoinwebhook, is_async=True)
        embed = Embed(
            description=f"I've joined {guild.name}!", color=5_810_826, timestamp=True
        )
        embed.set_author(
            name=f"{guild.name}",
            url="https://discordapp.com/oauth2/authorize?client_id=460383314973556756&scope=bot&permissions=469888118",
            icon_url=guildicon,
        )
        embed.set_thumbnail(url=guildicon)
        embed.add_field(
            name="Info",
            value=f"New guild count: **{len(self.bot.guilds)}**\nOwner: **{guild.owner}**\nUsers/Bot Ratio: **{findusers}/{findbots}**",
        )
        await webhook.execute(embeds=embed, username=guild.name, avatar_url=guildicon)
        await webhook.close()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        if not guild.icon_url:
            guildicon = "https://cdn.discordapp.com/attachments/443347566231289856/513380120451350541/2mt196.jpg"
        else:
            guildicon = guild.icon_url
        findbots = sum(1 for member in guild.members if member.bot)
        findusers = sum(1 for member in guild.members if not member.bot)
        webhook = Webhook(self.config.guildleavewebhook, is_async=True)
        embed = Embed(
            description=f"I've left {guild.name}...", color=5_810_826, timestamp=True
        )
        embed.set_author(
            name=f"{guild.name}",
            url="https://discordapp.com/oauth2/authorize?client_id=460383314973556756&scope=bot&permissions=469888118",
            icon_url=guildicon,
        )
        embed.set_thumbnail(url=guildicon)
        embed.add_field(
            name="Info",
            value=f"New guild count: **{len(self.bot.guilds)}**\nOwner: **{guild.owner}**\nUsers/Bot Ratio: **{findusers}/{findbots}**",
        )
        await webhook.execute(embeds=embed, username=guild.name, avatar_url=guildicon)
        await webhook.close()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        adminpanelcheck = await self.getserverstuff(member)
        serverstorecheck = await self.getstorestuff(member)
        automodcheck = await self.getautomod(member)
        if adminpanelcheck["automod"] == 1:
            if automodcheck["lockdown"] == 1:
                await member.send(
                    f"Sorry but **{member.guild.name}** is currently on lockdown, try again later! >.<"
                )
                return await member.kick(reason="[Automod] Lockdown Enabled")
            if automodcheck["autorole"] == 1:
                try:
                    autorolerole = member.guild.get_role(
                        serverstorecheck["autorolerole"]
                    )
                    await member.add_roles(autorolerole)
                except discord.Forbidden:
                    pass
        if adminpanelcheck["joins"] == 1:
            try:
                welcomechannel = member.guild.get_channel(serverstorecheck["joinchan"])
                welcomemsg = (
                    serverstorecheck["joinmsg"]
                    .replace("%member%", f"{member.name}#{member.discriminator}")
                    .replace(
                        "Default",
                        f"Please welcome **{member.name}#{member.discriminator}!**",
                    )
                )
                await welcomechannel.send(welcomemsg)
            except discord.Forbidden:
                pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        adminpanelcheck = await self.getserverstuff(member)
        serverstorecheck = await self.getstorestuff(member)
        if adminpanelcheck["leaves"] == 1:
            try:
                byechan = member.guild.get_channel(serverstorecheck["leavechan"])
                byemsg = (
                    serverstorecheck["leavemsg"]
                    .replace("%member%", f"{member.name}#{member.discriminator}")
                    .replace(
                        "Default",
                        f"Goodbye **{member.name}#{member.discriminator}** we'll miss you...",
                    )
                )
                await byechan.send(byemsg)
            except discord.Forbidden:
                pass

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        adminpanelcheck = await self.getserverstuffmessages(message)
        serverstorecheck = await self.getstorestuffmessages(message)
        automodcheck = await self.getautomodmessages(message)
        if message.author.bot:
            return
        try:
            self.bot.snipes[message.channel.id].appendleft(message)
        except KeyError:
            self.bot.snipes[message.channel.id] = SnipeHistory()
            self.bot.snipes[message.channel.id].appendleft(message)
        if adminpanelcheck["automod"] == 1:
            if automodcheck["actionlog"] == 1:
                if message.author.bot:
                    return
                logchan = message.guild.get_channel(serverstorecheck["actionlogchan"])
                now = datetime.utcnow()
                now = now.strftime(" %c ")
                messagecontent = message.content
                if len(messagecontent) > 1500:
                    messagecontent = "Too big xwx"
                if adminpanelcheck["embeds"] == 0:
                    try:
                        return await logchan.send(
                            f"```\nMessage Deleted\nUser: {message.author}\nMessage: {messagecontent}\n\nDone at: {now} (UTC)\n```"
                        )
                    except discord.Forbidden:
                        pass
                if not message.author.avatar_url:
                    useravatar = "https://cdn.discordapp.com/attachments/443347566231289856/513380120451350541/2mt196.jpg"
                else:
                    useravatar = message.author.avatar_url
                embed = discord.Embed(
                    title="Message Deleted", colour=0xFF0000, description=messagecontent
                )
                embed.set_author(name=message.author, icon_url=useravatar)
                embed.set_footer(text=f"Deleted at: {now}")
                await logchan.send("", embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        adminpanelcheck = await self.getserverstuffmessages(after)
        serverstorecheck = await self.getstorestuffmessages(after)
        automodcheck = await self.getautomodmessages(after)
        if adminpanelcheck["automod"] == 1:
            if automodcheck["actionlog"] == 1:
                if before.author.bot:
                    return
                logchan = before.guild.get_channel(serverstorecheck["actionlogchan"])
                now = datetime.utcnow()
                now = now.strftime(" %c ")
                beforecontent = before.content
                if len(beforecontent) > 600:
                    beforecontent = "Too big xwx"
                aftercontent = after.content
                if len(aftercontent) > 600:
                    aftercontent = "Too big xwx"
                if adminpanelcheck["embeds"] == 0:
                    try:
                        return await logchan.send(
                            f"```\nMessage Edited\nUser: {before.author}\nMessage Before: {beforecontent}\nMessage After: {aftercontent}\n\nDone at: {now} (UTC)\n```"
                        )
                    except discord.Forbidden:
                        pass
                if not before.author.avatar_url:
                    useravatar = "https://cdn.discordapp.com/attachments/443347566231289856/513380120451350541/2mt196.jpg"
                else:
                    useravatar = before.author.avatar_url
                embed = discord.Embed(title="Message Edited", colour=0xFFF000)
                embed.set_author(name=before.author, icon_url=useravatar)
                embed.add_field(name="Before", value=beforecontent)
                embed.add_field(name="After", value=aftercontent)
                embed.set_footer(text=f"Edited at: {now}")
                await logchan.send("", embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        adminpanelcheck = await self.getserverstuffalt(guild)
        serverstorecheck = await self.getstorestuffalt(guild)
        if adminpanelcheck["modlog"] == 1:
            logchan = guild.get_channel(serverstorecheck["modlogchan"])
            casenum = self.generatecase()
            reason = (
                f"Responsible moderator, please type `paw reason {casenum} <reason>`"
            )
            try:
                logmsg = await logchan.send(
                    f"**Ban** | Case {casenum}\n**User**: {user} ({user.id}) ({user.mention})\n**Reason**: {reason}\n**Responsible Moderator**: unknown moderator"
                )
            except discord.Forbidden:
                pass
            query = "INSERT INTO modlogs VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(
                query,
                guild.id,
                logmsg.id,
                int(casenum),
                "Ban",
                user.id,
                460_383_314_973_556_756,
                reason,
            )

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        adminpanelcheck = await self.getserverstuffalt(guild)
        serverstorecheck = await self.getstorestuffalt(guild)
        if adminpanelcheck["modlog"] == 1:
            logchan = guild.get_channel(serverstorecheck["modlogchan"])
            casenum = self.generatecase()
            reason = (
                f"Responsible moderator, please type `paw reason {casenum} <reason>`"
            )
            try:
                logmsg = await logchan.send(
                    f"**Unban** | Case {casenum}\n**User**: {user.name}#{user.discriminator} ({user.id}) ({user.mention})\n**Reason**: {reason}\n**Responsible Moderator**: unknown moderator"
                )
            except discord.Forbidden:
                pass
            query = "INSERT INTO modlogs VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(
                query,
                guild.id,
                logmsg.id,
                int(casenum),
                "Unban",
                user.id,
                460_383_314_973_556_756,
                reason,
            )

    @commands.Cog.listener()
    async def on_command(self, ctx):
        logchan = self.bot.get_channel(508_420_200_815_656_966)
        now = datetime.utcnow()
        cmdmsg = await logchan.send(
            f'`[INFO]` `Command Run`\n```\nCommand: {ctx.command}\nUser: {ctx.author} ({ctx.author.id})\nChannel: {ctx.channel} ({ctx.channel.id})\n\nPerformed at: {now.strftime("%c")}```'
        )


def setup(bot):
    bot.add_cog(Events(bot))
