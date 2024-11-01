import logging

import constants

from showdown.engine.damage_calculator import calculate_damage, get_move
from showdown.engine.objects import StateMutator
from showdown.engine.select_best_move import pick_safest
from showdown.engine.select_best_move import get_payoff_matrix


logger = logging.getLogger(__name__)


from config import ShowdownConfig
gen = ShowdownConfig.get_generation()
search_depth = ShowdownConfig.search_depth
opts_for_max = ShowdownConfig.dynsearch_opts_for_max
battle_threshold = ShowdownConfig.dynsearch_battle_threshold


def format_decision(battle, decision):
    # Formats a decision for communication with Pokemon-Showdown
    # If the pokemon can mega-evolve, it will
    # If the move can be used as a Z-Move, it will be, unless there are detrimental conditions

    if decision.is_switch:
        switch_pokemon = decision.id
        for pkmn in battle.user.reserve:
            if pkmn.name == switch_pokemon and pkmn.hp > 0:
                message = "/switch {}".format(pkmn.index)
                break
        else:
            raise ValueError("Tried to switch to: {}".format(switch_pokemon))
    else:
        message = "/choose move {}".format(decision.id)
        if battle.user.active.can_mega_evo:
            message = "{} {}".format(message, constants.MEGA)
        elif battle.user.active.can_ultra_burst:
            message = "{} {}".format(message, constants.ULTRA_BURST)

        # only dynamax on last pokemon
        if battle.user.active.can_dynamax and all(p.hp == 0 for p in battle.user.reserve):
            message = "{} {}".format(message, constants.DYNAMAX)

        # Terastallization: try to predict usefulness, but use Stellar for the last mon if nothing was terastallized yet
        # TODO: proper Stellar support
        elif battle.user.active.can_terastallize:
            if ShowdownConfig.allow_tera_to_stellar_type or battle.user.active.tera_type != 'stellar':
                if decision.terastallize or \
                    (all(p.hp == 0 for p in battle.user.reserve) and battle.user.active.tera_type == 'stellar'):
                        message = "{} {}".format(message, constants.TERASTALLIZE)

        # Z move
        if battle.user.active.get_move(decision.id).can_z:
            # predict damage without Z, only consider Z if the standard (non-Z) move is not enough to deal lethal
            battle_state = battle.create_state()
            damage_without_Z = 0 
            damage_with_Z = 0
            predict_damage = calculate_damage(battle_state, constants.USER, decision.id, constants.DO_NOTHING_MOVE, calc_type='average') # FIXME: maybe calc_type=max (or average)?
            if predict_damage is not None:
                damage_without_Z = predict_damage[0]
                base_power = get_move(decision.id)[constants.BASE_POWER]
                coeff = 2
                if base_power >= 140: coeff = 200.0/base_power
                elif base_power >= 130: coeff = 195.0/base_power
                elif base_power >= 120: coeff = 190.0/base_power
                elif base_power >= 110: coeff = 185.0/base_power
                elif base_power >= 100: coeff = 180.0/base_power
                elif base_power >= 90: coeff = 175.0/base_power
                elif base_power >= 80: coeff = 160.0/base_power
                elif base_power >= 70: coeff = 140.0/base_power
                elif base_power >= 60: coeff = 120.0/base_power
                else: coeff = 100.0/base_power
                damage_with_Z = damage_without_Z * coeff
            
            print(f"Damage without Z for {decision.id} = {damage_without_Z}")
            print(f"Damage with Z for {decision.id} = {damage_with_Z}")

            bad_z_conditions = constants.SUBSTITUTE in battle.opponent.active.volatile_statuses \
                or damage_without_Z >= battle_state.opponent.active.hp \
                # or (damage_without_Z != 0 and damage_with_Z < battle_state.opponent.active.hp)
            if not bad_z_conditions:
                message = "{} {}".format(message, constants.ZMOVE)

    return [message, str(battle.rqid)]


def prefix_opponent_move(score_lookup, prefix):
    new_score_lookup = dict()
    for k, v in score_lookup.items():
        bot_move, opponent_move = k
        new_opponent_move = "{}_{}".format(opponent_move, prefix)
        new_score_lookup[(bot_move, new_opponent_move)] = v

    return new_score_lookup


def pick_safest_move_from_battles(battles):
    all_scores = dict()
    for i, b in enumerate(battles):
        state = b.create_state()
        mutator = StateMutator(state)
        user_options, opponent_options = b.get_all_options()
        logger.debug("Searching through the state: {}".format(mutator.state))
        scores = get_payoff_matrix(mutator, user_options, opponent_options, prune=True)

        prefixed_scores = prefix_opponent_move(scores, str(i))
        all_scores = {**all_scores, **prefixed_scores}

    decision, payoff = pick_safest(all_scores, remove_guaranteed=True)
    bot_choice = decision[0]
    logger.debug("Safest: {}, {}".format(bot_choice, payoff))
    return bot_choice


def pick_safest_move_using_dynamic_search_depth(battles):
    """
    Dynamically decides how far to look into the game.

    This requires a strong computer to be able to search 3/4 turns ahead.
    Using a pypy interpreter will also result in better performance.

    """
    all_scores = dict()
    num_battles = len(battles)

    search_depth = 2 if num_battles > battle_threshold else 3

    if num_battles > 1:

        for i, b in enumerate(battles):
            state = b.create_state()
            mutator = StateMutator(state)
            user_options, opponent_options = b.get_all_options()
            logger.debug("Searching through the state: {}".format(mutator.state))
            scores = get_payoff_matrix(mutator, user_options, opponent_options, depth=search_depth, prune=True)
            prefixed_scores = prefix_opponent_move(scores, str(i))
            all_scores = {**all_scores, **prefixed_scores}

    elif num_battles == 1:

        b = battles[0]
        state = b.create_state()
        mutator = StateMutator(state)
        user_options, opponent_options = b.get_all_options()

        num_user_options = len(user_options)
        num_opponent_options = len(opponent_options)
        options_product = num_user_options * num_opponent_options
        if options_product < opts_for_max and num_user_options > 1 and num_opponent_options > 1:
            logger.debug("Low options product, looking an additional depth")
            search_depth += 1

        logger.debug("Searching through the state: {}".format(mutator.state))
        logger.debug("Options Product: {}".format(options_product))
        logger.debug("My Options: {}".format(user_options))
        logger.debug("Opponent Options: {}".format(opponent_options))
        logger.debug("Search depth: {}".format(search_depth))
        all_scores = get_payoff_matrix(mutator, user_options, opponent_options, depth=search_depth, prune=True)

    else:
        raise ValueError("less than 1 battle?: {}".format(battles))

    decision, payoff = pick_safest(all_scores, remove_guaranteed=True)
    bot_choice = decision[0]
    logger.debug("Safest: {}, {}".format(bot_choice, payoff))
    logger.debug("Depth: {}".format(search_depth))
    return bot_choice
