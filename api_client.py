__author__ = 'Steven'

import json
import hashlib
import random
try:
    import httplib
except:
    import http.client as httplib

import urllib
import uuid
import os
import pytz
import datetime
import base64
import hmac
import time

import config


class Client(object):
    def __init__(self, host):
        self._host = host
        self._hash = config.HASH
        self._uuid = config.UUID

    def _sign(self, d, method, url, datas=None):
        if method == "POST":
            data = datas.decode("utf-8") if datas else ""
        else:
            data = url
        print("data: %s" % "{0}-{1}".format(str(int(time.mktime(d.timetuple()))),
            data).encode("utf-8"))
        hm = hmac.new(self._hash.encode("utf-8"), "{0}-{1}".format(str(int(time.mktime(d.timetuple()))),
            data).encode("utf-8"), hashlib.sha256)

        l = hm.hexdigest() if not self._uuid else "%s:%s" % (self._uuid, hm.hexdigest())
        return "Sign %s" % base64.b64encode(l.encode("utf-8")).decode("utf-8")

    def _storeFile(self, url, response):
        dir = "."
        url = os.path.join(dir, str(uuid.uuid4()) + ".zip")
        with open(url, 'wb') as f:
            resp = response.read(65 * 1024)
            while resp:
                f.write(resp)
                resp = response.read(65 * 1024)
        return {"file": url}

    def _req(self, method, url, datas=None, data_type="application/json"):
        conn = httplib.HTTPConnection(self._host)
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        headers = {"Content-type": "application/json"}
        d = datetime.datetime.now(pytz.timezone('Europe/Paris'))
        headers["Date"] = d.strftime('%a, %d %b %Y %H:%M:%S %z')
        print("Date: %s" % headers["Date"])
        headers["Authorization"] = self._sign(d, method, url, json.dumps(datas).encode("utf-8") if data_type == "application/json" else datas.encode("utf-8"))
        print("Authorization: %s" % headers["Authorization"])
        #conn.request(method, url, urllib.urlencode(datas) if datas else None, headers=headers)
        if data_type == "application/json":
            conn.request(method, url, urllib.parse.urlencode(datas) if datas and method == "GET" else json.dumps(datas).encode("utf-8"), headers=headers)
        else:
            conn.request(method, url, urllib.parse.urlencode(datas) if datas and method == "GET" else datas.encode("utf-8"), headers=headers)
        conn.set_debuglevel(1)
        response = conn.getresponse()
        content_type = response.getheader("Content-Type")
        print('%s: [%s] (%s)' % (url, response.status, response.reason))
        try:
            if content_type.find("zip") >= 0:
                return self._storeFile(url, response)
            return json.loads(response.read().decode())
        except Exception as e:
            print("get Exception: %s" % e)
            return {}

    def get(self, url):
        return self._req("GET", url)

    def post(self, url, datas):
        return self._req("POST", url, datas)

    def delete(self, url):
        return self._req("DELETE", url)

    def upload(self, url, f,form="PUT"):
        import requests
        print(os.path.basename(f))
        headers = {}
        res = requests.put("http://" + self._machine + url, files={"file": (os.path.basename(f), open(f, 'rb'))}, headers=headers)
        print(res.text)

    def post_notes(self, url, filename):
        raw_datas = ""
        with open(filename, "r") as f:
            raw_datas = f.readlines()
        print(raw_datas)
        return self._req("POST", url, "".join(raw_datas), "text/csv")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        print("USAGE python3 %s /1.0/..." % (sys.argv[0]))
        sys.exit(1)
    g = Client(config.URI)
    if "notes" in sys.argv[1]:
        r = g.post_notes(sys.argv[1], sys.argv[2])
        print(str(r))
    else:
        print(str(g.get(sys.argv[1])))
    #print(str(g.post("/1.0/user/", {"login": "couval_j", "firstname": "Jean-Baptiste", "lastname": "COUVAL"})))
