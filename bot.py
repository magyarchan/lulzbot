#!/usr/bin/env python
#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import re
import sys
import time
import random
import inspect
import datetime

import irc.client
import irc.bot
import irc.strings

import log
import sed
import commands
import urlparser
import database
from config import Config


general_error = 'There is no problem sir.'

# strip !, preprocess special commands
def prepare_command(command, args, full_msg):
    if command[0] == '?':
        args = command[1:] + ' ' + args
        command = "ddg"
    elif command[0] == '!':
        command = command[1:]
    elif command.startswith("s/"):
        args = full_msg
        command = "sed"
    return command, args


def is_command(message):
    return message.startswith("?") or message.startswith("!") or message.startswith("s/")


def find_matching_paren(s, paren_idx):
    idx = paren_idx
    push = 0

    while idx < len(s):
        if s[idx] == '(':
            push += 1
        elif s[idx] == ')':
            if push == 0: # nem egy sub(ben vagyunk
                return idx
            else:
                push -= 1

        idx += 1

    return -1


def find_embed_cmd(s):
    start = s.find("!(")

    if start == -1:
        return

    start += 2
    end = find_matching_paren(s, start)

    if end == -1:
        return

    return (start, end)


class LulzBot(irc.bot.SingleServerIRCBot):
    def __init__(self):
        configFile = "dev.conf"
        if(len(sys.argv) > 1):
            configFile = sys.argv[1]
        self.config = Config(configFile)
        server = self.config.getString('irc.server')
        port = self.config.getInt('irc.port')
        name = self.config.getString('irc.name')
        channel = self.config.getString('irc.channel')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], name, name)
        self.channel = channel
        commands.bot = self
        self.sed_history = sed.SedHistory()

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e)

    def on_pubmsg(self, c, e):
        if self.config.getBoolean('irc.logging'):
            log.log(e)
        message = e.arguments[0]
        self.sed_history.update(e.source.nick, message)
        if is_command(message) and len(message) > 1 and len(''.join(set(message))) > 1:
            self.do_command(e)
        # TODO: ezt itt lent kiegesziteni egy whitelisttel, amit egy adatbazis tablabol olvasunk befele
        for url in message.split():
            if ('http://' in url or 'https://' in url):
                if('imgur' in url):
                    url = re.sub(r'.gifv?', '', url)
                #print('trying to parse: ' + url.decode('utf-8', 'ignore'))
                title = urlparser.get_title(url)
                if title:
                    self.say_public(title)

    def on_join(self, c, e):
        if self.config.getBoolean('irc.logging'):
            log.log(e)
        if e.source.nick != c.get_nickname():
            welcomes = []
            for user in database.session.query(database.User):
                if any(re.search(pattern.pattern, e.source.nick, flags=re.IGNORECASE) for pattern in user.patterns):
                    welcomes += [welcome.welcome for welcome in user.welcomes]
            if welcomes:
                self.say_public(random.choice(welcomes))
            else:
                self.say_public('Újbuzik nem tudnak háromerő :/')

    def on_quit(self, c, e):
        if self.config.getBoolean('irc.logging'):
            log.log(e)
        seen = database.session.query(database.Seen).filter_by(nick=e.source.nick).all()
        if seen:
            seen[0].time = datetime.datetime.now()
            seen[0].reason = 'quit'
            seen[0].args = e.arguments[0]
        else:
            database.session.add(
                database.Seen(time=datetime.datetime.now(), nick=e.source.nick, reason='quit', args=e.arguments[0]))
        database.session.commit()
        if len(e.source.nick) < len(c.get_nickname()) and re.search(r'^' + c.get_nickname().rstrip('_') + r'_*$',
                                                                    e.source.nick):
            c.nick(e.source.nick)

    def on_part(self, c, e):
        if self.config.getBoolean('irc.logging'):
            log.log(e)
        seen = database.session.query(database.Seen).filter_by(nick=e.source.nick).all()
        if seen:
            seen[0].time = datetime.datetime.now()
            seen[0].reason = 'part'
            seen[0].args = e.arguments[0] if e.arguments else ''
        else:
            database.session.add(
                database.Seen(time=datetime.datetime.now(), nick=e.source.nick, reason='part',
                              args=e.arguments[0] if e.arguments else ''))
        database.session.commit()

    def on_nick(self, c, e):
        if self.config.getBoolean('irc.logging'):
            log.log(e)
        seen = database.session.query(database.Seen).filter_by(nick=e.source.nick).all()
        if seen:
            seen[0].time = datetime.datetime.now()
            seen[0].reason = 'nick'
            seen[0].args = e.target
        else:
            database.session.add(
                database.Seen(time=datetime.datetime.now(), nick=e.source.nick, reason='nick', args=e.target))
        database.session.commit()

    def on_kick(self, c, e):
        if self.config.getBoolean('irc.logging'):
            log.log(e)
        seen = database.session.query(database.Seen).filter_by(nick=e.arguments[0]).all()
        if seen:
            seen[0].time = datetime.datetime.now()
            seen[0].reason = 'kick'
            seen[0].args = e.source.nick + ' ' + e.arguments[1]
        else:
            database.session.add(
                database.Seen(time=datetime.datetime.now(), nick=e.arguments[0], reason='kick',
                              args=e.source.nick + ' ' + e.arguments[1]))
        database.session.commit()
        if e.arguments[0] == c.get_nickname():
            self.connection.join(self.channel)

    def on_mode(self, c, e):
        if self.config.getBoolean('irc.logging'):
            log.log(e)

    def say(self, target, message):
        if message:
            for i in range(0, len(message), 350):
                self.connection.privmsg(target, '\x0305' + message[i:i + 350].replace('\r', '').replace('\n', ' '))

    def say_public(self, message):
        self.say(self.channel, message)

    def reply(self, e, message):
        if e.type == 'privmsg':
            self.say(e.source.nick, message)
        else:
            self.say_public(message)

    def do_command(self, e):
        # noinspection PyBroadException
        try:
            response = self.exec_command(e.source.nick, e.arguments[0])
            self.reply(e, response)
        except:
            self.reply(e, general_error )
            return ""

    def exec_command(self, nick, msg):
        start_end = find_embed_cmd(msg)

        if start_end is not None:
            start, end = start_end
            subcmd = msg[start:end]
            response = self.exec_command(nick, subcmd)
            msg = msg.replace('!(%s)' % subcmd, response)

        command = msg.split()[0].lower()
        args = ' '.join(msg.split()[1:])
        command, args = prepare_command(command, args, msg)

        handler = getattr(sys.modules["commands"], "cmd_" + command)
        response = handler(self, nick, args, self.is_operator(nick))
        return response

    def is_operator(self, nick):
        chanop = self.channels[self.channel].is_oper(nick)
        dbop = False
        # for user in database.session.query(database.User):
        #     if any(str.lower(pattern.pattern) in pattern for pattern in user.patterns):
        #         print(user, bool(user.is_admin))
        #         dbop = bool(user.is_admin)

        return chanop or dbop

def main():
    bot = LulzBot()
    database.initialize(bot.config)
    bot.connection.set_keepalive(300)
    connected = False
    while not connected:
        try:
            bot.start()
        except irc.client.ServerConnectionError:
            time.sleep(60)
        else:
            connected = True


if __name__ == "__main__":
    main()
