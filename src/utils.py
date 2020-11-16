import importlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import List

from discord import Message, TextChannel, Guild, User, Embed
from discord.ext.commands import Bot, Context

from src.objects import server

exec_path: Path
bot: Bot
server_manager: server.Manager

start_time: int


def current_dir():
    """
    gets the current running directory

    :rtype: Path
    """
    return Path(os.getcwd())


def current_millis():
    """
    gets the current millis

    :rtype: int
    """
    return int(round(time.time() * 1000))


def read_json(path: Path):
    """
    reads a json from a path

    :rtype: object
    """

    with open(path) as file:
        content = json.loads(file.read())

    return content


def isnum(value: str):
    """
    determines if the value is a number

    :param value: the string value
    :return: `True` if the value is a number, `False` is otherwise
    """
    try:
        float(value)
        return True
    except:
        return False


def from_elapsed_millis(millis: int):
    """parses an elapsed millis into a human readable format"""
    seconds = millis / 1000
    return '{:0d}h {:0d}m {:0d}s'.format(
        int(seconds / 3600),
        int((seconds % 3600) / 60),
        int((seconds % 3600 % 60))
    )


def is_match_usermention(value: str, full: bool = False):
    """
    determines if the value matches a user id

    :param value: the possible user mention
    :param full: should it be a full match?
    """

    regex = re.compile('<@!?[0-9]{18}>')
    if not full:
        return regex.match(value)

    return regex.fullmatch(value)


def parse_user_mention(value: str):
    """parses the user mention string into a full user id"""

    if not is_match_usermention(value):
        return None

    return int(value.replace('<@!', '').replace('>', ''))


def unpack(value):
    """unpacks a specific value"""
    if isinstance(value, Message):
        channel: TextChannel = value.channel
        guild: Guild = value.guild
        user: User = value.author

        return channel, guild, user
    elif isinstance(value, Context):
        channel: TextChannel = value.channel
        guild: Guild = value.guild
        user: User = value.author
        message: Message = value.message

        return channel, guild, user, message
    else:
        raise NotImplemented()


def shutdown(closeall: bool = True, restart: bool = False):
    """
    shuts down the program

    :param closeall: should everything be closed?
    :param restart: should the program be restarted?
    """
    if closeall:
        try:
            bot.loop.create_task(bot.close)
        except:
            pass

    if restart:
        print('Rebooting...')
        os.system('cls') if os.name == 'nt' else os.system('clear')
        os.execl(sys.executable, str(exec_path), *sys.argv)
    else:
        print('Exiting...')
        exit(0)


def load_python_files(dir_path: Path, filter_func=None):
    """
    loads python files within a directory

    :param dir_path: the directory path
    :param filter_func: the filter function this accepts a file name (string) as the parameter
        and returns a `bool`

    :raise FileNotFoundError: if the directory path doesn't exists
    :raise IOError: if the python file failed to load

    Example
    --------
    ::

        dir_path = Path(os.getcwd(), 'listeners')
        # filters the listed file names
        def filter_func(file_name: str):
            return not file_name.startsWith('__')

        utils.load_python_files(dir_path, filter_func)

    :return: the list of file names that got loaded
    """

    if not dir_path.exists():
        raise FileNotFoundError(f'Cannot find {dir_path} path!')

    file_list: List[Path] = []

    for file_name in os.listdir(dir_path):
        # filters all files
        if file_name.startswith('__'):
            continue
        if filter_func and not filter_func(file_name):
            continue

        file_list.append(Path(dir_path, file_name))

    for file in file_list:
        module_name = str(file).replace(os.sep, ".")[:-3]
        importlib.import_module(module_name)
        print(f"Loaded {file.name}!")


async def super_eval(raw: str, msg: Message):
    """
    Evaluates a code but not in the python way

    This works by getting a raw input of a code from a discord message
    and then parses that input into a python readable code,
    then it'll execute the code and then returns the result of that code!

    So, what's the difference? Unlike python `eval` and `exec`, this is more similar to the NodeJS `eval`
    which means the code evaluation runs with full permissions and could be an issue so PLEASE BE CAREFUL!
    The normal python `eval` has a lot of limitations which is good for security reasons
    but for this case, it doesn't have that limitations

    :param raw: the raw input code
    :param msg: the message instance
    """

    channel, guild, user = unpack(msg)  # type: TextChannel, Guild, User
    regex = re.compile(r'```py(thon)?.*')

    # the inputted code must have a specific beginning and ending
    if not regex.match(raw) or not raw.endswith("```"):
        await channel.send("That ain't python!")
        return

    # parses the inputted code
    code_input = regex.sub(repl="", string=raw).replace("\n```", "").replace("```", "")[1:]
    # compiles the inputted code
    compiled = compile(source=code_input, filename="none", mode="exec")

    await msg.delete(delay=1)
    error = None
    found_error = False

    embed = Embed()
    embed.colour = 0xFFBF00
    embed.set_author(name='Python Code Evaluation')
    embed.set_footer(text=f'Executed by {user}', icon_url=user.avatar_url)

    try:
        exec(compiled)

        # catches the last variable or expression that is found
        code_lines = code_input.split("\n")
        last_variable = code_lines[len(code_lines) - 1]

        # evaluates the variable which will always returns something no matter what.
        # because the variables that was executed stayed we can grab it and then gets the value
        response = eval(last_variable)

        if os.environ['BOT_TOKEN'] in str(response):
            await channel.send('Big no!')
            return

        embed.description = f'''
                Code Input: {raw}
                Output: ```py\n{response}```
                '''

        await channel.send(embed=embed)
    except:
        error = sys.exc_info()
        found_error = True

    if found_error:
        embed.colour = 0xFF0000
        embed.description = f'''
                Code Input: {raw}
                Error: ```py\n{error}```
                '''

        await channel.send(embed=embed)
