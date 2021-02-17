from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from telegram import Update
import logging
import pandas as pd
import os
import config as cfg
#from instApi import 
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

credDirPath = os.path.join(os.path.dirname(os.path.realpath(__file__)),"tgWS/credits") #cartella dove salvo i dataframe

USERNAME, PASSWD= 21, 12

if not os.path.exists("tgWS"):
    os.makedirs("tgWS")

def start(update, context):
    resp="Ciao {} ti dò il benvenuto su MastBot,\nPer una lista completa di comandi: /help".format(update.message.from_user.first_name)
    if not os.path.exists("tgWS/"+str(update.message.from_user.id)):
        os.makedirs("tgWS/"+str(update.message.from_user.id))
        os.makedirs("tgWS/"+str(update.message.from_user.id+"/stats"))

    context.bot.send_message(chat_id=update.message.from_user.id, text=resp)
    context.bot.delete_message(chat_id=update.message.from_user.id, message_id=update.message.message_id)

def help(update, context):
    resp="Command List:\n1. /login \n2. \n3."
    context.bot.send_message(chat_id=update.message.from_user.id, text=resp)
    #context.bot.delete_message(chat_id=update.message.from_user.id, message_id=update.message.message_id-1)
    context.bot.delete_message(chat_id=update.message.from_user.id, message_id=update.message.message_id)

def unknown(update, context):
    context.bot.delete_message(chat_id=update.message.from_user.id, message_id=update.message.message_id)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Non conosco questo comando, /help per vedere quelli disponibili.")


def login(update: Update, context: CallbackContext) -> int:
    resp="Per accedere ho bisogno della tuo username e password(Ricorda di disabilitare 2FA)\nLe tue credenziali non saranno salvate ma soltanto la sessione del browser.\nPer annullare /exit ."
    context.bot.send_message(chat_id=update.message.from_user.id, text=resp)
    context.bot.delete_message(chat_id=update.message.from_user.id, message_id=update.message.message_id)
    resp="Inserire username:"
    context.bot.send_message(chat_id=update.message.from_user.id, text=resp)
    return USERNAME

def username(update: Update, context: CallbackContext) -> int:
    unTable = pd.read_parquet(os.path.join(credDirPath,"usernameTable"))
    unTable=unTable.append({'tg_id':update.message.from_user.id,'username':update.message.text.replace(' ','')},ignore_index=True).drop_duplicates(subset='tg_id',keep="last")
    unTable.to_parquet(os.path.join(credDirPath,"usernameTable"), index=False)
    context.bot.delete_message(chat_id=update.message.from_user.id, message_id=(update.message.message_id)-1)
    context.bot.delete_message(chat_id=update.message.from_user.id, message_id=update.message.message_id)
    resp="Inserire password:"
    context.bot.send_message(chat_id=update.message.from_user.id, text=resp)
    return PASSWD

def passwd(update: Update, context: CallbackContext) -> int:
    unTable = pd.read_parquet(os.path.join(credDirPath,"usernameTable"))
    un=unTable[unTable["tg_id"]==update.message.from_user.id].iloc[0]["username"]
    pw=(update.message.text)
    print(un,pw)
    context.bot.delete_message(chat_id=update.message.from_user.id, message_id=(update.message.message_id)-1)
    context.bot.delete_message(chat_id=update.message.from_user.id, message_id=update.message.message_id)
    return ConversationHandler.END

def exit(update: Update, context: CallbackContext) -> int:
    return ConversationHandler.END

def pulisci(update: Update, context: CallbackContext):
    context.bot.delete_message(chat_id=update.message.from_user.id, message_id=update.message.message_id)




if __name__=="__main__":
    updater = Updater(token=cfg.TG_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    
    start_handler = CommandHandler('help', help)
    dispatcher.add_handler(start_handler)

    

  
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('login', login)],
        states={
            USERNAME: [MessageHandler(Filters.text & ~Filters.command, username)],
            PASSWD: [MessageHandler(Filters.text & ~Filters.command, passwd)],
        },
        fallbacks=[CommandHandler('exit', exit)],
    )
    dispatcher.add_handler(conv_handler)


    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    insulta_handler = MessageHandler(Filters.text |Filters.voice |Filters.video | Filters.photo | Filters.document, pulisci)
    dispatcher.add_handler(insulta_handler)



    #TODO conversation handler per il login
    updater.start_polling()
    updater.idle()


