import random
import re

from time import time, sleep
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

api_hash = 'bb85650739037a67603d57146707722a'

api_id = 409382

game_id = 265204902

client = TelegramClient('CW3bot', api_id, api_hash)


def print_what_you_send(func):
    def wrap():
        pass

    return wrap


class Hero:
    # button's coordinates in main menu
    attack_button = (0, 0)
    def_button = (0, 1)
    quest_button = (0, 2)
    hero_button = (1, 0)
    custle_button = (2, 0)

    quests_button_list = {
        'forest_button': (0, 0),
        'corovan_button': (0, 1),
        'swamp_button': (1, 0),
        'valley_button': (1, 1),
        'arena_button': (2, 0)
    }

    # TODO: add arena buttons if need it

    def __init__(self, quests, forest, valley, swamp):
        print('Hero created')
        self.quests = quests
        self.forest = forest
        self.valley = valley
        self.swamp = swamp

        self.endurance = 0
        self.endurance_max = 0
        self.state = ''

    async def action(self, command, event):
        print('Sending: ', event.message.reply_markup.rows[command[0]].buttons[command[1]].text)
        await client.send_message(game_id, event.message.reply_markup.rows[command[0]].buttons[command[1]].text)

    def quest_declaration(self):

        declared_quests = []

        if self.forest:
            declared_quests.append('forest_button')
        if self.swamp:
            declared_quests.append('swamp_button')
        if self.valley:
            declared_quests.append('valley_button')

        return declared_quests


MyHero = Hero(True, True, False, False)


@client.on(events.NewMessage(from_users=game_id, pattern=r'Битва семи замков через|🌟Поздравляем! Новый уровень!🌟'))
async def get_message_hero(event):
    print('Received main message from bot')
    MyHero.endurance = int(re.search(r'Выносливость: (\d+)', event.raw_text).group(1))
    MyHero.endurance_max = int(re.search(r'Выносливость: (\d+)/(\d+)', event.raw_text).group(2))
    MyHero.state = re.search(r'Состояние:\n(.*)', event.raw_text).group(1)
    print('endurance: {0} / {1}, State: {2}'.format(MyHero.endurance, MyHero.endurance_max, MyHero.state))

    if MyHero.endurance > 0:  # if we have some endurance go to the quests area
        sleep(1)
        await MyHero.action(MyHero.quest_button, event)


# if bot ready to go to the quest. This func chooses one
@client.on(events.NewMessage(from_users=game_id, pattern=r'🌲Лес 5мин.'))
async def go_quest(event):
    sleep(random.randint(1, 3))
    # choose random enabled quest
    await MyHero.action(MyHero.quests_button_list[random.choice(MyHero.quest_declaration())], event)


if __name__ == '__main__':
    client.start()
    client.run_until_disconnected()
