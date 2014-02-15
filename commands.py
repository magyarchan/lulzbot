import inspect
import sys

import sqlalchemy.exc

import database


def cmd_help(args, admin):
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


def cmd_ping(args, admin):
    """Pong!!!"""
    return 'Pong!'


def cmd_adduser(args, admin):
    """Felhasználó hozzáadása. Használat: !adduser user"""
    if admin:
        if args:
            database.session.add(database.User(name=args.split()[0]))
            try:
                database.session.commit()
            except sqlalchemy.exc.IntegrityError:
                return 'Már létezik felhasználó ilyen névvel.'
            else:
                return args.split()[0] + ' hozzáadva!'
        else:
            return cmd_help('adduser', admin)
    else:
        return 'Nem-nem.'


def cmd_addpattern(args, admin):
    """Hozzáad egy regex pattern-t a megadott felhasználóhoz. Használat: !addpattern user pattern"""
    if admin:
        if len(args.split()) >= 2:
            user = database.session.query(database.User).filter_by(name=args.split()[0]).all()
            if len(user):
                user[0].patterns.append(database.Pattern(pattern=' '.join(args.split()[1:])))
                try:
                    database.session.commit()
                except sqlalchemy.exc.IntegrityError:
                    return 'Ez a pattern már hozzá van rendelve ehhez a felhasználóhoz.'
                else:
                    return ' '.join(args.split()[1:]) + ' hozzáadva!'
            else:
                return 'Nincs ilyen nevű felhasználó!'
        else:
            return cmd_help('addpattern', admin)
    else:
        return 'Nem-nem.'


def cmd_addwelcome(args, admin):
    """Hozzáad egy köszöntő üzenetet a megadott felhasználóhoz. Használat: !addwelcome user welcome"""
    if admin:
        if len(args.split()) >= 2:
            user = database.session.query(database.User).filter_by(name=args.split()[0]).all()
            if len(user):
                user[0].welcomes.append(database.Welcome(welcome=' '.join(args.split()[1:])))
                try:
                    database.session.commit()
                except sqlalchemy.exc.IntegrityError:
                    return 'Ez a köszöntés már hozzá van rendelve ehhez a felhasználóhoz.'
                else:
                    return ' '.join(args.split()[1:]) + ' hozzáadva!'
            else:
                return 'Nincs ilyen nevű felhasználó!'
        else:
            return cmd_help('addwelcome', admin)
    else:
        return 'Nem-nem.'


def cmd_rmuser(args, admin):
    """Felhasználó törlése. Használat: !rmuser user"""
    if admin:
        if args:
            user = database.session.query(database.User).filter_by(name=args.split()[0]).all()
            if len(user):
                database.session.delete(user[0])
                database.session.commit()
                return args.split()[0] + ' törölve!'
            else:
                return 'Nincs ilyen nevű felhasználó!'
        else:
            return cmd_help('rmuser', admin)
    else:
        return 'Nem-nem.'


def cmd_rmpattern(args, admin):
    """Pattern törlése. Használat: !rmpattern user pattern"""
    if admin:
        if args:
            pattern = database.session.query(database.Pattern).filter(
                database.Pattern.pattern.__eq__(' '.join(args.split()[1:])),
                database.Pattern.user.has(name=args.split()[0])).all()
            if len(pattern):
                database.session.delete(pattern[0])
                database.session.commit()
                return ' '.join(args.split()[1:]) + ' törölve!'
            else:
                return 'Nincs ilyen nevű felhasználó/pattern páros!'
        else:
            return cmd_help('rmpattern', admin)
    else:
        return 'Nem-nem.'


def cmd_rmwelcome(args, admin):
    """Üdvözlet törlése. Használat: !rmwelcome user pattern"""
    if admin:
        if args:
            welcome = database.session.query(database.Welcome).filter(
                database.Welcome.welcome.__eq__(' '.join(args.split()[1:])),
                database.Welcome.user.has(name=args.split()[0])).all()
            if len(welcome):
                database.session.delete(welcome[0])
                database.session.commit()
                return ' '.join(args.split()[1:]) + ' törölve!'
            else:
                return 'Nincs ilyen nevű felhasználó/üdvözlet páros!'
        else:
            return cmd_help('rmwelcome', admin)
    else:
        return 'Nem-nem.'


def cmd_admin(args, admin):
    """Megállapítja az erőszintedet. Használat: !admin"""
    return 'Yes yes!' if admin else 'Nope :C'


def cmd_garoi(args, admin):
    rules = [
        ('ddzs', 'CCS'),
        ('dzs', 'CS'),
        ('ccs', 'DDZS'),
        ('ddz', 'TSSZ'),
        ('ggy', 'TTY'),
        ('lly', 'JJ'),
        ('ssz', 'ZZ'),
        ('tty', 'GGY'),
        ('zzs', 'SS'),
        ('dj', 'gy'),
        ('sz', 'Z'),
        ('ch', 'cs'),
        ('ts', 'cs'),
        ('cs', 'DZS'),
        ('dz', 'TSZ'),
        ('gy', 'TY'),
        ('ly', 'J'),
        ('cc', 'TSSZ'),
        ('ty', 'GY'),
        ('zs', 'S'),
        ('jj', 'LLY'),
        ('zz', 'SSZ'),
        ('b', 'P'),
        ('c', 'TSZ'),
        ('d', 'T'),
        ('f', 'V'),
        ('g', 'K'),
        ('j', 'LY'),
        ('k', 'G'),
        ('p', 'B'),
        ('s', 'ZS'),
        ('s', 'ZZS'),
        ('t', 'D'),
        ('v', 'F'),
        ('z', 'SZ'),
        ('x', 'GZ')]
    if not args:
        return 'Mid agarz?'
    else:
        text = args.lower()
        for _f, _t in rules:
            text = text.replace(_f, _t)
        return text.lower()