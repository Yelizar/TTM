import telepot
bot_token = '867027665:AAGdRxN7xHNussXH5BvOTj_tvVXv_RGzvE4'
bot = telepot.Bot(bot_token)
bot.setWebhook('https://82236e30.ngrok.io/tplatform/{bot_token}'.format(bot_token=bot_token))