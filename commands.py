import inspect
import sys


def cmd_help(args):
    """Te mit?"""
    if not args:
        return 'Parancsok: ' + ', '.join(
            [x[0][4:] for x in inspect.getmembers(sys.modules[__name__], inspect.isfunction) if x[0][:4] == 'cmd_'])
    else:
        try:
            cmd_handler = getattr(sys.modules[__name__], 'cmd_' + args)
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


def cmd_garoi(args):
    rules = [
        ('ddzs', 'CCS'),
        ('dzs',  'CS'),
        ('ccs',  'DDZS'),
        ('ddz',  'TSSZ'),
        ('ggy',  'TTY'),
        ('lly',  'JJ'),
        ('ssz',  'ZZ'),
        ('tty',  'GGY'),
        ('zzs',  'SS'),
        ('dj',   'gy'),
        ('sz',   'Z'),
        ('ch',   'cs'),
        ('ts',   'cs'),
        ('cs',   'DZS'),
        ('dz',   'TSZ'),
        ('gy',   'TY'),
        ('ly',   'J'),
        ('cc',   'TSSZ'),
        ('ty',   'GY'),
        ('zs',   'S'),
        ('jj',   'LLY'),
        ('zz',   'SSZ'),
        ('b',    'P'),
        ('c',    'TSZ'),
        ('d',    'T'),
        ('f',    'V'),
        ('g',    'K'),
        ('j',    'LY'),
        ('k',    'G'),
        ('p',    'B'),
        ('s',    'ZS'),
        ('s',    'ZZS'),
        ('t',    'D'),
        ('v',    'F'),
        ('z',    'SZ'),
        ('x',    'GZ')]
    if not args:
        return 'Mid agarz?'
    else:
        text = args.lower()
        for _f, _t in rules:
            text = text.replace(_f, _t)
        return text.lower()