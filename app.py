import os
import sys
import json
from logging import getLogger, Formatter, FileHandler, DEBUG, INFO
logger = getLogger(__name__)
file_handler = FileHandler("disson.log")
format = Formatter("%(asctime)s,%(message)s,", datefmt='%Y-%m-%d_%H:%M:%S')
#,[%(levelname)s]
file_handler.setFormatter(format)
logger.addHandler(file_handler)
logger.setLevel(INFO)

import discord
import openai
import deepl

data = { "hoge": "hoge", "fuga": "fuga" }

with open("config.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

intents = discord.Intents.all()
client = discord.Client(intents=intents)
TOKEN = os.environ['DISCORD_BOT_TOKEN']

translator = deepl.Translator(os.getenv("DEEPL_AUTH_KEY"))

openai.api_key = os.getenv("OPENAI_API_KEY")


def reclog(message):
    timestamp = message.created_at.strftime('%Y-%m-%d_%H:%M:%S')
    string = "[RECIVED],"
    string = string + f"{timestamp}, {message.author.name}#{message.author.discriminator}({message.author.id}),{message.content}"
    string = string + "," + str(len(message.content))
    logger.info(string)

def fromtranslog(result,timestamp):
    string = "[FROMTRANSLATE],"
    string = string + timestamp + ",," + str(result.text) + "," + str(len(result.text))
    logger.info(string)
    print(string)

def totranslog(retext,timestamp):
    string = "[TOTRANSLATE]," + timestamp + ",," + str(retext) + "," + str(len(retext))
    logger.info(string)
    print(string)

def sendlog(message,timestamp,p,c):
    string = "[SEND],"
    string = string + timestamp + ",," + str(message.content) + "," + str(len(message.content))
    string = string + "," + str(p) + "," + str(c)
    logger.info(string)
    print(string)

@client.event
async def on_ready():
    channel = client.get_channel(1156520755845148712)
    logger.info("Start")
    ##await channel.send("Start!")

@client.event
async def on_message(message):
    if message.author.bot:
        return
    else:
        timestamp = message.created_at.strftime('%Y-%m-%d_%H:%M:%S')
        reclog(message)

        result = translator.translate_text(message.content, target_lang="EN-US")
        fromtranslog(result,timestamp)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "nomal GPT4",
                },
                {
                    "role": "user",
                    "content": result.text,
                }
            ],
        )
        ptokens = response['usage']['prompt_tokens']
        ctokens = response['usage']['completion_tokens']
        restext = response['choices'][0]['message']['content']

        totranslog(restext,timestamp)

        jaresult = translator.translate_text(restext, target_lang="JA")
        await message.channel.send(jaresult.text)
        sendlog(message,timestamp,ptokens,ctokens)


client.run(TOKEN)