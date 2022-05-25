import requests
import constants.config as defs
import pandas as pd
from dateutil import parser
from datetime import datetime as dt


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


    def get_candles_df(self, pair_name, **kwargs):

        data = self.fetch_candles(pair_name, **kwargs)

        if data is None :
            return None 
        if len(data) == 0:
            return pd.DataFrame()

        
        price = ['mid', 'bid', 'ask'] # prezzo medio, prezzo di vendita, prezzo di acquisto

        ohlc = ['o', 'h', 'l', 'c'] # open, high, low, close (mid_o, mid_h, mid_l, mid_c,...)

        final_data = []


        for d in data:

            if d['complete'] == False:
                continue
            new_dict = {}
            new_dict['time'] = parser.parse( d['time'])
            new_dict['volume'] = d['volume']
            

            for p in price:
                if p in d:
                    for o in ohlc:
                     new_dict[f'{p}_{o}'] = float(d[p][o])
            final_data.append(new_dict)


        df = pd.DataFrame(final_data)

        return df


    # funzione per ottenere le candele 
    def fetch_candles(self, pair_name, count= 10, granularity = 'H1', price="MBA", date_f = None, date_t = None):
        url = f'/instruments/{pair_name}/candles'

        params = dict(
            granularity = granularity,
            price= price,

        )

        if date_f is not None and date_t is not None:
            formato_data = "%Y-%m-%dT%H:%M:%SZ"
            # converto la data in formato stringa
            params['from'] = dt.strftime(date_f, formato_data )
            params['to'] = dt.strftime(date_t, formato_data )
        else:
            params['count'] = count


        # facciamo la richiesta
        ok, data = self.make_request(url, params=params)

        
        # controllo la risposta
        if ok == True and 'candles' in data:
            return data['candles']
        else:
            print('Errore in fetch_candles()', data)
            return None