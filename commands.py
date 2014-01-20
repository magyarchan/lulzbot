import inspect
import sys


def cmd_help(args):
    """Te mit?"""
    if len(args) == 0:
        return 'Parancsok: ' + ', '.join([x[0][4:] for x in inspect.getmembers(sys.modules[__name__], inspect.isfunction) if x[0][:4] == 'cmd_'])
    else:
        try:
            cmd_handler = getattr(sys.modules[__name__], 'cmd_' + args[0])
        except AttributeError:
            return 'Nincs ilyen parancs :C'
        else:
            if cmd_handler.__doc__:
                return cmd_handler.__doc__
            else:
                return 'Nincs segítség :C'


def cmd_ping(args):
    """Pong!!!"""
    return 'Pong!'