from fantasy_api import FantasyAPI
from fantasy_bot import FantasyBot

if __name__ == '__main__':
    fantasy_token_file = 'C:\\Users\\vitia\\OneDrive\\Рабочий стол\\MAIN_\\soft_\\telegram_fantasy\\token_one.txt'
    fantasy_api = FantasyAPI(fantasy_token_file)
    bot = FantasyBot('YOUR_TELEGRAM_BOT_TOKEN', fantasy_api)  # Замените 'YOUR_TELEGRAM_BOT_TOKEN' на ваш настоящий токен
    bot.updater.start_polling()
