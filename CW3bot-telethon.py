import random

from time import time, sleep
from telethon import TelegramClient, events

api_hash = 'bb85650739037a67603d57146707722a'

api_id = 409382

game_id = 265204902

client = TelegramClient('CW3bot', api_id, api_hash)
client.start()

@client.on(events.NewMessage(from_users = game_id, pattern = r'Битва семи замков через'))
async def get_message_hero(event):
	print('Received message from bot')


if __name__ == '__main__':
	client.run_until_disconnected()