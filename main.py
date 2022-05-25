from api.oanda_api import OandaApi
from infrastucture.instrument_collection import instrumentCollection
from simulazioni.ma_cross import run_ma_sim
from dateutil import parser
from infrastucture.collect_data import run_collection

if __name__ == '__main__':
    api = OandaApi()
    
    instrumentCollection.LoadInstrument("./Data")

    # decommenta qua sotto per ottenere le candele (modifiare i dati direttamente nella funzione)
    # TODO: togliere hard code dalla funzione sotto
    run_collection(instrumentCollection, api)
    

    # run_ma_sim()

    
