import json

import discord
from discord import Message, Guild, TextChannel, Member, User
from discord.ext.commands import Context

from src import utils

bot = utils.bot


@bot.command(name='clear')
async def clear_cmd(ctx: Context, *args: str):
    """Clears the messages within the channel that was sent to"""
    channel, guild, user, msg = utils.unpack(ctx)  # type: TextChannel, Guild, User, Message
    member: Member = guild.get_member(user.id)

    if not member.guild_permissions.administrator:
        await channel.send('No permission!')
        return

    if not args:
        await channel.send(f'Usage: {bot.command_prefix}clear <amount>')
        return

    if not utils.isnum(args[0]):
        await channel.send("wtf? that ain't a number you stupid head!")
        return

    amount = int(args[0])
    if amount < 1:
        await channel.send('What are you trying to delete with those numbers?')
        return
    if amount > 100:
        await channel.send('The discord limit to delete multiple messages is 100!')
        return

    deleted_messages = await channel.purge(limit=amount)

    response = await channel.send(f'{len(deleted_messages)} messages are purged!')
    await response.delete(delay=5)


@bot.command(name='permission', aliases=['perm'])
async def show_perm(ctx: Context, *args: str):
    """shows the permission of a discord user"""

    channel, guild, user, msg = utils.unpack(ctx)  # type: TextChannel, Guild, User, Message
    member: Member = guild.get_member(user.id)

    if not member.guild_permissions.administrator:
        await channel.send('No permission!')
        return

    target_member: Member
    if not args:
        target_member = member
    else:
        if len(msg.mentions) == 0:
            await channel.send('Mention someone to view their permissions!')
            return

        mentioned_user: User = msg.mentions[0]
        target_member = guild.get_member(mentioned_user.id)

    if not target_member:
        await channel.send('Who are you trying to call?')
        return

    embed = discord.Embed(title=f'{target_member} permisions', color=0xFF0000)
    count = 0

    indexes = []
    perms = []
    statuses = []

    for perm, status in target_member.guild_permissions:
        count += 1

        indexes.append(str(count))
        perms.append(f'**{perm}**')
        statuses.append(str(status).lower())

    embed.add_field(name='Indexes', value='\n'.join(indexes), inline=True)
    embed.add_field(name='Permissions', value='\n'.join(perms), inline=True)
    embed.add_field(name='Statuses', value='\n'.join(statuses), inline=True)

    await channel.send(embed=embed)


@bot.command(name='prefix')
async def prefix_cmd(ctx: Context, *args: str):
    """handles the prefix command, get or set here"""

    channel, guild, user, msg = utils.unpack(ctx)  # type: TextChannel, Guild, User, Message
    member: Member = guild.get_member(user.id)
    current_prefix = await bot.get_prefix(msg)

    if not len(args):
        await channel.send(f'The command prefix is `{current_prefix}`')
        return

    if not member.guild_permissions.administrator:
        await channel.send('No permission!')
        return

    new_prefix = args[0]

    server = utils.server_manager.find_server(guild)
    server.set_prefix(new_prefix)
    utils.server_manager.save_servers()

    await channel.send(f'The bot command prefix for this server has changed to `{new_prefix}`!')


@bot.command(name='eval', aliases=['exec'])
async def eval_cmd(ctx: Context, *args: str):
    """Evaluates a given python code"""

    channel, guild, user, msg = utils.unpack(ctx)  # type: TextChannel, Guild, User, Message
    member: Member = guild.get_member(user.id)

    if not member.guild_permissions.administrator:
        await channel.send('No permission!')
        return

    if not len(args):
        await channel.send('Cannot evaluate an empty string!')
        return

    raw_input = ' '.join(args)
    await utils.super_eval(raw=raw_input, msg=ctx.message)


@bot.command(name='reboot')
async def reboot_cmd(ctx: Context, *args: str):
    """Reboots the discord bot"""

    channel, guild, user, msg = utils.unpack(ctx)  # type: TextChannel, Guild, User, Message
    member: Member = guild.get_member(user.id)

    if not member.guild_permissions.administrator:
        await channel.send('No permission!')
        return

    await channel.send('Rebooting the bot....')

    with open('reboot.json', 'w') as file:
        data = {
            'guild': guild.id,
            'channel': channel.id
        }

        file.write(json.dumps(data))
        file.flush()

    utils.shutdown(closeall=False, restart=True)
