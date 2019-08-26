import discord

from discord.ext import commands
from utils import permissions, default


class AdminPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")

    defaultmsg = "Default"

    async def getserverstuff(self, ctx):
        query = "SELECT * FROM adminpanel WHERE serverid = $1;"
        row = await self.bot.db.fetchrow(query, ctx.guild.id)
        if row is None:
            query = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(query, ctx.guild.id, 0, 0, 1, 0, 0, 0)
            query = "SELECT * FROM adminpanel WHERE serverid = $1;"
            row = await self.bot.db.fetchrow(query, ctx.guild.id)
        return row

    async def getautomod(self, ctx):
        query = "SELECT * FROM automod WHERE serverid = $1;"
        row = await self.bot.db.fetchrow(query, ctx.guild.id)
        if row is None:
            query = "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            await self.bot.db.execute(query, ctx.guild.id, 0, 0, 0, 0, 10, 10, 0, 0)
            query = "SELECT * FROM automod WHERE serverid = $1;"
            row = await self.bot.db.fetchrow(query, ctx.guild.id)
        return row

    async def getstorestuff(self, ctx):
        storequery = "SELECT * FROM idstore WHERE serverid = $1;"
        storerow = await self.bot.db.fetchrow(storequery, ctx.guild.id)
        if storerow is None:
            query = "INSERT INTO idstore VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            await self.bot.db.execute(
                query, ctx.guild.id, "Default", "Default", 0, 0, 0, 0, 0, 0
            )
            query = "SELECT * FROM idstore WHERE serverid = $1;"
            storerow = await self.bot.db.fetchrow(query, ctx.guild.id)
        return storerow

    @commands.command(aliases=["adminpanel", "botconfig"])
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def conf(self, ctx):
        """ Displays current information on the config """
        automodrowcheck = await self.getautomod(ctx)
        storerow = await self.getstorestuff(ctx)

        query = "SELECT * FROM adminpanel WHERE serverid = $1;"
        row = await self.bot.db.fetchrow(query, ctx.guild.id)

        if row is None:
            query = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(query, ctx.guild.id, 0, 0, 1, 0, 0, 0)
            query = "SELECT * FROM adminpanel WHERE serverid = $1;"
            row = await self.bot.db.fetchrow(query, ctx.guild.id)
        if row["embeds"] == 1:
            embedscheck = "<:enabled:513831607355047964>"
        else:
            embedscheck = "<:disabled:513831606855794709>"
        if row["joins"] == 1:
            joincheck = "<:enabled:513831607355047964>"
        else:
            joincheck = "<:disabled:513831606855794709>"
        if row["leaves"] == 1:
            leavecheck = "<:enabled:513831607355047964>"
        else:
            leavecheck = "<:disabled:513831606855794709>"
        if row["nsfw"] == 1:
            nsfwcheck = "<:enabled:513831607355047964>"
        else:
            nsfwcheck = "<:disabled:513831606855794709>"
        if row["automod"] == 1:
            automodcheck = "<:enabled:513831607355047964>"
        else:
            automodcheck = "<:disabled:513831606855794709>"
        if row["modlog"] == 1:
            modlogcheck = "<:enabled:513831607355047964>"
        else:
            modlogcheck = "<:disabled:513831606855794709>"

        embed = discord.Embed(colour=discord.Colour(249_742))
        embed.add_field(name="Embeds", value=embedscheck, inline=True)
        embed.add_field(name="Join Messages", value=joincheck, inline=True)
        embed.add_field(name="Leave Messages", value=leavecheck, inline=True)
        embed.add_field(name="NSFW", value=nsfwcheck, inline=True)
        embed.add_field(name="Automod", value=automodcheck, inline=True)
        embed.add_field(name="Modlog", value=modlogcheck, inline=True)

        if row["automod"] == 1:
            if automodrowcheck["autorole"] == 1:
                embed.add_field(
                    name="Autorole", value="<:enabled:513831607355047964>", inline=True
                )
            else:
                embed.add_field(
                    name="Autorole", value="<:disabled:513831606855794709>", inline=True
                )
            if automodrowcheck["adblock"] == 1:
                embed.add_field(
                    name="Adblock", value="<:enabled:513831607355047964>", inline=True
                )
            else:
                embed.add_field(
                    name="Adblock", value="<:disabled:513831606855794709>", inline=True
                )
            if automodrowcheck["lockdown"] == 1:
                embed.add_field(
                    name="Lockdown", value="<:enabled:513831607355047964>", inline=True
                )
            else:
                embed.add_field(
                    name="Lockdown", value="<:disabled:513831606855794709>", inline=True
                )
            if automodrowcheck["antispam"] == 1:
                embed.add_field(
                    name="Antispam", value="<:enabled:513831607355047964>", inline=True
                )
            else:
                embed.add_field(
                    name="Antispam", value="<:disabled:513831606855794709>", inline=True
                )
            if automodrowcheck["ignorerole"] == 1:
                embed.add_field(
                    name="Ignore Role",
                    value="<:enabled:513831607355047964>",
                    inline=True,
                )
            else:
                embed.add_field(
                    name="Ignore Role",
                    value="<:disabled:513831606855794709>",
                    inline=True,
                )
            if automodrowcheck["actionlog"] == 1:
                embed.add_field(
                    name="Actionlog", value="<:enabled:513831607355047964>", inline=True
                )
            else:
                embed.add_field(
                    name="Actionlog",
                    value="<:disabled:513831606855794709>",
                    inline=True,
                )
        if row["joins"] == 1:
            guildjoinschannel = ctx.guild.get_channel(storerow["joinchan"])
            if guildjoinschannel is None:
                pass
            else:
                guildjoinsmsg = storerow["joinmsg"]
                embed.add_field(
                    name="Join Message & Channel",
                    value=f"`{guildjoinsmsg}` in {guildjoinschannel.mention}",
                    inline=False,
                )
        if row["leaves"] == 1:
            guildleaveschannel = ctx.guild.get_channel(storerow["leavechan"])
            if guildleaveschannel is None:
                pass
            else:
                guildleavesmsg = storerow["leavemsg"]
                embed.add_field(
                    name="Leave Message & Channel",
                    value=f"`{guildleavesmsg}` in {guildleaveschannel.mention}",
                    inline=False,
                )
        if row["modlog"] == 1:
            modlogchannel = ctx.guild.get_channel(storerow["modlogchan"])
            if modlogchannel is None:
                pass
            else:
                embed.add_field(
                    name="Moderation Log",
                    value=f"{modlogchannel.mention}",
                    inline=False,
                )
        if row["automod"] == 1:
            if automodrowcheck["actionlog"] == 1:
                actionlogchan = ctx.guild.get_channel(storerow["actionlogchan"])
                if actionlogchan is None:
                    pass
                else:
                    embed.add_field(
                        name="Action Log Channel",
                        value=f"{actionlogchan.mention}",
                        inline=False,
                    )
            if automodrowcheck["autorole"] == 1:
                autorole = ctx.guild.get_role(storerow["autorolerole"])
                if autorole is None:
                    pass
                else:
                    embed.add_field(
                        name="Auto Role-Role", value=f"{autorole.mention}", inline=False
                    )
            if automodrowcheck["ignorerole"] == 1:
                ignorerole = ctx.guild.get_role(storerow["ignorerolerole"])
                if ignorerole is None:
                    pass
                else:
                    embed.add_field(
                        name="Ignore Role", value=f"{ignorerole.mention}", inline=False
                    )
        try:
            await ctx.send(embed=embed)
        except discord.Forbidden:
            try:
                await ctx.author.send(embed=embed)
            except discord.Forbidden:
                await ctx.send("I can't send embeds or dm you ;-;")

    @commands.group()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def enable(self, ctx):
        """ Enables different modules """
        if ctx.invoked_subcommand is None:
            _help = await ctx.bot.formatter.format_help_for(ctx, ctx.command)

            for page in _help:
                await ctx.send(page)

    @enable.command(name="embeds", hidden=True)
    async def enable_embeds(self, ctx):
        """ Enables embeds on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT embeds FROM adminpanel WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
                await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 1, 0, 0, 0)
            thequery = "UPDATE adminpanel SET embeds=1 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully enabled **embeds**")
        thequery = "SELECT embeds FROM adminpanel WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 1, 0, 0, 0)
        thequery = "UPDATE adminpanel SET embeds=1 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="Embeds", description="<:enabled:513831607355047964>"
        )
        await ctx.send(embed=embed)

    @enable.command(name="joins", hidden=True)
    async def enable_joinmsg(
        self, ctx, joinschannel: discord.TextChannel, *, setjoinmsg: str = None
    ):
        """ Enables Join messages on the server """
        if setjoinmsg is None:
            setjoinmsg = "Welcome $member$ to the server!"
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT joins FROM adminpanel WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
                await self.bot.db.execute(thequery, ctx.guild.id, 1, 1, 0, 0, 0, 0)
            thequery = "UPDATE adminpanel SET joins=1 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            thequery = "SELECT * FROM idstore WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = (
                    "INSERT INTO idstore VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
                )
                await self.bot.db.execute(
                    thequery, ctx.guild.id, "Default", "Default", 0, 0, 0, 0, 0, 0
                )
            thequery = "UPDATE idstore SET joinchan=$2 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id, joinschannel.id)
            thequery = "UPDATE idstore SET joinmsg=$2 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id, setjoinmsg)
            return await ctx.send(
                f"I have successfully enabled **Join Messages**, with the message: **{setjoinmsg}**"
            )
        thequery = "SELECT joins FROM adminpanel WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(thequery, ctx.guild.id, 1, 1, 0, 0, 0, 0)
        thequery = "UPDATE adminpanel SET joins=1 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        thequery = "SELECT * FROM idstore WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO idstore VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(
                thequery, ctx.guild.id, "Default", "Default", 0, 0, 0, 0, 0, 0
            )
        thequery = "UPDATE idstore SET joinchan=$2 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id, joinschannel.id)
        thequery = "UPDATE idstore SET joinmsg=$2 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id, setjoinmsg)
        embed = discord.Embed(
            title="Join Messages",
            description=f"<:enabled:513831607355047964>\n\nJoin message: {setjoinmsg}",
        )
        await ctx.send(embed=embed)

    @enable.command(name="leaves", hidden=True)
    async def enable_leavemsg(
        self, ctx, leaveschannel: discord.TextChannel, *, setleavemsg: str = None
    ):
        """ Enables Leave messages on the server """
        if setleavemsg is None:
            setleavemsg = "$member$ left the server.."
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT leaves FROM adminpanel WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
                await self.bot.db.execute(thequery, ctx.guild.id, 1, 0, 1, 0, 0, 0)
            thequery = "UPDATE adminpanel SET leaves=1 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            thequery = "SELECT * FROM idstore WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = (
                    "INSERT INTO idstore VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
                )
                await self.bot.db.execute(
                    thequery, ctx.guild.id, "Default", "Default", 0, 0, 0, 0, 0, 0
                )
            thequery = "UPDATE idstore SET leavechan=$2 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id, leaveschannel.id)
            thequery = "UPDATE idstore SET leavemsg=$2 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id, setleavemsg)
            return await ctx.send(
                f"I have successfully enabled **Leave Messages** with the message: **{setleavemsg}**"
            )
        thequery = "SELECT leaves FROM adminpanel WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(thequery, ctx.guild.id, 1, 0, 1, 0, 0, 0)
        thequery = "UPDATE adminpanel SET leaves=1 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        thequery = "SELECT * FROM idstore WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO idstore VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(
                thequery, ctx.guild.id, "Default", "Default", 0, 0, 0, 0, 0, 0
            )
        thequery = "UPDATE idstore SET leavechan=$2 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id, leaveschannel.id)
        thequery = "UPDATE idstore SET leavemsg=$2 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id, setleavemsg)
        embed = discord.Embed(
            title="Leave Messages",
            description=f"<:enabled:513831607355047964>\n\nLeave message: {setleavemsg}",
        )
        await ctx.send(embed=embed)

    @enable.command(name="nsfw", hidden=True)
    async def enable_nsfw(self, ctx):
        """ Enables NSFW on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT nsfw FROM adminpanel WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
                await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 1, 0, 0)
            thequery = "UPDATE adminpanel SET nsfw=1 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully enabled **NSFW**")
        thequery = "SELECT nsfw FROM adminpanel WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 1, 0, 0)
        thequery = "UPDATE adminpanel SET nsfw=1 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(title="NSFW", description="<:enabled:513831607355047964>")
        await ctx.send(embed=embed)

    @enable.command(name="automod", hidden=True)
    async def enable_automod(self, ctx):
        """ Enables Automoderator on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT automod FROM adminpanel WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
                await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 1, 0, 0)
            thequery = "UPDATE adminpanel SET automod=1 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully enabled **Automoderator**")
        thequery = "SELECT automod FROM adminpanel WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 1, 0, 0)
        thequery = "UPDATE adminpanel SET automod=1 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="Automoderator",
            description="<:enabled:513831607355047964>\n\nConfigure with `paw enable`",
        )
        await ctx.send(embed=embed)

    @enable.command(name="modlog", hidden=True)
    async def enable_modlog(self, ctx, modlogchan: discord.TextChannel):
        """ Enables Moderation Logging on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT modlog FROM adminpanel WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
                await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 1, 0, 0)
            thequery = "UPDATE adminpanel SET modlog=1 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully enabled **Moderation Log**")
        thequery = "SELECT modlog FROM adminpanel WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 1, 0, 0)
        thequery = "SELECT * FROM idstore WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO idstore VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(
                thequery,
                ctx.guild.id,
                "Default",
                "Default",
                0,
                0,
                modlogchan.id,
                0,
                0,
                0,
            )
        thequery = "UPDATE idstore SET modlogchan=$2 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id, modlogchan.id)
        thequery = "UPDATE adminpanel SET modlog=1 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="Moderation Log",
            description=f"<:enabled:513831607355047964>\n\nLogging to: {modlogchan.mention}",
        )
        await ctx.send(embed=embed)

    @enable.command(name="autorole", hidden=True)
    async def enable_autorole(self, ctx, autoRoleRole: discord.Role):
        """ Enables Auto Role on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["automod"] == 0 or None:
            return await ctx.send("Automod must be enabled first! ><")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT autorole FROM automod WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = (
                    "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
                )
                await self.bot.db.execute(
                    thequery, ctx.guild.id, 1, 0, 0, 0, 10, 10, 0, 0
                )
            thequery = "SELECT * FROM idstore WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = (
                    "INSERT INTO idstore VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
                )
                await self.bot.db.execute(
                    thequery,
                    ctx.guild.id,
                    "Default",
                    "Default",
                    0,
                    0,
                    0,
                    0,
                    autoRoleRole.id,
                    0,
                )
            thequery = "UPDATE automod SET autorole=1 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            thequery = "UPDATE idstore SET autorolerole=$2 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id, autoRoleRole.id)
            return await ctx.send("I have successfully enabled **Auto Role**")
        thequery = "SELECT autorole FROM automod WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(thequery, ctx.guild.id, 1, 0, 0, 0, 10, 10, 0, 0)
        thequery = "SELECT * FROM idstore WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO idstore VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(
                thequery,
                ctx.guild.id,
                "Default",
                "Default",
                0,
                0,
                0,
                0,
                autoRoleRole.id,
                0,
            )
        thequery = "UPDATE automod SET autorole=1 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        thequery = "UPDATE idstore SET autorolerole=$2 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id, autoRoleRole.id)
        embed = discord.Embed(
            title="Autorole",
            description=f"<:enabled:513831607355047964>\n\nAuto Role-Role: {autoRoleRole.mention}",
        )
        await ctx.send(embed=embed)

    @enable.command(name="adblock", hidden=True)
    async def enable_adblock(self, ctx):
        """ Enables adblock on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["automod"] == 0 or None:
            return await ctx.send("Automod must be enabled first! ><")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT adblock FROM automod WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = (
                    "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
                )
                await self.bot.db.execute(
                    thequery, ctx.guild.id, 0, 1, 0, 0, 10, 10, 0, 0
                )
            thequery = "UPDATE automod SET adblock=1 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully enabled **Adblock**")
        thequery = "SELECT adblock FROM automod WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 1, 0, 0, 10, 10, 0, 0)
        thequery = "UPDATE automod SET adblock=1 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="Adblock", description=f"<:enabled:513831607355047964>"
        )
        await ctx.send(embed=embed)

    @enable.command(name="lockdown", hidden=True)
    async def enable_lockdown(self, ctx):
        """ Enables lockdown on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["automod"] == 0 or None:
            return await ctx.send("Automod must be enabled first! ><")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT lockdown FROM automod WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = (
                    "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
                )
                await self.bot.db.execute(
                    thequery, ctx.guild.id, 0, 0, 1, 0, 10, 10, 0, 0
                )
            thequery = "UPDATE automod SET lockdown=1 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully enabled **Lockdown**")
        thequery = "SELECT lockdown FROM automod WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 1, 0, 10, 10, 0, 0)
        thequery = "UPDATE automod SET lockdown=1 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="Lockdown", description=f"<:enabled:513831607355047964>"
        )
        await ctx.send(embed=embed)

    @enable.command(name="antispam", hidden=True)
    async def enable_antispam(self, ctx):
        """ Enables antispam on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["automod"] == 0 or None:
            return await ctx.send("Automod must be enabled first! ><")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT antispam FROM automod WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = (
                    "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
                )
                await self.bot.db.execute(
                    thequery, ctx.guild.id, 0, 0, 1, 0, 10, 10, 0, 0
                )
            thequery = "UPDATE automod SET antispam=1 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully enabled **Antispam**")
        thequery = "SELECT antispam FROM automod WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 1, 0, 10, 10, 0, 0)
        thequery = "UPDATE automod SET antispam=1 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="Antispam", description=f"<:enabled:513831607355047964>"
        )
        await ctx.send(embed=embed)

    @enable.command(name="ignorerole", hidden=True)
    async def enable_ignorerole(self, ctx, ignoreRole: discord.Role):
        """ Enables perms bypass on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["automod"] == 0 or None:
            return await ctx.send("Automod must be enabled first! ><")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT ignorerole FROM automod WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = (
                    "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
                )
                await self.bot.db.execute(
                    thequery, ctx.guild.id, 1, 0, 0, 0, 10, 10, 0, 0
                )
            thequery = "SELECT * FROM idstore WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = (
                    "INSERT INTO idstore VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
                )
                await self.bot.db.execute(
                    thequery,
                    ctx.guild.id,
                    "Default",
                    "Default",
                    0,
                    0,
                    0,
                    ignoreRole.id,
                    0,
                    0,
                )
            thequery = "UPDATE automod SET ignorerole=1 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            thequery = "UPDATE idstore SET ignorerolerole=$2 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id, ignoreRole.id)
            return await ctx.send("I have successfully enabled **Auto Role**")
        thequery = "SELECT ignorerole FROM automod WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(thequery, ctx.guild.id, 1, 0, 0, 0, 10, 10, 0, 0)
        thequery = "SELECT * FROM idstore WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO idstore VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(
                thequery,
                ctx.guild.id,
                "Default",
                "Default",
                0,
                0,
                0,
                ignoreRole.id,
                0,
                0,
            )
        thequery = "UPDATE automod SET ignorerole=1 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        thequery = "UPDATE idstore SET ignorerolerole=$2 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id, ignoreRole.id)
        embed = discord.Embed(
            title="Perms Bypass Role",
            description=f"<:enabled:513831607355047964>\n\nPerms Bypass Role: {ignoreRole.mention}",
        )
        await ctx.send(embed=embed)

    @enable.command(name="actionlog", hidden=True)
    async def enable_actionlog(self, ctx, actionLogChan: discord.TextChannel):
        """ Enables Action Logging on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["automod"] == 0 or None:
            return await ctx.send("Automod must be enabled first! ><")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT actionlog FROM automod WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = (
                    "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
                )
                await self.bot.db.execute(
                    thequery, ctx.guild.id, 0, 0, 0, 0, 10, 10, 0, 1
                )
            thequery = "UPDATE automod SET actionlog=1 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            thequery = "SELECT * FROM idstore WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = (
                    "INSERT INTO idstore VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
                )
                await self.bot.db.execute(
                    thequery,
                    ctx.guild.id,
                    "Default",
                    "Default",
                    0,
                    0,
                    0,
                    0,
                    0,
                    actionLogChan.id,
                )
            thequery = "UPDATE idstore SET actionlogchan=$2 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id, actionLogChan.id)
            return await ctx.send("I have successfully enabled **Action Logging**")
        thequery = "SELECT actionlog FROM automod WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 10, 10, 0, 1)
        thequery = "UPDATE automod SET actionlog=1 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        thequery = "SELECT * FROM idstore WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO idstore VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(
                thequery,
                ctx.guild.id,
                "Default",
                "Default",
                0,
                0,
                0,
                0,
                0,
                actionLogChan.id,
            )
        thequery = "UPDATE idstore SET actionlogchan=$2 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id, actionLogChan.id)
        embed = discord.Embed(
            title="Action Logging",
            description=f"<:enabled:513831607355047964>\n\nAction Log: {actionLogChan.mention}",
        )
        await ctx.send(embed=embed)

    @commands.group()
    @commands.guild_only()
    @permissions.has_permissions(manage_guild=True)
    async def disable(self, ctx):
        """ Disables different modules """
        if ctx.invoked_subcommand is None:
            _help = await ctx.bot.formatter.format_help_for(ctx, ctx.command)

            for page in _help:
                await ctx.send(page)

    @disable.command(name="embeds", hidden=True)
    async def disable_embeds(self, ctx):
        """ Disables embeds on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT embeds FROM adminpanel WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
                await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 0, 0)
            thequery = "UPDATE adminpanel SET embeds=0 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully disabled **embeds**")
        thequery = "SELECT embeds FROM adminpanel WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 0, 0)
        thequery = "UPDATE adminpanel SET embeds=0 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="Embeds", description="<:disabled:513831606855794709>"
        )
        await ctx.send(embed=embed)

    @disable.command(name="joins", hidden=True)
    async def disable_joins(self, ctx):
        """ Disables join messages on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT joins FROM adminpanel WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
                await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 0, 0)
            thequery = "UPDATE adminpanel SET joins=0 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully disabled **Join Messages**")
        thequery = "SELECT joins FROM adminpanel WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 0, 0)
        thequery = "UPDATE adminpanel SET joins=0 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="Join Messages", description="<:disabled:513831606855794709>"
        )
        await ctx.send(embed=embed)

    @disable.command(name="leaves", hidden=True)
    async def disable_leaves(self, ctx):
        """ Disables leave messages on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT leaves FROM adminpanel WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
                await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 0, 0)
            thequery = "UPDATE adminpanel SET leaves=0 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully disabled **Leave Messages**")
        thequery = "SELECT leaves FROM adminpanel WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 0, 0)
        thequery = "UPDATE adminpanel SET leaves=0 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="Leave Messages", description="<:disabled:513831606855794709>"
        )
        await ctx.send(embed=embed)

    @disable.command(name="nsfw", hidden=True)
    async def disable_nsfw(self, ctx):
        """ Disables NSFW on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT nsfw FROM adminpanel WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
                await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 0, 0)
            thequery = "UPDATE adminpanel SET nsfw=0 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully disabled **NSFW**")
        thequery = "SELECT nsfw FROM adminpanel WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 0, 0)
        thequery = "UPDATE adminpanel SET nsfw=0 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="NSFW", description="<:disabled:513831606855794709>"
        )
        await ctx.send(embed=embed)

    @disable.command(name="automod", hidden=True)
    async def disable_automod(self, ctx):
        """ Disables automoderator on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT automod FROM adminpanel WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
                await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 0, 0)
            thequery = "UPDATE adminpanel SET automod=0 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully disabled **Automoderator**")
        thequery = "SELECT automod FROM adminpanel WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 0, 0)
        thequery = "UPDATE adminpanel SET automod=0 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="Automoderator", description="<:disabled:513831606855794709>"
        )
        await ctx.send(embed=embed)

    @disable.command(name="modlog", hidden=True)
    async def disable_modlog(self, ctx):
        """ Disables Moderation Logging on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT modlog FROM adminpanel WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
                await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 0, 0)
            thequery = "UPDATE adminpanel SET modlog=0 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully disabled **Moderation Logging**")
        thequery = "SELECT modlog FROM adminpanel WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = "INSERT INTO adminpanel VALUES ($1, $2, $3, $4, $5, $6, $7);"
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 0, 0)
        thequery = "UPDATE adminpanel SET modlog=0 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="Moderation Logging", description="<:disabled:513831606855794709>"
        )
        await ctx.send(embed=embed)

    @disable.command(name="autorole", hidden=True)
    async def disable_autorole(self, ctx):
        """ Disables autorole on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["automod"] == 0 or None:
            return await ctx.send("Automod must be enabled first! ><")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT autorole FROM automod WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = (
                    "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
                )
                await self.bot.db.execute(
                    thequery, ctx.guild.id, 0, 0, 0, 0, 10, 10, 0, 0
                )
            thequery = "UPDATE automod SET autorole=0 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully disabled **Autorole**")
        thequery = "SELECT autorole FROM automod WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 10, 10, 0, 0)
        thequery = "UPDATE automod SET autorole=0 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="Autorole", description=f"<:disabled:513831606855794709>"
        )
        await ctx.send(embed=embed)

    @disable.command(name="adblock", hidden=True)
    async def disable_adblock(self, ctx):
        """ Disables adblock on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["automod"] == 0 or None:
            return await ctx.send("Automod must be enabled first! ><")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT adblock FROM automod WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = (
                    "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
                )
                await self.bot.db.execute(
                    thequery, ctx.guild.id, 0, 0, 0, 0, 10, 10, 0, 0
                )
            thequery = "UPDATE automod SET adblock=0 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully disabled **Adblock**")
        thequery = "SELECT adblock FROM automod WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 10, 10, 0, 0)
        thequery = "UPDATE automod SET adblock=0 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="Adblock", description=f"<:disabled:513831606855794709>"
        )
        await ctx.send(embed=embed)

    @disable.command(name="lockdown", hidden=True)
    async def disable_lockdown(self, ctx):
        """ Disables Lockdown on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["automod"] == 0 or None:
            return await ctx.send("Automod must be enabled first! ><")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT lockdown FROM automod WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = (
                    "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
                )
                await self.bot.db.execute(
                    thequery, ctx.guild.id, 0, 0, 0, 0, 10, 10, 0, 0
                )
            thequery = "UPDATE automod SET lockdown=0 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully disabled **Lockdown**")
        thequery = "SELECT lockdown FROM automod WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 10, 10, 0, 0)
        thequery = "UPDATE automod SET lockdown=0 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="Lockdown", description=f"<:disabled:513831606855794709>"
        )
        await ctx.send(embed=embed)

    @disable.command(name="antispam", hidden=True)
    async def disable_antispam(self, ctx):
        """ Disables antispam on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["automod"] == 0 or None:
            return await ctx.send("Automod must be enabled first! ><")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT antispam FROM automod WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = (
                    "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
                )
                await self.bot.db.execute(
                    thequery, ctx.guild.id, 0, 0, 0, 0, 10, 10, 0, 0
                )
            thequery = "UPDATE automod SET antispam=0 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully disabled **Antispam**")
        thequery = "SELECT antispam FROM automod WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 10, 10, 0, 0)
        thequery = "UPDATE automod SET antispam=0 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="Antispam", description=f"<:disabled:513831606855794709>"
        )
        await ctx.send(embed=embed)

    @disable.command(name="ignorerole", hidden=True)
    async def disable_ignorerole(self, ctx):
        """ Disables an Ignore Role on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["automod"] == 0 or None:
            return await ctx.send("Automod must be enabled first! ><")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT ignorerole FROM automod WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = (
                    "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
                )
                await self.bot.db.execute(
                    thequery, ctx.guild.id, 0, 0, 0, 0, 10, 10, 0, 0
                )
            thequery = "UPDATE automod SET ignorerole=0 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully disabled **Ignore Roles**")
        thequery = "SELECT ignorerole FROM automod WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 10, 10, 0, 0)
        thequery = "UPDATE automod SET ignorerole=0 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="Ignore Role", description=f"<:disabled:513831606855794709>"
        )
        await ctx.send(embed=embed)

    @disable.command(name="actionlog", hidden=True)
    async def disable_actionlog(self, ctx):
        """ Disables actionlog on the server """
        rowcheck = await self.getserverstuff(ctx)
        if rowcheck["automod"] == 0 or None:
            return await ctx.send("Automod must be enabled first! ><")
        if rowcheck["embeds"] == 0 or not permissions.can_embed(ctx):
            thequery = "SELECT actionlog FROM automod WHERE serverid = $1;"
            therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
            if therow is None:
                thequery = (
                    "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
                )
                await self.bot.db.execute(
                    thequery, ctx.guild.id, 0, 0, 0, 0, 10, 10, 0, 0
                )
            thequery = "UPDATE automod SET actionlog=0 WHERE serverid=$1;"
            await self.bot.db.execute(thequery, ctx.guild.id)
            return await ctx.send("I have successfully disabled **Actionlog**")
        thequery = "SELECT actionlog FROM automod WHERE serverid = $1;"
        therow = await self.bot.db.fetchrow(thequery, ctx.guild.id)
        if therow is None:
            thequery = (
                "INSERT INTO automod VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9);"
            )
            await self.bot.db.execute(thequery, ctx.guild.id, 0, 0, 0, 0, 10, 10, 0, 0)
        thequery = "UPDATE automod SET actionlog=0 WHERE serverid=$1;"
        await self.bot.db.execute(thequery, ctx.guild.id)
        embed = discord.Embed(
            title="Actionlog", description=f"<:disabled:513831606855794709>"
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(AdminPanel(bot))
