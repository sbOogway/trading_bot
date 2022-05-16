from warnings import catch_warnings
from dotenv import dotenv_values

from binance.client import Client



config = dotenv_values(".env")

# ottengo le chiavi segrete


api_key = config['API_KEY_TEST']

secret_key = config['SECRET_KEY_TEST']

print("API KEY:" , api_key)
print("SECRET KEY:" , secret_key)

try:
    client =  Client(api_key, secret_key)

    catch_warnings()
    # verifico se il client è connesso
    if client.ping() == {}:
        print("Client connesso")
    else:
        exit

    client.API_URL = 'https://testnet.binance.vision/api'
except ValueError:
    print("Errore di connessione")







