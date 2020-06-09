import os
import asyncio
import asyncpg

from data import Bot
from utils import default

config = default.get("config.json")
description = """
A discord bot written in python, made for managing communities.
"""


async def run():
    # Create a Dictionary under the name help attrs
    help_attrs = dict(hidden=True)
    # Log into the database
    credentials = {
        "user": config.dbname,
        "password": config.dbpass,
        "database": config.database,
        "host": "127.0.0.1",
    }
    db = await asyncpg.create_pool(**credentials)

    # Add tables if they don't exist
    await db.execute(
        "CREATE TABLE IF NOT EXISTS warnings(serverid bigint, userid bigint, warnings int);"
    )
    await db.execute(
        "CREATE TABLE IF NOT EXISTS modlogs(serverid bigint, caseid bigint, casenumber int, casetype varchar, target bigint, moderator bigint, reason varchar);"
    )
    await db.execute(
        "CREATE TABLE IF NOT EXISTS adminpanel(serverid bigint, joins int, leaves int, embeds int, nsfw int, automod int, modlog int);"
    )
    await db.execute(
        "CREATE TABLE IF NOT EXISTS automod(serverid bigint, autorole int, adblock int, lockdown int, antispam int, owo int, uwu int, ignorerole int, actionlog int);"
    )
    await db.execute(
        "CREATE TABLE IF NOT EXISTS idstore(serverid bigint, joinmsg varchar, leavemsg varchar, joinchan bigint, leavechan bigint, modlogchan bigint, ignorerolerole bigint, autorolerole bigint, actionlogchan bigint);"
    )
    await db.execute(
        "CREATE TABLE IF NOT EXISTS tags(serverid bigint, tagname varchar, tagtext varchar);"
    )
    await db.execute("CREATE TABLE IF NOT EXISTS userbal(userid bigint, money bigint);")

    # Make the client
    bot = Bot(command_prefix=config.prefix, pm_help=True, help_attrs=help_attrs, db=db)
    # Remove help command
    bot.remove_command("help")
    # Get the cogs, send a startup message
    try:
        print("Logging in...")
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                bot.load_extension(f"cogs.{name}")
        await bot.start(config.token)
    except KeyboardInterrupt:
        await db.close()
        await bot.logout()


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
