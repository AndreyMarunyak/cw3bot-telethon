import random
import re
import asyncio
import logging
import sys
from threading import Thread

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
    custle_button = '🏰Замок'

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

    async def action(self, command):
        logging.info('Sending: {}'.format(command))
        await client.send_message(game_id, command)

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
async def get_message_hero(event):
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
            await go_quest()
        else:
            logging.info('So busy for quests')

    # attack corovan between certain time
    if MyHero.endurance >= 2 and MyHero.corovan and 3 <= MyHero.current_time.hour <= 6:
        await attack_corovan()

    # TODO: fix this bad part
    if MyHero.time_to_battle > 3600 and MyHero.endurance == 0:
        logging.info('Time to battle > 1 hour and Endurance = 0. Delay = 30 min')
        MyHero.delay = 1800


# if bot ready to go to the quest. This func chooses one
async def go_quest():
    await MyHero.action(quest_button)
    await asyncio.sleep(random.randint(1, 3))
    # choose random quest from quest list and 'press' quest button
    await MyHero.action(quests_button_list[random.choice(MyHero.quest_list)])


async def attack_corovan():
    await MyHero.action(quest_button)
    await asyncio.sleep(random.randint(1, 3))
    await MyHero.action(quests_button_list['corovan'])


@client.on(events.NewMessage(from_users=game_id, pattern=r'Ты заметил'))
async def defend_corovan(event):
    await MyHero.action('/go')
    logging.info('Your pledges are safe')


@client.on(events.NewMessage(from_users=admin_id))
async def get_admin_message(event):
    if event.raw_text == 'help':
        await client.send_message(admin_id, '\n'.join([
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
        await client.send_message(admin_id, 'Quests disabled')
    elif event.raw_text == 'corovan_off':
        MyHero.corovan = False
        await client.send_message(admin_id, 'Corovans disabled')
    elif event.raw_text == 'bot_off':
        MyHero.bot_enable = False
        async_loop.close()
        await client.send_message(admin_id, 'Bot enabled')
    elif event.raw_text == 'valley_off':
        MyHero.valley = False
        await quest_switch_off('valley')
    elif event.raw_text == 'forest_off':
        MyHero.forest = False
        await quest_switch_off('forest')
    elif event.raw_text == 'swamp_off':
        MyHero.swamp = False
        await quest_switch_off('swamp')
    elif event.raw_text == 'quest_on':
        MyHero.quests = True
        await client.send_message(admin_id, 'Quests enabled')
    elif event.raw_text == 'corovan_on':
        MyHero.corovan = True
        await client.send_message(admin_id, 'Corovans enabled')
    elif event.raw_text == 'bot_on':
        MyHero.bot_enable = True
        await client.send_message(admin_id, 'Bot enabled')
    elif event.raw_text == 'forest_on':
        MyHero.forest = True
        await quest_switch_on('forest')
    elif event.raw_text == 'swamp_on':
        MyHero.swamp = True
        await quest_switch_on('swamp')
    elif event.raw_text == 'valley_on':
        MyHero.valley = True
        await quest_switch_on('valley')
    elif event.raw_text == 'status':
        await client.send_message(admin_id, '\n'.join([
            str(MyHero.quest_list),
            'quest = ' + str(MyHero.quests),
            'corovan = ' + str(MyHero.corovan),
            'bot = ' + str(MyHero.bot_enable)
        ]))


@client.on(events.NewMessage(from_users=game_id, pattern='After a successful act of'))
async def pledge(event):
    logging.info('We got pledge!')
    await MyHero.action('/pledge')


async def quest_switch_on(quest_name):
    if quest_name not in MyHero.quest_list:
        MyHero.quest_list.append(quest_name)
        await client.send_message(admin_id, quest_name + ' added to quests list')
        if not MyHero.quests:
            await client.send_message(admin_id, 'Quest switch is off. Turn in on')

    else:
        await client.send_message(admin_id, quest_name + ' already in list')

    await client.send_message(admin_id, 'Quest list: ' + str(MyHero.quest_list))


async def quest_switch_off(quest_name):
    if quest_name in MyHero.quest_list:
        MyHero.quest_list.remove(quest_name)
        await client.send_message(admin_id, quest_name + ' deleted from quest list')
        if not MyHero.quest_list:
            await client.send_message(admin_id, 'list is empty')
            MyHero.quests = False

    else:
        await client.send_message(admin_id, quest_name + ' is not in list')


@client.on(events.NewMessage(from_users=order_id, pattern=r'⚔️(🐢|🍁|🌹|☘️|🦇|🖤|🍆)'))
async def get_order(event):
    order = re.search(r'⚔️(🐢|🍁|🌹|☘️|🦇|🖤|🍆)', event.raw_text).group(1)
    await MyHero.action(order)


@client.on(events.NewMessage(from_users=helper_id, pattern=r'Изменения в вашем стоке:'))
async def get_report_from_battle(event):
    await MyHero.action('/report')


@client.on(events.NewMessage(from_users=game_id, pattern='.+\nТвои результаты в бою:'))
async def send_report(event):
    await client.forward_messages(helper_id, event.message)


async def worker():
    while True:

        try:
            if MyHero.bot_enable:

                MyHero.current_time = datetime.now()
                await MyHero.action('🏅Герой')

                if MyHero.current_time.hour >= 23 or MyHero.current_time.hour <= 6:
                    MyHero.delay = random.randint(600, 800)  # increase delay at night
                else:
                    MyHero.delay = random.randint(300, 500)

                if MyHero.current_time.hour == 7:
                    MyHero.delay = 14400

                await asyncio.sleep(MyHero.delay)
        except Exception as error:
            logging.info('Some trouble in worker: {}'.format(error))


if __name__ == '__main__':
    client.start()
    try:
        client.run_until_disconnected()
    # async_loop = asyncio.get_event_loop()
    # async_loop.run_until_complete(worker())
    except KeyboardInterrupt:
        async_loop.close()
        logging.info('Keyboard interrupt')
        sys.exit(0)
