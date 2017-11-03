import os
import logging

from telegram.ext import Updater
from telegram.ext import CommandHandler

from config import Config

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
        ## Define Updater class
        self.updater = Updater(token = self.TOKEN)
        ## Definition of logger
        self.logger = logging.getLogger('')
        if self.DEBUG:
            logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s')
        else:
            logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s')
        self.logger.debug('Finished __init__')

    def start(self):
        if self.WEBHOOKS:
            self.logger.info('Using webhooks configuration...')
            self.updater.start_webhook(listen='127.0.0.1',
                                       key=Config['key_file'],
                                       cert=Config['cert_file'],
                                       webhook_url='https://caddybot.bonny.pw/'+self.TOKEN,
                                       port=self.PORT,
                                       url_path=self.TOKEN)
        else:
            self.logger.info('Using polling configuration...')
            self.updater.start_polling()
        self.updater.idle()

if __name__ == '__main__':
    bot = CaddyBot()
    bot.start()