import requests
import json, csv, io, codecs, time, datetime, os

class Reseau():
    def __init__(self):
        print('|| --- Construct reseau --- ||')
        self._urlBase = "https://intra.epitech.eu/"
        self._s = requests.session()
        
    def _get(self, path, params):
        print('|| --- Get -> (' + self._urlBase + path + ') --- ||')
        try:
            r = self._s.get(self._urlBase + path, params=params)
            cleaned = ""
            for line in r.content.decode('utf-8').split("\n"):
                if line.startswith('//') == False:
                    cleaned += line
            obj = json.loads(cleaned)
        except Exception as e:
            print(str(e))
            return {}
        return obj

    def _post(self, path, payload, headers):
        print('|| --- Post -> (' + self._urlBase + path + ') --- ||')
        try:
            print('Payload->')
            print(payload)
            print('Headers->')
            print(headers)
            r = self._s.post(self._urlBase + path, data=payload, headers=headers)
            print(r.text)
            cleaned = ""
            for line in r.content.decode('utf-8').split("\n"):
                if line.startswith('//') == False:
                    cleaned += line
            obj = json.loads(cleaned)
        except Exception as e:
            print(str(e))
            return {}
        return obj

    def authenticate(self, login, passwd):
        print('|| --- Authenticate --- ||')
        values = {'login': login,
                    'password': passwd,
                    'remind': 'on'}
        try:
            r = self._s.post(self._urlBase, data=values)
            return True
        except Exception as e:
            print(e)
            return False
        if r.status_code is not 200:
            print("Mauvais Login ou MDP")
            return False
