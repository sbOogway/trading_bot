import time
import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from colorama import Fore, Back, Style
import colorama
import logging
import telegram
from telegram.ext import Updater
import traceback

# VARIABILI E COSTANTI

CHART_LINK = 'https://it.tradingview.com/chart/vEP0XL9h/?symbol=BITSTAMP%3ABTCUSD'
PATH = "C:\\Program Files (x86)\\chromedriver.exe"
BOT_TOKEN = '5351494229:AAFBJrGK77ik5nO5FupumIvXrUAjs6LBQ_M'
CHAT_ID = '-1001533043019'
PAIR = 'BTC/USD'
ACCOUNT_BALANCE = 10000
TAKE_PROFIT = 3.60
STOP_LOSS = -2 # dipende dalla volatilita (? 1/2 di https://www.buybitcoinworldwide.com/volatility-index/ ?)
RISK = -0.5
CLEAR_SCREEN = '\033[2J'
RED = '\033[31m'
GREEN = '\033[32m'
PURPLE = '\033[35m'
RESET = '\033[0m'

bear_mkt = False
bull_mkt = False
mkt_status = ''
prv_mkt_status = ''
pos_open = False
price_col = ''
prv_price = 0
long_open = False
short_open = False
long_price = 0
short_price = 0
current_profit = 0
max_profit = 0
entry_price = 0
counter = 0
entry_price_print = ''
current_profit_percent = 0

# FUNZIONI

colorama.init()

def telegram_bot(mex):

  # Enable logging
  logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                      level=logging.INFO)
  logger = logging.getLogger(__name__)

  def emit():             
    bot = telegram.Bot(token=BOT_TOKEN)
    status = bot.send_message(chat_id=CHAT_ID, text=mex, parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True )
    time.sleep(0.2)        
    print(status)
              
  def main():
    print('####################################---INIZIO-BOT-TELEGRAM---####################################') 
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    updater.start_polling()
    emit()
    time.sleep(0.2)
    updater.stop()
    print('#####################################---FINE-BOT-TELEGRAM---#####################################')

  time.sleep(0.3)
  main()

def open_long():
    global long_price, pos_open
    long_price = price
    telegram_bot('🚨 Alert 🚨\n⬆️ Open Long Position 🟢\n\n🧾 Pair: '+ PAIR +'🧾\n💸 Price: ' + str(entry_price_print) + ' 💸\n⌚ Time: ' + ora + ' ⌚\n🐂 Trend: Bullish 🐂' + tp_sl_long())
    
def open_short():
    global short_price, pos_open
    short_price = price
    telegram_bot('🚨 Alert 🚨\n⬇️ Open Short Position 🔴\n\n🧾 Pair: '+ PAIR +'🧾\n💸 Price: ' + str(entry_price_print) + ' 💸\n⌚ Time: ' + ora + ' ⌚\n🐻 Trend: Bearish 🐻' + tp_sl_short())

def close_long():
    telegram_bot('🚨 Alert 🚨\n⬆️ Close Long Position 🟢\n\n🧾 Pair: '+ PAIR +'🧾\n💸 Price: ' + str(price) + ' 💸\n⌚ Time: ' + ora + ' ⌚\n🐂 Trend: Bullish 🐂' + profit_loss_long())

def close_short():
    telegram_bot('🚨 Alert 🚨\n⬇️ Close Short Position 🔴\n\n🧾 Pair: '+ PAIR +'🧾\n💸 Price: ' + str(price) + ' 💸\n⌚ Time: ' + ora + ' ⌚\n🐻 Trend: Bearish 🐻' + profit_loss_short())

def profit_loss_long():
    sub = -1 * (long_price - price)
    percent = sub/long_price * 100
    if sub < 0:
        return '\n\n💰 P&L 💰\n🔴 Loss: ' + str(round(sub, 2)) + ' 🔴\n💯 Percent: ' + str(round(percent, 2)) + '% 💯\n\n' 
    if sub >= 0:
        return '\n\n💰 P&L 💰\n🟢 Profit: ' + str(round(sub, 2)) + ' 🟢\n💯 Percent: ' + str(round(percent, 2)) + '% 💯\n\n'
    
def tp_sl_long():
    global sl
    sl = round(price + (price * STOP_LOSS / 100), 2) 
    tp = round(price + (price * TAKE_PROFIT / 100), 2) 
    return '\n\n📰 Stop Loss & Take Profit 💎\n🔴 Stop Loss: ' + str(sl) + ' 🔴\n🟢 Take Profit: ' + str(tp) + ' 🟢\n📒 Lot Size: ' + lot_size() + ' 📒/n'   

