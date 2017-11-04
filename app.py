import os
import logging

from functools import wraps

from telegram import ParseMode
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import RegexHandler
from telegram.ext import Filters

import vhosts_ops
import services_ops

from config import Config

GET_HOST_NEW, GET_PORT_NEW, CONFIRM_HOST_NEW = range(3)

class CaddyBot:
    ## Restricting decorator
    def restricted(func):
        @wraps(func)
        def wrapped(self, bot, update, *args, **kwargs):
            logger = logging.getLogger('')
            user_id = update.effective_user.id
            if user_id not in Config['Admins']:
                logger.error("Unauthorized access denied for {}.".format(user_id))
                return
            return func(self, bot, update, *args, **kwargs)
        return wrapped

    def __init__(self):
        ## Get vars from env
        self.WEBHOOKS = os.getenv('USE_WEBHOOKS', False)
        self.TOKEN = os.getenv('TG_TOKEN', '')
        self.PORT = os.getenv('PORT', 5001)
        self.DEBUG = os.getenv('DEBUG', False)
        print('Webhooks: {}\nToken: {}\nPort: {}\nDebug: {}'.format(self.WEBHOOKS, self.TOKEN, self.PORT, self.DEBUG))
        ## Define Updater class and dispatcher object
        self.updater = Updater(token = self.TOKEN)
        self.dispatcher = self.updater.dispatcher
        ## Definition of logger
        self.logger = logging.getLogger('')
        if self.DEBUG:
            logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s')
        else:
            logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s')
        ## Definition of commands
        new_vhost_handler = self.new()
        self.dispatcher.add_handler(new_vhost_handler)
        self.logger.debug('Finished __init__')

    def _test(self, bot, update):
        result = services_ops.restart_service()
        update.message.reply_text(
            str(result),
            parse_mode=ParseMode.MARKDOWN)

    def start(self):
        if self.WEBHOOKS:
            self.logger.info('Using webhooks configuration...')
            self.updater.start_webhook(listen='127.0.0.1', port=self.PORT, url_path=self.TOKEN)
            full_cert = open(Config['cert_file'], 'r').read() + '\n' + open(Config['key_file'], 'r').read()
            self.updater.bot.set_webhook(url='https://caddybot.bonny.pw/' + self.TOKEN,
                                         certificate = full_cert)
            # self.updater.start_webhook(listen='127.0.0.1',
            #                            key=Config['key_file'],
            #                            cert=Config['cert_file'],
            #                            webhook_url='https://caddybot.bonny.pw/' + self.TOKEN,
            #                            port=self.PORT,
            #                            url_path=self.TOKEN)
        else:
            self.logger.info('Using polling configuration...')
            self.updater.start_polling()
        self.updater.idle()

    ## Commands !! IMPORTANT !! Try to find a way to separate that shit
    def new(self):
        new_handler = ConversationHandler(
            entry_points = [CommandHandler('new', self._new)],
            states = {
                GET_HOST_NEW: [MessageHandler(Filters.text, self._new_vhost_port)],
                GET_PORT_NEW: [MessageHandler(Filters.text, self._confirm_new_vhost)],
                CONFIRM_HOST_NEW: [RegexHandler('^(Si)$', self._create_new_vhost),
                                   RegexHandler('^(No)$', self._new_cancel),]
            },
            fallbacks = [CommandHandler('cancel', self._new_cancel)])
        return new_handler


    @restricted
    def _new(self, bot, update):
        self.logger.info('New Vhost creation started by {id}'.format(id=update.effective_user.id))
        message = 'Inserisci il dominio del nuovo vhost che vuoi creare.\nCancella con /cancel'
        bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
        return GET_HOST_NEW

    new_vhost_url = ''
    new_vhost_port = ''

    def _new_vhost_port(self, bot, update):
        url = str(update.message.text).strip()
        CaddyBot.new_vhost_url = url.lower()
        message = 'Inserisci la porta del servizio.'
        bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
        return GET_PORT_NEW

    def _confirm_new_vhost(self, bot, update):
        port = str(update.message.text).strip()
        CaddyBot.new_vhost_port = port
        reply_keyboard = [['Si'], ['No']]
        message = '''
        Confermi di voler creare un nuovo vhost con url *{url}* riferito alla porta *{port}*?
        Nota che se non hai ancora creato il dominio sul provider Caddy non funzionerà
        '''.format(url=CaddyBot.new_vhost_url,port=CaddyBot.new_vhost_port)
        update.message.reply_text(
                message,
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
                parse_mode=ParseMode.MARKDOWN)
        return CONFIRM_HOST_NEW


    def _create_new_vhost(self, bot, update):
        self.logger.info({'new-vhost': CaddyBot.new_vhost_url, 'port': CaddyBot.new_vhost_port})
        vhost_creation = vhosts_ops.new_vhost(address = CaddyBot.new_vhost_url, internal_port = CaddyBot.new_vhost_port)
        if vhost_creation:
            services_ops.restart_service()
            message = 'Vhost {} = {}:{} creato!'.format(CaddyBot.new_vhost_url, '127.0.0.1', CaddyBot.new_vhost_port)
            bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
        else:
            message = 'Vhost {} = {}:{} *non* creato!\nPrego controllare logs!'.format(CaddyBot.new_vhost_url, '127.0.0.1', CaddyBot.new_vhost_port)
            bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END

    def _new_cancel(self, bot, update):
        reply_markup = ReplyKeyboardRemove()
        message = 'Nessun vhost creato!'
        update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup)
        return ConversationHandler.END


if __name__ == '__main__':
    bot = CaddyBot()
    bot.start()
