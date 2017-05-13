__autor__ = 'Gaetan'

import urllib

class Cour():
    def __init__(self, module, ville, acticode, codeevent, title, year):
        self._module = module
        self._ville = ville
        self._acticode = acticode
        self._codeevent = codeevent
        self._title = title
        self._year = year
        self._student = []

    def reqRegistered(self, reseau):
        print('*** Req Registered ***')
        students = reseau._get("module/%s/%s/%s/%s/%s/registered?format=json" % (self._year, self._module, self._ville, self._acticode, self._codeevent), None)
        for student in students:
            print(student['login'])
            self._student.append(student['login'])

    def setPresent(self, reseau, login, status):
        print('*** Set Present ***')
        items = {
            'items[0][login]' : login,
            'items[0][present]' : status
            }
        try:
            headers = {'content-type': "application/x-www-form-urlencoded"}
            ret = reseau._post("module/%s/%s/%s/%s/%s/updateregistered?format=json" % (self._year, self._module, self._ville, self._acticode, self._codeevent), urllib.urlencode(items), headers)
        except Exception as e:
            print(e)
            return
