import random
import re
import asyncio

from time import time, sleep
from datetime import datetime
from telethon import TelegramClient, events


api_hash = 'bb85650739037a67603d57146707722a'

api_id = 409382

game_id = 265204902

client = TelegramClient('CW3bot', api_id, api_hash)


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

    def __init__(self, quests, forest, valley, swamp, corovan):
        print(self.current_time, 'Hero created')
        self.quests = quests
        self.forest = forest
        self.valley = valley
        self.swamp = swamp
        self.corovan = corovan

        self.quest_list = self.quest_declaration()

        self.endurance = 0
        self.endurance_max = 0
        self.state = ''

        self.delay = 300

        if not any([self.forest, self.valley, self.swamp]):
            print('There is no quests enabled. Quests switch is turned off now as well')
            self.quests = False

    async def action(self, command):
        print('Sending: ', command)
        await client.send_message(game_id, command)

    def quest_declaration(self):

        declared_quests = []

        if self.forest:
            declared_quests.append('forest_button')
        if self.swamp:
            declared_quests.append('swamp_button')
        if self.valley:
            declared_quests.append('valley_button')

        return declared_quests


MyHero = Hero(False, False, True, True, True)


@client.on(events.NewMessage(from_users=game_id, pattern=r'Битва семи замков через|🌟Поздравляем! Новый уровень!🌟'))
async def get_message_hero(event):

    print('Received main message from bot')
    MyHero.endurance = int(re.search(r'Выносливость: (\d+)', event.raw_text).group(1))
    MyHero.endurance_max = int(re.search(r'Выносливость: (\d+)/(\d+)', event.raw_text).group(2))
    MyHero.state = re.search(r'Состояние:\n(.*)', event.raw_text).group(1)
    print('endurance: {0} / {1}, State: {2}'.format(MyHero.endurance, MyHero.endurance_max, MyHero.state))

    if MyHero.endurance > 0 and MyHero.quests:
        await go_quest()

    if MyHero.endurance >= 2 and MyHero.corovan:
        pass


# if bot ready to go to the quest. This func chooses one
async def go_quest():
    await client.send_message(game_id, MyHero.quest_button)
    await asyncio.sleep(random.randint(1, 3))
    await client.send_message(game_id, random.choice(MyHero.quest_list))


async def attack_corovan():
    await client.send_message(game_id, MyHero.quest_button)
    await asyncio.sleep(random.randint(1, 3))
    await client.send_message(game_id, MyHero.quests_button_list['corovan_button'])


async def worker():

    while True:
        MyHero.current_time = datetime.now()
        await client.send_message(game_id, '🏅Герой')

        await asyncio.sleep(MyHero.delay)


if __name__ == '__main__':
    client.start()
    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(worker())
    ioloop.close()
    client.run_until_disconnected()
