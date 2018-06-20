import collections

def should_ignore(message):
    return message.startswith('s/') or message.startswith("!") or message.startswith("?")

class SedHistory:
    def __init__(self):
        self.personal_history = {} # nick -> deque(msg) map
        self.global_history = collections.deque(maxlen = 15) # (nick, msg) tuples

    def update(self, nick, message):
        if should_ignore(message):
            return
        if not nick in self.personal_history:
            self.personal_history[nick] = collections.deque(maxlen = 5)
        self.personal_history[nick].appendleft(message)
        self.global_history.appendleft((nick, message))

    def get_personal(self, nick, hist_idx):
        hist = self.personal_history.get(nick, None)
        if not hist or hist_idx >= len(hist):
            raise ValueError
        return hist[hist_idx]

    def get_global(self, hist_idx):
        if hist_idx >= len(self.global_history):
            raise ValueError
        return self.global_history[hist_idx]
