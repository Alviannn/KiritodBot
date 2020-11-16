import re

import discord
from discord import TextChannel, Guild, User

from src import utils

bot = utils.bot


@bot.listen()
async def on_message(msg: discord.Message):
    channel, guild, user = utils.unpack(msg)  # type: TextChannel, Guild, User
    content = str(msg.content)

    if content.startswith('```py') or content.startswith('```python') and content.endswith('```'):
        await utils.super_eval(content, msg)
        return

    try:
        match = re.compile(r'^<@!?[0-9]{18}>$')
        if user.bot or not match.match(content) or msg.mentions[0] != bot.user:
            return

        prefix = await bot.get_prefix(message=msg)
        await channel.send(f"Hello {user.mention}! My command prefix is `{prefix}`!")
    except Exception as error:
        print(error)
