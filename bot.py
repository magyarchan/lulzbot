#! /usr/bin/env python

import re
import time
import irc.bot
import irc.strings

import log
import commands
import urlparser


class LulzBot(irc.bot.SingleServerIRCBot):
    def __init__(self):
        irc.bot.SingleServerIRCBot.__init__(self, [("adams.freenode.net", 6667)], "LulzBot", "LulzBot")
        self.channel = '#lulztest'
        commands.bot = self

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e)

    def on_pubmsg(self, c, e):
        log.log(e)
        message = e.arguments[0]
        if message[0] == '!':
            self.do_command(e)
        # TODO: ezt itt lent kiegesziteni egy whitelisttel, amit egy adatbazis tablabol olvasunk befele
        for url in message.split():
            title = urlparser.get_title(url)
            if title:
                self.say_public(title)

    def on_join(self, c, e):
        log.log(e)

    def on_quit(self, c, e):
        log.log(e)

    def on_part(self, c, e):
        log.log(e)

    def on_nick(self, c, e):
        log.log(e)

    def on_kick(self, c, e):
        log.log(e)
        if e.arguments[0] == c.get_nickname():
            self.connection.join(self.channel)

    def on_mode(self, c, e):
        log.log(e)

    def say(self, target, message):
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
        arguments = ' '.join(e.arguments[0].split()[1:])
        if command[0] == '!':
            command = command[1:]
        if '(' in command:
            self.reply(e, 'There is no problem sir.')
        else:
            arguments = re.sub(r'\\(.)', '\\1', arguments).replace('\\', '\\\\').replace('\'', '\\\'')
            arguments = re.sub(r'!\(([^\s\)]*) ?', '\'+commands.cmd_\\1(\'', arguments)
            while re.search(r'[^\\]\)', arguments):
                arguments = re.sub(r'([^\\])\)', '\\1\'' + chr(0xE000) + '+\'', arguments)
            arguments = arguments.replace(chr(0xE000), ')')
            # noinspection PyBroadException
            try:
                response = eval('commands.cmd_' + command + '(\'' + arguments + '\')')
            except:
                self.reply(e, 'There is no problem sir.')
            else:
                self.reply(e, response)


def main():
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