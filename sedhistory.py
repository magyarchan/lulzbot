import collections

# idealis esetben ezek az ircbot class fieldje lennenek, de sajnos
# a cmd_* fuggvenyek nem kapjak meg a bot instancet

# nick -> deque(msg)
_history = {}
# deque((nick, msg))
_global_history = collections.deque(maxlen = 15)

def _filter(message):
    return message.startswith('s/') or message.startswith("!")

def _update_personal(nick, message):
    if not nick in _history:
        _history[nick] = collections.deque(maxlen = 5)
    _history[nick].appendleft(message)

def _update_global(nick, message):
    _global_history.appendleft((nick, message))

def update(nick, message):
    if not _filter(message):
        _update_personal(nick, message)
        _update_global(nick, message)

def get_personal(nick):
    return _history.get(nick, None)

def get_global():
    return _global_history
