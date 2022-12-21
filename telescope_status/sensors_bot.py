import telebot
import os, sys
import read_sensors_v3

##for this I use python3 and have to install the following packages
##pip3 install pyTelegramBotAPI
##pip3 install --upgrade pyTelegramBotAPI

API_KEY = "5653402781:AAE6NxmL09zU9Zu2zUuP2uCr3Qx1se_bifY"
roach_ip = "10.17.89.91"

bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=['temperature'])
def temperature(message):
    tn = read_sensors_v3.roach_connect(roach_ip)
    ambient, ppc, fpga, inlet, outlet = read_sensors_v3.read_temperatures(tn)
    ans = ("ambient : "+str(ambient)+"\n ppc :"+str(ppc)+
           "\n fpga: "+str(fpga)+ "\n inlet: "+str(inlet)+"\n outlet: "+str(outlet))
    bot.reply_to(message,ans)
    tn.close()


bot.polling()