def profit_loss_short():
    sub = short_price - price
    percent = sub/short_price * 100
    if sub < 0:
        return '\n\n💰 P&L 💰\n🔴 Loss: ' + str(round(sub, 2)) + ' 🔴\n💯 Percent: ' + str(round(percent, 2)) + '% 💯\n\n' 
    if sub >= 0:
        return '\n\n💰 P&L 💰\n🟢 Profit: ' + str(round(sub, 2)) + ' 🟢\n💯 Percent: ' + str(round(percent, 2)) + '% 💯\n\n' 
    
def tp_sl_short():
    global sl
    sl = round(price + (price * -1 * STOP_LOSS / 100 ), 2) 
    tp = round(price + (price * -1 * TAKE_PROFIT / 100), 2)
    return '\n\n📰 Stop Loss & Take Profit 💎\n🔴 Stop Loss: ' + str(sl) + ' 🔴\n🟢 Take Profit: ' + str(tp) + ' 🟢\n📒 Lot Size: ' + lot_size() + ' 📒'
    
# LOT SIZE CALCULATOR
def lot_size():
    spread = price - sl
    if (((ACCOUNT_BALANCE * RISK) / 100) / spread) < 0:
        return str(round(((-1 * ACCOUNT_BALANCE * RISK) / 100) / spread, 2))
    else:
        return str(round(((ACCOUNT_BALANCE * RISK) / 100) / spread, 2))

    

# INIZIO SCRAPING

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--test-type')
options.add_argument('--disable-notifications')
options.add_argument('--headless')
options.add_argument('--log-level=3')
#options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(executable_path=PATH, options=options)
actionChains = ActionChains(driver)
driver.get(CHART_LINK)
driver.maximize_window()


time.sleep(10)

# loop che aggiorna i prezzi 

