import os
from pathlib import Path

import dotenv
from discord import Message, Guild
from discord.ext.commands import Bot

from src import utils
from src.objects.server import Manager

dotenv.load_dotenv('.env')
config = utils.read_json(Path('resources', 'config.json'))

__bot = Bot(command_prefix=config['default-prefix'], help_command=None, description=None)
utils.server_manager = Manager(
    __bot,
    Path(os.getcwd(), 'resources', 'servers.json'),
    config['default-prefix']
)


def get_prefix(_bot: Bot, msg: Message):
    """Handles getting the command prefix when executing a command"""

    guild: Guild = msg.guild
    manager = utils.server_manager

    try:
        server = manager.find_server(guild)
        return server.get_prefix()
    except:
        return config['default-prefix']


__bot.command_prefix = get_prefix

if __name__ == '__main__':
    utils.bot = __bot
    utils.exec_path = Path(utils.current_dir(), 'main.py')
    utils.start_time = utils.current_millis()

    commands_dir = Path("src", "commands")
    listeners_dir = Path("src", "listeners")

    utils.load_python_files(commands_dir)
    utils.load_python_files(listeners_dir)

    __bot.run(os.environ['BOT_TOKEN'])
