#-*- coding:ISO-8859-1 -*-
import asyncio

import requests, pandas as pd, time, csv, traceback, discord, lxml, math
from threading import Thread
from twilio.rest import Client
leastAmount = 500000 #Least amount for it to send a message
api_key = ""
emailforopenfigi = ""


send = False


def clearLst():
    while True:
        with open('list_of_trades.csv', 'w') as f:
            f.write("Person,Price,Volume\n")
        time.sleep(86400)

def checkTrade(isin, price, volume):
    data = pd.read_csv('list_of_trades.csv')
    tradeList = []
    for index, row in data.iterrows():
        usedName = data.at[index, 'Person'].strip("[]'")

        tradeList = tradeList + [usedName]

    for lst in tradeList:
        if usedName in tradeList:
            return False
        else:
            return True
    else:
        print("trade list is empty")
        return True


def addTradeToList(person, price, volume):
    with open('list_of_trades.csv', 'a+') as f:
        list = str(person).split(), str(price).split(), str(volume).split()
        csv.writer(f, lineterminator='\n').writerow(list)

def getTicker(isin):
    try:
        url = 'https://api.openfigi.com/v1/mapping'
        headers = {'Content-Type': 'text/json', 'X-OPENFIGI-APIKEY': api_key}
        payload = '[{"idType":"ID_ISIN","idValue":"' + isin + '"}]'
        r = requests.post(url, headers=headers, data=payload)

        ticker = r.json()[0]["data"][0]["ticker"]
        return(ticker)
    except Exception as e:
        print(traceback.format_exc())



def sendSms(pris, volym, befattning, ticker, namn, valuta):
    try:
        # Your Account SID from twilio.com/console
        account_sid = ""
        # Your Auth Token from twilio.com/console
        auth_token = ""

        client = Client(account_sid, auth_token)

        message = client.messages.create(
            to="+",
            from_="+",
            body="" + str(befattning) + " köpte " + str(ticker) + " för " + str(float(pris)*float(volym)/1000000) + " M" + valuta +" i " + namn + " för " + str(pris) + " per aktie")
    except Exception as e:
        print(traceback.format_exc())



token = ''
class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await self.monitor()

    async def monitor(self):
        try:
            columns = ['Karaktär', 'Person i ledande ställning', 'ISIN', 'Volym', 'Pris']
            firstdf = pd.read_html('https://marknadssok.fi.se/publiceringsklient?Page=1', thousands=",")[0]
            print("Started!")

            while True:
                df = pd.read_html('https://marknadssok.fi.se/publiceringsklient?Page=1', thousands=None)[0]

                for index, row in df.iterrows():
                    if df.at[index, 'Karaktär'] == "Förvärv" and df.at[index, 'Instrumenttyp'] == 'Aktie':
                        isin = df.at[index, 'ISIN']
                        namn = df.at[index, 'Instrumentnamn']
                        volym = str(df.at[index, 'Volym']).replace(u'\xa0', "")  # Ta bort NBSP
                        pris = float(df.at[index, 'Pris'].replace(",", "."))  # Pris är utan comma
                        valuta = df.at[index, 'Valuta']
                        befattning = df.at[index, 'Befattning']
                        person = df.at[index, 'Person i ledande ställning']

                        if float(pris) * float(volym) >= leastAmount:
                            if checkTrade(isin, pris, volym):
                                if valuta == "SEK":
                                    print(isin, "is a new trade")
                                    addTradeToList(person, pris, volym)
                                    await self.sendTrade(pris, volym, befattning, getTicker(isin), namn, valuta)
                                else:
                                    print('found new trade', isin)
                                    addTradeToList(person, pris, volym)
                                    await self.sendTrade(pris, volym, befattning, getTicker(isin), namn, valuta)
                            else:
                                print(isin, "is not a new trade")

                print("Kollade sidan")
                await asyncio.sleep(300)  # Kolla sidan var 5:e minut
        except Exception as e:
            print(traceback.format_exc())
            id = 
            channel = self.get_channel(id)
            await channel.send(traceback.format_exc())
            await client.close()


    async def sendTrade(self, pris, volym, befattning, ticker, namn, valuta):
        id = 
        channel = self.get_channel(id)
        await channel.send("Befattninng: " + str(befattning)
                           + "\nTicker: " + str(ticker)
                           + "\nSumma: " + str(round(float(pris)*float(volym)/1000000, 3)) + " M" + valuta
                           +"\nNamn: " + namn
                           + "\nPris: " + str(pris) + " " + valuta + " per aktie" +
                           "\n----------------------------------")



if __name__ == '__main__':
    Thread(target=clearLst).start()
    client = MyClient()
    client.run(token)
