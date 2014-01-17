import inspect
import sys


def help(args):
    help.help = 'Te mit?'
    if len(args) == 0:
        return 'Parancsok: ' + ', '.join([x[0] for x in inspect.getmembers(sys.modules[__name__], inspect.isfunction)])
    else:
        try:
            cmd_handler = getattr(sys.modules[__name__], args[0])
        except AttributeError:
            return 'Nincs ilyen parancs :C'
        else:
            if hasattr(cmd_handler, 'help'):
                return cmd_handler.help
            else:
                return 'Nincs segítség :C'


def ping(args):
    ping.help = 'Pong!!!'
    return 'Pong!'