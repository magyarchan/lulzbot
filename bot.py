#!/usr/bin/env python

import re
import sys
import time
import random
import datetime

import irc.client
import irc.bot
import irc.strings

import log
import commands
import urlparser
import database
from config import Config


class LulzBot(irc.bot.SingleServerIRCBot):
    def __init__(self):
        configFile = "development.conf"
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
        if message[0] == '!':
            self.do_command(e)
        # TODO: ezt itt lent kiegesziteni egy whitelisttel, amit egy adatbazis tablabol olvasunk befele
        for url in message.split():
            if ('http://' in url or 'https://' in url):
                print('trying to parse: ' + url)
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
                self.say_public('Szervusz ismeretlen! :/')

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
        command = e.arguments[0].split()[0].lower()
        if len(command) < 2:
            return
        arguments = ' '.join(e.arguments[0].split()[1:])
        if command[0] == '!':
            command = command[1:]
        if '(' in command:
            self.reply(e, 'There is no problem sir.')
        else:
            arguments = re.sub(r'\\(.)', '\\1', arguments).replace('\\', '\\\\').replace('\'', '\\\'')
            arguments = re.sub(r'!\(([^\s\)]*) ?', '\'+commands.cmd_\\1(\'' + e.source.nick + '\',\'', arguments)
            while re.search(r'[^\\]\)', arguments):
                arguments = re.sub(r'([^\\])\)', '\\1\'' + chr(0xE000) + '+\'', arguments)
            arguments = arguments.replace(chr(0xE000), ',' +
                                                       self.isOperator(e.source.nick) + ')')
            # noinspection PyBroadException
            try:
                response = eval('commands.cmd_' + command + '(\'' + e.source.nick + '\',\'' + arguments + '\',' +
                                self.isOperator(e.source.nick) + ')')
            except:
                self.reply(e, 'There is no problem sir.')
            else:
                self.reply(e, response)

    def isOperator(self, nick):
        chanop = self.channels[self.channel].is_oper(nick)
        dbop = False
        for user in database.session.query(database.User):
            if any(re.search(pattern.pattern, nick, flags=re.IGNORECASE) for pattern in user.patterns):
                dbop = bool(user.is_admin)
        return str(chanop or dbop)

def main():
    database.initialize()
    bot = LulzBot()
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
