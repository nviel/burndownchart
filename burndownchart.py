#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" 
but:
Tracer le burndown charte à partir du json exporté du board trello du sprint.
 * La charge des cartes est lue dans le titre de la carte
 * La charge des cartes qui sont dans la liste "Fini" ne sont pas prises en compte
 * Le json ne contient pas l'historique: il faut faire le comte tous les jours en cron
 * le script complète un tableau csv sous la forme: [date; chage restante]
 * Le numéro du sprint est récupéré sur la ligne de commande (dans un premier temps)
 * on a en sortie un fichier mis à jour chaque jour.
 * le json est récupéré en cron par une requête http
 * Le graphique est géné sous forme d'image.

demander un token: 
------------------
  https://trello.com/1/authorize?
                                key=substitutewithyourapplicationkey
                                &name=My+Application
                                &expiration=never
                                &response_type=token
Rendre le json lisible:
------------------------
 cat sprint_2014-06-10.json | python -mjson.tool > sprint_2014-06-10_beau.json

exemple info board sprint:
--------------------------
https://api.trello.com/1/board/lkhlskqj?key=81r2476197846c560999993e1105ec19&token=d8b5ea9a9b94f727334bc4b2c11f3efc41ff3ecac5be9e92206ecxxxxxxxxxxx&lists="open"&cards="visible"

   o POST /1/cards
   o DELETE /1/cards/[card id or shortlink]/attachments/[idAttachment]
   o POST /1/cards/[cart id]/attachments/   (https://github.com/plish/Trolly/blob/master/trolly/card.py)
   o PUT /1/cards/[card id or shortlink]/idAttachmentCover
"""

from trello_client import TrelloClient 
from datetime import date
from iteration import Iteration
import make_chart


#--------------------------------------------------------------------------------------------------
def get_card_charge(card):
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
def get_card_by_name(board, name):
	for c in board['cards']:
		if c['name'] == name:
			return c
	return None
	
#--------------------------------------------------------------------------------------------------
def get_done_list_id(board):
	# trouver l'id de la liste dont le nom est 'Fini'
	lists = board['lists']
	for l in lists:
		if l['name'] == 'Fini':
			return l['id']
	return None

#--------------------------------------------------------------------------------------------------
def get_remaining_charge(board, doneListId):
	charge = 0
	cards = board['cards']
	for c in cards:
		if c['idList'] == doneListId or c['closed']:
			continue
		charge += get_card_charge(c)

	return charge


#--------------------------------------------------------------------------------------------------
# FIXME: la lecture du fichier de conf est vraiment faite à l'arrache.
#--------------------------------------------------------------------------------------------------
def get_conf():
	trello_conf = open("trello.conf","r")
	conf={}
	for line in trello_conf:
		# traitement des commentaires unilignes
		if line[-1] == '\n':
			line = line[:-1]
		com_pos = line.find('#')
		if (com_pos != -1):
			line = line[:com_pos]
		line = line.replace(' ','')
		if len(line) < 2:
			continue
		(key,val)=line.split('=')
		conf[key] = val
	trello_conf.close()
	return (conf['key'],conf['token'],conf['boardId'])


#--------------------------------------------------------------------------------------------------
#  MAIN
#--------------------------------------------------------------------------------------------------
CHART_CARD_NAME='BURN DOWN CHART'

iteration = Iteration()
(key, token, board_id) = get_conf()
connector = TrelloClient(key, token)
board = connector.get_board(board_id)

done_list_id = get_done_list_id(board)
charge = get_remaining_charge(board, done_list_id)
iteration.log_new_charge(charge)

print(str(date.today()) + "\t" + str(charge))

# calcul du graphique mis à jour
chart_file_name = iteration.id + '.png'
make_chart.build_chart_file( chart_file_name, iteration)

# récupération de la carte du chart
chart_card = get_card_by_name(board,CHART_CARD_NAME)

# si elle n'existe pas on la cree
if chart_card is None:
	chart_card = connector.add_card(done_list_id, CHART_CARD_NAME)

# recupération de l'attachement de couverture
attach= connector.get_cover_attachment(chart_card['id'])
# s'il existe on le supprime

if attach.__class__.__name__ == 'list':
	attach = attach[0]
	connector.del_attachment(chart_card['id'], attach['id'])

# attachement du chart mis à jour (en coverture par défaut)
chart_file = open(chart_file_name,"rb")
connector.add_attachment(chart_card['id'], chart_file, 'chart')
chart_file.close()

# déplacement de la carte du chart en tête de liste.
connector.put_card_on_top(chart_card['id'])

