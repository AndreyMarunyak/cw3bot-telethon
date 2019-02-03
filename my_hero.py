import logging
from time import sleep, time
from datetime import datetime
import random

GAME_ID = 'ChatWarsBot'

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

    def __init__(self, bot_enable, quests, forest, valley, swamp, corovan, client):
        logging.info('Hero created')
        self.bot_enable = bot_enable
        self.quests = quests
        self.forest = forest
        self.valley = valley
        self.swamp = swamp
        self.corovan = corovan
        self.client = client

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
    def action(self, command):
        sleep(random.randint(2, 3))
        logging.info('Sending: {}'.format(command))
        self.client.send_message(GAME_ID, command)

    def __quest_declaration(self):  # creates list with enabled quests during initialization

        declared_quests = []

        if self.forest:
            declared_quests.append('forest')
        if self.swamp:
            declared_quests.append('swamp')
        if self.valley:
            declared_quests.append('valley')

        return declared_quests

    def is_bot_enabled(self):
        if self.bot_enable:
            return True
        return False