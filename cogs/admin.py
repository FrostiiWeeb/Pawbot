import time
import aiohttp
import traceback
import discord
import textwrap
import io
import json

from dhooks import Webhook
from utils.chat_formatting import pagify
from contextlib import redirect_stdout
from copy import copy
from typing import Union
from utils import repo, default, http, dataIO
from discord.ext import commands


class Admin:
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self._last_result = None
        self.sessions = set()

    @staticmethod
    def cleanup_code(content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @staticmethod
    def get_syntax_error(e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    @commands.command()
    async def amiadmin(self, ctx):
        """ Are you admin? """
        if ctx.author.id in self.config.owners:
            await ctx.send(f"Yes **{ctx.author.name}** you are admin! ✅")
        elif ctx.author.id in self.config.contributors:
            await ctx.send(f"No, but you're a contributor **{ctx.author.name}** 💙")
        elif ctx.author.id in self.config.friends:
            await ctx.send(f"No, but you're a friend of Paws **{ctx.author.name}** 💜")
        else:
            await ctx.send(f"No, heck off **{ctx.author.name}**.")

    @commands.command()
    @commands.check(repo.is_owner)
    async def reload(self, ctx, name: str):
        """ Reloads an extension. """
        try:
            self.bot.unload_extension(f"cogs.{name}")
            self.bot.load_extension(f"cogs.{name}")
        except FileNotFoundError as e:
            return await ctx.send(f"```\n{e}```")
        await ctx.send(f"Reloaded extension **{name}.py**")

    @commands.command()
    @commands.check(repo.is_owner)
    async def reboot(self, ctx):
        """ Reboot the bot """
        await ctx.send('Rebooting now...')
        time.sleep(1)
        await self.bot.logout()

    @commands.command()
    @commands.check(repo.is_owner)
    async def load(self, ctx, name: str):
        """ Reloads an extension. """
        try:
            self.bot.load_extension(f"cogs.{name}")
        except FileNotFoundError as e:
            await ctx.send(f"```diff\n- {e}```")
            return
        await ctx.send(f"Loaded extension **{name}.py**")

    @commands.command()
    @commands.check(repo.is_owner)
    async def unload(self, ctx, name: str):
        """ Reloads an extension. """
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except FileNotFoundError as e:
            await ctx.send(f"```diff\n- {e}```")
            return
        await ctx.send(f"Unloaded extension **{name}.py**")

    @commands.group()
    @commands.check(repo.is_owner)
    async def change(self, ctx):
        if ctx.invoked_subcommand is None:
            _help = await ctx.bot.formatter.format_help_for(ctx, ctx.command)

            for page in _help:
                await ctx.send(page)

    @change.command(name="playing")
    @commands.check(repo.is_owner)
    async def change_playing(self, ctx, *, playing: str):
        """ Change playing status. """
        try:
            await self.bot.change_presence(
                activity=discord.Game(type=0, name=playing),
                status=discord.Status.online
            )
            dataIO.change_value("config.json", "playing", playing)
            await ctx.send(f"Successfully changed playing status to **{playing}**")
        except discord.InvalidArgument as err:
            await ctx.send(err)
        except Exception as e:
            await ctx.send(e)

    @change.command(name="username")
    @commands.check(repo.is_owner)
    async def change_username(self, ctx, *, name: str):
        """ Change username. """
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"Successfully changed username to **{name}**")
        except discord.HTTPException as err:
            await ctx.send(err)

    @change.command(name="nickname")
    @commands.check(repo.is_owner)
    async def change_nickname(self, ctx, *, name: str = None):
        """ Change nickname. """
        try:
            await ctx.guild.me.edit(nick=name)
            if name:
                await ctx.send(f"Successfully changed nickname to **{name}**")
            else:
                await ctx.send("Successfully removed nickname")
        except Exception as err:
            await ctx.send(err)

    @change.command(name="avatar")
    @commands.check(repo.is_owner)
    async def change_avatar(self, ctx, url: str = None):
        """ Change avatar. """
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip('<>')

        try:
            bio = await http.get(url, res_method="read")
            await self.bot.user.edit(avatar=bio)
            await ctx.send(f"Successfully changed the avatar. Currently using:\n{url}")
        except aiohttp.InvalidURL:
            await ctx.send("The URL is invalid...")
        except discord.InvalidArgument:
            await ctx.send("This URL does not contain a usable image")
        except discord.HTTPException as err:
            await ctx.send(err)

    @commands.command()
    @commands.check(repo.is_owner)
    async def steal(self, ctx, emojiname, url: str = None):
        """Steals emojis"""
        if emojiname is None or "http" in emojiname:
            return await ctx.send("No emoji name provided")
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip('<>')

        try:
            botguild = self.bot.get_guild(423879867457863680)
            bio = await http.get(url, res_method="read")
            await botguild.create_custom_emoji(name=emojiname, image=bio)
            await ctx.message.delete()
            await ctx.send(f"Successfully stolen emoji.")
        except aiohttp.InvalidURL:
            await ctx.send("The URL is invalid...")
        except discord.InvalidArgument:
            await ctx.send("This URL does not contain a usable image")
        except discord.HTTPException as err:
            await ctx.send(err)

    @commands.command(pass_context=True, name='eval')
    @commands.check(repo.is_owner)
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        if "bot.http.token" in body:
            return await ctx.send(f"You can't take my token {ctx.author.name}")
        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            reactiontosend = self.bot.get_emoji(508388437661843483)
            await ctx.message.add_reaction(reactiontosend)

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                if self.config.token in ret:
                    ret = self.config.realtoken
                self._last_result = ret
                await ctx.send(f'Inputted code:\n```py\n{body}\n```\n\nOutputted Code:\n```py\n{value}{ret}\n```')

    @commands.group(aliases=["as"])
    @commands.check(repo.is_owner)
    async def sudo(self, ctx):
        """Run a cmd under an altered context
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("...")

    @sudo.command(aliases=["u", "--u", "--user", "user"])
    @commands.check(repo.is_owner)
    async def sudo_user(self, ctx, who: Union[discord.Member, discord.User], *, command: str):
        """Run a cmd under someone else's name
        """
        msg = copy(ctx.message)
        msg.author = who
        msg.content = ctx.prefix + command
        new_ctx = await self.bot.get_context(msg)
        await self.bot.invoke(new_ctx)

    @sudo.command(aliases=["c", "--c", "--channel", "channel"])
    @commands.check(repo.is_owner)
    async def sudo_channel(self, ctx, chid: int, *, command: str):
        """Run a command as another user."""
        cmd = copy(ctx.message)
        cmd.channel = self.bot.get_channel(chid)
        cmd.content = ctx.prefix + command
        new_ctx = await self.bot.get_context(cmd)
        await self.bot.invoke(new_ctx)

    @commands.command()
    @commands.check(repo.is_owner)
    async def cogs(self, ctx):
        mod = ", ".join(list(self.bot.cogs))
        await ctx.send(f"The current modules are:\n```\n{mod}\n```")

    @commands.command(aliases=['gsi'])
    @commands.check(repo.is_owner)
    async def getserverinfo(self, ctx, *, guild_id: int):
        """ Makes me get the information from a guild id"""
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return await ctx.send("Hmph.. I got nothing..")
        members = set(guild.members)
        bots = filter(lambda m: m.bot, members)
        bots = set(bots)
        members = len(members) - len(bots)
        if guild == ctx.guild:
            roles = " ".join([x.mention for x in guild.roles != "@everyone"])
        else:
            roles = ", ".join([x.name for x in guild.roles if x.name != "@everyone"])

        info = discord.Embed(title="Guild info", description=f"» Name: {guild.name}\n» Members/Bots: `{members}:{len(bots)}`"f"\n» Owner: {guild.owner}\n» Created at: {guild.created_at}"f"\n» Roles: {roles}", color=discord.Color.blue())
        info.set_thumbnail(url=guild.icon_url)
        await ctx.send(embed=info)

    @commands.command(alisases=['bsl'])
    @commands.check(repo.is_owner)
    async def botservers(self, ctx):
        """Lists servers"""
        owner = ctx.author
        guilds = sorted(list(self.bot.guilds),
                        key=lambda s: s.name.lower())
        msg = ""
        for i, guild in enumerate(guilds, 1):
            members = set(guild.members)
            bots = filter(lambda m: m.bot, members)
            bots = set(bots)
            members = len(members) - len(bots)
            msg += "`{}:` {}, `{}` `{} members, {} bots` \n".format(i, guild.name, guild.id, members, len(bots))

        for page in pagify(msg, ['\n']):
            await ctx.send(page)

    @commands.command(aliases=["webhooktest"])
    @commands.check(repo.is_owner)
    async def whtest(self, ctx, whlink: str, *, texttosend):
        try:
            await ctx.message.delete()
            hook = Webhook(whlink, is_async=True)
            await hook.send(texttosend)
            await hook.close()
        except ValueError:
            return await ctx.send("I couldn't send the message..")

    @commands.command()
    @commands.check(repo.is_owner)
    async def blacklist(self, ctx, uid: int):
        with open("blacklist.json", "r+") as file:
            content = json.load(file)
            content["blacklist"].append(uid)
            file.seek(0)
            json.dump(content, file)
            file.truncate()
        await ctx.send(f"I have successfully blacklisted the id **{uid}**")


def setup(bot):
    bot.add_cog(Admin(bot))
