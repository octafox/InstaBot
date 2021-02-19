from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
import logging
import pandas as pd
import os
import config as cfg
import chrome 
from datetime import datetime
from instApi import getALLFollowS, translateDfToTxt
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.WARNING)

credDirPath = os.path.join(os.path.dirname(os.path.realpath(__file__)),"tgWS/credits") #cartella dove salvo i dataframe

USERNAME, PASSWD, SEARCHUN, SHOW= 21, 12, 99, 98

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
    resp="Command List:\n1. /login \n2. /search\n3. /info"
    context.bot.send_message(chat_id=update.message.from_user.id, text=resp)
    #context.bot.delete_message(chat_id=update.message.from_user.id, message_id=update.message.message_id-1)
    context.bot.delete_message(chat_id=update.message.from_user.id, message_id=update.message.message_id)

def info(update, context):
    resp="Questo bot e le tutte librerie sono sviluppate da MAST e XEDOM sotto la community di OctaFox, l'intero progetto è pubblico su github sotto MIT License. Ci trovate su ts.octafox.it o simone@mastella.eu"
    context.bot.send_message(chat_id=update.message.from_user.id, text=resp)
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
    context.bot.delete_message(chat_id=update.message.from_user.id, message_id=(update.message.message_id)-1)
    context.bot.delete_message(chat_id=update.message.from_user.id, message_id=update.message.message_id)
    unTable = pd.read_parquet(os.path.join(credDirPath,"usernameTable"))
    un=unTable[unTable["tg_id"]==update.message.from_user.id].iloc[0]["username"]
    pw=(update.message.text)

    resp="Attendi qualche istante...\nTi dirò quando ho finito"
    resp=context.bot.send_message(chat_id=update.message.from_user.id, text=resp)

    browser = chrome.start(str(update.message.from_user.id),un,pw, forceLogin=True)
    browser.close()

    context.bot.delete_message(chat_id=update.message.from_user.id, message_id= resp.message_id)
    resp="Log In effettuato con SUCCESSO"
    context.bot.send_message(chat_id=update.message.from_user.id, text=resp)
    return ConversationHandler.END

def search(update: Update, context: CallbackContext) -> int:
    resp="Quale username vuoi cercare?"
    context.bot.send_message(chat_id=update.message.from_user.id, text=resp)
    context.bot.delete_message(chat_id=update.message.from_user.id, message_id=update.message.message_id)
    return SEARCHUN

def searchun(update: Update, context: CallbackContext) -> int:
    un=(update.message.text)
    context.bot.delete_message(chat_id=update.message.from_user.id, message_id=(update.message.message_id)-1)
    context.bot.delete_message(chat_id=update.message.from_user.id, message_id=update.message.message_id)
    resp="Attendi pazientemente la ricerca di tutti i dati..."
    resp=context.bot.send_message(chat_id=update.message.from_user.id, text=resp)
    new_stoping, new_stoped, new_adding, new_added = getALLFollowS(str(update.message.from_user.id),un,datetime.now())
    if new_stoping is None and new_stoped is None and new_adding is None and new_added is None:
        resp="Qualcosa è andato storto... Probabilmente "+un+" non esiste."
        context.bot.send_message(chat_id=update.message.from_user.id, text=resp)
        return ConversationHandler.END
    context.bot.delete_message(chat_id=update.message.from_user.id, message_id= resp.message_id)
    
    resp=str(len(new_adding))+" iniziati a seguire.\n"
    resp+=str(len(new_added))+" hanno aggiunto "+un+".\n"
    resp+=str(len(new_stoping))+" smessi di seguire.\n"
    resp+=str(len(new_stoped))+" non seguono più "+un+".\n"
    context.bot.send_message(chat_id=update.message.from_user.id, text=resp)
    reply_keyboard = [['si', 'no']]
    context.user_data["ag"]=new_adding
    context.user_data["ad"]=new_added
    context.user_data["sg"]=new_stoping
    context.user_data["sd"]=new_stoped
    context.user_data["un"]=un
    update.message.reply_text("Vuoi vedere di chi si tratta?",reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),)
    #TODO: aggiungere un messaggio e una inline keyboard per i risultati 
    return SHOW

def show(update: Update, context: CallbackContext) -> int:
    if update.message.text == "no":
        return ConversationHandler.END
    context.bot.delete_message(chat_id=update.message.from_user.id, message_id=update.message.message_id)
    new_adding= context.user_data["ag"]
    new_added= context.user_data["ad"]
    new_stoping= context.user_data["sg"]
    new_stoped= context.user_data["sd"]
    un= context.user_data["un"]

    resp=translateDfToTxt(str(update.message.from_user.id),new_adding,target="ing")
    if resp != "":
        resp= un+" HA SEGUITO:\n"+resp
        context.bot.send_message(chat_id=update.message.from_user.id, text=resp)
    
    resp=translateDfToTxt(str(update.message.from_user.id),new_added,target="ed")
    if resp != "":
        resp= "ACCOUNT CHE HANNO SEGUITO "+un+":\n"+resp
        context.bot.send_message(chat_id=update.message.from_user.id, text=resp)

    resp=translateDfToTxt(str(update.message.from_user.id),new_stoping,target="ing")
    if resp != "":
        resp= un+" HA SMESSO DI SEGUIRE:\n"+resp
        context.bot.send_message(chat_id=update.message.from_user.id, text=resp)

    resp=translateDfToTxt(str(update.message.from_user.id),new_stoped,target="ed")
    if resp != "":
        resp= "ACCOUNT CHE HANNO SMESSO DI SEGUIRE "+un+":\n"+resp
        context.bot.send_message(chat_id=update.message.from_user.id, text=resp)

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
    
    help_handler = CommandHandler('help', help)
    dispatcher.add_handler(help_handler)
 
    info_handler = CommandHandler('info', info)
    dispatcher.add_handler(info_handler)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('login', login)],
        states={
            USERNAME: [MessageHandler(Filters.text & ~Filters.command, username)],
            PASSWD: [MessageHandler(Filters.text & ~Filters.command, passwd)],
        },
        fallbacks=[CommandHandler('exit', exit)],
    )
    dispatcher.add_handler(conv_handler)

    search_handler = ConversationHandler(
        entry_points=[CommandHandler('search', search)],
        states={
            SEARCHUN: [MessageHandler(Filters.text & ~Filters.command, searchun)],
            SHOW: [MessageHandler(Filters.text & ~Filters.command, show)],
        },
        fallbacks=[CommandHandler('exit', exit)],
    )
    dispatcher.add_handler(search_handler)




    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    insulta_handler = MessageHandler(Filters.text |Filters.voice |Filters.video | Filters.photo | Filters.document, pulisci)
    dispatcher.add_handler(insulta_handler)



    updater.start_polling()
    updater.idle()


