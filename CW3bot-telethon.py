import random
import re
import logging
import sys

from time import sleep
from datetime import datetime
from telethon import TelegramClient, events

api_hash = 'bb85650739037a67603d57146707722a'

api_id = 409382

game_id = 'ChatWarsBot'  # id of ChatWars3 bot

admin_id = 306869781

order_id = 614493767  # id of user/bot gives orders for battle

helper_id = 615010125  # helper bot's id

client = TelegramClient('CW3bot', api_id, api_hash)

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


class Hero:
	# button's coordinates in bot`s menu
	attack_button = '⚔️Атака'
	def_button = '🛡Защита'
	quest_button = '🗺Квесты'
	hero_button = '🏅Герой'
	castle_button = '🏰Замок'

	quests_button_list = {
		'forest': '🌲Лес',
		'corovan': '🗡ГРАБИТЬ КОРОВАНЫ',
		'swamp': '🍄Болото',
		'valley': '⛰️Долина',
		'arena': ''
	}

	current_time = datetime.now()

	# TODO: add arena buttons if need it

	def __init__(self, bot_enable, quests, forest, valley, swamp, corovan):
		logging.info('Hero created')
		self.bot_enable = bot_enable
		self.quests = quests
		self.forest = forest
		self.valley = valley
		self.swamp = swamp
		self.corovan = corovan

		self.quest_list = self.__quest_declaration()

		self.endurance = 0
		self.endurance_max = 0
		self.state = ''
		self.time_to_battle = 0

		self.delay = 300

		if not any([self.forest, self.valley, self.swamp]):
			print('There is no quests enabled. Quests switch is turned off now as well')
			self.quests = False

	@staticmethod
	def action(command):
		logging.info('Sending: {}'.format(command))
		client.send_message(game_id, command)

	def __quest_declaration(self):  # creates list with enabled quests during initialization

		declared_quests = []

		if self.forest:
			declared_quests.append('forest')
		if self.swamp:
			declared_quests.append('swamp')
		if self.valley:
			declared_quests.append('valley')

		return declared_quests


MyHero = Hero(bot_enable=True, quests=False, forest=True, valley=True, swamp=True, corovan=True)


@client.on(events.NewMessage(from_users=game_id, pattern=r'Битва семи замков через|🌟Поздравляем! Новый уровень!🌟'))
def get_message_hero(event):
	logging.info('Received main message from bot')
	MyHero.endurance = int(re.search(r'Выносливость: (\d+)', event.raw_text).group(1))
	MyHero.endurance_max = int(re.search(r'Выносливость: (\d+)/(\d+)', event.raw_text).group(2))
	MyHero.state = re.search(r'Состояние:\n(.*)', event.raw_text).group(1)

	if re.search(r'Битва семи замков через ?((\d+)ч\.)?( (\d+) ?(мин\.|минуты|минуту))?!', event.raw_text):

		try:
			hours = int(re.search(r'Битва семи замков через ?((\d+)ч\.)?( (\d+) ?(мин\.|минуты|минуту))?!',
								  event.raw_text).group(2))
		except TypeError:
			hours = 0

		try:
			minutes = int(re.search(r'Битва семи замков через ?((\d+)ч\.)?( (\d+) ?(мин\.|минуты|минуту))?!',
									event.raw_text).group(4))
		except TypeError:
			minutes = 0
		MyHero.time_to_battle = (hours if hours else 0) * 3600 + (minutes if minutes else 0) * 60  # convert to seconds

		logging.info('Time to battle: {0} : {1}. In seconds (approximately): {2}'.format(
			hours if hours else 0, minutes if minutes else 0, MyHero.time_to_battle))

	logging.info('endurance: {0} / {1}, State: {2}'.format(MyHero.endurance, MyHero.endurance_max, MyHero.state))

	MyHero.current_time = datetime.now()  # refresh current time

	if MyHero.endurance > 0 and MyHero.quests:
		if MyHero.state == '🛌Отдых':
			go_quest()
		else:
			logging.info('So busy for quests')

	# attack corovan between certain time
	if MyHero.endurance >= 2 and MyHero.corovan and 3 <= MyHero.current_time.hour <= 6:
		attack_corovan()


#  if MyHero.time_to_battle > 3600 and MyHero.endurance == 0:
#      logging.info('Time to battle > 1 hour and Endurance = 0. Delay = 30 min')
#      MyHero.delay = 1800


# if bot ready to go to the quest. This func chooses one
def go_quest():
	MyHero.action(MyHero.quest_button)
	sleep(random.randint(1, 3))
	# choose random quest from quest list and 'press' quest button
	MyHero.action(MyHero.quests_button_list[random.choice(MyHero.quest_list)])


def attack_corovan():
	MyHero.action(MyHero.quest_button)
	sleep(random.randint(1, 3))
	MyHero.action(MyHero.quests_button_list['corovan'])


