import random
import re
import asyncio
import logging
import sys


from datetime import datetime
from telethon import TelegramClient, events

api_hash = 'bb85650739037a67603d57146707722a'

api_id = 409382

game_id = 265204902

client = TelegramClient('CW3bot', api_id, api_hash)

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)


def print_what_you_send(func):
    def wrap():
        pass

    return wrap


class Hero:
    # button's coordinates in bot`s menu
    attack_button = '⚔️Атака'
    def_button = '🛡Защита'
    quest_button = '🗺Квесты'
    hero_button = '🏅Герой'
    custle_button = '🏰Замок'

    quests_button_list = {
        'forest_button': '🌲Лес',
        'corovan_button': '🗡ГРАБИТЬ КОРОВАНЫ',
        'swamp_button': '🍄Болото',
        'valley_button': '⛰️Долина',
        'arena_button': ''
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
            declared_quests.append('forest_button')
        if self.swamp:
            declared_quests.append('swamp_button')
        if self.valley:
            declared_quests.append('valley_button')

        return declared_quests


MyHero = Hero(bot_enable=True, quests=True, forest=True, valley=True, swamp=True, corovan=True)


@client.on(events.NewMessage(from_users=game_id, pattern=r'Битва семи замков через|🌟Поздравляем! Новый уровень!🌟'))
async def get_message_hero(event):
    logging.info('Received main message from bot')
    MyHero.endurance = int(re.search(r'Выносливость: (\d+)', event.raw_text).group(1))
    MyHero.endurance_max = int(re.search(r'Выносливость: (\d+)/(\d+)', event.raw_text).group(2))
    MyHero.state = re.search(r'Состояние:\n(.*)', event.raw_text).group(1)

    if re.search(r'Битва семи замков через ?((\d+)ч\.)?( (\d+) ?(мин\.|минуты|минуту))?!', event.raw_text):

        hours = int(re.search(r'Битва семи замков через ?((\d+)ч\.)?( (\d+) ?(мин\.|минуты|минуту))?!',
                              event.raw_text).group(2))
        minutes = int(re.search(r'Битва семи замков через ?((\d+)ч\.)?( (\d+) ?(мин\.|минуты|минуту))?!',
                                event.raw_text).group(4))

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

    if MyHero.time_to_battle > 3600 and MyHero.endurance == 0:
        logging.info('Time to battle > 1 hour and Endurance = 0. Delay = 30 min')
        MyHero.delay = 1800


# if bot ready to go to the quest. This func chooses one
async def go_quest():
    await client.send_message(game_id, MyHero.quest_button)
    await asyncio.sleep(random.randint(1, 3))
    # choose random quest from quest list and 'press' quest button
    await client.send_message(game_id, MyHero.quests_button_list[random.choice(MyHero.quest_list)])


async def attack_corovan():
    await client.send_message(game_id, MyHero.quest_button)
    await asyncio.sleep(random.randint(1, 3))
    await client.send_message(game_id, MyHero.quests_button_list['corovan_button'])


@client.on(events.NewMessage(from_users=game_id, pattern=r'Ты заметил'))
async def defend_corovan(event):
    await client.send_message(game_id, '/go')
    logging.info('Your pledges are safe')


async def worker():
    while True:

        if MyHero.bot_enable:

            MyHero.current_time = datetime.now()
            await MyHero.action('🏅Герой')

            if MyHero.current_time.hour >= 23 or MyHero.current_time.hour <= 6:
                MyHero.delay = random.randint(600, 800)  # increase delay at night
            else:
                MyHero.delay = random.randint(300, 500)

            await asyncio.sleep(MyHero.delay)


if __name__ == '__main__':
    client.start()

    try:
        ioloop = asyncio.get_event_loop()
        ioloop.run_until_complete(worker())
        client.run_until_disconnected()
    except KeyboardInterrupt:
        ioloop.close()
        logging.info('Keyboard interrupt')
        sys.exit(0)


