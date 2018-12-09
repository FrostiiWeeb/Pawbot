import discord
import re
import random

from io import BytesIO
from discord.ext import commands
from utils import permissions, default


class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
        else:
            can_execute = ctx.author.id == ctx.bot.owner_id or \
                          ctx.author == ctx.guild.owner or \
                          ctx.author.top_role > m.top_role

            if not can_execute:
                raise commands.BadArgument('You cannot do this action on this user due to role hierarchy.')
            return m.id


class ActionReason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = argument

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
        return ret


class Moderation:
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")

    @staticmethod
    def generatecase():
        case = random.randint(11111, 99999)
        return f"{int(case)}"
    
    async def getmodlogstuff(self, ctx):
        storequery = "SELECT * FROM idstore WHERE serverid = $1;"
        storerow = await self.bot.db.fetchrow(storequery, ctx.guild.id)
        if storerow is None:
            query = "INSERT INTO idstore VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            await self.bot.db.execute(query, ctx.guild.id, "Default", "Default", 0, 0, 0, 0, 0, 0)
            query = "SELECT * FROM idstore WHERE serverid = $1;"
            row = await self.bot.db.fetchrow(query, ctx.guild.id)
        return storerow 

    async def getautomod(self, ctx):
        query = "SELECT * FROM automod WHERE serverid = $1;"
        row = await self.bot.db.fetchrow(query, ctx.guild.id)
        if row is None:
            query = "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            await self.bot.db.execute(query, ctx.guild.id, 0, 0, 0, 0, 10, 10, 0, 0)
            query = "SELECT * FROM automod WHERE serverid = $1;"
            row = await self.bot.db.fetchrow(query, ctx.guild.id)
        return row 

    async def getserverstuff(self, ctx):
        query = "SELECT * FROM adminpanel WHERE serverid = $1;"
        row = await self.bot.db.fetchrow(query, ctx.guild.id)
        if row is None:
            query = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(query, ctx.guild.id, 0, 0, 1, 0, 0, 0)
            query = "SELECT * FROM adminpanel WHERE serverid = $1;"
            row = await self.bot.db.fetchrow(query, ctx.guild.id)
        return row

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(kick_members=True)
    async def reason(self, ctx, case: int = None, *, reason: str = None):
        """ Kicks a user from the current server. """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck['modlog'] is 0 or None:
            return await ctx.send("Modlog isn't enabled ;-;")
        if case is None:
            return await ctx.send("That isn't a valid case...")
        query = "SELECT * FROM modlogs WHERE serverid = $1 AND casenumber = $2;"
        row = await self.bot.db.fetchrow(query, ctx.guild.id, case)
        if row is None:
            return await ctx.send("That isn't a valid case...")
        query = "UPDATE modlogs SET reason = $1 WHERE serverid = $2 AND casenumber = $3;"
        await self.bot.db.execute(query, reason, ctx.guild.id, case)
        target = self.bot.get_user(row['target'])
        query = "UPDATE modlogs SET moderator = $1 WHERE serverid = $2 AND casenumber = $3;"
        await self.bot.db.execute(query, ctx.author.id, ctx.guild.id, case)
        moderator = self.bot.get_user(row['moderator'])
        logchannel = await self.getmodlogstuff(ctx)
        logchannel = ctx.guild.get_channel(logchannel['modlogchan'])
        try:
            msgtoedit = await logchannel.get_message(row['caseid'])
            await msgtoedit.edit(content=f"**{row['casetype']}** | Case {row['casenumber']}\n**User**: {target.name}#{target.discriminator} ({target.id}) ({target.mention})\n**Reason**: {reason}\n**Responsible Moderator**: {moderator.name}#{moderator.discriminator}")
        except discord.Forbidden:
            return await ctx.send("Something broke ;w;")
        await ctx.message.delete()

    @commands.command()
    @commands.guild_only()
    async def warns(self, ctx, member: discord.Member = None):
        """ Checks user warns """
        if member is None:
            member = ctx.author
        query = "SELECT warnings FROM warnings WHERE serverid = $1 AND userid = $2;"
        row = await self.bot.db.fetchrow(query, ctx.guild.id, member.id)
        if row is None:
            query = "INSERT INTO warnings VALUES ($1, $2, 0);"
            await self.bot.db.execute(query, ctx.guild.id, member.id)
            await ctx.send(f"{member.name} currently has **0** warnings.")
        else:
            await ctx.send(f"{member.name} currently has **{row['warnings']}** warnings.")

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(ban_members=True)
    async def warn(self, ctx, member: discord.Member, amount: int = None):
        """ Gives a user a set amount of warnings """
        query = "SELECT warnings FROM warnings WHERE serverid = $1 AND userid = $2;"
        row = await self.bot.db.fetchrow(query, ctx.guild.id, member.id)
        if row is None:
            query = "INSERT INTO warnings VALUES ($1, $2, $3);"
            await self.bot.db.execute(query, ctx.guild.id, member.id, amount)
            await ctx.send(f"I added **{amount}** to {member.mention}'s warns! They now have **{amount}**.")
        else:
            query = "SELECT warnings FROM warnings WHERE serverid = $1 AND userid = $2;"
            row = await self.bot.db.fetchrow(query, ctx.guild.id, member.id)
            amountgiven = int(row['warnings'] + amount)
            query = "UPDATE warnings SET warnings = $1 WHERE serverid = $2 AND userid = $3;"
            await self.bot.db.execute(query, amountgiven, ctx.guild.id, member.id)
            await ctx.send(f"I added **{amount}** to {member.mention}'s warns! They now have **{amountgiven}**.")

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(ban_members=True)
    async def unwarn(self, ctx, member: discord.Member, amount: int = None):
        """ Takes warnings from a user """
        query = "SELECT warnings FROM warnings WHERE serverid = $1 AND userid = $2;"
        row = await self.bot.db.fetchrow(query, ctx.guild.id, member.id)
        if row is None:
            query = "INSERT INTO warnings VALUES ($1, $2, $3);"
            await self.bot.db.execute(query, ctx.guild.id, member.id, amount)
            await ctx.send(f"{member.name} was not in my database! They have **0** warns though!")
        else:
            query = "SELECT warnings FROM warnings WHERE serverid = $1 AND userid = $2;"
            row = await self.bot.db.fetchrow(query, ctx.guild.id, member.id)
            amountgiven = int(row['warnings'] - amount)
            query = "UPDATE warnings SET warnings = $1 WHERE serverid = $2 AND userid = $3;"
            await self.bot.db.execute(query, amountgiven, ctx.guild.id, member.id)
            await ctx.send(f"I took **{amount}** from {member.mention}'s warns! They now have **{amountgiven}**.")

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        """ Kicks a user from the current server. """
        try:
            await member.kick()
            logchannel = await self.getmodlogstuff(ctx)
            logchannel = ctx.guild.get_channel(logchannel['modlogchan'])
            casenum = self.generatecase()
            if reason is None:
                reason = f"Responsible moderator, please type `paw reason {casenum} <reason>`"
            
            rowcheck = await self.getserverstuff(ctx)
            if rowcheck['modlog'] is 0 or None:
                return

            logmsg = await logchannel.send(f"**Kick** | Case {casenum}\n**User**: {member.name}#{member.discriminator} ({member.id}) ({member.mention})\n**Reason**: {reason}\n**Responsible Moderator**: {ctx.author.name}#{ctx.author.discriminator}")
            query = "INSERT INTO modlogs VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(query, ctx.guild.id, logmsg.id, int(casenum), "Kick", member.id, ctx.author.id, reason)
        except discord.Forbidden as e:
            await ctx.send(e)

    @commands.command(aliases=["nick"])
    @commands.guild_only()
    @permissions.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: discord.Member, *, name: str = None):
        """ Nicknames a user from the current server. """
        try:
            await member.edit(nick=name)
            message = f"👌 Changed **{member.name}'s** nickname to **{name}**"
            if name is None:
                message = f"👌 Reset **{member.name}'s** nickname"
            await ctx.send(message)
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):
        """ Bans a user from the current server. """
        try:
            await ctx.guild.ban(member)
            logchannel = await self.getmodlogstuff(ctx)
            logchannel = ctx.guild.get_channel(logchannel['modlogchan'])
            casenum = self.generatecase()
            if reason is None:
                reason = f"Responsible moderator, please type `paw reason {casenum} <reason>`"

            rowcheck = await self.getserverstuff(ctx)
            if rowcheck['modlog'] is 0 or None:
                return

            logmsg = await logchannel.send(f"**Ban** | Case {casenum}\n**User**: {member.name}#{member.discriminator} ({member.id}) ({member.mention})\n**Reason**: {reason}\n**Responsible Moderator**: {ctx.author.name}#{ctx.author.discriminator}")
            query = "INSERT INTO modlogs VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(query, ctx.guild.id, logmsg.id, int(casenum), "Ban", member.id, ctx.author.id, reason)
        except discord.Forbidden as e:
            await ctx.send(e)

    @commands.command(aliases=['hackban'])
    @commands.guild_only()
    @permissions.has_permissions(ban_members=True)
    async def idban(self, ctx, banmember: int, *, reason: str = None):
        """ Bans a user id from the current server. """
        try:
            await ctx.guild.ban(discord.Object(id=banmember))
            member = self.bot.get_user(banmember)
            logchannel = await self.getmodlogstuff(ctx)
            logchannel = ctx.guild.get_channel(logchannel['modlogchan'])
            casenum = self.generatecase()
            if reason is None:
                reason = f"Responsible moderator, please type `paw reason {casenum} <reason>`"

            rowcheck = await self.getserverstuff(ctx)
            if rowcheck['modlog'] is 0 or None:
                return

            logmsg = await logchannel.send(f"**Hackban** | Case {casenum}\n**User**: {member.name}#{member.discriminator} ({member.id}) ({member.mention})\n**Reason**: {reason}\n**Responsible Moderator**: {ctx.author.name}#{ctx.author.discriminator}")
            query = "INSERT INTO modlogs VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(query, ctx.guild.id, logmsg.id, int(casenum), "Hackban", member.id, ctx.author.id, reason)
        except discord.Forbidden as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(ban_members=True)
    async def unban(self, ctx, banmember: int, *, reason: str = None):
        """ Unbans a user from the current server. """
        try:
            await ctx.guild.unban(discord.Object(id=banmember))
            member = self.bot.get_user(banmember)
            logchannel = await self.getmodlogstuff(ctx)
            logchannel = ctx.guild.get_channel(logchannel['modlogchan'])
            casenum = self.generatecase()
            if reason is None:
                reason = f"Responsible moderator, please type `paw reason {casenum} <reason>`"

            rowcheck = await self.getserverstuff(ctx)
            if rowcheck['modlog'] is 0 or None:
                return

            logmsg = await logchannel.send(f"**Unban** | Case {casenum}\n**User**: {member.name}#{member.discriminator} ({member.id}) ({member.mention})\n**Reason**: {reason}\n**Responsible Moderator**: {ctx.author.name}#{ctx.author.discriminator}")
            query = "INSERT INTO modlogs VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(query, ctx.guild.id, logmsg.id, int(casenum), "Unban", member.id, ctx.author.id, reason)
        except discord.Forbidden as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason: str = None):
        """ Mutes a user from the current server. """
        message = []
        for role in ctx.guild.roles:
            if role.name == "Muted":
                message.append(role.id)
        try:
            therole = discord.Object(id=message[0])
        except IndexError:
            return await ctx.send("Are you sure you've made a role called **Muted**? Remember that it's case sensitive too...")

        try:
            await member.add_roles(therole)
            logchannel = await self.getmodlogstuff(ctx)
            logchannel = ctx.guild.get_channel(logchannel['modlogchan'])
            casenum = self.generatecase()
            if reason is None:
                reason = f"Responsible moderator, please type `paw reason {casenum} <reason>`"

            rowcheck = await self.getserverstuff(ctx)
            if rowcheck['modlog'] is 0 or None:
                return

            logmsg = await logchannel.send(f"**Mute** | Case {casenum}\n**User**: {member.name}#{member.discriminator} ({member.id}) ({member.mention})\n**Reason**: {reason}\n**Responsible Moderator**: {ctx.author.name}#{ctx.author.discriminator}")
            query = "INSERT INTO modlogs VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(query, ctx.guild.id, logmsg.id, int(casenum), "Mute", member.id, ctx.author.id, reason)
        except discord.Forbidden as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = None):
        """ Unmutes a user from the current server. """
        message = []
        for role in ctx.guild.roles:
            if role.name == "Muted":
                message.append(role.id)
        try:
            therole = discord.Object(id=message[0])
        except IndexError:
            return await ctx.send("Are you sure you've made a role called **Muted**? Remember that it's case sensitive too...")

        try:
            await member.remove_roles(therole)
            logchannel = await self.getmodlogstuff(ctx)
            logchannel = ctx.guild.get_channel(logchannel['modlogchan'])
            casenum = self.generatecase()
            if reason is None:
                reason = f"Responsible moderator, please type `paw reason {casenum} <reason>`"

            rowcheck = await self.getserverstuff(ctx)
            if rowcheck['modlog'] is 0 or None:
                return

            logmsg = await logchannel.send(f"**Unmute** | Case {casenum}\n**User**: {member.name}#{member.discriminator} ({member.id}) ({member.mention})\n**Reason**: {reason}\n**Responsible Moderator**: {ctx.author.name}#{ctx.author.discriminator}")
            query = "INSERT INTO modlogs VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(query, ctx.guild.id, logmsg.id, int(casenum), "Unmute", member.id, ctx.author.id, reason)
        except discord.Forbidden as e:
            await ctx.send(e)

    @commands.group()
    @commands.guild_only()
    @permissions.has_permissions(ban_members=True)
    async def find(self, ctx):
        """ Finds a user within your search term """
        if ctx.invoked_subcommand is None:
            _help = await ctx.bot.formatter.format_help_for(ctx, ctx.command)

            for page in _help:
                await ctx.send(page)

    @find.command(name="playing")
    async def find_playing(self, ctx, *, search: str):
        result = [f"{i} | {i.activity.name}\r\n" for i in ctx.guild.members if (i.activity is not None) and (search.lower() in i.activity.name.lower()) and (not i.bot)]
        if result is None:
            return await ctx.send("Your search result was empty...")
        data = BytesIO(''.join(result).encode('utf-8'))
        await ctx.send(content=f"Found **{len(result)}** on your search for **{search}**",
                       file=discord.File(data, filename=default.timetext(f'PlayingSearch')))

    @find.command(name="username", aliases=["name"])
    async def find_name(self, ctx, *, search: str):
        result = [f"{i}\r\n" for i in ctx.guild.members if (search.lower() in i.name.lower())]
        if result is None:
            return await ctx.send("Your search result was empty...")
        data = BytesIO(''.join(result).encode('utf-8'))
        await ctx.send(content=f"Found **{len(result)}** on your search for **{search}**",
                       file=discord.File(data, filename=default.timetext(f'NameSearch')))

    @find.command(name="discriminator", aliases=["discrim"])
    async def find_discriminator(self, ctx, *, search: str):
        result = [f"{i}\r\n" for i in ctx.guild.members if (search in i.discriminator)]
        if result is None:
            return await ctx.send("Your search result was empty...")
        data = BytesIO(''.join(result).encode('utf-8'))
        await ctx.send(content=f"Found **{len(result)}** on your search for **{search}**",
                       file=discord.File(data, filename=default.timetext(f'DiscriminatorSearch')))

    @commands.group()
    @commands.guild_only()
    @permissions.has_permissions(manage_messages=True)
    async def prune(self, ctx):
        """ Removes messages from the current server. """

        if ctx.invoked_subcommand is None:
            _help = await ctx.bot.formatter.format_help_for(ctx, ctx.command)

            for page in _help:
                await ctx.send(page)

    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None, message=True):
        if limit > 2000:
            return await ctx.send(f'Too many messages to search given ({limit}/2000)')

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden:
            return await ctx.send('I do not have permissions to delete messages.')
        except discord.HTTPException as e:
            return await ctx.send(f'Error: {e} (try a smaller search?)')

        deleted = len(deleted)
        if message is True:
            await ctx.send(f'🚮 Successfully removed {deleted} message{"" if deleted == 1 else "s"}.')

    @prune.command()
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @prune.command()
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @prune.command()
    async def images(self, ctx, search=100):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))

    @prune.command(name='all')
    async def _remove_all(self, ctx, search=100):
        """Removes all messages."""
        await self.do_removal(ctx, search, lambda e: True)

    @prune.command()
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @prune.command()
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring.
        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.send('The substring length must be at least 3 characters.')
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @prune.command(name='bots')
    async def _bots(self, ctx, prefix=None, search=100):
        """Removes a bot user's messages and messages with their optional prefix."""

        def predicate(m):
            return m.author.bot or (prefix and m.content.startswith(prefix))

        await self.do_removal(ctx, search, predicate)

    @prune.command(name='users')
    async def _users(self, ctx, search=100):
        """Removes only user messages. """

        def predicate(m):
            return m.author.bot is False

        await self.do_removal(ctx, search, predicate)

    @prune.command(name='emoji')
    async def _emoji(self, ctx, search=100):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r'<:(\w+):(\d+)>')

        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def ra(self, ctx, member: discord.Member, *, rolename: str = None):
        """ Gives the role to the user. """
        role = discord.utils.get(ctx.guild.roles, name=rolename)
        await member.add_roles(role)
        await ctx.send(f"👌 I have given **{member.name}** the **{role.name}** role!")

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def rr(self, ctx, member: discord.Member, *, rolename: str = None):
        """ Removes the role from a user. """
        role = discord.utils.get(ctx.guild.roles, name=rolename)
        await member.remove_roles(role)
        await ctx.send(f"👌 I have removed **{member.name}** from the **{role.name}** role!")

    @commands.command()
    @commands.guild_only()
    async def move(self, ctx, msgid: int, channel: discord.TextChannel):
        """ Moves a message id to another channel. """
        msgtodel = await ctx.channel.get_message(msgid)
        rowcheck = await self.getserverstuff(ctx)
        await msgtodel.delete()
        await ctx.message.delete()
        if rowcheck['embeds'] is 0 or not permissions.can_embed(ctx):
            return await channel.send(f"```\n{msgtodel.author.name}#{msgtodel.author.discriminator}: {msgtodel.content}\n```")
        embed = discord.Embed(colour=discord.Colour(0x5fa05e), description=f"{msgtodel.content}")
        embed.set_author(name=f"{msgtodel.author.name}", icon_url=f"{msgtodel.author.avatar_url}")
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Moderation(bot))
