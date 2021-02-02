#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# pylint: disable=unused-argument
import inspect
import sys
import random
import re

import sqlalchemy.exc

import database
import duckduckgo
from util import paren,strip_margin

errmsg = 'Kit mit hogy?'
autherror = 'Nem-nem.'
argerror = '???'


def cmd_ddg(self, nick, args, admin):
    """Használat: !ddg query"""
    if not args:
        return self.cmd_help(nick, 'ddg', admin)
    return duckduckgo.search(args)


def cmd_choice(self, nick, args, admin):
    """Véletlenszerűen választ a felsorolt lehetőségek közül.
       Használat: !choice lehetőség1, lehetőség2, .."""
    if not args:
        return self.cmd_help(nick, 'choice', admin)
    return random.choice(args.split(",")).strip()


def cmd_kocka(self, nick, args, admin):
    """Dob egy n oldalú kockával. Használat: !kocka n"""
    try:
        if len(args) > 10:
            return argerror
        if int(args) == 2:
            return 'Loli' if random.random() > 0.5 else 'Feri'
        return str(random.randint(1, int(args)))
    except ValueError:
        return 'Te mit tesa?'


def sed_common(_, nick, args, get_hist, get_help, format_msg):
    args = args.split(' ')
    hist_idx = 0
    if len(args) > 1 and args[0].startswith('-') and len(args[0]) > 1:
        hist_idx = args[0]
        hist_idx = abs(int(hist_idx))
        hist_idx -= 1
        hist_idx = 0 if hist_idx < 0 else hist_idx
        args = args[1:]
    sed = ' '.join(args) # az 's/pat/repl/' resz
    if not sed.startswith('s'):
        return get_help()
    try:
        hist = get_hist(hist_idx)
    except ValueError:
        return "Nem."
    split_ch = sed[1]
    tmp = sed.split(split_ch)
    pattern, repl = tmp[1], tmp[2] # skip az 's't
    flags = tmp[3] if len(tmp) >= 4 else ''
    count = 0
    iflag = 0
    if 'i' in flags: # case-insensitive
        iflag = re.IGNORECASE
    if 'g' not in flags: # nem global
        count = 1
    return format_msg(nick, pattern, repl, hist, iflag, count)[:512]


def cmd_sed(self, nick, args, admin):
    """sed. Használat: !sed (-idx) s/regex/repl/"""
    def format_msg(nick, pattern, repl, hist, iflag, count):
        return '%s erre gondolt: %s' % (nick,
                re.sub(pattern, repl, hist, flags = iflag, count = count))

    return sed_common(self, nick, args,
                    lambda idx: self.sed_history.get_personal(nick, idx),
                    lambda: self.cmd_help(nick, 'sed', admin),
                    format_msg)


def cmd_gsed(self, nick, args, admin):
    """Global sed. Használat: !sed (-idx) s/regex/repl/"""
    def format_msg(nick, pattern, repl, hist, iflag, count):
        return '%s szerint %s erre gondolt: %s' % (nick,
                hist[0],
                re.sub(pattern, repl, hist[1], flags = iflag, count = count))

    return sed_common(self, nick, args,
                    lambda idx: self.sed_history.get_global(idx),
                    lambda: self.cmd_help(nick, 'gsed', admin),
                    format_msg)


def cmd_help(self, nick, args, admin):
    """Te mit?"""
    if not args:
        members = inspect.getmembers(sys.modules[__name__], inspect.isfunction)
        cmds = [x[0][4:] for x in members if x[0][:4] == 'cmd_']
        return 'Parancsok: ' + ', '.join(cmds)
    try:
        cmd_handler = getattr(sys.modules[__name__], 'cmd_' + args)
    except AttributeError:
        return 'Nincs ilyen parancs :C'
    else:
        if cmd_handler.__doc__:
            return strip_margin(cmd_handler.__doc__)
        return 'Nincs segítség :C'


def cmd_ping(self, nick, args, admin):
    """Pong!!!"""
    return 'Pong!'


def cmd_adduser(self, nick, args, admin):
    """Felhasználó hozzáadása. Használat: !adduser user"""
    if admin:
        if args:
            database.session.add(database.User(name=args.split()[0], is_admin=0))
            try:
                database.session.commit()
            except sqlalchemy.exc.IntegrityError:
                return 'Már létezik felhasználó ilyen névvel.'
            else:
                return args.split()[0] + ' hozzáadva!'
        else:
            return self.cmd_help(nick, 'adduser', admin)
    else:
        return autherror


