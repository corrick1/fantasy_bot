from fantasy_api import FantasyAPI
from fantasy_bot import FantasyBot

if __name__ == '__main__':
    fantasy_token_file = 'YOUR_PATH'
    fantasy_api = FantasyAPI(fantasy_token_file)
    bot = FantasyBot('YOUR_TELEGRAM_BOT_TOKEN', fantasy_api)
    bot.updater.start_polling()
    bot.updater.idle()
