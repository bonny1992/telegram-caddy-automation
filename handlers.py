from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram import ParseMode

GET_HOST_NEW, GET_PORT_NEW, CONFIRM_HOST_NEW = range(3)

def new():
    new_handler = ConversationHandler(
        entry_points = [CommandHandler('new', self._new)],
        states = {
            GET_HOST_NEW: [MessageHandler(Filters.text, self._new_vhost_port)],
            GET_PORT_NEW: [MessageHandler(Filters.text, self._confirm_new_vhost)],
            CONFIRM_HOST_NEW: [RegexHandler('^(Si)$', self._create_new_vhost),
                               RegexHandler('^(No)$', self._new_cancel),]
        },
        fallbacks = [CommandHandler('cancel', self._new_cancel)]


@restricted
def _new(self, bot, update):
    self.logger.info('New Vhost creation started by {id}'.format(id=update.effective_user.id))
    message = 'Inserisci il dominio del nuovo vhost che vuoi creare.\nCancella con /cancel'
    bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
    return GET_HOST_NEW

new_vhost_url = ''
new_vhost_port = ''

@restricted
def _new_vhost_port(self, bot, update):
    url = str(update.message.text).strip()
    CaddyBot.new_vhost_url = url.lower()
    message = 'Inserisci la porta del servizio.'
    bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
    return GET_PORT_NEW

@restricted
def _confirm_new_vhost(self, bot, update):
    port = str(update.message.text).strip()
    CaddyBot.new_vhost_port = port
    reply_keyboard = [['Si'], ['No']]
    message = '''Confermi di voler creare un nuovo vhost con url *{url}* riferito alla porta *{port}*?
                 Nota che se non hai ancora creato il dominio sul provider Caddy non funzionerà'''.format(url=CaddyBot.new_vhost_url,
                                                                                                          port=CaddyBot.new_vhost_port)
    update.message.reply_text(
            message,
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
            parse_mode=ParseMode.MARKDOWN)
    return CONFIRM_HOST_NEW

def _create_new_vhost(self, bot, update):
    self.logger.info({'new-vhost': CaddyBot.new_vhost_url, 'port': CaddyBot.new_vhost_port})
    try:
        vhosts_ops.new_vhost(address = CaddyBot.new_vhost_url, internal_port = CaddyBot.new_vhost_port)
        message = 'Vhost {} = {}:{} creato!'.format(CaddyBot.new_vhost_url, '127.0.0.1', CaddyBot.new_vhost_port)
        bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
    except:
        message = 'Vhost {} = {}:{} *non* creato!\nPrego controllare logs!'.format(CaddyBot.new_vhost_url, '127.0.0.1', CaddyBot.new_vhost_port)
        bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
    finally:
        return ConversationHandler.END