try:

    while True:

        try:

            # refresh time
            time.sleep(10)

            tempo = time.strftime("%d-%m-%Y %H:%M:%S GMT", time.gmtime())

            ema_str = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div[1]/div/table/tr[1]/td[2]/div/div/div[2]/div[2]/div[3]/div[2]/div/div/div').text
            sar_str = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div[1]/div/table/tr[1]/td[2]/div/div/div[2]/div[2]/div[2]/div[2]/div/div[1]/div').text
            rsi_str = driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div[1]/div/table/tr[5]/td[2]/div/div/div/div[2]/div[2]/div[2]/div/div[1]/div').text
            price_str = driver.find_element(By.XPATH, '/html/body/div[2]/div[5]/div/div[1]/div[1]/div[1]/div[2]/div[2]/div/div[2]/div[4]/span[1]/span[1]').text
            #BTCUSD                                   #/html/body/div[2]/div[5]/div/div[1]/div[1]/div[1]/div[2]/div[2]/div/div[2]/div[4]/span[1]/span[1]
                                                    
            ema = float(ema_str)
            sar = float(sar_str)
            rsi = float(rsi_str)
            price = float(price_str)

            # calcola lo stato del mercato
            if price > sar:
                prv_mkt_status = mkt_status
                bull_mkt = True
                bear_mkt = False
                mkt_status = GREEN + 'Bullish' + RESET 
                
            if price < sar:
                prv_mkt_status = mkt_status
                bear_mkt = True
                bull_mkt = False
                mkt_status = RED + 'Bearish' + RESET   

            # cambio di trend: possibile opportunità per entrare
            if prv_mkt_status != mkt_status and prv_mkt_status != '':

                print('cambio di trend')
                ora = time.strftime("%d-%m-%Y %H:%M:%S GMT", time.gmtime())
                
                # il grafico dice il contrario di come ho scritto !!!mettere a posto!!!
                if not pos_open:
                    if bull_mkt:
                        print('da bear a bull')
                        print(ora)
                        if rsi >= 70 and ema < price:
                            pos_open= True # // integrare in funzioni close/open long/short
                            long_open = True
                            entry_price = price
                            entry_price_print = price
                            open_short() # !!! contrario ? !!!
                            print('entrare short | entry price: ' + str(entry_price))
                            print(str(pos_open) + ' ' + str(long_open))                           
                    if bear_mkt:
                        print('da bull a bear')
                        print(ora)
                        if rsi <= 30 and ema > price:
                            pos_open = True # // integrare in funzioni close/open long/short
                            short_open = True
                            entry_price = price
                            entry_price_print = price
                            open_long() # !!! contrario ? !!!
                            print('entrare long | entry price: ' + str(entry_price))
                            print(str(pos_open) + ' ' + str(short_open))

            if long_open and entry_price != 0:
                current_profit = round(entry_price - price, 2)
                current_profit_percent = round(current_profit / entry_price * 100, 2)

            if short_open and entry_price != 0:
                current_profit = round(price - entry_price, 2)
                current_profit_percent = round(current_profit / entry_price * 100, 2)                              
        
            if pos_open:

                # stop loss: chiudere posizione quando la perdita è minore/uguale dello 0,5% (dopo almeno 5 min (1 candela))            
                if short_open and entry_price != 0:
                    if current_profit_percent <= STOP_LOSS:
                        print('chiudere posizione long /// stop loss a -1%')
                        close_long()
                        short_open = False
                        max_profit = 0
                        entry_price = 0
                        pos_open = False
                        counter = 0
                        current_profit = 0
                        current_profit_percent = 0
                if long_open and entry_price != 0:
                    if current_profit_percent <= STOP_LOSS:
                        print('chiudere posizione short /// stop loss a -1%')
                        close_short()
                        long_open = False
                        max_profit = 0
                        entry_price = 0
                        pos_open = False
                        counter = 0
                        current_profit = 0
                        current_profit_percent = 0

                # take profit: chiudere posizione quando il guadagno è maggiore/uguale dello 1,5% (dopo almeno 5 min (1 candela))
                if short_open and entry_price != 0 :
                    if current_profit_percent >= TAKE_PROFIT:
                        print('chiudere posizione long /// take profit a 1%')
                        close_long()
                        short_open = False
                        max_profit = 0
                        entry_price = 0
                        pos_open = False
                        counter = 0
                        current_profit = 0
                        current_profit_percent = 0
                if long_open and entry_price:
                    if current_profit_percent >= TAKE_PROFIT:
                        print('chiudere posizione short /// take profit a 1%')
                        close_short()
                        long_open = False
                        max_profit = 0
                        entry_price = 0
                        pos_open = False
                        counter = 0
                        current_profit = 0
                        current_profit_percent = 0

            if current_profit < 0:
                string_current_profit = RED + str(current_profit) + RESET
            
            if current_profit >= 0:
                string_current_profit = GREEN + str(current_profit) + RESET

            if prv_price == price:
                print(tempo + PURPLE + ' ----- ' + RESET + ema_str + PURPLE + " # " + RESET + sar_str + PURPLE +" # " + RESET + rsi_str + PURPLE + " # " + RESET +  price_str + PURPLE +' # ' + RESET + mkt_status + PURPLE +' ||||| ' +RESET +  prv_mkt_status + PURPLE +' ***** ' + RESET + 'Current Profit: ' + string_current_profit + PURPLE + " # " + RESET + 'Profit %: ' + str(current_profit_percent) + PURPLE + " # " + RESET + 'Entry price: ' + str(entry_price))
                print(PURPLE + '===========================================================================================================================================================================' + RESET)

            if prv_price > price:
                price_col = RED + price_str + RESET 
                print(tempo + PURPLE + ' ----- ' + RESET + ema_str + PURPLE + " # " + RESET + sar_str + PURPLE +" # " + RESET + rsi_str + PURPLE + " # " + RESET + price_col + PURPLE +' # ' + RESET + mkt_status + PURPLE +' ||||| ' + RESET + prv_mkt_status + PURPLE +' ***** ' + RESET + 'Current Profit: ' + string_current_profit + PURPLE + " # " + RESET + 'Profit %: ' + str(current_profit_percent) + PURPLE + " # " + RESET + 'Entry price: ' + str(entry_price))
                print(PURPLE + '===========================================================================================================================================================================' + RESET)

            if prv_price < price:
                price_col = GREEN + price_str + RESET 
                print(tempo + PURPLE + ' ----- ' + RESET + ema_str + PURPLE + " # " + RESET + sar_str + PURPLE +" # " + RESET + rsi_str + PURPLE + " # " + RESET + price_col + PURPLE +' # ' + RESET + mkt_status + PURPLE +' ||||| ' + RESET + prv_mkt_status + PURPLE +' ***** ' + RESET + 'Current Profit: ' + string_current_profit + PURPLE + " # " + RESET + 'Profit %: ' + str(current_profit_percent) + PURPLE + " # " + RESET + 'Entry price: ' + str(entry_price))
                print(PURPLE + '===========================================================================================================================================================================' + RESET)

            prv_price = price

        except:
            print(traceback.format_exc())

except:
    print(traceback.format_exc())