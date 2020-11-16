import sys
from typing import Set

import discord
import html5lib
import requests
from bs4 import BeautifulSoup
from discord import Message, User, TextChannel, Guild, Colour
from discord.ext.commands import Context, Command

from src import utils

bot = utils.bot


@bot.command(name='info', aliases=['information', 'question'])
async def info_cmd(ctx: Context, *args: str):
    channel, guild, user, msg = utils.unpack(ctx)  # type: TextChannel, Guild, User, Message

    embed = discord.Embed(title='Information', description='''
    Just a bot that is made for fun!
    Actually... to learn python :P
    
    [You can go to my GitHub profile here](https://github.com/Alviannn)
    ''', color=Colour.blue())

    try:
        embed.set_thumbnail(url=bot.user.avatar_url)
        embed.set_footer(text='Made by Alvian#1341')
        embed.add_field(name='Python', value=sys.version.split(' ')[0])
        embed.add_field(name='discord.py', value=discord.__version__)

        # first time learning elapsed and string formatting
        elapsed = utils.current_millis() - utils.start_time
        elapsed_format = utils.from_elapsed_millis(elapsed)

        embed.add_field(name='Online Time', value=elapsed_format, inline=False)
        embed.add_field(name='Source Code', value='This bot is open-source, you can view it '
                                                  '[here](https://github.com/Alviannn/KiritodBot/)',
                        inline=False)

        headers = {'user-agent': 'Mozilla/5.0'}
        with requests.get('https://github.com/Alviannn/KiritodBot', headers=headers) as res:
            version = html5lib.__version__
            soup = BeautifulSoup(res.text, 'html5lib')

        if soup:
            grabbed_list = soup.find_all('span', attrs={'class': 'd-none d-sm-inline'})

            repo_info = grabbed_list[1] if len(grabbed_list) == 2 else grabbed_list[0]
            total_commits = int(repo_info.strong.text)

            embed.add_field(name='Total Commits', value=f'**{total_commits}** commits')

        await channel.send(embed=embed)
    except Exception as error:
        print(error)


@bot.command(name='help', aliases=['howto'])
async def help_cmd(ctx: Context, *args: str):
    channel, guild, user, msg = utils.unpack(ctx)  # type: TextChannel, Guild, User, Message
    commands_list: Set[Command] = bot.commands

    if not args:
        embed = discord.Embed(title='Command List', color=0x79FF00)
        embed.set_thumbnail(url=bot.user.avatar_url)

        name_list = []
        for cmd in commands_list:
            name_list.append(cmd.name)

        embed.description = f'**Unknown commands**\n`{", ".join(name_list)}`'
        await channel.send(embed=embed)
    else:
        cmd: Command = bot.get_command(args[0])

        if not cmd:
            await channel.send(f'Cannot find any command called {args[0]}!')
            return

        embed = discord.Embed(title='Command Info', color=0x79FF00)
        embed.set_thumbnail(url=bot.user.avatar_url)
        embed.description = f'''
            Information for command named {args[0].lower()}

            **Name**: {cmd.name}
            **Aliases**: [{', '.join(cmd.aliases)}]
            **Description**: {'-' if not cmd.description else cmd.description}
        '''

        await channel.send(embed=embed)
