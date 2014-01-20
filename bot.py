#! /usr/bin/env python

import re
import irc.bot
import irc.strings

import log
import commands
import urlparser


class LulzBot(irc.bot.SingleServerIRCBot):
    def __init__(self):
        irc.bot.SingleServerIRCBot.__init__(self, [("irc.freenode.net", 6667)], "LulzBot", "LulzBot")
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
        cnt = 0
        escape = False
        for char in arguments:
            if char == '\\':
                escape = not escape
            elif char == '{' and not escape:
                cnt += 1
            elif char == '}' and not escape:
                cnt -= 1
            else:
                escape = False
            if cnt < 0:
                break
        if cnt != 0:
            self.reply(e, 'Páratlan zárójelek!')
        else:
            while re.search(r'^{', arguments) or re.search(r'[^\\]{', arguments):
                if re.search(r'[^\\]({)', arguments):
                    match = None
                    for match in re.finditer(r'[^\\]({)', arguments):
                        pass
                    if match:
                        i1 = match.start(1)
                    else:
                        i1 = 0
                else:
                    i1 = 0
                match = re.search(r'[^\\](})', arguments[i1:])
                i2 = i1 + match.start(1)
                if i1 + 1 == i2:
                    self.reply(e, 'Hogy mit?')
                    return
                subcommand = arguments[i1 + 1:i2].split()[0].lower()
                subarguments = ' '.join(arguments[i1 + 1:i2].split()[1:]).\
                    replace('\\{', '{').replace('\\}', '}').replace('\\\\', '\\')
                try:
                    cmd_handler = getattr(commands, 'cmd_' + subcommand)
                except AttributeError:
                    self.reply(e, 'Hogy mit?')
                    return
                else:
                    subresult = cmd_handler(subarguments).replace('\\', '\\\\').replace('{', '\\{').replace('}', '\\}')
                    arguments = arguments[:i1] + subresult + arguments[i2 + 1:]
            try:
                cmd_handler = getattr(commands, 'cmd_' + command)
            except AttributeError:
                self.reply(e, 'Hogy mit?')
            else:
                self.reply(e, cmd_handler(arguments.replace('\\{', '{').replace('\\}', '}').replace('\\\\', '\\')))


def main():
    bot = LulzBot()
    bot.start()


if __name__ == "__main__":
    main()