def cmd_addpattern(self, nick, args, admin):
    """Hozzáad egy regex pattern-t a megadott felhasználóhoz. Használat: !addpattern user pattern"""
    if admin:
        if len(args.split()) >= 2:
            user = database.session.query(database.User).filter_by(name=args.split()[0]).all()
            if len(user) > 0:
                try:
                    user[0].patterns.append(database.Pattern(pattern=' '.join(args.split()[1:])))
                except:
                    # traceback.print_exc()
                    pass
                try:
                    database.session.commit()
                except sqlalchemy.exc.IntegrityError:
                    return 'Ez a pattern már hozzá van rendelve ehhez a felhasználóhoz.'
                else:
                    return ' '.join(args.split()[1:]) + ' hozzáadva!'
            else:
                return 'Nincs ilyen nevű felhasználó!'
        else:
            return self.cmd_help(nick, 'addpattern', admin)
    else:
        return autherror


def cmd_patterns(self, nick, args, admin):
    """Felhasználóhoz tartozó patternek listázása. E.g.: !patterns user"""
    if admin:
        patterns = []
        for user in database.session.query(database.User):
            if any(re.search(pattern.pattern, nick, flags=re.IGNORECASE)
                    for pattern in user.patterns):
                patterns = [p.pattern for p in user.patterns]
                return ','.join(patterns)
    else:
        return autherror


def cmd_addwelcome(self, nick, args, admin):
    """Hozzáad egy köszöntő üzenetet a megadott felhasználóhoz.
        Használat: !addwelcome user welcome"""
    if admin:
        if len(args.split()) >= 2:
            user = database.session.query(database.User).filter_by(name=args.split()[0]).all()
            if len(user) > 0:
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
            return self.cmd_help(nick, 'addwelcome', admin)
    else:
        return autherror




def cmd_rmuser(self, nick, args, admin):
    """Felhasználó törlése. Használat: !rmuser user"""
    if admin:
        if args:
            user = database.session.query(database.User).filter_by(name=args.split()[0]).all()
            if len(user) > 0:
                database.session.delete(user[0])
                database.session.commit()
                return args.split()[0] + ' törölve!'
            return 'Nincs ilyen nevű felhasználó!'
        else:
            return self.cmd_help(nick, 'rmuser', admin)
    else:
        return autherror


def cmd_rmpattern(self, nick, args, admin):
    """Pattern törlése. Használat: !rmpattern user pattern"""
    if admin:
        if args:
            pattern = database.session.query(database.Pattern).filter(
                database.Pattern.pattern == ' '.join(args.split()[1:]),
                database.Pattern.user.has(name=args.split()[0])).all()
            if len(pattern) > 0:
                database.session.delete(pattern[0])
                database.session.commit()
                return ' '.join(args.split()[1:]) + ' törölve!'
            return 'Nincs ilyen nevű felhasználó/pattern páros!'
        else:
            return self.cmd_help(nick, 'rmpattern', admin)
    else:
        return autherror


def cmd_rmwelcome(self, nick, args, admin):
    """Üdvözlet törlése. Használat: !rmwelcome user pattern"""
    if admin:
        if args:
            welcome = database.session.query(database.Welcome).filter(
                database.Welcome.welcome == ' '.join(args.split()[1:]),
                database.Welcome.user.has(name=args.split()[0])).all()
            if len(welcome) > 0:
                database.session.delete(welcome[0])
                database.session.commit()
                return ' '.join(args.split()[1:]) + ' törölve!'
            return 'Nincs ilyen nevű felhasználó/üdvözlet páros!'
        else:
            return self.cmd_help(nick, 'rmwelcome', admin)
    else:
        return autherror


def cmd_admin(self, nick, args, admin):
    """Megállapítja az erőszintedet. Használat: !admin"""
    return 'Yes yes!' if admin else 'Nope :C'


def cmd_seen(self, nick, args, admin):
    """Használat: !seen nick"""
    user_seen = list(filter(lambda x: re.search(args, x.nick),
                       database.session.query(database.Seen).all()))
    if user_seen:
        seen = user_seen[0]
        if seen.reason == 'quit':
            return (seen.nick +
                    ' legutóbb ekkor volt online: ' +
                    str(seen.time) +
                    ' (kilépett: ' +
                    seen.args + ')')
        if seen.reason == 'part':
            return (seen.nick +
                    ' legutóbb ekkor volt online: ' +
                    str(seen.time) +
                    ' (elhagyta a csatornát' +
                    (': ' + seen.args + ')' if seen.args else ')'))
        if seen.reason == 'nick':
            return (seen.nick +
                    ' legutóbb ekkor volt online: ' +
                    str(seen.time) +
                    ' (nicket váltott: ' +
                    seen.args + ')')
        return (seen.nick +
                ' legutóbb ekkor volt online: ' +
                str(seen.time) +
                paren(seen.args.split()[0] + ' kirúgta: ' +
                        ' '.join(seen.args.split()[1:])))
    return f"{args} nem járt erre."


