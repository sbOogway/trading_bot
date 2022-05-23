import json
from constants.config import API_KEY
from models.instruments import Instrument

class InstrumentCollection:
    FILENAME = 'instrument.json'
    API_KEYS = ['name', 'type', 'displayName', 'pipLocation', 'displayPrecision', 'tradeUnitsPrecision', 'marginRate' ]


    def __init__(self):
        self.instrument_dict = {}

    
    def LoadInstrument(self, path):
        self.instrument_dict = {}
        filename = f'{path}/{self.FILENAME}'
        with open(filename, 'r') as f:
            data = json.loads(f.read())
            for k, v in data.items():
                self.instrument_dict[k] = Instrument.FromApiObject(v)

    def CreateFile(self, data, path ):
        if data is None:
            print('NOn è possibile create il file Instrument', data)
            return 

        instrument_dict = {}
        for i in data:
            key = i['name']
            instrument_dict[key] = { k: i[k] for k in self.API_KEYS}
        
        filename = f'{path}/{self.FILENAME}'
        with open(filename, 'w') as f:
            f.write(json.dumps(instrument_dict, indent=2))

                
    def PrintInstrument(self):
        [print(k, v) for k, v in self.instrument_dict.items()]
        print(len(self.instrument_dict.keys()), 'instruments')


instrumentCollection = InstrumentCollection()

