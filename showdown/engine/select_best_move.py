import math
from collections import defaultdict
from copy import deepcopy

import constants

from .evaluate import evaluate
from .find_state_instructions import get_all_state_instructions
from .find_state_instructions import get_effective_speed
from .damage_calculator import get_move, is_immune


WON_BATTLE = 100


import random
from config import ShowdownConfig
gen = ShowdownConfig.get_generation()
search_depth = ShowdownConfig.search_depth


def remove_guaranteed_opponent_moves(score_lookup):
    """This method removes enemy moves from the score-lookup that do not give the bot a choice.
       For example - if the bot has 1 pokemon left, the opponent is faster, and can kill your active pokemon with move X
       then move X for the opponent will be removed from the score_lookup

       The bot behaves much better when it cannot see these types of decisions"""
    move_combinations = list(score_lookup.keys())
    if len(set(k[0] for k in move_combinations)) == 1:
        return score_lookup
    elif len(set(k[1] for k in move_combinations)) == 1:
        return score_lookup

    # find the opponent's moves where the bot has a choice
    opponent_move_scores = dict()
    opponent_decisions = set()
    for k, score in score_lookup.items():
        opponent_move = k[1]
        if opponent_move not in opponent_move_scores:
            opponent_move_scores[opponent_move] = score
        elif opponent_move in opponent_move_scores and score != opponent_move_scores[opponent_move] and not math.isnan(score):
            opponent_decisions.add(opponent_move)

    # re-create score_lookup with only the opponent's move acquired above
    new_opponent_decisions = dict()
    for k, v in score_lookup.items():
        if k[1] in opponent_decisions:
            new_opponent_decisions[k] = v

    return new_opponent_decisions


def pick_safest(score_lookup, remove_guaranteed=False):
    modified_score_lookup = score_lookup
    if remove_guaranteed:
        modified_score_lookup = remove_guaranteed_opponent_moves(score_lookup)
        if not modified_score_lookup:
            modified_score_lookup = score_lookup
    worst_case = defaultdict(lambda: (tuple(), float('inf')))
    for move_pair, result in modified_score_lookup.items():
        if worst_case[move_pair[0]][1] > result:
            worst_case[move_pair[0]] = move_pair, result

    safest = max(worst_case, key=lambda x: worst_case[x][1])
    return worst_case[safest]


def move_item_to_front_of_list(l, item):
    all_indicies = list(range(len(l)))
    this_index = l.index(item)
    all_indicies.remove(this_index)
    all_indicies.insert(0, this_index)
    return [l[i] for i in all_indicies]


def modify_score_conditionally(score, depth, mutator, user_move, state_scores):
        # Buff Sleep Talk in sleep, reduce the weight for Spikes if at max layers, etc.
        if (user_move.id == "sleeptalk" or user_move.id == "snore") and mutator.state.user.active.status == constants.SLEEP and mutator.state.user.side_conditions[constants.SLEEP_COUNT] < 3:
            highest_nonswitch_score = 0
            for state_score_id in state_scores.keys():
                user_move_1 = state_score_id[0]
                if (not user_move_1.is_switch) and state_scores[state_score_id] > highest_nonswitch_score:
                    highest_nonswitch_score = state_scores[state_score_id]
            score = highest_nonswitch_score + 10 # try to weigh Sleep Talk above other moves but not above meaningful switches
        elif user_move.id == constants.SPIKES:
            max_layers = 3 if gen >= 3 else 1 # Gen 1-2 had only one layer of Spikes
            if mutator.state.opponent.side_conditions[constants.SPIKES] >= max_layers:
                score = -1000 # not worth throwing extra Spikes
        elif user_move.id == constants.TOXIC_SPIKES:
            if mutator.state.opponent.side_conditions[constants.TOXIC_SPIKES] >= 2:
                score = -1000 # not worth throwing extra Toxic Spikes
        elif user_move.id == constants.STEALTH_ROCK:
            if mutator.state.opponent.side_conditions[constants.STEALTH_ROCK] >= 1:
                score = -1000 # not worth throwing extra Stealth Rock
        
        # Reduce the score for Trick Room if already at Trick Room and deduced speed is lower than opponent's
        opponent_effective_speed = get_effective_speed(mutator.state, mutator.state.opponent)
        bot_effective_speed = get_effective_speed(mutator.state, mutator.state.user)
        outspeed = opponent_effective_speed > bot_effective_speed if mutator.state.trick_room \
            else bot_effective_speed > opponent_effective_speed
        if user_move.id == constants.TRICK_ROOM:
            if outspeed:
                score -= 1000 # no need to switch the Trick Room status since we outspeed the opponent
            else:
                highest_nonswitch_score = 0
                for state_score_id in state_scores.keys():
                    user_move_1 = state_score_id[0]
                    if (not user_move_1.is_switch) and state_scores[state_score_id] > highest_nonswitch_score:
                        highest_nonswitch_score = state_scores[state_score_id]
                score = highest_nonswitch_score + 100 # FIXME: fixed value doesn't work very well here?

        # Reduce the score for Counter and Mirror Coat if the opponent used a move of the incorrect type before
        last_opp_move = get_move(mutator.state.opponent.last_used_move.move)
        if last_opp_move:
            if user_move.id == 'counter' and last_opp_move[constants.CATEGORY] != constants.PHYSICAL:
                score -= 300
            elif user_move.id == 'mirrorcoat' and last_opp_move[constants.CATEGORY] != constants.SPECIAL:
                score -= 300

        # Metronome: randomly play this move above others except the switch ones
        #if user_move.id == 'metronome' and random.choice([True, False]):
        #    highest_nonswitch_score = 0
        #    for state_score_id in state_scores.keys():
        #        user_move_1 = state_score_id[0]
        #        if (not user_move_1.is_switch) and state_scores[state_score_id] > highest_nonswitch_score:
        #            highest_nonswitch_score = state_scores[state_score_id]
        #    score = highest_nonswitch_score + 10

        considered_move = get_move(user_move.id)
        if considered_move:
            # FIXME: Additionally debuff moves that the target would be immune to (e.g. Electric vs. Ground)
            if is_immune(considered_move["type"], mutator.state.opponent.active.types):
                score -= 1000
            # FIXME: Debuff Substitute when at <25% hp
            if considered_move["id"] == constants.SUBSTITUTE and mutator.state.user.active.hp <= mutator.state.user.active.maxhp / 4:
                score -= 1000
            # FIXME: Reflectable moves vs. Magic Bounce and Magic Coat
            if hasattr(considered_move, constants.REFLECTABLE) and ((mutator.state.opponent.active.ability == "magicbounce") or ("magiccoat" in mutator.state.opponent.volatile_status)):
                score -= 1000
            # FIXME: Buff/debuff Baton Pass depending on the presence of boosts
            # TODO: Actually implement the state modification in instruction_generator to properly account for the game state
            #if considered_move["id"] == 'batonpass' and len(mutator.state.user.reserve) > 0:
            #    if len(mutator.state.user.reserve) == 0:
            #        score -= 1000
            #    else:
            #        score += 30 * (mutator.state.user.active.attack_boost + mutator.state.user.active.defense_boost + \
            #                       mutator.state.user.active.special_attack_boost + mutator.state.user.active.special_defense_boost + mutator.state.user.active.speed_boost)

        # FIXME: Debuff a switch in case another conscious switch was just made. Helps avoid repeated switches.
        if user_move.is_switch and mutator.state.user.last_used_move.move.startswith("switch") and mutator.state.user.last_used_move.turn > 0:
            if not(mutator.state.opponent.last_used_move.move.startswith("switch")):
                score -= 300

        return score


