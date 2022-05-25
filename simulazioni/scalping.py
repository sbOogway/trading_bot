import pandas as pd
import os.path
from infrastucture.instrument_collection import InstrumentCollection as ic


def analyse_pair():
    pass

# funzione principale
def run_scalping(curr_list=['USD', 'BTC'], granularity=['M5'], ema = "200" ):
    ic.LoadInstrument(ic, "./Data")
    for g in granularity:
        for p1 in curr_list:
            for p2 in curr_list:
                pair = f"{p1}_{p2}"
                if pair in ic.instrument_dict.keys():
                    analyse_pair(
                        ic.instrument_dict[pair],
                        g,
                        ema,
                        pair
                    )