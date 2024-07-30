# Showdown  ![umbreon](https://play.pokemonshowdown.com/sprites/xyani/umbreon.gif)
MariBot, an extension of pmariglia's Pokémon battle-bot that can play battles on [Pokemon Showdown](https://pokemonshowdown.com/).
The bot can play single battles in generations 1 through 9.

This is a modification for pmariglia's original Pokemon battle-bot which contains some experimental modifications and extensions. The project was born out of an idea to try to extend the capability of the bot to play gen 1 and gen 2 at a basic support level, which then snowballed into a variety of small-ish changes to the code base which, in my subjective opinion, enhance the experience with the bot in a variety of ways. A lot of the code is experimental and isn't meant to be written in the cleanest way possible, it may also contain bugs, so please be warned :) There's no support for any of these changes at the moment, as this is mostly meant as a personal "sandbox" fork for my friends and me. Please don't bother the original bot author with bug reports as well if you're playing this fork and experiencing any issues.

Core features of this fork (not meant to be an extensive list):
- The bot differentiates between generations when it comes to the type chart and various other (mostly minor) ways. Not comprehensive.
- Gen 1 and Gen 2 singles are supported at a basic level, the AI will not crash upon entering the match, and some quirks of these early generations are understood by the bot (such as e.g. type differences), but definitely not all, so many things are still seen by the bot through the lens of the newer generations (leading to suboptimal choices).
- Additional configuration options are available in the "env" file, namely "STATE_SEARCH_DEPTH" (which defines the search depth for the AI, defaulting to 2 and allowing the value of 0 to set up the dynamic search depth which increases the depth as the game goes longer), "STATE_SEARCH_PRUNE_TREE" (experimental option that removes the pruning of the state search tree, used to test the bot behavior with and without pruning), "DYNAMIC_SEARCH_OPTS_FOR_MAX" (how many total options are allowed for the AI to go for the maximum state search depth of 4 when dynamic search depth is enabled), "DYNAMIC_SEARCH_BATTLE_THRESHOLD" (how many battles can there be for the dynamic search to increase the depth to 3), "BATTLE_TIMER" (can be disabled so that the 5-minute timer is not used, helpful for higher search depths), "EXPECTED_MODS" (see below), "PREFERRED_AVATAR" (the avatar that the AI will set for itself), "LOCAL_INSECURE_LOGIN" (if set to True, will try to connect to the server with no authentication or password - this should only be done when using the patched local server/client which allows unregistered insecure login!).
- Support for more random formats. Namely, Battle Factory and BSS Factory will now work as expected without crashing, and there are now sets for randbats in every generation, so hopefully the bot will be a little bit more discerning in which sets to expect depending on which gen it is playing.
- Support for some mods, namely, Scalemons, Camomons and 350 Cup, through the "EXPECTED_MODS" option (these mods can be listed by name in the EXPECTED_MODS variable, then the AI will try to account for the mon stat changes in the relevant modded formats).
- Some improvements and fixes are attempted to the AI (namely, the AI properly understands Sleep/Rest Talk now, understands Trick Room teams better, understands Counter and Mirror Coat better for all those Wobbuffet shenanigans, will try not to throw extra layers of hazards when already at max, etc.)
- The bot will no longer crash if it fails to load the Smogon stats from the online source (which is possible for some obscure formats like gen7nu which is no longer played much, if at all). Also, the bot can load a local Smogon stats file as a fallback, from the "smogon" folder (put e.g. the gen7nu-0.json file in there, downloaded from the "chaos" subfolder of one of the folders at https://www.smogon.com/stats/), this allows you to use the local Smogon stats base, including some obscure older formats that are no longer played today and which the bot can't detect and download stats for automatically.
- Bot profiles/personalities (name + avatar combinations) can be set up for the local server/client, but this is mostly undocumented for now, and it ONLY works on the local server which requires some patching to support password-less insecure login. If you're interested, check out the source code (e.g. for LOCAL_INSECURE_LOGIN, PS_USERNAME and PS_PASSWORD, as well as PREFERRED_AVATAR) and keep in mind that you're on your own if you decide to try it! Don't try it on the official Pokemon Showdown, it won't work and you may possibly even be banned!
- Some minor features from other forks are integrated here, e.g. the Random battle bot, courtesy of its original author SwagMander.
- There's now a rudimentary GUI configuration tool which allows you to set up the "env" file, check out configure_tk.py. Note that it requires TkInter, and for some reason it's reported not to work on MacOS - sadly, can't test or comment on this since I don't own a Mac personally.
- Probably some other (mostly minor) stuff that I forgot.

This fork may be modified further as time goes by in case I find something interesting to try, test, and improve.
Anyone is welcome to use and reuse the code from this fork if you find anything here useful. Any of this code can also be backported into the original repo, with any needed changes, if the author of the bot finds anything here of interest.

The original readme by pmariglia follows. Please note that it's unmodified and doesn't contain any additional information about the modifications in this fork. Any additional documentation regarding the changes and improvements in this fork may be committed at a later date given enough time.

![badge](https://github.com/pmariglia/showdown/actions/workflows/pythonapp.yml/badge.svg)

## Python version
Developed and tested using Python 3.8.

## Getting Started

### Configuration
Environment variables are used for configuration.
You may either set these in your environment before running,
or populate them in the [env](https://github.com/pmariglia/showdown/blob/master/env) file.

The configurations available are:

| Config Name | Type | Required | Description |
|---|:---:|:---:|---|
| **`BATTLE_BOT`** | string | yes | The BattleBot module to use. More on this below in the Battle Bots section |
| **`WEBSOCKET_URI`** | string | yes | The address to use to connect to the Pokemon Showdown websocket |
| **`PS_USERNAME`** | string | yes | Pokemon Showdown username |
| **`PS_PASSWORD`** | string | yes | Pokemon Showdown password  |
| **`BOT_MODE`** | string | yes | The mode the the bot will operate in. Options are `CHALLENGE_USER`, `SEARCH_LADDER`, or `ACCEPT_CHALLENGE` |
| **`POKEMON_MODE`** | string | yes | The type of game this bot will play: `gen8ou`, `gen7randombattle`, etc. |
| **`USER_TO_CHALLENGE`** | string | only if `BOT_MODE` is `CHALLENGE_USER` | If `BOT_MODE` is `CHALLENGE_USER`, this is the name of the user you want your bot to challenge |
| **`RUN_COUNT`** | int | no | The number of games the bot will play before quitting |
| **`TEAM_NAME`** | string | no | The name of the file that contains the team you want to use. More on this below in the Specifying Teams section. |
| **`ROOM_NAME`** | string | no | If `BOT_MODE` is `ACCEPT_CHALLENGE`, the bot will join this chatroom while waiting for a challenge. |
| **`SAVE_REPLAY`** | boolean | no | Specifies whether or not to save replays of the battles (`True` / `False`) |
| **`LOG_LEVEL`** | string | no | The Python logging level (`DEBUG`, `INFO`, etc.) |

### Running without Docker

**1. Clone**

Clone the repository with `git clone https://github.com/pmariglia/showdown.git`

**2. Install Requirements**

Install the requirements with `pip install -r requirements.txt`.

**3. Configure your [env](https://github.com/pmariglia/showdown/blob/master/env) file**

Here is a sample:
```
BATTLE_BOT=safest
WEBSOCKET_URI=wss://sim3.psim.us/showdown/websocket
PS_USERNAME=MyUsername
PS_PASSWORD=MyPassword
BOT_MODE=SEARCH_LADDER
POKEMON_MODE=gen7randombattle
RUN_COUNT=1
```

**4. Run**

Run with `python run.py`

### Running with Docker
This requires Docker 17.06 or higher.

**1. Clone the repository**

`git clone https://github.com/pmariglia/showdown.git`

**2. Build the Docker image**

`docker build . -t showdown`

**3. Run with an environment variable file**

`docker run --env-file env showdown`

## Battle Bots

This project has a few different battle bot implementations.
Each of these battle bots use a different method to determine which move to use.

### Safest
use `BATTLE_BOT=safest`

The bot searches through the game-tree for two turns and selects the move that minimizes the possible loss for a turn.

For decisions with random outcomes a weighted average is taken for all possible end states.
For example: If using draco meteor versus some arbitrary other move results in a score of 1000 if it hits (90%) and a score of 900 if it misses (10%), the overall score for using
draco meteor is (0.9 * 1000) + (0.1 * 900) = 990.

This is equivalent to the [Expectiminimax](https://en.wikipedia.org/wiki/Expectiminimax) strategy.

This decision type is deterministic - the bot will always make the same move given the same situation again.

### Nash-Equilibrium (experimental)
use `BATTLE_BOT=nash_equilibrium`

Using the information it has, plus some assumptions about the opponent, the bot will attempt to calculate the [Nash-Equilibrium](https://en.wikipedia.org/wiki/Nash_equilibrium) with the highest payoff
and select a move from that distribution.

The Nash Equilibrium is calculated using command-line tools provided by the [Gambit](http://www.gambit-project.org/) project.
This decision method should only be used when running with Docker and will fail otherwise.

This decision method is **not** deterministic. The bot **may** make a different move if presented with the same situation again.

### Team Datasets (experimental)

use `BATTLE_BOT=team_datasets`

Using a file of sets & teams, this battle-bot is meant to have a better
understanding of Pokeon sets that may appear.
Populate this dataset by editing `data/team_datasets.json`.

Still uses the `safest` decision making method for picking a move, but in theory the knowledge of sets should
result in better decision making.

### Most Damage
use `BATTLE_BOT=most_damage`

Selects the move that will do the most damage to the opponent

Does not switch

## Write your own bot
Create a package in [showdown/battle_bots](https://github.com/pmariglia/showdown/tree/master/showdown/battle_bots) with
a module named `main.py`. In this module, create a class named `BattleBot`, override the Battle class,
and implement your own `find_best_move` function.

Set the `BATTLE_BOT` environment variable to the name of your package and your function will be called each time PokemonShowdown prompts the bot for a move

## The Battle Engine
The bots in the project all use a Pokemon battle engine to determine all possible transpositions that may occur from a pair of moves.

For more information, see [ENGINE.md](https://github.com/pmariglia/showdown/blob/master/ENGINE.md) 

## Specifying Teams
You can specify teams by setting the `TEAM_NAME` environment variable.
Examples can be found in `teams/teams/`.

Passing in a directory will cause a random team to be selected from that directory.

The path specified should be relative to `teams/teams/`.

#### Examples

Specify a file:
```
TEAM_NAME=gen8/ou/clef_sand
```

Specify a directory:
```
TEAM_NAME=gen8/ou
```
