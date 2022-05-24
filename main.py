from api.oanda_api import OandaApi

from infrastucture.instrument_collection import instrumentCollection

from simulazioni.ma_cross import run_ma_sim

if __name__ == '__main__':
    api = OandaApi()
    
    

    # instrumentCollection.CreateFile(api.get_account_instruments(), "./Data")
    # instrumentCollection.LoadInstrument("./Data")
    # instrumentCollection.PrintInstrument()

    run_ma_sim(curr_list=['EUR', "USD", "AUD", "GBP", "AUD", "JPY", "CAD", "BTC"])