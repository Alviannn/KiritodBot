import random

from discord import Message, User, TextChannel, Guild, Embed
from discord.ext.commands import Context

from src import utils

bot = utils.bot


@bot.command(name='varied', aliases=['sarcasm'])
async def varied_cmd(ctx: Context, *args: str):
    channel, guild, user, msg = utils.unpack(ctx)  # type: TextChannel, Guild, User, Message
    target_msg = ' '.join(args)

    if not args:
        await channel.send('Try filling up a random word!')
        return

    def rand():
        return random.randint(0, 1) == 1

    builder = []
    for char in target_msg:
        if rand():
            builder.append(char.upper())
            continue

        builder.append(char)

    await channel.send(f"Oi {user.mention}! Here's your varied words: `{''.join(builder)}`")


@bot.command(name='icon', aliases=['pfp', 'pp'])
async def icon_cmd(ctx: Message, *args: str):
    channel, guild, user, msg = utils.unpack(ctx)  # type: TextChannel, Guild, User, Message

    if not args:
        url = str(user.avatar_url)

        embed = Embed(color=user.color)
        embed.set_image(url=url)
        embed.set_author(name=f"{user}'s icon")
        embed.set_footer(text=f'Executed by {user}')

        await channel.send(embed=embed)
        return

    mentioned = args[0]
    if not utils.is_match_usermention(mentioned):
        await channel.send("That's not a user mention!")
        return

    target = guild.get_member(utils.parse_user_mention(mentioned))
    if not target:
        await channel.send(f'Cannot find user with the ID of `{utils.parse_user_mention(mentioned)}`!')
        return

    embed = Embed(color=target.color)
    embed.set_image(url=str(target.avatar_url))
    embed.set_author(name=f"{target}'s icon")
    embed.set_footer(text=f'Executed by {user}')

    await channel.send(embed=embed)
