#! /usr/bin/env python

import irc.bot
import irc.strings

import log
import commands


class LulzBot(irc.bot.SingleServerIRCBot):
    def __init__(self):
        irc.bot.SingleServerIRCBot.__init__(self, [("irc.freenode.net", 6667)], "LulzBot", "LulzBot")
        self.channel = '#lulztest'
        commands.bot = self

    # noinspection PyUnusedLocal
    @staticmethod
    def on_nicknameinuse(c, e):
        c.nick(c.get_nickname() + "_")

    # noinspection PyUnusedLocal
    def on_welcome(self, c, e):
        c.join(self.channel)

    # noinspection PyUnusedLocal
    def on_privmsg(self, c, e):
        self.do_command(e)

    # noinspection PyUnusedLocal
    def on_pubmsg(self, c, e):
        log.log(e)
        if e.arguments[0][0] == '!':
            self.do_command(e)

    # noinspection PyUnusedLocal
    @staticmethod
    def on_join(c, e):
        log.log(e)

    # noinspection PyUnusedLocal
    @staticmethod
    def on_quit(c, e):
        log.log(e)

    # noinspection PyUnusedLocal
    @staticmethod
    def on_part(c, e):
        log.log(e)

    # noinspection PyUnusedLocal
    @staticmethod
    def on_nick(c, e):
        log.log(e)

    # noinspection PyUnusedLocal
    def on_kick(self, c, e):
        log.log(e)
        if e.arguments[0] == c.get_nickname():
            self.connection.join(self.channel)

    # noinspection PyUnusedLocal
    @staticmethod
    def on_mode(c, e):
        log.log(e)

    def say(self, target, message):
        for i in range(0, len(message), 350):
            self.connection.privmsg(target, '\x0305' + message[i:i + 350])

    def say_public(self, message):
        self.say(self.channel, message)

    def reply(self, e, message):
        if e.type == 'privmsg':
            self.say(e.source.nick, message)
        else:
            self.say_public(message)

    def do_command(self, e):
        command = e.arguments[0].split()[0].lower()
        arguments = e.arguments[0].split()[1:]
        if command[0] == '!':
            command = command[1:]
        try:
            cmd_handler = getattr(commands, command)
        except AttributeError:
            pass
        else:
            self.reply(e, cmd_handler(e.arguments[0].split()[1:]))


def main():
    bot = LulzBot()
    bot.start()

if __name__ == "__main__":
    main()