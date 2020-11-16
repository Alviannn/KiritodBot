import json
import os
from pathlib import Path

import discord
from discord import Guild, TextChannel, Status

from src import utils

bot = utils.bot


@bot.listen()
async def on_ready():
    print('The bot has started completely!')

    activity = discord.CustomActivity("I'm getting experimented everyday :<")
    await bot.change_presence(activity=activity, status=Status.online)

    reboot_file = Path(utils.current_dir(), 'reboot.json')
    if not reboot_file.exists():
        return

    with open(reboot_file) as file:
        data = json.loads(file.read())

    os.remove(reboot_file)

    last_guild: Guild = bot.get_guild(data['guild'])
    if not last_guild:
        return

    last_channel: TextChannel = last_guild.get_channel(data['channel'])
    if not last_channel:
        return

    await last_channel.send('The bot is now back and running!')
