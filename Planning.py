__autor__ = 'Gaetan'

import time, datetime
from smartcard.CardMonitoring import CardMonitor

from Cour import Cour
from Reseau import Reseau
from api_client import Client
from ComUsb import ComUsb
import config

class Planning():
    def reqDay(self, reseau):
        print('Oo Construct init oO')
        date = datetime.date.today()
        ret = reseau._get("planning/load?format=json&start=%s-%s-%s&end=%s-%s-%s" % (date.year, date.month, date.day, date.year, date.month, date.day), None)
        len_ret = len(ret)
        i = 0
        obj = []
        try:
            while (i < len_ret):
                obj.append(Cour(ret[i]['codemodule'], ret[i]['codeinstance'],  ret[i]['codeacti'],  ret[i]['codeevent'],  ret[i]['acti_title'], ret[i]['scolaryear']))
                print('id=', i, ret[i]['codemodule'], ret[i]['codeinstance'],  ret[i]['codeacti'],  ret[i]['codeevent'],  ret[i]['acti_title'], ret[i]['scolaryear'])
                i += 1
            return obj
        except Exception as e:
            print("Planning exception: %s" % str(e))
            return obj

if __name__ == "__main__":
    reseau = Reseau()
    planning = Planning()

    reseau.authenticate("gaetan.therou@epitech.eu", "hjR5HQq.")

    cours = planning.reqDay(reseau)

    # Attente selection du cours !!!!
    id_cour = input('Selection du cours: ')
    cours[int(id_cour)].reqRegistered(reseau)

    # Creation client com avec Serveur NFC
    client = Client(config.URI)

    print('Place card')
    lastID = ""
    try:
        while True:
            cardmonitor = CardMonitor()
            cardobserver = ComUsb()
            cardmonitor.addObserver(cardobserver)
            
            time.sleep(1)
            tmp = cardobserver.repUid
            if tmp != "" and tmp != lastID:
                lastID = tmp
                data = client.get('/1.0/user/byTag/' + tmp)
                cours[int(id_cour)].setPresent(reseau, data["login"], "present")
                
            cardmonitor.deleteObserver(cardobserver)
    except Exception as e:
        print (str(e))