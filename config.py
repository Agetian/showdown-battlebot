import logging
import os
import random
import re
import sys
from logging.handlers import RotatingFileHandler
from typing import Union

from environs import Env

import constants

env = Env()
env.read_env(path="env", recurse=False)


class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.module = "[{}]".format(record.module)
        record.levelname = "[{}]".format(record.levelname)
        return "{} {}".format(record.levelname.ljust(10), record.msg)


class CustomRotatingFileHandler(RotatingFileHandler):
    def __init__(self, file_name, **kwargs):
        self.base_dir = "logs"
        if not os.path.exists(self.base_dir):
            os.mkdir(self.base_dir)

        super().__init__("{}/{}".format(self.base_dir, file_name), **kwargs)

    def do_rollover(self, new_file_name):
        self.baseFilename = "{}/{}".format(self.base_dir, new_file_name)
        self.doRollover()


def init_logging(level, log_to_file):
    websockets_logger = logging.getLogger("websockets")
    websockets_logger.setLevel(logging.INFO)
    requests_logger = logging.getLogger("urllib3")
    requests_logger.setLevel(logging.INFO)

    # Gets the root logger to set handlers/formatters
    logger = logging.getLogger()
    logger.setLevel(level)
    if log_to_file:
        log_handler = CustomRotatingFileHandler("init.log")
    else:
        log_handler = logging.StreamHandler(sys.stdout)

    ShowdownConfig.log_handler = log_handler
    log_handler.setFormatter(CustomFormatter())
    logger.addHandler(log_handler)


class _ShowdownConfig:
    battle_bot_module: str
    websocket_uri: str
    username: str
    password: str
    bot_mode: str
    pokemon_mode: str
    run_count: int
    team: str
    user_to_challenge: str
    save_replay: bool
    room_name: str
    damage_calc_type: str
    log_level: str
    log_to_file: bool
    log_handler: Union[CustomRotatingFileHandler, logging.StreamHandler]
    battle_timer: bool
    expected_mods: str
    expected_mods_derived: str
    local_insecure_login: bool
    avatar: str
    search_depth: int
    prune_search_tree: bool
    dynsearch_opts_for_max: int
    dynsearch_battle_threshold: int

    def configure(self):
        self.battle_bot_module = env("BATTLE_BOT")
        self.websocket_uri = env("WEBSOCKET_URI")
        if not hasattr(self, "username"): # avoid overwriting an existing username on a subsequent call to configure
            self.username = env("PS_USERNAME")
        self.password = env("PS_PASSWORD")
        self.bot_mode = env("BOT_MODE")
        self.pokemon_mode = env("POKEMON_MODE")

        self.search_depth = env.int("STATE_SEARCH_DEPTH", 2)
        self.prune_search_tree = env.bool("STATE_SEARCH_PRUNE_TREE", True)
        self.dynsearch_opts_for_max = env.int("DYNAMIC_SEARCH_OPTS_FOR_MAX", 20)
        self.dynsearch_battle_threshold = env.int("DYNAMIC_SEARCH_BATTLE_THRESHOLD", 1)
        self.run_count = env.int("RUN_COUNT", 1)
        self.team = env("TEAM_NAME", None)
        self.user_to_challenge = env("USER_TO_CHALLENGE", None)

        self.save_replay = env.bool("SAVE_REPLAY", False)
        self.room_name = env("ROOM_NAME", None)
        self.damage_calc_type = env("DAMAGE_CALC_TYPE", "average")

        self.log_level = env("LOG_LEVEL", "DEBUG")
        self.log_to_file = env.bool("LOG_TO_FILE", False)

        self.battle_timer = env.bool("BATTLE_TIMER", True)

        self.expected_mods = env("EXPECTED_MODS", "")
        if "@@@" in self.pokemon_mode:
            self.expected_mods += f" @@@{self.pokemon_mode.split('@@@')[1]}"
        if not hasattr(self, "expected_mods_derived"):
            self.expected_mods_derived = ""
        else:
            self.expected_mods += self.expected_mods_derived

        self.local_insecure_login = env.bool("LOCAL_INSECURE_LOGIN", False)
        if not hasattr(self, "preferred_avatar"):
            self.preferred_avatar = env("PREFERRED_AVATAR", "")

        # Use bot identities in case '@' was specified for the username,
        # uses the file 'bot-identities' from the working path, 
        # which is a list of identities in the format: name[=avatar]
        # (only works on a local server with insecure no-auth login)
        if self.username == '@':
            if self.local_insecure_login:
                try:
                    with open('bot-identities', 'r') as ident_file:
                        identity = random.choice(ident_file.readlines())
                        if identity.strip() == '':
                            self.username = 'MariBot'
                        else:
                            if '=' in identity:
                                self.username = identity.split('=')[0].strip()
                                self.preferred_avatar = identity.split('=')[1].strip()
                            else:
                                self.username = identity.strip()
                except:
                    self.username = 'MariBot'
            else:
                self.username = 'MariBot'

        self.validate_config()

    def validate_config(self):
        assert self.bot_mode in constants.BOT_MODES

        if self.bot_mode == constants.CHALLENGE_USER:
            assert self.user_to_challenge is not None, (
                "If bot_mode is `CHALLENGE_USER, you must declare USER_TO_CHALLENGE"
            )
    
    # TODO: Ideally, refactor this so that it's set up once and accessible everywhere where needed
    # (see also battle.generation which serves a similar purpose but is rather limited in where it's accessible)
    def get_generation(self):
        gen = 9 # Should default to the latest generation
        if not hasattr(self, "pokemon_mode"):
            self.configure()
        format_gen = re.findall(r"^gen(\d+)", ShowdownConfig.pokemon_mode)
        if len(format_gen) > 0:
            gen = int(format_gen[0])
        return gen


ShowdownConfig = _ShowdownConfig()
