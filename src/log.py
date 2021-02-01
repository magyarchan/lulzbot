#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import time

def open_logfile(name, mode='a', enc='utf-8'):
    file = open(name, mode=mode, encoding=enc)
    return file

def log(e):
    directory = './log'
    if not os.path.exists(directory):
        os.mkdir(directory)
    filename = time.strftime("%Y-%m-%d_%H")
    file = open_logfile(f"{directory}/{filename}.txt")
    # global filename, file

    log_text = ''
    arg0 = f"({e.arguments[0]})" if e.arguments else ''
    nick = e.source.nick
    if e.type == 'pubmsg':
        log_text = nick + ': ' + arg0
    elif e.type == 'join':
        log_text = f" -- {e.source} has joined"
    elif e.type == 'quit':
        log_text = f" -- {nick} has quit {arg0}"
    elif e.type == 'part':
        log_text = f" -- {nick} has left {arg0}"
    elif e.type == 'nick':
        log_text = f" --  {nick} has changed his nickname to {e.target}"
    elif e.type == 'kick':
        log_text = f" -- {nick} has kicked {arg0} ({e.arguments[1]})"
    elif e.type == 'mode':
        log_text = f" -- {nick} has set mode  {' '.join(e.arguments)}"

    filename_new = time.strftime("%Y-%m-%d_%H")
    if filename_new != filename:
        file.close()
        filename = filename_new
        file = open_logfile(f"{directory}/{filename}.txt")
    file.write(f"{time.strftime('%M:%S')} {log_text}\n")
    file.flush()
