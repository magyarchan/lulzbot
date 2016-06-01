import random

class ufgame(object):
	running = None ##bool
	players = None ##list of strings
	dead = None ##list of ints
	detective = None ##int
	mafia = None ##list of ints
	is_night = None ##bool
	infect_votes = None ##dictionary with keys and values of ints
	has_detected = None ##bool
	votes = None ##dictionary with keys and values of ints

	def reset(self): ##ok, tested
		##print "RESET CALLED"
		result = []
		if self.running:
			if len(self.mafia) == 2:
				result += [("c", u'A szőrgecyk '+self.players[self.mafia[0]]+u' és '+self.players[self.mafia[1]]+u', a nigger pedig '+self.players[self.detective]+u' volt.')]
			else:
				result += [("c", u'A szőrgecy '+self.players[self.mafia[0]]+u', a nigger pedig '+self.players[self.detective]+u' volt.')]
		self.running = False
		self.players = []
		self.dead = []
		self.detective = None
		self.mafia = []
		self.is_night = False
		self.infect_votes = {}
		self.has_detected = False
		self.votes = {}
		return result + [("c", u'A játék alaphelyzetbe állt.')]

	def __init__(self):
		self.reset()

	def num_mafia(self): ##ok, tested
		##print "NUM_MAFIA CALLED"
		result = 0
		for i in self.mafia:
			if not i in self.dead:
				result += 1
		return result

	def new(self, player): ##ok, tested, hooked up
		##print "NEW CALLED, PLAYER="+str(player)
		if len(self.players):
			if not self.running:
				return [("p", self.players[0]+u' már kezdeményezett egy játékot!')]
			else:
				return [("p", u'Már folyamatban van egy játék, kérlek várd ki a végét!')]
		else:
			self.players.append(player)
			return [("c", self.players[0]+u' új játékot kezdeményezett!')]

	def list(self): ##ok, tested
		##print "LIST CALLED"
		return [("c", u'Csatlakozott játékosok: '+u', '.join(self.players))]

	def join(self, player): ##ok, tested, hooked up
		##print "JOIN CALLED, PLAYER="+str(player)
		if not len(self.players):
			return self.new(player)
		elif self.running:
			return [("p", u'Már folyamatban van egy játék, kérlek várd ki a végét!')]
		elif player in self.players:
			return [("p", u'Már beléptél a játékba!')]
		else:
			self.players.append(player)
			return [("c", self.players[-1]+u' csatlakozott a játékhoz!')] + self.list()

	def check(self): ##ok, tested
		##print "CHECK CALLED"
		if (len(self.mafia) == 1 and self.mafia[0] in self.dead) or (self.mafia[0] in self.dead and self.mafia[1] in self.dead):
			return [("c", u'Meghaltak a szőrgecyk, az enberek nyertek!')]+self.reset()
		elif 2 * self.num_mafia() >= len(self.players) - len(self.dead):
			return [("c", u'Egyenlő számú enber és szőrgecy maradt, a szőrgecyk nyertek!')]+self.reset()
		return []

	def kill(self, player): ##ok, tested
		##print "KILL CALLED, PLAYER="+str(player)
		if not player in self.players or self.players.index(player) in self.dead:
			return [("p", u'u wot m8')]
		self.dead.append(self.players.index(player))
		if self.players.index(player) == self.detective:
			return [("c", player+u' meghalt! Boncolása után kiderült, hogy nigger volt!')]+self.check()
		elif self.players.index(player) in self.mafia:
			return [("c", player+u' meghalt! Boncolása után kiderült, hogy szőrgecy volt!')]+self.check()
		else:
			return [("c", player+u' meghalt! Boncolása után kiderült, hogy egy átlagos ircező volt!')]+self.check()

	def leave(self, player): ##ok, tested, hooked up
		##print "LEAVE CALLED, PLAYER="+str(player)
		if self.running:
			return self.kill(player)
		elif not self.players:
			return [("p", u'Nincs kezdeményezett játék!')]
		elif not player in self.players:
			return [("p", u'Eddig sem voltál a játékban!')]
		else:
			if len(self.players) == 1:
				return [("c", player+u' kilépett a játékból!')]+self.reset()
			elif player==self.players[0]:
				result = self.players[0]
				del self.players[0]
				return [("c", result+u' kilépett a játékból! Ő volt a kezdeményező, mostantól '+self.players[0]+u' veszi át a szerepét!')] + self.list()
			else:
				result = player
				del self.players[self.players.index(player)]
				return [("c", result+u' kilépett a játékból')] + self.list()

	def night(self): ##ok, tested
		##print "NIGHT CALLED"
		self.is_night = True
		result = [("c", u'Éjszaka van...')]
		if len(self.mafia) > 1:
			if not self.mafia[0] in self.dead:
				result += [(self.players[self.mafia[0]], u'Te és '+self.players[self.mafia[1]]+u' vagytok a szőrgecyk! Privátban beszéljetek, majd használjátok a fertoz parancsot ugyanarra az enberre!')]
			if not self.mafia[1] in self.dead:
				result += [(self.players[self.mafia[1]], u'Te és '+self.players[self.mafia[0]]+u' vagytok a szőrgecyk! Privátban beszéljetek, majd használjátok a fertoz parancsot ugyanarra az enberre!')]
		else:
			if not self.mafia[0] in self.dead:
				result += [(self.players[self.mafia[0]], u'Te vagy a szőrgecy! Használd a fertoz parancsot!')]
		if not self.detective in self.dead:
			result += [(self.players[self.detective], u'Te vagy a nigger! Használd a latomas parancsot!')]
		return result

	def has_player(self, player):
		return player in self.players

	def start(self, player): ##ok, tested, hooked up
		##print "START CALLED, PLAYER="+str(player)
		if not self.players:
			return self.new(player)
		elif self.running:
			return [("p", u'Már folyamatban van egy játék, kérlek várd ki a végét!')]
		elif player != self.players[0]:
			return [("p", u'A játékot a kezdeményező ('+self.players[0]+u') indíthatja.')]
		elif len(self.players) < 4:
			return [("p", u'A játék indításához legalább 4 enber kell.')]
		else:
			self.running = True
			result = [("c", u'A játék elkezdődött!')]
			if len(self.players) < 8:
				roles = random.sample(range(len(self.players)), 2)
				self.detective = roles[0]
				self.mafia.append(roles[1])
			else:
				roles = random.sample(range(len(self.players)), 3)
				self.detective = roles[0]
				self.mafia.append(roles[1])
				self.mafia.append(roles[2])
			for i in range(len(self.players)):
				if not i in self.mafia and i != self.detective:
					result += [(self.players[i], u'Egy átlagos ircező vagy!')]
		return result + self.night()
	
	def check_night(self): ##ok, tested
		##print "CHECK_NIGHT CALLED"
		if len(self.infect_votes) == self.num_mafia() and (self.num_mafia() == 1 or (self.infect_votes.values()[0] == self.infect_votes.values()[1])) and (self.detective in self.dead or self.has_detected) and len(self.players):
			self.is_night = False
			return [("c", u'Eljött a reggel!')] + self.kill(self.players[self.infect_votes.values()[0]]) + [("c", u'Játékosok: ' + u', '.join(self.players)), ("c", u'Halottak: '+u', '.join([self.players[player] for player in self.dead]))]
		return []

	def stats(self):
		if len(self.players):
			if self.running:
				return [("p", u'Játékosok: ' + u', '.join(self.players)), ("p", u'Halottak: '+u', '.join([self.players[player] for player in self.dead]))]
			else:
				return [("p", u'Játékosok: ' + u', '.join(self.players))]

	def infect(self, player, target): ##ok, hooked up
		##print "INFECT CALLED, PLAYER="+str(player)+", TARGET="+str(target)
		if not self.running:
			return [("p", u'Nincs folyamatban játék!')]
		elif not player in self.players:
			return [("p", u'Nem vagy benne a játékban!')]
		elif self.players.index(player) in self.dead:
			return [("p", u'Halott vagy!')]
		elif not self.is_night:
			return [("p", u'Nincs éjszaka!')]
		elif not target in self.players:
			return [("p", u'Ez az enber nincs a játékosok között!')]
		elif self.players.index(target) in self.dead:
			return [("p", u'Ez az enber már halott!')]
		elif not self.players.index(player) in self.mafia:
			return [(player, u'Nem vagy szőrös, nem tudsz fertőzni!')]
		else:
			self.infect_votes[self.players.index(player)] = self.players.index(target)
			return [(player, u'A döntésedet elkönyveltem.')]+self.check_night()

	def detect(self, player, target): ##ok, hooked up
		##print "DETECT CALLED, PLAYER="+str(player)+", TARGET="+str(target)
		if not self.running:
			return [("p", u'Nincs folyamatban játék!')]
		elif not player in self.players:
			return [("p", u'Nem vagy benne a játékban!')]
		elif self.players.index(player) in self.dead:
			return [("p", u'Halott vagy!')]
		elif not self.is_night:
			return [("p", u'Nincs éjszaka!')]
		elif not target in self.players:
			return [("p", u'Ez az enber nincs a játékosok között!')]
		elif self.players.index(target) in self.dead:
			return [("p", u'Ez az enber már halott!')]
		elif self.players.index(player) != self.detective:
			return [(player, u'Nem vagy nigger!')]
		elif self.has_detected:
			return [(player, u'Éjjelente csak egyszer használhatod az afród!')]
		else:
			self.has_detected = True
			if self.players.index(target) in self.mafia:
				return [(player, u'Ez a személy egy szőrgecy!')]+self.check_night()
			elif self.players.index(target) == self.detective:
				return [(player, u'Igen, te vagy a nigger, de ezt eddig is tudtad!')]+self.check_night()
			else:
				return [(player, u'Ez a személy egy átlagos ircező.')]+self.check_night()

	def check_day(self): ##ok
		##print "CHECK_DAY CALLED"
		result = []
		voted = {}
		for _p, _t in self.votes.items():
			if not _t in voted.keys():
				voted[_t] = 1
			else:
				voted[_t] += 1
		for _n, _c in voted.items():
			if _c >= (len(self.players) - len(self.dead) + 1) / 2:
				result += self.kill(self.players[_n])
				break
		if self.running and result:
			result += self.night()
		return result

	def vote_information(self): ##ok
		##print "VOTE_INFORMATION CALLED"
		voted = {}
		result = u''
		for _p, _t in self.votes.items():
			if not _t in voted.keys():
				voted[_t] = 1
			else:
				voted[_t] += 1
		return [("c", u'Szavazatok: '+u', '.join(
		[self.players[_n]+u': '+unicode(_c) for _n, _c in voted.items()])+u' ('+str((len(self.players) - len(self.dead) + 1) / 2)+u' szavazat szükséges)')]

	def vote(self, player, target): ##ok, hooked up
		##print "VOTE CALLED, PLAYER="+str(player)+", TARGET="+str(target)
		if not self.running:
			return [("p", u'Nincs folyamatban játék!')]
		elif player not in self.players:
			return [("p", u'Nem vagy benne a játékban!')]
		elif self.players.index(player) in self.dead:
			return [("p", u'Halott vagy!')]
		elif self.is_night:
			return [("p", u'Nincs nappal!')]
		elif target not in self.players:
			return [("p", u'Ez az enber nincs a játékosok között!')]
		elif self.players.index(target) in self.dead:
			return [("p", u'Ez az enber már halott!')]
		else:
			self.votes[self.players.index(player)] = self.players.index(target)
			return [("c", player+u' '+target+u' megölésére szavazott.')] + self.vote_information() + self.check_day()

	def rename(self, player, newname):
		if player in self.players:
			self.players[self.players.index(player)] = newname
