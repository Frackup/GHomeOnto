#!/usr/bin/python3
# _*_ coding:utf8 _*_

from owlready2 import *
import owlready2
import sys

from flask import Flask
from flask import request
from flask import make_response

import json
import os
import types
import unidecode

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    print("_______________  Appel au WebHook depuis DialogFlow _______________")
    req = request.get_json(silent=True, force=True)

    res = processRequest(req)

    res = json.dumps(res, indent=4)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r



def processRequest(req):

    global financement 
    global AGE_client 

    print("_______________ Execution de la requête _______________")

    if req["queryResult"]["action"] == "peutFinancer":
        json_params = req["queryResult"]["parameters"]
        typeFinancement = json_params['financement']
        typeBien = json_params['bien']

        #speech = Ontologie(typeBien, typeFinancement)

        speech = " Vous voulez financer " + bien + " avec " + financement

        print(speech)
    else:
        return {}

    return {
        "fulfillmentText": speech
        #"speech": speech,
        #"displayText": speech,
        # "data": data,
        # "contextOut": [],
        #"source": "apiai-weather-webhook-sample"
    }

########################
#Gestion des ontologies#
########################

def Ontologie(typeBien, typeFinancement):

    deterIndef = "un"

    #Recherche de la JVM pour pouvoir charger le reasoner (il est écrit en JAVA)
    #owlready2.JAVA_EXE = "C:\\Program Files (x86)\\Common Files\\Oracle\\Java\\javapath\\java.exe"

    #Mise en place de l'ontologie
    onto_path = "https://github.com/Frackup/GHomeOnto/"
    onto_name = "OWLReadyTuto3.owl"
    onto_file = onto_path + onto_name

    onto = get_ontology(onto_file).load()

    #Création des classes de l'ontologie
    with onto:
        #Parsing des classes de l'ontologie via boucle for
        '''
        for mesClasses in onto.classes():
            print("classes : " + mesClasses.name)

        for sub in onto.BienExterieur.subclasses():
            print("subclass : " + sub.name)
            '''

        class estFinancablePar(onto.Bien >> onto.PretImmobilier):
            pass

        class BiensFinancables(onto.Bien):
            equivalent_to = [onto.Bien & estFinancablePar.some(onto.PretImmobilier)]

        sync_reasoner()

    #Fin du with

    trouve = False

    for biensTrouves in BiensFinancables.subclasses():
        if (biensTrouves.name.casefold() == unidecode.unidecode(typeBien.casefold())):
            if(biensTrouves.comment == "masculin"):
                deterIndef = "un"
            else:
                deterIndef = "une"

            return "Il est possible de financer " + deterIndef + " " + typeBien + " avec un prêt immobilier"
            trouve = True

    if (not(trouve)):
        return "Votre demande de financement n'est malheureusement pas possible"
        #Pour obtenir les sous-classes directes d'une classe donnée (ici Thing)
    #mesClasses = [c for c in onto.classes() if c.__bases__ == (Thing,)]
    #print(mesClasses)

##############################
# Main de l'appel au webhook #
##############################

if __name__ == '__main__':

    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
