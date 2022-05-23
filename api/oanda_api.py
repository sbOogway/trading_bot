import json
import requests
import constants.config as defs


class OandaApi:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': 'Bearer ' + defs.API_KEY,
            'Content-Type': 'application/json'
            })

    def make_request(self, url, verb="get", code=200, params = None, data=None, headers=None):
        url = f'{defs.OANDA_URL}/{url}'

        try:
            response = None
            if verb == "get":
                response = self.session.get(url, params=params, data = data, headers = headers)
            
            # tipo di richiesta sbagliata
            if response == None:
                return False, {'errore' : 'verb non trovato'}

            # richiesta corretta
            if response.status_code == code:
                return True, response.json()
            # errore
            else:
                return False, response.json()

        except Exception as e:
            return False, {'Exception' : e}

    def get_account_ep(self, ep, data_key):
        url = f'accounts/{defs.ACCOUND_ID}/{ep}'
        ok, data = self.make_request(url)
        
        if ok == True and data_key in data:
            return data[data_key]
        else:
            print('Errore in get_account_ep', data)
            return None

    def get_account_summary(self):
        return self.get_account_ep('summary', 'account')

    def get_account_instruments(self):
        return self.get_account_ep('instruments', 'instruments')

