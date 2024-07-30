#!/usr/bin/env python3

import tkinter.messagebox

from tkinter import *
from tkinter.ttk import *

BOT_TYPES = ["safest", "nash_equilibrium", "most_damage", "random"]
BOT_MODES = ["ACCEPT_CHALLENGE", "CHALLENGE_USER", "SEARCH_LADDER"]
LOG_LEVELS = ["DEBUG", "INFO"]
BATTLE_FORMATS = [] # dynamically populated
BATTLE_FORMAT_MODS = ["Camomons", "Scalemons", "350 Cup"]

def load_env():
    ents = {}
    try:
        with open("env", "r") as env_file:
            for line in env_file.readlines():
                if "=" in line:
                    entry = line.split("=")
                    ents[entry[0].strip()] = entry[1].strip()
    except:
        pass
    return ents
    

def save_env(ents):
    try:
        with open("env", "w") as env_file:
            env_file.write(f'BATTLE_BOT={ents["BATTLE_BOT"]}\n')
            env_file.write(f'WEBSOCKET_URI={ents["WEBSOCKET_URI"]}\n')
            env_file.write(f'PS_USERNAME={ents["PS_USERNAME"]}\n')
            env_file.write(f'PS_PASSWORD={ents["PS_PASSWORD"]}\n')
            env_file.write(f'BOT_MODE={ents["BOT_MODE"]}\n')
            env_file.write(f'POKEMON_MODE={ents["POKEMON_MODE"]}\n')
            env_file.write(f'STATE_SEARCH_DEPTH={ents["STATE_SEARCH_DEPTH"]}\n')
            env_file.write(f'STATE_SEARCH_PRUNE_TREE={ents["STATE_SEARCH_PRUNE_TREE"]}\n')
            env_file.write(f'DYNAMIC_SEARCH_OPTS_FOR_MAX={ents["DYNAMIC_SEARCH_OPTS_FOR_MAX"]}\n')
            env_file.write(f'DYNAMIC_SEARCH_BATTLE_THRESHOLD={ents["DYNAMIC_SEARCH_BATTLE_THRESHOLD"]}\n')
            env_file.write(f'RUN_COUNT={ents["RUN_COUNT"]}\n')
            env_file.write("\n")
            env_file.write(f'USER_TO_CHALLENGE={ents["USER_TO_CHALLENGE"]}\n')
            env_file.write(f'TEAM_NAME={ents["TEAM_NAME"]}\n')
            env_file.write(f'SAVE_REPLAY={ents["SAVE_REPLAY"]}\n')
            env_file.write(f'BATTLE_TIMER={ents["BATTLE_TIMER"]}\n')
            env_file.write(f'EXPECTED_MODS={ents["EXPECTED_MODS"]}\n')
            env_file.write(f'PREFERRED_AVATAR={ents["PREFERRED_AVATAR"]}\n')
            env_file.write(f'LOCAL_INSECURE_LOGIN={ents["LOCAL_INSECURE_LOGIN"]}\n')
            env_file.write(f'LOG_LEVEL={ents["LOG_LEVEL"]}\n')
    except:
        print("ERROR: unable to save the env file!")


def load_formats():
    try:
        with open("configure_tk_formats.txt", "r") as f:
            formats = f.readlines()
            for format in formats:
                BATTLE_FORMATS.append(format.replace("\n", ""))
    except:
        pass


def is_true(env_var):
    return 1 if env_var.lower() == "true" else 0


def btn_save_click():
    ents = {
        "BATTLE_BOT": lbx_bottype.get(),
        "WEBSOCKET_URI": txt_websocket.get(),
        "PS_USERNAME": txt_username.get(),
        "PS_PASSWORD": txt_password.get(),
        "BOT_MODE": lbx_botmode.get(),
        "POKEMON_MODE": lbx_format.get(),
        "STATE_SEARCH_DEPTH": txt_searchdepth.get(),
        "STATE_SEARCH_PRUNE_TREE": "True" if chk_prunetree.get() == 1 else "False",
        "DYNAMIC_SEARCH_OPTS_FOR_MAX": txt_dynsmaxopts.get(),
        "DYNAMIC_SEARCH_BATTLE_THRESHOLD": txt_dynsbatthreshold.get(),
        "RUN_COUNT": txt_runcount.get(),
        "USER_TO_CHALLENGE": txt_challuser.get(),
        "TEAM_NAME": txt_teamfolder.get(),
        "SAVE_REPLAY": "True" if chk_savereplay.get() == 1 else "False",
        "BATTLE_TIMER": "True" if chk_battletimer.get() == 1 else "False",
        "PREFERRED_AVATAR": txt_prefavatar.get(),
        "LOCAL_INSECURE_LOGIN": "True" if chk_locallogin.get() == 1 else "False",
        "LOG_LEVEL": lbx_loglevel.get(),
    }
    expmods = ""
    for expmod_id in lbx_expmods.curselection():
        expmods += f"{lbx_expmods.get(expmod_id)}; "
    ents["EXPECTED_MODS"] = expmods.rstrip("; ")
    save_env(ents)
    tkinter.messagebox.showinfo(title="Done", message="Settings saved!")


