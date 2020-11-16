import json
from pathlib import Path
from typing import Set, Union, Optional

from discord import Guild, TextChannel
from discord.ext.commands import Bot


class Server:
    guild: Guild = None
    '''The guild instance'''

    def_prefix: str = None
    '''The default prefix'''

    prefix: Optional[str] = None
    '''The server prefix'''

    bot_channel: Optional[TextChannel] = None
    '''The channel where the bot can be executed'''

    def __init__(self, guild: Guild, def_prefix: str, prefix: Optional[str], bot_channel: Optional[TextChannel]):
        self.guild = guild
        self.prefix = prefix
        self.bot_channel = bot_channel
        self.def_prefix = def_prefix

    def get_prefix(self):
        """Gets the server prefix"""
        return self.prefix if self.prefix else self.def_prefix

    def set_prefix(self, prefix: str):
        """Sets the new command prefix for server"""
        if not prefix or prefix == self.def_prefix:
            self.prefix = None

        self.prefix = prefix

    def to_json(self):
        """Transforms the object into a jsonable dictionary"""
        result = {'guild': self.guild.id}

        if self.bot_channel:
            result['bot_channel'] = self.bot_channel.id
        if self.prefix and self.prefix != self.def_prefix:
            result['prefix'] = self.prefix

        return result


# noinspection PyMethodMayBeStatic
class Manager:
    bot: Bot = None
    '''The main bot instance'''

    db_path: Path = None
    '''The server database path'''

    serverlist: Set[Server] = None
    '''Stores the server objects'''

    def_prefix = None
    '''The default server prefix'''

    def __init__(self, bot: Bot, db_path: Path, def_prefix: str):
        self.bot = bot
        self.db_path = db_path
        self.def_prefix = def_prefix
        self.serverlist = set()

    def find_server(self, guild: Union[Guild, int]):
        """Searches for a server based on the guild id or instance"""

        final_guild: Guild
        if isinstance(guild, Guild):
            final_guild = guild
        elif isinstance(guild, int):
            final_guild = self.bot.get_guild(guild)
        else:
            raise TypeError('guild must be a Guild instance or an int')

        if not final_guild:
            raise ValueError('Invalid guild instance')

        iter_res = filter(lambda s: s.guild.id == final_guild.id, self.serverlist)
        final_result = list(iter_res)

        try:
            return final_result[0]
        except:
            server = Server(guild, self.def_prefix, None, None)

            self.serverlist.add(server)
            self.save_servers()

            return server

    def load_servers(self):
        """Loads the server instances from a database file"""
        if not self.serverlist:
            try:
                self.serverlist.clear()
            except:
                self.serverlist = set()

        path = self.db_path
        raw_list = []

        if path.exists():
            # loads the content as a raw server
            try:
                with open(path) as file:
                    raw_list = json.loads(file.read())
            except:
                pass

        # loops through all raw server
        # and then parses all of them into a valid Server object
        for raw in raw_list:
            try:
                guild_id = int(raw['guild'])

                # prevent server duplication
                if self.find_server(guild_id):
                    continue

                guild: Guild = self.bot.get_guild(guild_id)
                channel = guild.get_channel(int(raw['bot_channel'])) if raw['bot_channel'] else None
                prefix = str(raw['prefix']) if raw['prefix'] else None

                server = Server(guild=guild, def_prefix=self.def_prefix, prefix=prefix, bot_channel=channel)
                self.serverlist.add(server)
            except:
                print(f'Cannot parse data {raw}!')

    def save_servers(self):
        """Saves the server instances"""
        result = list(map(lambda s: s.to_json(), self.serverlist))
        json_str = json.dumps(result, indent=2)

        with open(self.db_path, 'w') as file:
            file.write(json_str)
