from showdown.battle import Battle

from ..helpers import format_decision
from ..helpers import pick_safest_move_from_battles, pick_safest_move_using_dynamic_search_depth

from config import ShowdownConfig
ShowdownConfig.configure()
search_depth = ShowdownConfig.search_depth

class BattleBot(Battle):
    def __init__(self, *args, **kwargs):
        super(BattleBot, self).__init__(*args, **kwargs)

    def find_best_move(self):
        battles = self.prepare_battles(join_moves_together=True)
        if search_depth > 0:
            safest_move = pick_safest_move_from_battles(battles)
        else:
            safest_move = pick_safest_move_using_dynamic_search_depth(battles)

        return format_decision(self, safest_move)