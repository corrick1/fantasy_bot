from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from threading import Thread
from telegram.ext import Updater


class FantasyBot:
    def __init__(self, token, fantasy_api):
        self.token = token
        self.updater = Updater(token=self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.fantasy_api = fantasy_api

        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("wallet", self.wallet))
        self.dispatcher.add_handler(CommandHandler("edit_wallet", self.edit_wallet))
        self.dispatcher.add_handler(CommandHandler("balance", self.balance))
        self.dispatcher.add_handler(CommandHandler("edit_trigger", self.edit_trigger))
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_wallet))
        
        self.user_data = {}

    def start(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            'Welcome!',
            reply_markup=self.menu_keyboard()
        )

    def menu_keyboard(self):
        keyboard = [[KeyboardButton("/wallet"), KeyboardButton("/edit_wallet")],
                    [KeyboardButton("/balance"), KeyboardButton("/edit_trigger")]]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    def wallet(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        if chat_id in self.user_data and 'wallet_address' in self.user_data[chat_id]:
            wallet_address = self.user_data[chat_id]['wallet_address']
            portfolio_value = self.fantasy_api.get_portfolio_value(wallet_address)
            if portfolio_value is not None:
                update.message.reply_text(f'Your current wallet: {wallet_address}\nThe current price of your portfolio: ETH {portfolio_value}')
            else:
                update.message.reply_text('Failed to get the portfolio price. Try again later.')
        else:
            update.message.reply_text('Enter your wallet address')
            self.user_data[chat_id] = {'awaiting_wallet': True}

    def edit_wallet(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        if chat_id in self.user_data and 'wallet_address' in self.user_data[chat_id]:
            update.message.reply_text('Enter the new address of your wallet')
            self.user_data[chat_id]['awaiting_wallet'] = True
        else:
            update.message.reply_text('First, specify the wallet address using the /wallet command')

    def balance(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        if chat_id in self.user_data and 'wallet_address' in self.user_data[chat_id]:
            wallet_address = self.user_data[chat_id]['wallet_address']
            portfolio_value = self.fantasy_api.get_portfolio_value(wallet_address)
            if portfolio_value is not None:
                update.message.reply_text(f'The current price of your portfolio: ETH {portfolio_value}')
            else:
                update.message.reply_text('Failed to get the portfolio price. Try again later.')
        else:
            update.message.reply_text('First, specify the wallet address using the /wallet command')

    def edit_trigger(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        if chat_id in self.user_data and 'wallet_address' in self.user_data[chat_id]:
            update.message.reply_text(
                'Select a percentage for further notification:',
                reply_markup=self.tracker_options()
            )
            self.user_data[chat_id]['awaiting_trigger'] = True
        else:
            update.message.reply_text('First, specify the wallet address using the /wallet command')

    def handle_wallet(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        if chat_id in self.user_data:
            if 'awaiting_wallet' in self.user_data[chat_id] and self.user_data[chat_id]['awaiting_wallet']:
                wallet_address = update.message.text.strip()
                if len(wallet_address) == 42 and wallet_address.startswith('0x'):
                    self.user_data[chat_id]['wallet_address'] = wallet_address
                    self.user_data[chat_id].pop('awaiting_wallet', None)  # Remove 'awaiting_wallet'
                    portfolio_value = self.fantasy_api.get_portfolio_value(wallet_address)
                    if portfolio_value is not None:
                        update.message.reply_text(
                            f'The wallet address has been successfully saved! The current price of your portfolio: ETH {portfolio_value}',
                            reply_markup=self.menu_keyboard()
                        )
                    else:
                        update.message.reply_text(
                            'The wallet address was successfully saved, but failed to retrieve the portfolio price. Try again later.',
                            reply_markup=self.menu_keyboard()
                        )
                else:
                    update.message.reply_text('The address is incorrect. Try again.')

            elif 'awaiting_trigger' in self.user_data[chat_id] and self.user_data[chat_id]['awaiting_trigger']:
                selected_option = update.message.text.strip()
                self.user_data[chat_id]['tracker_option'] = selected_option
                self.user_data[chat_id].pop('awaiting_trigger', None)  # Remove 'awaiting_trigger'
                update.message.reply_text(
                    f'Tracking mode is set to {selected_option}.',
                    reply_markup=self.menu_keyboard()
                )
                self.start_tracking(chat_id, context)

    def tracker_options(self):
        reply_keyboard = [['3%', '5%', '10%', '20%', '30%']]
        return ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    def start_tracking(self, chat_id, context: CallbackContext):
        wallet_address = self.user_data[chat_id].get('wallet_address')
        tracker_option = self.user_data[chat_id].get('tracker_option')

        if wallet_address and tracker_option:
            def track():
                try:
                    previous_value = self.fantasy_api.get_portfolio_value(wallet_address)
                    if previous_value is not None:
                        self.user_data[chat_id]['previous_value'] = previous_value

                        while True:
                            current_value = self.fantasy_api.get_portfolio_value(wallet_address)
                            if current_value and previous_value:
                                change_percent = (abs(current_value - previous_value) / previous_value) * 100
                                if change_percent >= float(tracker_option.strip('%')):
                                    context.bot.send_message(chat_id=chat_id, text=f'The price of your portfolio has changed by {tracker_option}. New Price: ETH {current_value}')
                                    previous_value = current_value

                            time.sleep(10)
                    else:
                        context.bot.send_message(chat_id=chat_id, text='Failed to get the initial price of the portfolio. Try again later.')
                except Exception as e:
                    print("Error when starting tracking:", e)

            tracking_thread = Thread(target=track)
            tracking_thread.daemon = True
            tracking_thread.start()
