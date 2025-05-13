from telethon import TelegramClient
from telethon.sessions import StringSession

from config import SESSION_STRING, API_ID, API_HASH, channels, for_regex

from datetime import datetime, timezone, timedelta

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

MOSCOW_TZ = timezone(timedelta(hours=3))

async def fetch_todays_messages():
    today_start = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=MOSCOW_TZ)
    all_messages = []
    
    for channel in channels:
        entity = await client.get_entity(channel)
        async for message in client.iter_messages(entity):
            if message.date > today_start:
                break

            if message.text:
                all_messages.append({
                    'text': message.text,
                    'date': message.date,
                    'channel': channel,
                    'views': message.views
                })
    
    return all_messages


def filter_messages(ticker, messages):
    matched = []
    for message in messages:
        for kw in for_regex[ticker]:
            if kw.lower() in message['text'].lower():
                matched.append(message)
                break
    matched.sort(key=lambda el: -el['views'])
    return matched[:5]


async def get_news_for(ticker):
    async with client:
        today_messages = await fetch_todays_messages()
    return filter_messages(ticker, today_messages)
