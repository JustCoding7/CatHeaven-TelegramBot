import requests
import json
import random
import telebot
from flask import Flask,request
from telebot import types as tp

# Credentials
token = '<Bot-Token>'
secret = '<Client-Secret>'
url = '<Webhook-URL>' + secret

# APIs Used
TheCatAPI = 'https://api.thecatapi.com/v1/images/search'
RandomFact = 'https://some-random-api.ml/facts/cat'
RandomCat = 'https://some-random-api.ml/img/cat'


# Bot and Webhook setup
bot = telebot.TeleBot(token,threaded=False)
bot.remove_webhook()
bot.set_webhook(url=url)

app = Flask(__name__)
@app.route('/'+secret,methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok',200

# Functions to make bot do something
@bot.message_handler(commands=['start','help'])
def info(msg):
    '''Just a Start and Help Message.'''

    stickers = ['CAACAgQAAxkBAAJ-3V_VMUfP-SGwAqLx1QUVjY8zFPkgAAJrAAPOOQgNWWbqY3aSS9AeBA','CAACAgQAAxkBAAJ-3l_VMUc9OAAB1zKdGciGas8grPsVOwACcAADzjkIDZMJAAG9MCuf2x4E','CAACAgQAAxkBAAJ-31_VMUcpY3fVCg0OSpsBOvNMRfFkAAJXAAPOOQgNJ_X95v16SYYeBA','CAACAgQAAxkBAAJ-4F_VMUf-Amxpskmxx42Aet2Z6ne_AAJAAAPOOQgNUZwB0Ax-hi8eBA','CAACAgQAAxkBAAJ-4l_VMUe10NcORnwaDSRCyaIckLlmAAKMAAPOOQgNIejK3IKPfGUeBA','CAACAgQAAxkBAAJ-4V_VMUfuSSMap9Rxae4Fp1nr-j5rAAKmAAPOOQgNP6D-YMP1bPYeBA','CAACAgQAAxkBAAJ-41_VMUeihhOn0toylHFWp2k4dsx1AAKNAAPOOQgNdJBOIeLESeAeBA']
    r_sticker = random.choice(stickers)
    bot.send_message(msg.chat.id,'*Hello, Welcome to Cat Heaven.*\nWant more cats in your life? I got you covered.\nUse - /cat, /gif, /pic, /fact', parse_mode='markdown')
    bot.send_sticker(msg.chat.id,r_sticker)

@bot.message_handler(commands=['cat'])
def cat(msg):
    '''Sends random cat images and gifs using The Cat API'''

    response = requests.get(TheCatAPI).json()[0]
    pic = response['url']

    main = tp.InlineKeyboardMarkup(row_width=2)
    link = tp.InlineKeyboardButton('Link',url=pic)
    file_ = tp.InlineKeyboardButton('File',callback_data=f'{pic}|file')

    if pic.endswith('png') or pic.endswith('jpg'):
        main.add(link,file_)
        bot.send_photo(msg.chat.id,pic,reply_markup=main)
    if pic.endswith('gif'):
        main.add(link)
        bot.send_animation(msg.chat.id,pic,reply_markup=main)

@bot.message_handler(commands=['gif'])
def gif(msg):
    '''Sends only Gifs from The Cat API'''

    response = requests.get(TheCatAPI+'?mime_types=gif').json()[0]
    pic = response['url']

    main = tp.InlineKeyboardMarkup(row_width=1)
    link = tp.InlineKeyboardButton('Link',url=pic)
    main.add(link)

    bot.send_animation(msg.chat.id,pic,reply_markup=main)

@bot.message_handler(commands=['pic'])
def pics(msg):
    '''Sends only Images from The Cat API '''

    response = requests.get(TheCatAPI+'?mime_types={}'.format(random.choice(['png','jpg']))).json()[0]
    pic = response['url']

    main = tp.InlineKeyboardMarkup(row_width=2)
    link = tp.InlineKeyboardButton('Link',url=pic)
    file_ = tp.InlineKeyboardButton('File',callback_data=f'{pic}|file')
    main.add(link,file_)

    bot.send_photo(msg.chat.id,pic,reply_markup=main)

@bot.message_handler(commands=['fact'])
def fact(msg):
    '''Sends Cat facts with an image attached.'''

    fact_ = requests.get(RandomFact).json()['fact']
    cat_ = requests.get(RandomCat).json()['link']

    main = tp.InlineKeyboardMarkup(row_width=2)
    next_ = tp.InlineKeyboardButton('Next',callback_data='next')
    delete_ = tp.InlineKeyboardButton('Delete',callback_data='delete')
    main.add(delete_,next_)

    bot.send_photo(msg.chat.id,cat_,caption=f'*{fact_}*',parse_mode='markdown',reply_markup=main)


# Callback handlers to provide links, files, etc.
@bot.callback_query_handler(func=lambda call:call.data.endswith('file'))
def file(call):
    '''Sends the File when File button is pressed.''' 

    bot.send_document(call.message.chat.id,call.data.split('|')[0])


@bot.callback_query_handler(func=lambda call:call.data == 'next')
def next_fact(call):
    '''Sends Next Fact when Next button is pressed.'''

    fact_ = requests.get(RandomFact).json()['fact']
    cat_ = requests.get(RandomCat).json()['link']

    main = tp.InlineKeyboardMarkup(row_width=2)
    next_ = tp.InlineKeyboardButton('Next',callback_data='next')
    delete_ = tp.InlineKeyboardButton('Delete',callback_data='delete')
    main.add(delete_,next_)

    bot.edit_message_media(tp.InputMediaPhoto(cat_),chat_id=call.message.chat.id,message_id=call.message.message_id)
    bot.edit_message_caption(caption=f'*{fact_}*',parse_mode='markdown',chat_id=call.message.chat.id,message_id=call.message.message_id,reply_markup=main)

@bot.callback_query_handler(func=lambda call:call.data == 'delete')
def delete_fact(call):
    '''Deletes the message when Delete button is pressed'''

    bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)