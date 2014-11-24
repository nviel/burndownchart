import collections
from datetime import date

class Iteration:
	def __init__(self):
		self.id         = '' 
		self.start_date  = ''
		self.end_date = ''
		self.stats_file_name = ''
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
				(self.id, self.start_date, self.end_date) = t
				#print("["+self.id+"]["+ self.start_date+"]["+ self.end_date+"]")
		confFile.close()
		self.stats_file_name = self.id + ".stat"
		self.duration = self.str2day(self.end_date) - self.str2day(self.start_date) + 1
		
		# chargement de l'historique de l'itération
		self.load_stats()

	#------------------------------------------------------------------------------
	def __str__(self):
		s = "itération ["     + self.id         + "]\n"
		s+= "départ ["        + self.start_date  + "]\n" 	
		s+= "fin ["           + self.end_date + "]\n"
		s+= "stats_file_name [" + self.stats_file_name + "]\n"
		s+= "duration ["      + str(self.duration) + "]\n"
		s+= "stats ["         + str(self.stats)      + "]\n"
		return s

	# enregistre une nouvelle charge dans les stats de l'itération
	#------------------------------------------------------------------------------
	def log_new_charge(self, charge):
		statFile = open(self.stats_file_name,'a')
		statFile.write(str(date.today()) + "\t" + str(charge) + '\n')
		statFile.close()
		self.load_stats()

	#------------------------------------------------------------------------------
	@staticmethod
	def str2day(s_date):
		""" 
		entree: une chaine du type "aaaa-mm-jj"
		retourne le nombre de jour depuis le 01-01-01
		"""
		t = list(map(int,s_date.split('-')))
		return date(t[0],t[1],t[2]).toordinal()


	#------------------------------------------------------------------------------
	def load_stats(self):
		""" 
		charge les enregistrements de l'itération dans une liste triée 
		par l'ordre chronologique
		"""
		stats = {}
		t0 = self.str2day(self.start_date)
		try: 
			f  = open(self.stats_file_name,"r")
		except:
			print("aucun enregistrement existant pour l'itération courrante")
			return {}
		
		for line in f:
			line = line.strip()
			if len(line) == 0: continue
			(s_date, val) = line.split()
			t = self.str2day(s_date) - t0
			if t < 0 or t > self.duration:
				continue
			stats[t] = float(val)
		self.stats = sorted(stats.items())
		f.close()


