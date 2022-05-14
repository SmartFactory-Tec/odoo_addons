from odoo import http
from requests.auth import HTTPBasicAuth

import requests



class Factory(http.Controller):
    url = "https://prod400azdb02.svcs.itesm.mx/piwebapi/"

    @http.route('/factory/', auth='public', website=True)
    def index(self, **kw):
        battery_request = requests.get(self.url + "streams/F1DPAVp1V4jMukCbSUCQw1guxAuAIAAAUFJPRDQwMEFaREIwMlxCQVRURVJZ/end", headers={
            'Authorization': 'Basic VEVDXHQtZXJpay5vbHZlcmE6KkVTT01zaW9zMDE=',
        }, verify=False)
        print(battery_request.json())
        return http.request.render('SmartFactory.index', qcontext={
            'battery1' : battery_request.json()["Value"]
        })