@client.on(events.NewMessage(from_users=game_id, pattern=r'Ты заметил'))
def defend_corovan(event):
	MyHero.action('/go')
	logging.info('Your pledges are safe')


@client.on(events.NewMessage(from_users=admin_id))
def get_admin_message(event):
	if event.raw_text == 'help':
		client.send_message(admin_id, '\n'.join([
			'quest_on/off',
			'corovan_on/off',
			'bot_on/off',
			'forest_on/off',
			'swamp_on/off',
			'valley_off',
			'status'
		]))
	elif event.raw_text == 'quest_off':
		MyHero.quests = False
		client.send_message(admin_id, 'Quests disabled')
	elif event.raw_text == 'corovan_off':
		MyHero.corovan = False
		client.send_message(admin_id, 'Corovans disabled')
	elif event.raw_text == 'bot_off':
		MyHero.bot_enable = False
		client.send_message(admin_id, 'Bot disabled')
	elif event.raw_text == 'valley_off':
		MyHero.valley = False
		quest_switch_off('valley')
	elif event.raw_text == 'forest_off':
		MyHero.forest = False
		quest_switch_off('forest')
	elif event.raw_text == 'swamp_off':
		MyHero.swamp = False
		quest_switch_off('swamp')
	elif event.raw_text == 'quest_on':
		MyHero.quests = True
		client.send_message(admin_id, 'Quests enabled')
	elif event.raw_text == 'corovan_on':
		MyHero.corovan = True
		client.send_message(admin_id, 'Corovans enabled')
	elif event.raw_text == 'bot_on':
		MyHero.bot_enable = True
		client.send_message(admin_id, 'Bot enabled')
	elif event.raw_text == 'forest_on':
		MyHero.forest = True
		quest_switch_on('forest')
	elif event.raw_text == 'swamp_on':
		MyHero.swamp = True
		quest_switch_on('swamp')
	elif event.raw_text == 'valley_on':
		MyHero.valley = True
		quest_switch_on('valley')
	elif event.raw_text == 'status':
		client.send_message(admin_id, '\n'.join([
			str(MyHero.quest_list),
			'quest = ' + str(MyHero.quests),
			'corovan = ' + str(MyHero.corovan),
			'bot = ' + str(MyHero.bot_enable)
		]))


@client.on(events.NewMessage(from_users=game_id, pattern='After a successful act of'))
def pledge(event):
	logging.info('We got pledge!')
	MyHero.action('/pledge')


def quest_switch_on(quest_name):
	if quest_name not in MyHero.quest_list:
		MyHero.quest_list.append(quest_name)
		client.send_message(admin_id, quest_name + ' added to quests list')
		if not MyHero.quests:
			client.send_message(admin_id, 'Quest switch is off. Turn in on')

	else:
		client.send_message(admin_id, quest_name + ' already in list')

	client.send_message(admin_id, 'Quest list: ' + str(MyHero.quest_list))


def quest_switch_off(quest_name):
	if quest_name in MyHero.quest_list:
		MyHero.quest_list.remove(quest_name)
		client.send_message(admin_id, quest_name + ' deleted from quest list')
		if not MyHero.quest_list:
			client.send_message(admin_id, 'list is empty')
			MyHero.quests = False

	else:
		client.send_message(admin_id, quest_name + ' is not in list')


@client.on(events.NewMessage(from_users=order_id, pattern=r'⚔️(🐢|🍁|🌹|☘️|🦇|🖤|🍆)'))
def get_order(event):
	order = re.search(r'⚔️(🐢|🍁|🌹|☘️|🦇|🖤|🍆)', event.raw_text).group(1)
	MyHero.action(order)


@client.on(events.NewMessage(from_users=helper_id, pattern=r'Изменения в вашем стоке:'))
def get_report_from_battle(event):
	MyHero.action('/report')


@client.on(events.NewMessage(from_users=game_id, pattern='.+\nТвои результаты в бою:'))
def send_report(event):
	client.forward_messages(helper_id, event.message)


def worker():
	while True:

		try:
			if MyHero.bot_enable:

				MyHero.action('🏅Герой')
				logging.info('Delay = {}'.format(MyHero.delay))

				MyHero.current_time = datetime.now()
				if MyHero.current_time.hour >= 23 or MyHero.current_time.hour <= 6:
					MyHero.delay = random.randint(600, 800)  # increase delay at night
				else:
					MyHero.delay = random.randint(300, 500)

			else:
				logging.info('Bot is going to sleep')
				break
		except Exception as error:
			logging.info('Some trouble in worker: {}'.format(error))


if __name__ == '__main__':
	client.start()
	try:

		# async_loop = asyncio.get_event_loop()
		# if MyHero.bot_enable:
		#	async_loop.run_until_complete(worker())
		client.run_until_disconnected()
	except KeyboardInterrupt:
		client.disconnect()
		logging.info('Keyboard interrupt')
		sys.exit(0)
