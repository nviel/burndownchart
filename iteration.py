import collections

class Iteration:
	def __init__(self):
		self.id         = '' 
		self.startDate  = ''
		self.finishDate = ''
		self.statsFileName = ''
		self.duration   = 0       # duree de l'itération en jour calendaire
		self.stats      = []      # [(N° du jour, charge restante), (,)..]
		
		# lecture de la configuration des itérations.
		confFile = open("iteration.conf",'r')
		for line in confFile:
			# traitement des commentaires unilignes
			comPos = line.find('#')
			if (comPos != -1):
				line = line[:comPos]
			line = line.strip()

			t = line.split()
			if len(t) == 3:
				(self.id, self.startDate, self.finishDate) = t
				#print("["+self.id+"]["+ self.startDate+"]["+ self.finishDate+"]")
		confFile.close()
		self.statFileName = "../" + self.id + ".stat"
		self.duration = str2day(self.finishDate) - str2day(self.startDate) + 1
		
		# chargement de l'historique de l'itération
		loadStats()

	#------------------------------------------------------------------------------
	def __str__(self):
		s = "itération [" + self.id         + "]\n"
		s+= "départ ["    + self.startDate  + "]\n" 	
		s+= "fin ["       + self.finishDate + "]\n"
		return s

	# enregistre une nouvelle charge dans les stats de l'itération
	#------------------------------------------------------------------------------
	def logNewCharge(self, charge):
		statFile = open(self.statFileName,'a')
		statFile.write(str(date.today()) + "\t" + str(charge) + '\n')
		statFile.close()
		loadStats()

	# entree: une chaine du type "aaaa-mm-jj"
	# retourne le nombre de jour depuis le 01-01-01
	#------------------------------------------------------------------------------
	def str2day(s_date):
		t = map(int,s_date.split('-'))
		return date(t[0],t[1],t[2]).toordinal()


	# charge les enregistrements de l'itération dans un dictionnaire ordonné.
	#------------------------------------------------------------------------------
	def loadStats(self):
		stats = {}
		t0 = str2day(sprint_start)
		try: 
			f  = open(self.statsFileName,"r")
		except:
			print("aucun enregistrement existant pour l'itération courrante")
			return {}
		
		for line in f:
			line = line.strip()
			if len(line) == 0: continue
			(s_date, val) = line.split()
			t = str2day(s_date) - t0
			if t < 0 or t > self.duration:
				continue
			stats[t] = float(val)
		self.stats = sorted(stats.items())
		f.close()

