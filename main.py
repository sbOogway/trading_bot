from api.oanda_api import OandaApi

from infrastucture.instrument_collection import instrumentCollection

if __name__ == '__main__':
    api = OandaApi()

    instrumentCollection.CreateFile(api.get_account_instruments(), "./Data")
    instrumentCollection.LoadInstrument("./Data")
    instrumentCollection.PrintInstrument()