def cmd_beer(self, nick, args, admin):
    if not args:
        return errmsg
    return f"{args}: {nick} meghívott egy sörre!"


def cmd_random(self, nick, args, admin):
    if not args:
        return errmsg
    part1 = [u'kurvára', u'alattomos módon', u'rejtélyesen',
             u'mocskosul', u'önzetlenül', u'udvariasan',
             u'humánusan', u'sunyin', u'álnokmód',
             u'galád módon', u'álszentül', u'titokzatosan',
             u'sejtelmes módon', u'angyali technikával',
             u'jámbor szeretettel', u'barátságosan', u'csábosan',
             u'lendületből', u'háromszor', u'véletlenül',
             u'hirtelen felindulásból', u'hangosan']
    part2 = [u'fülön', u'taknyon', u'vaginán', u'pocaklakón',
             u'tarsolyon', u'tenyéren', u'pofán', u'arcon',
             u'lábon', u'seggen', u'ujjhegyen', u'hajon',
             u'fejen', u'makkon', u'lábujjon', u'könyökön', u'szemen',
             u'orron', u'nyelven', u'nyálon', u'homlokon',
             u'öklön', u'bokán', u'fültövön', u'hónaljba']
    part3 = [u'erőszakolt', u'öklözött', u'hányt',
             u'térdelt', u'zsályázott', u'szart',
             u'fosott', u'csókolt', u'maszturbált',
             u'toszott', u'nyalt', u'ölelt',
             u'ütött', u'köpött', u'rúgott',
             u'faszozott', u'vert', u'orrolt',
             u'fejelt', u'nyelvelt', u'hasalt',
             u'pofozott', u'kúrt', 'harapott']
    r1 = random.choice(part1)
    r2 = random.choice(part2)
    r3 = random.choice(part3)
    return f"{args}: {nick} {r1} {r2} {r3}!"


def cmd_brohoof(self, nick, args, admin):
    if not args:
        return errmsg
    return f"{args} /)(\\ {nick}"


def cmd_bulimeghivas(self, nick, args, admin):
    if not args:
        return errmsg
    return f"{args}: {nick} meghívott a következő bulijába!"


def cmd_fuck(self, nick, args, admin):
    if not args:
        return errmsg
    return f"{args}: {nick} kegyelmet nem ismerve, ordasmód megkúrt!"


def cmd_hug(self, nick, args, admin):
    if not args:
        return errmsg
    return f"{args}: {nick} megölelt!"


def cmd_lick(self, nick, args, admin):
    if not args:
        return errmsg
    return f"{args} : {nick} alattomos módon pofánnyalt!"


def cmd_pacsi(self, nick, args, admin):
    if not args:
        return errmsg
    return f"{args} o/\\o {nick}"

def cmd_heil(self, nick, args, admin):
    return strip_margin(f"""Erőt egészséget kíván nemzetünk legnagyobb formátumú államférfijának,
        |országunk bölcs miniszterelnökének, Vitéz Al- és Felcsúti Orbán Viktornak
        |alázatos szolgája, {nick}! Heil Viktor!""")

def cmd_tea(self, nick, args, admin):
    if not args:
        return errmsg
    return f"{args} : {nick} kiöntötte a lelkét a /t/eádba."


def cmd_summon(self, nick, args, admin):
    """Megidézheted akár azt is aki online."""
    if not args:
        return errmsg
    if args in ['ercsi', 'erendis', 'Erendis']:
        return 'Nem.'
    if random.random() > 0.5:
        return f"{args} hamarosan feltűnik!"
    return f"{args} megidézése kudarcba fulladt."

def cmd_vaccpaor(self, nick, args, admin):
    """angol -> magyar fordítás. Használat: !vaccpaor [kifejezés]"""
    return 'throw new NotImplementedException'

def cmd_garoi(self, nick, args, admin):
    """garoi fordító. Használat: !garoi [kifejezés]"""
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
    text = args.lower()
    for _f, _t in rules:
        text = text.replace(_f, _t)
    return text.lower()
