#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Rendre le json lisible:
#------------------------
# cat sprint_2014-06-10.json | python -mjson.tool > sprint_2014-06-10_beau.json

# but:
# Tracer le burndown charte à partir du json exporté du board trello du sprint.
# * La charge des cartes est lue dans le titre de la carte
# * La charge des cartes qui sont dans la liste "Fini" ne sont pas prises en compte
# * Le json ne contient pas l'historique: il faut faire le comte tous les jours en cron
# * le script complète un tableau csv sous la forme: [date; chage restante]
# * Le numéro du sprint est récupéré sur la ligne de commande (dans un premier temps)
#
# En première étape: 
# * on a en sortie un fichier mis à jour chaque jour.
# * Le fichier json est exporté manuellement la date du jour du sprint est celle du fichier.
#
# Idéalement:
# * le json est récupéré en cron par une requête http
# * Le graphique est géné sous forme d'image.
#
# demander un token: 
#  https://trello.com/1/authorize?
#                                key=substitutewithyourapplicationkey
#                                &name=My+Application
#                                &expiration=never
#                                &response_type=token

# exemple info board sprint:
# --------------------------
#https://api.trello.com/1/board/lkhlskqj?key=81r2476197846c560999993e1105ec19&token=d8b5ea9a9b94f727334bc4b2c11f3efc41ff3ecac5be9e92206ecxxxxxxxxxxx&lists="open"&cards="visible"

# la lib https://github.com/plish/Trolly me semble fort sympathique : à tester
# https://bitbucket.org/btubbs/trollop semble bien aussi (delete implémenté)  

# DONE:
# * admettre les ',' dans les estimations numérique (ex: 0,5 au lieu de 0.5)
# * Récupérer l'id du sprint dans un fichier de conf

# TODO: 
#   o consulter le fichier de conf des sprint et comparer avec la date du jour?
# * Mettre à jour le fichier du sprint
#   o Comment gérer les reprises
# * générer l'image du chart
# * mettre à jour l'image du chart dans la carte qui va bien?
#   o POST /1/cards
#   o DELETE /1/cards/[card id or shortlink]/attachments/[idAttachment]
#   o POST /1/cards/[cart id]/attachments/   (https://github.com/plish/Trolly/blob/master/trolly/card.py)
#   o PUT /1/cards/[card id or shortlink]/idAttachmentCover


from trello_client import TrelloClient 
from datetime import date
from iteration import Iteration
import make_chart


#--------------------------------------------------------------------------------------------------
def getCardCharge(card):
	charge = 0
	name = card['name']
	try:
		d = name.index("[")
		f = name.index("]", d)
		c = name[d+1:f]
		vals = c.split("+")
		if len(vals) > 2 or len(vals) == 0:
			raise NameError('nombre de + incorrect')
		charge += float(vals[0].strip().replace(',','.'))
		if len(vals) == 2:
			charge += float(vals[1].strip()) * 0.5 # facteur de risque... à affiner
	except:
		print("problème sur l'évaluation de la charge de ["+ card['name'] +"]")
		charge = 1  # valeur par défaut??
		
	return charge



#--------------------------------------------------------------------------------------------------
def getCardByName(board, name):
	for c in board['cards']:
		if c['name'] == name:
			return c
	return None
	
#--------------------------------------------------------------------------------------------------
def getDoneListId(board):
	# trouver l'id de la liste dont le nom est 'Fini'
	lists = board['lists']
	for l in lists:
		if l['name'] == 'Fini':
			return l['id']
	return None

#--------------------------------------------------------------------------------------------------
def getRemainingCharge(board, doneListId):
	charge = 0
	cards = board['cards']
	for c in cards:
		if c['idList'] == doneListId or c['closed']:
			continue
		charge += getCardCharge(c)

	return charge


#--------------------------------------------------------------------------------------------------
# FIXME: la lecture du fichier de conf est vraiment faite à l'arrache.
#--------------------------------------------------------------------------------------------------
def getConf():
	trelloConf = open("trello.conf","r")
	conf={}
	for line in trelloConf:
		# traitement des commentaires unilignes
		if line[-1] == '\n':
			line = line[:-1]
		comPos = line.find('#')
		if (comPos != -1):
			line = line[:comPos]
		line = line.replace(' ','')
		if len(line) < 2:
			continue
		(key,val)=line.split('=')
		conf[key] = val
	trelloConf.close()
	return (conf['key'],conf['token'],conf['boardId'])


#--------------------------------------------------------------------------------------------------
#  MAIN
#--------------------------------------------------------------------------------------------------
CHART_CARD_NAME='BURN DOWN CHART'

iteration = Iteration()
(key, token, board_id) = getConf()
connector = TrelloClient(key, token)
board = connector.getBoard(board_id)

done_list_id = getDoneListId(board)
charge = getRemainingCharge(board, done_list_id)
iteration.logNewCharge(charge)

print(str(date.today()) + "\t" + str(charge))

# calcul du graphique mis à jour
chart_file_name = iteration.id + '.png'
make_chart.build_chart_file( chart_file_name, iteration)

# récupération de la carte du chart
chart_card = getCardByName(board,CHART_CARD_NAME)

# si elle n'existe pas on la cree
if chart_card is None:
	chart_card = connector.addCard(done_list_id, CHART_CARD_NAME)

# recupération de l'attachement de couverture
attach= connector.getCoverAttach(chart_card['id'])
# s'il existe on le supprime

if attach.__class__.__name__ == 'list':
	attach = attach[0]
	connector.delAttachment(chart_card['id'], attach['id'])

# attachement du chart mis à jour (en coverture par défaut)
chart_file = open(chart_file_name,"rb")
connector.addAttachment(chart_card['id'], chart_file, 'chart')
chart_file.close()

# déplacement de la carte du chart en tête de liste.
connector.putCardOnTop(chart_card['id'])

