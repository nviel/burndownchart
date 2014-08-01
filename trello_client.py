# -*- coding: utf-8 -*-

import requests

class TrelloClient(object):
    def __init__(self, api_key, token):
        self.base_url = 'https://api.trello.com/1'
        self.api_key = api_key
        self.token = token


#--------------------------------------------------------------------------------------------------
    def add_authorisation(self, query_params):
        query_params['key'] = self.api_key
        query_params['token'] = self.token
        return query_params


#--------------------------------------------------------------------------------------------------
    def check_http_status(self, r):
        if r.status_code != 200:
            print("ERREUR! HTTP:" + str(r.status_code) + "\n")
            print("==> " + str(r.request) + "\n")
            print("--> " + str(r.content))
            raise Exception()

#--------------------------------------------------------------------------------------------------
    def getBoard(self, board_id):
        #return self.fetch_json("/board/" + board_id, 'GET', {'lists' : 'open', 'cards' : 'visible', 'card_attachments' : 'cover'})
         r = requests.get(self.base_url + "/board/" + board_id, 
                          params =  self.add_authorisation({'lists' : 'open', 'cards' : 'visible', 'card_attachments' : 'cover'}))
         self.check_http_status(r)
         return r.json()

#--------------------------------------------------------------------------------------------------
    def addCard(self, list_id, cardName):
        # bizarrement il semble qu'on puisse utiliser les parametres dans l'url alors qu'on est en post
        # comme je ne parvenais pas a le faire dans le body... c'est parti comme ca.
#       return self.fetch_json("/lists/" + list_id + "/cards", 'POST', {'name' : cardName})
         r = requests.post( self.base_url + "/lists/" + list_id + "/cards",
                           params = self.add_authorisation({'name' : cardName}))
         self.check_http_status(r)
         return r.json()

    def putCardOnTop(self, card_id):
         r = requests.put(self.base_url + "/cards/" + card_id,
                          params = self.add_authorisation({'pos':'top'}))
         self.check_http_status(r)
         return r.json()

#--------------------------------------------------------------------------------------------------
    def getCoverAttach(self, card_id):
        r = requests.get( self.base_url + "/cards/" + card_id + "/attachments", 
                          params =  self.add_authorisation({'filter':'cover'}))
        self.check_http_status(r)
        return r.json()      

#--------------------------------------------------------------------------------------------------
    def addAttachment(self, card_id, attachedFile, name):
        # POST /1/cards/[card id or shortlink]/attachments
        r = requests.post( self.base_url + "/cards/" + card_id + "/attachments",
                           params =  self.add_authorisation({}),
                           files = {'file': attachedFile}
                         )
        self.check_http_status(r)
        return r.json()

#--------------------------------------------------------------------------------------------------
    def delAttachment(self, card_id, attachment_id):
        r = requests.delete( self.base_url + "/cards/" + card_id + "/attachments/" + attachment_id,
                            params =  self.add_authorisation({}))
        self.check_http_status(r)
        return r.json()


