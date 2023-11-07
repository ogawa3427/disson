import os
import re
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
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
model=config["model"]
ignore_channel = config["ignore_channel"]
import asyncio



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

def sendlog(mess,timestamp,p,c):
    string = "[SEND],"
    string = string + timestamp + ",," + str(mess) + "," + str(len(mess))
    string = string + "," + str(p) + "," + str(c)
    logger.info(string)
    print(string)


async def get_completion(prompt):
    # 非同期でAPIに問い合わせ
    completion = await openai.AsyncCompletions.create(
        engine=model,  # 使用するモデルを指定
        prompt=prompt,
        max_tokens=150  # 返答の最大トークン数を指定
    )
    return completion.choices[0].text.strip()

async def main():
    prompt = "こんにちは"
    response = await get_completion(prompt)
    print(response)

    # 結果を出力
   

@client.event
async def on_ready():
    logger.info("Start")
    ##await channel.send("Start!")

@client.event
async def on_message(message):
    print("RECIEVED")
    content = message.content
    if message.channel.id == ignore_channel:
        print("ignore")
        return
    if message.author.bot:
        return
    else:
        timestamp = message.created_at.strftime('%Y-%m-%d_%H:%M:%S')
        reclog(message)

        if client.user in message.mentions:
            content = re.sub(r'<@\d+>', '', content)
            print(content)

            # OpenAI API 非同期呼び出し
            response = await openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "nomal GPT4"},
                    {"role": "user", "content": content},
                ],
            )
            ptokens = response['usage']['prompt_tokens']
            ctokens = response['usage']['completion_tokens']
            restext = response['choices'][0]['message']['content']

            await message.channel.send(restext)
            sendlog(restext, timestamp, ptokens, ctokens)
            return
        else:
            # DeepL API 非同期呼び出し
            result = await translator.translate_text(message.content, target_lang="EN-US")
            fromtranslog(result, timestamp)

            # OpenAI API 非同期呼び出し
            response = await openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "nomal GPT4"},
                    {"role": "user", "content": result.text},
                ],
            )
            ptokens = response['usage']['prompt_tokens']
            ctokens = response['usage']['completion_tokens']
            restext = response['choices'][0]['message']['content']

            totranslog(restext, timestamp)

            # DeepL API 非同期呼び出し
            jaresult = await translator.translate_text(restext, target_lang="JA")
            sendlog(jaresult.text, timestamp, ptokens, ctokens)
            await message.channel.send(jaresult.text)



#client.run(TOKEN)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())