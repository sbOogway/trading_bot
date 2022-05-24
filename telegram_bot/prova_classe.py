import telegram_bot
import time

bot = telegram_bot.TelegramBot('-1001760450235', '5177613529:AAHjrHCTQdAfHSlwrpwZnIgYwDOsKgoJeEo')

print(bot)

while True:

    bot.emit('succo')

    time.sleep(5)