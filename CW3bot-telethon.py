import random
import re

from time import time, sleep
from telethon import TelegramClient, events

api_hash = 'bb85650739037a67603d57146707722a'

api_id = 409382

game_id = 265204902

client = TelegramClient('CW3bot', api_id, api_hash)
client.start()

class Hero():

	def __init__(self):
		print('Hero created')
		self.endurance = 0
		self.endurance_max = 0
		self.state = ''



@client.on(events.NewMessage(from_users = game_id, pattern = r'Битва семи замков через'))
async def get_message_hero(event):
	print('Received message from bot')
	MyHero.endurance = re.search(r'Выносливость: (\d+)', event.raw_text).group(1)
	MyHero.endurance_max = re.search(r'Выносливость: (\d+)/(\d+)', event.raw_text).group(2)
	MyHero.state = re.search(r'Состояние:\n(.*)', event.raw_text).group(1)
	print('endurance: {0} / {1}, State: {2}'.format(MyHero.endurance, MyHero.endurance_max, MyHero.state))

if __name__ == '__main__':
	MyHero = Hero()
	client.run_until_disconnected()