def get_payoff_matrix(mutator, user_options, opponent_options, depth=search_depth if search_depth > 0 else 2, prune=True):
    """
    :param mutator: a StateMutator object representing the state of the battle
    :param user_options: options for the bot
    :param opponent_options: options for the opponent
    :param depth: the remaining depth before the state is evaluated
    :param prune: specify whether or not to prune the tree
    :return: a dictionary representing the potential move combinations and their associated scores
    """

    winner = mutator.state.battle_is_finished()
    if winner:
        return {(constants.DO_NOTHING_MOVE, constants.DO_NOTHING_MOVE): evaluate(mutator.state) + WON_BATTLE*depth*winner}

    depth -= 1

    # if the battle is not over, but the opponent has no moves - we want to return the user options as moves
    # this is a special case in a random battle where the opponent's pokemon has fainted, but the opponent still
    # has reserves left that are unseen
    if opponent_options == [constants.DO_NOTHING_MOVE] and mutator.state.opponent.active.hp == 0:
        return {(user_option, constants.DO_NOTHING_MOVE): evaluate(mutator.state) for user_option in user_options}

    state_scores = dict()

    best_score = float('-inf')
    for i, user_move in enumerate(user_options):
        worst_score_for_this_row = float('inf')
        skip = False

        # opponent_options can change during the loop
        # using opponent_options[:] makes a copy when iterating to ensure no funny-business
        for j, opponent_move in enumerate(opponent_options[:]):
            if skip:
                state_scores[(user_move, opponent_move)] = float('nan')
                continue

            score = 0
            state_instructions = get_all_state_instructions(mutator, user_move, opponent_move)
            if depth == 0:
                for instructions in state_instructions:
                    mutator.apply(instructions.instructions)
                    t_score = evaluate(mutator.state)
                    score += (t_score * instructions.percentage)
                    mutator.reverse(instructions.instructions)

            else:
                for instructions in state_instructions:
                    this_percentage = instructions.percentage
                    mutator.apply(instructions.instructions)
                    next_turn_user_options, next_turn_opponent_options = mutator.state.get_all_options()
                    safest = pick_safest(get_payoff_matrix(mutator, next_turn_user_options, next_turn_opponent_options, depth=depth, prune=prune))
                    score += safest[1] * this_percentage
                    mutator.reverse(instructions.instructions)

            # make certain fixed modifications based on conditions (e.g. Trick Room, counters, etc.)
            score = modify_score_conditionally(score, depth, mutator, user_move, state_scores)

            state_scores[(user_move, opponent_move)] = score

            if score < worst_score_for_this_row:
                worst_score_for_this_row = score

            if ShowdownConfig.prune_search_tree:
                if prune and score < best_score:
                    skip = True

                    # MOST of the time in pokemon, an opponent's move that causes a prune will cause a prune elsewhere
                    # move this item to the front of the list to prune faster
                    opponent_options = move_item_to_front_of_list(opponent_options, opponent_move)

        if worst_score_for_this_row > best_score:
            best_score = worst_score_for_this_row

    return state_scores