def btn_quit_click():
    if tkinter.messagebox.askquestion(title="Please confirm", message="Would you like to quit the MariBot configurator?") == "yes":
        root.destroy()


if __name__ == '__main__':
    env = load_env()
    load_formats()
    root = Tk()
    root.title("MariBot Configurator")
    root.resizable(False, False)
    #root.geometry("500x400")
    #root.eval('tk::PlaceWindow . center')

    root.columnconfigure(0, weight = 1)
    root.columnconfigure(1, weight = 3)

    pad_opts = {"padx": 5, "pady": 5}

    # Websocket URI
    lbl_websocket = Label(root, text = "Websocket URI:")
    lbl_websocket.grid(row=0, column=0, sticky=W, **pad_opts)

    txt_websocket = StringVar()
    ent_websocket = Entry(root, textvariable = txt_websocket)
    ent_websocket.grid(row=0, column=1, sticky=E, **pad_opts)
    txt_websocket.set(env["WEBSOCKET_URI"])

    # Battle Bot Type
    lbl_bottype = Label(root, text = "Battle Bot Type (choose \"safest\" if unsure):")
    lbl_bottype.grid(row=1, column=0, sticky=W, **pad_opts)

    lbx_bottype = Combobox(root, state = "readonly", values = BOT_TYPES)
    lbx_bottype.grid(row=1, column=1, sticky=E, **pad_opts)
    lbx_bottype.set(env["BATTLE_BOT"])

    # Bot Username
    lbl_username = Label(root, text = "Bot Username (@ = choose from bot-identities file):")
    lbl_username.grid(row=2, column=0, sticky=W, **pad_opts)

    txt_username = StringVar()
    ent_username = Entry(root, textvariable = txt_username)
    ent_username.grid(row=2, column=1, sticky=E, **pad_opts)
    txt_username.set(env["PS_USERNAME"])

    # Bot Password
    lbl_password = Label(root, text = "Bot Password (leave empty if using password-less local login):")
    lbl_password.grid(row=3, column=0, sticky=W, **pad_opts)

    txt_password = StringVar()
    ent_password = Entry(root, textvariable = txt_password)
    ent_password.grid(row=3, column=1, sticky=E, **pad_opts)
    txt_password.set(env["PS_PASSWORD"])

    # Preferred Avatar
    lbl_prefavatar = Label(root, text = "Preferred Avatar (empty = random from bot-identities):")
    lbl_prefavatar.grid(row=4, column=0, sticky=W, **pad_opts)

    txt_prefavatar = StringVar()
    ent_prefavatar = Entry(root, textvariable = txt_password)
    ent_prefavatar.grid(row=4, column=1, sticky=E, **pad_opts)
    txt_prefavatar.set(env["PREFERRED_AVATAR"])

    # Battle Bot Mode
    lbl_botmode = Label(root, text = "Battle Bot Mode:")
    lbl_botmode.grid(row=5, column=0, sticky=W, **pad_opts)

    lbx_botmode = Combobox(root, state = "readonly", values = BOT_MODES)
    lbx_botmode.grid(row=5, column=1, sticky=E, **pad_opts)
    lbx_botmode.set(env["BOT_MODE"])

    # User To Challenge
    lbl_challuser = Label(root, text = "User To Challenge (only for CHALLENGE_USER mode):")
    lbl_challuser.grid(row=6, column=0, sticky=W, **pad_opts)

    txt_challuser = StringVar()
    ent_challuser = Entry(root, textvariable = txt_challuser)
    ent_challuser.grid(row=6, column=1, sticky=E, **pad_opts)
    txt_challuser.set(env["USER_TO_CHALLENGE"])

    # Battle Format ("Pokemon Mode") (gen, tier)
    lbl_format = Label(root, text = "Battle Format (choose from list or type in):")
    lbl_format.grid(row=7, column=0, sticky=W, **pad_opts)

    lbx_format = Combobox(root, values = BATTLE_FORMATS)
    lbx_format.grid(row=7, column=1, sticky=E, **pad_opts)
    lbx_format.set(env["POKEMON_MODE"])

    # Team Folder
    lbl_teamfolder = Label(root, text = "AI Teams Folder (subfolder under teams/teams):")
    lbl_teamfolder.grid(row=8, column=0, sticky=W, **pad_opts)

    txt_teamfolder = StringVar()
    ent_teamfolder = Entry(root, textvariable = txt_teamfolder)
    ent_teamfolder.grid(row=8, column=1, sticky=E, **pad_opts)
    txt_teamfolder.set(env["TEAM_NAME"])

    # Expected Mods
    lbl_expmods = Label(root, text = "Expected Mods (only if playing the relevant variants):")
    lbl_expmods.grid(row=9, column=0, sticky=W, **pad_opts)

    lbx_expmods = Listbox(root, selectmode="multiple", exportselection=0, height=3)
    for mod in BATTLE_FORMAT_MODS:
       lbx_expmods.insert(END, mod)
    lbx_expmods.grid(row=9, column=1, sticky=E, **pad_opts)
    # TODO: process --> lbx_expmods.select_set(0)

    # Run Count
    lbl_runcount = Label(root, text = "Run Count (0 = run indefinitely):")
    lbl_runcount.grid(row=10, column=0, sticky=W, **pad_opts)

    txt_runcount = StringVar()
    ent_runcount = Entry(root, textvariable = txt_runcount)
    ent_runcount.grid(row=10, column=1, sticky=E, **pad_opts)
    txt_runcount.set(env["RUN_COUNT"])

    # State Search Depth
    lbl_searchdepth = Label(root, text = "State Search Depth (default 2, 0 = dynamic):")
    lbl_searchdepth.grid(row=11, column=0, sticky=W, **pad_opts)

    txt_searchdepth = StringVar()
    ent_searchdepth = Entry(root, textvariable = txt_searchdepth)
    ent_searchdepth.grid(row=11, column=1, sticky=E, **pad_opts)
    txt_searchdepth.set(env["STATE_SEARCH_DEPTH"])

    # Dynamic Search Depth Option Product Threshold
    lbl_dynsmaxopts = Label(root, text = "Dynamic Depth Option Product Threshold (default 20):")
    lbl_dynsmaxopts.grid(row=12, column=0, sticky=W, **pad_opts)

    txt_dynsmaxopts = StringVar()
    ent_dynsmaxopts = Entry(root, textvariable = txt_dynsmaxopts)
    ent_dynsmaxopts.grid(row=12, column=1, sticky=E, **pad_opts)
    txt_dynsmaxopts.set(env["DYNAMIC_SEARCH_OPTS_FOR_MAX"])

    # Dynamic Search Depth Option Product Threshold
    lbl_dynsbatthreshold = Label(root, text = "Dynamic Depth Battle Threshold (default 1):")
    lbl_dynsbatthreshold.grid(row=13, column=0, sticky=W, **pad_opts)

    txt_dynsbatthreshold = StringVar()
    ent_dynsbatthreshold = Entry(root, textvariable = txt_dynsbatthreshold)
    ent_dynsbatthreshold.grid(row=13, column=1, sticky=E, **pad_opts)
    txt_dynsbatthreshold.set(env["DYNAMIC_SEARCH_BATTLE_THRESHOLD"])

    # Prune Search Tree?
    chk_prunetree = IntVar()
    cbx_prunetree = Checkbutton(root, text = "Prune Search Tree", variable = chk_prunetree)
    cbx_prunetree.grid(row=14, column=0, sticky=W, **pad_opts)
    chk_prunetree.set(is_true(env["STATE_SEARCH_PRUNE_TREE"]))

    # Save Replay?
    chk_savereplay = IntVar()
    cbx_savereplay = Checkbutton(root, text = "Save Replay", variable = chk_savereplay)
    cbx_savereplay.grid(row=15, column=0, sticky=W, **pad_opts)
    chk_savereplay.set(is_true(env["SAVE_REPLAY"]))

    # Use Battle Timer?
    chk_battletimer = IntVar()
    cbx_battletimer = Checkbutton(root, text = "Use Battle Timer", variable = chk_battletimer)
    cbx_battletimer.grid(row=16, column=0, sticky=W, **pad_opts)
    chk_battletimer.set(is_true(env["BATTLE_TIMER"]))

    # Local Insecure Login?
    chk_locallogin = IntVar()
    cbx_locallogin = Checkbutton(root, text = "Password-less Login (Local Server Only!)", variable = chk_locallogin)
    cbx_locallogin.grid(row=17, column=0, sticky=W, **pad_opts)
    chk_locallogin.set(is_true(env["LOCAL_INSECURE_LOGIN"]))

    # Log Level
    lbl_loglevel = Label(root, text = "Log Level:")
    lbl_loglevel.grid(row=18, column=0, sticky=W, **pad_opts)

    lbx_loglevel = Combobox(root, state = "readonly", values = LOG_LEVELS)
    lbx_loglevel.grid(row=18, column=1, sticky=E, **pad_opts)
    lbx_loglevel.set(env["LOG_LEVEL"])

    # Save Button
    btn_save = Button(root, text = "Save", command = btn_save_click)
    btn_save.grid(row=19, column=0, sticky=W, **pad_opts)

    # Quit Button
    btn_quit = Button(root, text = "Quit", command = btn_quit_click)
    btn_quit.grid(row=19, column=1, sticky=W, **pad_opts)

    root.mainloop()