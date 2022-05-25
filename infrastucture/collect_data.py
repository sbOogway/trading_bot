import pandas as pd
import datetime as dt
from dateutil import parser

from infrastucture.instrument_collection import InstrumentCollection 
from api.oanda_api import OandaApi 



'''
funzionamento:

limite candele ottenibili con l'api :5000

quindi se vogliamo ottenere le candele in M5 di 7 anni


date_from = 2015
date_to = 2022

quindi scriviamo una funzione che parte da 
2015-01-01 e arriva fino a 2015-01-08 e mette i dati in un dataframe e così via


poi concateniamo tutte le candele in un dataframe

'''

CANDLE_COUUNT = 3000

INCREMENTS = {
    'M5' : 5 * CANDLE_COUUNT,
    'H1' : 60 * CANDLE_COUUNT,
    'H4' : 240 * CANDLE_COUUNT  
}


def save_file(final_df: pd.DataFrame, file_prefix, granularity, pair):
    filename = f"{file_prefix}{pair}_{granularity}.pkl"

    # pulisco i dati prima di salvarli
    final_df.drop_duplicates(subset=['time'], inplace=True)
    final_df.sort_values(by='time', inplace=True)
    final_df.reset_index(drop=True, inplace=True)
    final_df.to_pickle(filename)


    s1 =f"{pair} {granularity} {final_df.time.min()} - {final_df.time.max()}"
    print(f"*** {s1}  ---> {final_df.shape[0]} CANDELE ***")



def fecth_candles(pair, granularity, date_f : dt.datetime, date_t: dt.datetime, api: OandaApi):
    
    attempts =  0


    # PERICOLOSO!!    
    while attempts < 3:

        candle_df = api.get_candles_df(pair, granularity=granularity, date_f=date_f, date_t=date_t)

        if candle_df is not None :
            break


        attempts += 1

    if candle_df is not None and candle_df.empty == False:
        return candle_df
    else:
        return None



def collect_data(pair, granularity, date_f, date_t, file_prefix, api:OandaApi):
    
    time_step = INCREMENTS[granularity]

    end_date = parser.parse(date_t)
    from_date = parser.parse(date_f)


    # lista di dataframe 
    candle_dfs = []  

    to_date = from_date

    while to_date < end_date:
        to_date = from_date + dt.timedelta(minutes=time_step)

        # controllo errori
        if to_date > end_date:
            to_date = end_date

        candles = fecth_candles(pair, granularity, from_date, to_date, api)


        # aggiungo le candele alla lista
        if candles is not None and candles.empty == False:
            candle_dfs.append(candles)
            print(f"{pair} {granularity}  {from_date} - {to_date}  ---> {candles.shape[0]} CANDELE CARICATE")

        else:
            print(f"{pair} {granularity}  {from_date} - {to_date}  ---> NO CANDELE!")

        from_date = to_date

    if len(candle_dfs) > 0:
        final_df = pd.concat(candle_dfs)
        save_file(final_df, file_prefix, granularity, pair)
    else:
        print(f"{pair} {granularity}   ---> NESSUN DATO SALVATO!")


# funzione principale
def run_collection(ic: InstrumentCollection, api: OandaApi):
    our_curr = ["AUD", "CAD", "JPY", "USD", "EUR", "GBP", "NZD", "BTC"]
    for p1 in our_curr:
        for p2 in our_curr:
            pair = f"{p1}_{p2}"
            if pair in ic.instrument_dict.keys():
                for granularity in [ "M5", "H1", "H4"]:
                    print(pair, granularity)
                    collect_data(pair, granularity, "2016-01-07T00:00:00Z","2016-12-31T00:00:00Z" , "./Data/", api)
