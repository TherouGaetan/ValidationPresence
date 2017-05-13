__autor__ = 'Gaetan'

from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString, toBytes
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import *

import config

class ComUsb(CardObserver):
    def __init__(self):
        self.repUid = ""
        
    def update(self, observable, actions):
        apdu = [0xff, 0xca, 0, 0, 0]
        (addedcards, removedcards) = actions
        for card in addedcards:
            try:
                cardtype = AnyCardType()
                cardrequest = CardRequest(timeout=1, cardType=cardtype)
                cardservice = cardrequest.waitforcard()
                cardservice.connection.connect()
                reponse, sw1, sw2 = cardservice.connection.transmit(apdu)
                tagid = toHexString(reponse).replace(' ', '')
                self.repUid = tagid
            except Exception as e:
                print('Exception detected: %s' % e)
